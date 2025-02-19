import gamedata.ts_parser as ts_parser
import gamedata.pbp_parser as pbp_parser

import json
import requests

from datetime import datetime, timedelta

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
            season: self.get_season_ids(season_dict=self.season_ranges[season],
                                        season=season)
            for season in self.season_ranges if season in selected_seasons
        }

        return report_ids


    def get_season_ids(self, season_dict: dict, season: str) -> dict:
        logger.info(f"Scraping of Report IDs for season: "
                    f"{season} started")
        report_data_all = []
        season_dates = generate_dates_between(
            start_date=season_dict["start_date"],
            end_date=season_dict["end_date"])
        for date in season_dates:
            report_data = self.get_daily_report_ids(date=date)
            report_data_all = report_data_all + report_data
            logger.debug(f"Report data for date {date}: {report_data}")

        season_dict = {}
        season_long = convert_season_format(season)
        season_dict["season_long"] = season_long 
        season_dict["report_data"] = report_data_all
        logger.info(f"Scraping of Report IDs for season: "
                    f"{season} finished")

        return season_dict

    def get_daily_report_ids(self, date: str) -> list:

        request_url = f"https://api-web.nhle.com/v1/score/{date}"
        data = requests.get(request_url).json()
        report_data = self.parse_response(data=data, date=date)

        return report_data

    def parse_response(self, data: dict, date: str) -> list:

        report_data = []
        for match_data in data["games"]:
            match_dict = {}
            match_dict["id"] = str(match_data["id"])[4:]
            match_dict["stadium"] = match_data["venue"]["default"]
            match_dict["date"] = date
            match_dict["start_time_UTC"] = match_data["startTimeUTC"]
            match_dict["HT"] = match_data["homeTeam"]["abbrev"]
            match_dict["VT"] = match_data["awayTeam"]["abbrev"]
            report_data.append(match_dict)
        
        return report_data
    

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
        self.report_dict["PBP"] = self.get_PBP_data()
        self.report_dict["TH"] = self.get_HTS_data()
        self.report_dict["TV"] = self.get_VTS_data()

        return self.report_dict


    def get_PBP_data(self) -> list:
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.PBP_id}.HTM"
        )
        print(request_url)
        htm = requests.get(request_url).content
        pbp_o = pbp_parser.PBPParser(htm=htm,
                                     report_id=self.report_id)
        plays = pbp_o.parse_htm_file()

        return plays
    
    
    def get_VTS_data(self) -> list:
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.VTS_id}.HTM"
        )
        htm = requests.get(request_url).content
        ts_o = ts_parser.TSParser(htm=htm,
                                   report_id=self.report_id)
        plays = ts_o.parse_htm_file()

        return plays
    
    
    def get_HTS_data(self) -> list:
        request_url = (
            f"https://www.nhl.com/scores/htmlreports"
            f"/{self.season}/{self.HTS_id}.HTM"
        )
        htm = requests.get(request_url).content
        ts_o = ts_parser.TSParser(htm=htm,
                                   report_id=self.report_id)
        plays = ts_o.parse_htm_file()

        return plays











