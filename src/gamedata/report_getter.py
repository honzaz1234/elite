import json

import gamedata.ts_parser as ts_parser
import gamedata.pbp_parser as pbp_parser

from datetime import datetime, timedelta

from common_functions import get_valid_request
from decorators import repeat_request_until_success
from logger.logger import logger


def generate_dates_between(start_date: str, end_date: str):
    """Generate a list of dates between two given dates in YYYY-MM-DD format."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]


def convert_season_format(season: str) -> str:
    """Convert season format from YYYY-YY to YYYYYYYY, handling the special case of 1999-00."""
    parts = season.split("–")
    if parts[1] == "00":
        full_year = "2000"
    else:
        full_year = parts[0][:2] + parts[1]  # Extract century from first part and append second part
    return parts[0] + full_year


class ReportIDGetter():


    def __init__(self):
        with open("./src/gamedata/season_ranges.json", "r") as f:
            self.season_ranges = json.load(f)

    
    def get_selected_season_ids(self, selected_seasons: list=None) -> dict:
        if selected_seasons is None:
            selected_seasons = self.season_ranges.keys()
        report_ids = {
            season: self.get_season_ids(
                season_ranges_dict=self.season_ranges[season],
                season=season)
            for season in self.season_ranges if season in selected_seasons
        }

        return report_ids


    def get_season_ids(
            self, season_ranges_dict: dict, season: str, 
            scraped_data: dict=None) -> dict:
        if scraped_data == None:
            scraped_data = {}
            scraped_data["season_long"] = convert_season_format(season) 
        logger.info(f"Scraping of Report IDs for season: "
                    f"{season} started")
        season_dates = generate_dates_between(
            start_date=season_ranges_dict["start_date"],
            end_date=season_ranges_dict["end_date"])
        scraped_data["report_data"] = self.get_report_ids(
            season_dates=season_dates,
            scraped_data=scraped_data["report_data"])
        logger.info(f"Scraping of Report IDs for season: "
                    f"{season} finished")

        return scraped_data
    
    
    def get_report_ids(
            self, season_dates: list, report_data_all: dict=None) -> list:
        if report_data_all == None:
            report_data_all = []
        scraped_dates = {game['date'] for game in report_data_all}
        dates_to_scrape = list(set(season_dates) - scraped_dates)
        for date in dates_to_scrape:
            report_data = self.get_daily_report_ids(date=date)
            report_data_all = report_data_all + report_data
            logger.debug(f"Report data for date {date}: {report_data}")

        return report_data_all


    @repeat_request_until_success
    def get_daily_report_ids(self, date: str) -> list:
        logger.debug(f"Scraping of daily report IDs for date {date} started..")
        request_url = f"https://api-web.nhle.com/v1/score/{date}"
        data = get_valid_request(request_url, 'json')
        report_data = self.parse_response(data=data, date=date)
        logger.debug(f"Scraping of daily report IDs for date {date} finished.")

        return report_data


    def parse_response(self, data: dict, date: str) -> list:

        report_data = []
        for match_data in data["games"]:
            match_dict = self.parse_game(match_data=match_data,
                                         date=date)
            report_data.append(match_dict)
        
        return report_data
    

    def parse_game(self, match_data: dict, date: str) -> dict:
        match_dict = {}
        match_dict["id"] = str(match_data["id"])[4:]
        match_dict["stadium"] = match_data["venue"]["default"]
        match_dict["date"] = date
        match_dict["start_time_UTC"] = match_data["startTimeUTC"]
        match_dict["HT"] = match_data["homeTeam"]["abbrev"]
        match_dict["VT"] = match_data["awayTeam"]["abbrev"]
        logger.debug(f"{match_dict}")

        return match_dict
    

class GetReportData():


    def __init__(self, report_dict: dict, season_long: str):
        self.report_dict = report_dict
        self.report_id = report_dict["id"]
        self.PBP_id = "PL" + self.report_id
        # visitor team report id
        self.VTS_id = "TV" + self.report_id
        # home team report id
        self.HTS_id = "TH" + self.report_id
        self.season = season_long


    def get_all_report_data(self) -> dict:
        logger.info(f"Scraping of data for a game {self.report_id} from date"
                    f" {self.report_dict["date"]} and season {self.season}"    f"started...")
        self.report_dict["PBP"] = self.get_PBP_data()
        self.report_dict["TH"] = self.get_HTS_data()
        self.report_dict["TV"] = self.get_VTS_data()
        logger.info(f"Scraping of data for a game {self.report_id} from date"
                    f" {self.report_dict["date"]} and season {self.season}"    f"finished.")

        return self.report_dict

    @repeat_request_until_success
    def get_PBP_data(self) -> list:
        logger.debug(f"Scraping of PBP data for report {self.report_id} from"
                     f"season {self.season} started...")
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.PBP_id}.HTM"
        )
        print(request_url)
        try:
            htm = get_valid_request(request_url, 'content')
            pbp_o = pbp_parser.PBPParser(htm=htm,
                                        report_id=self.report_id)
            plays = pbp_o.parse_htm_file()
        except Exception as e:
            logger.error(f"Scraping of PBP data for report {self.report_id}"
                         f"season {self.season} failed: {e}") 
        logger.debug(f"Scraping of PBP data for report {self.report_id} from"
                     f"season {self.season} finished.")

        return plays
    

    def get_VTS_data(self) -> list:
        logger.debug(f"Scraping of VTS data for report {self.report_id} from"
                     f"season {self.season} started...")
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.VTS_id}.HTM"
        )
        try:
            htm = get_valid_request(request_url, 'content')
            ts_o = ts_parser.TSParser(htm=htm,
                                    report_id=self.report_id)
            plays = ts_o.parse_htm_file()
        except Exception as e: 
            logger.error(f"Scraping of VTS data for report {self.report_id}"
                         f"season {self.season} failed: {e}") 
        logger.debug(f"Scraping of VTS data for report {self.report_id} from"
                     f"season {self.season} finished.")

        return plays
    
    
    @repeat_request_until_success
    def get_HTS_data(self) -> list:
        logger.debug(f"Scraping of HTS data for report {self.report_id} from"
                     f"season {self.season} started...")
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.HTS_id}.HTM"
        )
        try:
            htm = get_valid_request(request_url, 'content')
            ts_o = ts_parser.TSParser(htm=htm,
                                    report_id=self.report_id)
            plays = ts_o.parse_htm_file()
        except Exception as e:
            logger.error(f"Scraping of HTS data for report {self.report_id}"
                         f"season {self.season} failed: {e}") 
        logger.debug(f"Scraping of HTS data for report {self.report_id} from"
                     f"season {self.season} finished.")

        return plays











