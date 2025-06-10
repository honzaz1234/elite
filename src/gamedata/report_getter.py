import json

import gamedata.ts_parser as ts_parser
import gamedata.pbp_parser as pbp_parser

from datetime import datetime, timedelta

from common_functions import get_valid_request
from decorators import repeat_request_until_success, time_execution
from logger.logging_config import logger


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
        report_ids = {}
        for season in selected_seasons:
            report_ids[season] = self.get_season_ids(
                season_ranges_dict=self.season_ranges[season],
                season=season)

        return report_ids


    def get_season_ids(
            self, season_ranges_dict: dict, season: str, 
            scraped_data: dict=None) -> dict:
        if scraped_data == None:
            scraped_data = {}
            scraped_data["season_long"] = convert_season_format(season)
            scraped_data["report_data"] = []
        logger.info("Scraping of Report IDs for season: %s started", season)
        season_dates = generate_dates_between(
            start_date=season_ranges_dict["start_date"],
            end_date=season_ranges_dict["end_date"])
        scraped_data["report_data"] = self.get_report_ids(
            season_dates=season_dates,
            report_data_all=scraped_data["report_data"])
        logger.info("Scraping of Report IDs for season: %s finished", season)

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
            logger.debug("Report data for date %s: %s", date, report_data)

        return report_data_all


    @repeat_request_until_success
    def get_daily_report_ids(self, date: str) -> list:
        logger.debug(
            "Scraping of daily report IDs for date %s started..", date
            )
        request_url = f"https://api-web.nhle.com/v1/score/{date}"
        data = get_valid_request(request_url, 'json')
        report_data = self.parse_response(data=data, date=date)
        logger.debug(
            "Scraping of daily report IDs for date %s finished.", date
            )

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
        logger.debug("%s", match_dict)

        return match_dict
    

class GetReportData():


    def __init__(self, game_dict: dict, season_long: str):
        self.game_dict = game_dict
        self.report_id = game_dict["id"]
        self.PBP_id = "PL" + self.report_id
        # visitor team report id
        self.VTS_id = "TV" + self.report_id
        # home team report id
        self.HTS_id = "TH" + self.report_id
        self.season = season_long

    @time_execution
    def get_all_report_data(self) -> dict:
        logger.info(
            "Scraping of data for a game %s from date %s and season %s" "started...",
            self.report_id,
            self.game_dict['date'],
            self.season
        )
        self.game_dict["PBP"], self.game_dict["attendance"] = self.get_PBP_data()
        self.game_dict["HTS"] = self.get_TS_data(self.HTS_id, "HTS")
        self.game_dict["VTS"] = self.get_TS_data(self.VTS_id, "VTS")
        logger.info(
            "Scraping of data for a game %s from date %s and season %s finished.",
            self.report_id,
            self.game_dict['date'],
            self.season
            )

        return self.game_dict
    

    def get_PBP_data(self) -> list:
        logger.debug(
            "Scraping of PBP data for report %s from season %s started...",
            self.report_id,
            self.season
            )
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.PBP_id}.HTM"
        )
        htm = get_valid_request(request_url, 'content')
        pbp_o = pbp_parser.PBPParser(htm=htm,
                                    report_id=self.report_id)
        plays = pbp_o.parse_htm_file()
        attendance = pbp_o.get_attendance()
        logger.debug(
            "Scraping of PBP data for report %s from season %s finished.",
            self.report_id,
            self.season
            )
        
        return plays, attendance
        
    
    def get_TS_data(self, report_id: str, type_: str) -> list:

        logger.debug(
            "Scraping of HTS data for report %s from season %s started...",
            self.report_id,
            self.season
            )
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{report_id}.HTM"
        )
        try:
            htm = get_valid_request(request_url, 'content')
            ts_o = ts_parser.TSParser(htm=htm,
                                    report_id=self.report_id)
            plays = ts_o.parse_htm_file()
        except Exception as e:
            logger.error(
                "Scraping of %s data for report %s season %s failed: %s",
                type_, self.report_id, self.season, e
                )
        logger.debug(
            "Scraping of %s data for report %s from season %s finished.",
            type_, self.report_id, self.season
            )
        
        return plays