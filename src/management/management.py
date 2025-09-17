import common_functions as cf
import gamedata.input_dict.input_game_dict as input_game
import gamedata.report_getter as report_getter
import gamedata.update_dict.update_game as update_game
import google_tools as google
import hockeydata.scraper.league_scraper as league_scraper
import hockeydata.scraper.player_scraper as player_scraper
import hockeydata.scraper.team_scraper as team_scraper
import hockeydata.get_urls.get_urls as get_url
import hockeydata.update_dict.update_league as update_league
import hockeydata.update_dict.update_player as update_player
import hockeydata.update_dict.update_team as update_team
import hockeydata.input_dict.input_league_dict as input_league_dict
import hockeydata.input_dict.input_player_dict as input_player_dict
import hockeydata.input_dict.input_team_dict as input_team_dict
import hockeydata.playwright_setup.playwright_setup as ps
import mappers.db_mappers as db_mapper
import json
import os
import re

from constants import *
from decorators import repeat_request_until_success, time_execution
from errors import GameDataError
from logger.logging_config import logger
from database_creator.database_creator import *
from database_session.database_session import GetDatabaseSession



class Manage():


    DONE_FILE = None
    LINK_FILE = None
    REGEX_UID = None
    TYPE = None


    def __init__(
            self, session_o: GetDatabaseSession, done_folder_path: str, 
            links_folder_path: str):
        done_folder_path = done_folder_path + self.DONE_FILE
        links_folder_path = links_folder_path + self.LINK_FILE
        self.db_session = session_o.session
        self.done_path = done_folder_path
        self.url_list_path = links_folder_path
        self.done_file = None
        self.url_file = None
        self.urls = None
        self.update_dict = None
        self.input_dict = None
        self.scrape_id = session_o.create_scrape_table_entry(type_=self.TYPE)


    def set_up_management(self):
        self._load_done_file()
        self._load_url_file()
        

    def _load_done_file(self) -> None:
        if not os.path.exists(self.done_path):
            logger.info(
                "Creating %s done file at path: %s", 
                self.TYPE, self.done_path
                )
            self.done_file = self._create_done_file()
        else:
            logger.info(
                "Opening %s  done file at path: %s", 
                self.TYPE, self.done_path
                )
            with open(self.done_path) as f:
                self.done_file = json.load(f)


    def _create_done_file(self) -> None:
        logger.info(
            "Creating %s done file at path: %s", 
            self.TYPE, self.done_path
            )
        self.done_file = []
        self._save_done_file()
        logger.info(
            "%s done file at path: %s created.", 
            self.TYPE, self.done_path
            )


    def _save_done_file(self) -> None:
        logger.info(
            "Saving %s done file at path: %s...", 
            self.TYPE, self.done_path
            )
        if self.done_file is not None:
            with open(self.done_path, 'w') as f:
                json.dump(self.done_file, f)
            logger.info(
                "%s done file saved at path: %s.", self.TYPE, self.url_list_path
                )
        else:
            logger.info("Done file is equal to None, therefore data was not "
                        "saved.")


    def _load_url_file(self) -> None:
        if not os.path.exists(self.url_list_path):
            logger.info(
                "%s creating URL file at path: %s...", 
                self.TYPE, self.url_list_path
                )
            self._create_url_file()
        else:
            logger.info("Opening %s URL file at path: %s", 
                        self.TYPE, self.url_list_path
                        )
            with open(self.url_list_path) as f:
                self.urls = json.load(f)


    def _create_url_file(self) -> None:
        self.urls = {}
        self._save_url_file()
        logger.info(
            "%s URL file at path: %s created.", self.TYPE, self.url_list_path
            )


    def _save_url_file(self) -> None:
        logger.info(
            "Saving %s URL file at path: %s ...", 
            self.TYPE, self.url_list_path
            )
        if self.urls is not None:
            with open(self.url_list_path, 'w') as f:
                json.dump(self.urls, f)
            logger.info("%s URL file saved at path: %s.", 
                        self.TYPE, self.url_list_path
                        )
        else:
            logger.info("URL file is equal to None, therefore data was not "
                        "saved.")


    def scrape_input_into_db_wrapper(self, url: str) -> None:
        uid = self.get_uid(url=url)
        if uid in self.done_file:
            
            return
        try:
            self.scrape_and_input_into_db(url=url)
        except Exception as e:
            with open(self.done_path, 'w') as f:
                json.dump(self.done_file, f)
            raise e
        self.done_file.append(uid)


    def get_uid(self, url: str) -> str:
        uid = int(re.findall(self.REGEX_UID, url)[0])

        return uid


    @time_execution
    def scrape_and_input_into_db(self, url: str) -> None:
            scraped_dict = self.scrape(url)
            updated_dict = (
                self.update_dict
                .update_dict(scraped_dict)
                )
            self.input_dict.input_dict(dict=updated_dict)


    def save_data_to_google_drive(self):
        logger.info("Saving %s data to Google Drive...", self.TYPE)
        google_manage = google.GoogleManager()
        google_manage.upload_files_to_drive(
            files_include=[self.DONE_FILE, self.LINK_FILE]
            )
        logger.info("Data %s saved to Google Drive.", self.TYPE)


class ManagePlayer(Manage):


    DONE_FILE = "done_players.json"
    LINK_FILE =  "players.json"
    REGEX_UID = "([0-9]+)"
    TYPE = "Player"


    def __init__(
            self, session_o: GetDatabaseSession, done_folder_path: str, 
            links_folder_path: str):
        super().__init__(
            session_o=session_o, 
            done_folder_path=done_folder_path, links_folder_path=links_folder_path
            )
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_player.UpdatePlayer()
        self.input_dict = input_player_dict.InputPlayerDict(
            db_session=self.db_session, scrape_id=self.scrape_id
            )
        self.get_urls = get_url.LeagueUrlDownload(
            page=self.playwright_session.page
            )
            
        
    def add_from_leagues_to_db(self, seasons_to_get: dict={}) -> None:
         logger.info(
            "Process of obtaining data of players from following "
            "leagues: %s started", seasons_to_get.keys()
            )
         self.set_up_management()
         for league_uid in seasons_to_get.keys():
            self.add_from_league_to_db_wrapper(
                league_uid=league_uid, 
                seasons_to_get=seasons_to_get[league_uid]
                )
         logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {seasons_to_get.keys()} finished")
         

    def add_from_league_to_db_wrapper(
            self, league_uid: str, seasons_to_get: list) -> None:
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} started")
        self.get_player_urls_in_league(
                league_uid=league_uid, 
                seasons_to_get=seasons_to_get
                )
        if seasons_to_get == []:
            seasons_to_get = [
                season for season in self.urls[league_uid].keys() 
                if season != "season_range"
                ]
        for season in seasons_to_get:
            try:
                self.add_one_season_in_db(
                    season=season, league_uid=league_uid
                    )
            except Exception as e:
                logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} was disrupted")
                self._save_done_file()
                logger.info(f"List of uids of players already in the db was"
                            " written to a file")
                raise e
            self._save_done_file()
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} finished and written to file.")
        self.save_data_to_google_drive()
         

    def add_one_season_in_db(
            self, season: str, league_uid: str) -> None:
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} for season {season}"
                    f" started")
        for player_type in self.urls[league_uid][season]:
            self.add_one_type_in_db(
                league_uid=league_uid, season=season, player_type=player_type
                )
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} for season {season}"
                    f" finished")


    def add_one_type_in_db(
            self, league_uid: str, season: str, player_type: str) -> None:
        for url in self.urls[league_uid][season][player_type]:
            self.scrape_input_into_db_wrapper(url=url)


    @repeat_request_until_success
    def scrape(self, url: str) -> dict:
        player_o = player_scraper.PlayerScraper(
                url=url, page=self.playwright_session.page,
                )
        dict_player = player_o.get_info_all()

        return dict_player


    def get_player_urls_in_league(
            self, league_uid: str, seasons_to_get: list=[]) -> dict:
        self.add_league_to_player_url_dict(league_uid=league_uid)
        self.update_player_url_dict(
                league_uid=league_uid, seasons_to_get=seasons_to_get
                    )
        url_dict = {
            season:self.urls[league_uid][season]
            for season in self.urls[league_uid] 
            if season in seasons_to_get
            }

        return url_dict
    
    
    def add_league_to_player_url_dict(self, league_uid: str) -> None:
        if league_uid not in self.urls:
            self.urls[league_uid] = {}

    
    def update_player_url_dict(
            self, league_uid: str, seasons_to_get: list) -> None:
            new_season_urls = self.get_urls.get_player_refs(
                league_uid=league_uid, 
                url_dict=self.urls,
                seasons=seasons_to_get
                )
            if new_season_urls is None:
                return
            self.update_league_player_url_dict(
                league_uid=league_uid, new_data=new_season_urls)
            logger.info(
                "Updated URL dict for league %s will be saved now.",
                league_uid
                )
            with open(self.url_list_path, 'w') as f:
                json.dump(self.urls, f)
            logger.info(
                "Data were saved as a JSON file at the following path: %s",
                    self.url_list_path
                    )
            

    def update_league_player_url_dict(
            self, league_uid: str, new_data: dict) -> None:
        logger.info(
            "Player URLs for seasons %s from league %s will be added "
            "to player URL dictionary", new_data.keys(), league_uid
            )
        self.urls[league_uid].update(new_data)
        logger.info(
            "Player URLs for seasons %s from league %s were be added "
            "to player URL dictionary", new_data.keys(), league_uid
            )
            

class ManageTeam(Manage):


    DONE_FILE = "done_teams.json"
    LINK_FILE =  "teams.json"
    REGEX_UID = "team\/([0-9]+)\/"
    TYPE = "Team"


    def __init__(
            self, session_o: GetDatabaseSession, done_folder_path: str, 
            links_folder_path: str):
        super().__init__(
            session_o=session_o, 
            done_folder_path=done_folder_path, links_folder_path=links_folder_path
            )
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_team.UpdateTeamDict()
        self.input_dict = input_team_dict.InputTeamDict(
            db_session=self.db_session)
        self.get_urls = get_url.LeagueUrlDownload(
            page=self.playwright_session.page)


    @time_execution
    def add_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} started")
        self.set_up_management()
        for league_uid in league_uids:
            self.add_from_league_to_db_wrapper(league_uid=league_uid)
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} finished")
        

    def add_from_league_to_db_wrapper(self, league_uid: str) -> None:
        logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} started")
        url_list = self.get_team_urls_in_league(
            league_uid=league_uid)
        logger.info("Scraping of team data will now proceed.")
        try:
            for url in url_list:
                self.scrape_input_into_db_wrapper(url=url)
        except Exception as e:
            logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} was disrupted")
            with open(self.done_file, 'w') as f:
                json.dump(self.done_file, f)
            logger.info(f"List of uids of teams already in the db was"
                        f" written to a file")
            raise e
        with open(self.done_path, 'w') as f:
            json.dump(self.done_file, f)
        logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} finished")
        self.save_data_to_google_drive()
    

    @repeat_request_until_success
    def scrape(self, url: str) -> dict:
        team_o = team_scraper.TeamScraper(
            url=url, page=self.playwright_session.page)
        dict_team = team_o.get_info()

        return dict_team


    def get_team_urls_in_league(self, league_uid: str) -> list:
        if league_uid in self.urls:
            logger.info("URLs for league %s already scraped.", league_uid)
            return  self.urls[league_uid] 
        logger.info(
            "URLs for league %s not yet available, scraping will proceed.", league_uid)
        url_list = self.get_urls.get_team_refs(league=league_uid)
        if url_list != []:
            self.urls[league_uid] = url_list
            with open(self.url_list_path, 'w') as f:
                json.dump(self.urls, f)

        return url_list
    

class ManageLeague(Manage):


    DONE_FILE = "done_leagues.json"
    LINK_FILE =  "leagues.json"
    REGEX_UID = "league/(.+)$"
    TYPE = "League"


    def __init__(
            self, session_o: GetDatabaseSession, done_folder_path: str, 
            links_folder_path: str):
        super().__init__(
            session_o=session_o, 
            done_folder_path=done_folder_path, 
            links_folder_path=links_folder_path
            )
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_league.UpdateLeagueDict()
        self.input_dict = input_league_dict.InputLeagueDict(
            db_session=self.db_session
            )


    @time_execution
    def add_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} started")
        self.set_up_management()
        for league_uid in league_uids:
            self.add_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} finished")
        

    def add_league_to_db(self, league_uid: str) -> None:
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db started")
        url = ELITE_URL + self.urls[league_uid]
        self.scrape_input_into_db_wrapper(url=url)
        with open(self.done_file, 'w') as f:
            json.dump(self.done_file, f)
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db finished")   
        self.save_data_to_google_drive() 


    @repeat_request_until_success
    def scrape(self, url: str) -> None:
            league_o = league_scraper.LeagueScrapper(
                url=url, page=self.playwright_session.page)
            dict_league = league_o.get_info()

            return dict_league
    

    def get_uid(self, url: str) -> str:
        uid = re.findall(self.REGEX_UID, url)[0]

        return uid


class ManageGame(Manage):


    DONE_FILE = "done_games.json"
    LINK_FILE =  "games.json"
    TYPE = "Game"


    def __init__(
            self, session_o: GetDatabaseSession, done_folder_path: str, links_folder_path: str, update_on_conflict: bool):
        super().__init__(
            session_o=session_o, done_folder_path=done_folder_path,
            links_folder_path=links_folder_path)
        self.season_ranges_path = links_folder_path + "/season_ranges.json"
        self.season_ranges = None
        self.report_id_getter_o = report_getter.ReportIDGetter()
        self.mapper_o = db_mapper.GetDBID(self.db_session)
        self.input_mapper_o = input_game.InputEliteNHLmapper(self.db_session)
        self.update_on_conflict = update_on_conflict


    @time_execution
    def add_games_from_seasons_to_db(self, seasons: list) -> None:
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} started")
        self.set_up_management()
        for season in seasons:
            self._add_one_season_in_db(season=season)
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} finished")
        

    def set_up_management(self) -> None:
        super().set_up_management() 
        self._load_season_ranges()


    def _create_done_file(self) -> None:
        logger.info(
            "Creating %s done file at path: %s", 
            self.TYPE, self.done_path
            )
        self.done_file = {}
        self._save_done_file()
        logger.info(
            "%s done file at path: %s created.", 
            self.TYPE, self.done_path
            )


    def _load_season_ranges(self) -> None:
        try: 
            with open(self.season_ranges_path) as f:
                self.season_ranges = json.load(f)
        except FileNotFoundError as e:
            message = (
                f"Season ranges file not found in specified "
                f"location ({self.season_ranges_path})"
            )
            cf.log_and_raise(message, FileNotFoundError)
            raise e
        

    def _add_one_season_in_db(self, season: str) -> None:
        logger.info(f"Process of obtaining data of NHL games from"
                    f" season {season} started")
        if season not in self.done_file:
            season_dict = self.get_season_report_ids(season=season)
        else:
            season_dict = self.urls[season]
        self.get_season_data(
            season_dict=season_dict, season=season
            )
        logger.info(f"Process of obtaining data of games"
                    f" from season {season} finished")
        self.save_data_to_google_drive()
        

    def get_season_report_ids(self, season: str) -> dict:
        try:
            season_dict = self.report_id_getter_o.get_season_ids(
                season_ranges_dict=self.season_ranges[season],
                season=season, 
                game_data=self.done_file
                )
            self.urls[season] = season_dict
        except Exception as e:
            logger.error(f"Downloading of game report ids failed: {e}")
            logger.info("Downloading of game report ids failed..."
                        "Saving scraped IDs to file...")
            with open(self.done_path, "w") as f:
                json.dump(self.done_file, f)
            logger.debug("Scraped report IDs saved to a file.")
            raise e
        logger.info("Scraping of season report IDs finished.")
        with open(self.done_path, "w") as f:
                json.dump(self.done_file, f)
        logger.debug("Dates from which IDs of reports were already scraped"
                    " saved to a file")

        return season_dict
    
    
    def get_season_data(self, season: str, season_dict: dict) -> None:
        if season not in self.done_file:
            self.done_file[season] = []
        try:
            self.scrape_and_input_season_games_into_db(season, season_dict)
        except Exception as e:
            logger.info(f"Scraping of game report data for "
                        f"season {season} failed."
                        f"Saving scraped IDs to file...")
            with open(self.done_path, "w") as f:
                json.dump(self.done_file, f)
            logger.info(f"IDs of reports already in the database saved to"
                         f" a file")
            raise e
        logger.info(f"Scraping and inputting game data for season {season} "
                    "finished.")
        with open(self.done_path, "w") as f:
                json.dump(self.done_file, f)
        logger.debug("IDs of scraped report saved to a file.")
    
    
    def scrape_and_input_season_games_into_db(
            self, season: str, season_dict: dict) -> None:
        mappers = self.get_dict_with_all_mappers(season=season)
        try:
            for game in season_dict['report_data']:
                if game['id'] in self.done_file[season]:
                    continue
                report_id = self.scrape_and_input_game_into_db(
                    game_dict=game, season=season_dict["season"], mappers=mappers
                    )
                self.done_file[season].append(report_id)
            self.input_mapper_o.input_all_mappers(mappers=mappers)
        except Exception as e:
            self.input_mapper_o.input_all_mappers(mappers=mappers)
            self.db_session.close()
            raise e
        

    def get_dict_with_all_mappers(self, season: str) -> dict:
        logger.info("Getting mappers...")
        mappers = {}
        mappers["elite_nhl_detail"] = self.mapper_o.get_nhl_elite_mapper(
            [season])
        mappers["elite_nhl"] = self.mapper_o.get_elite_nhl_names()
        mappers["stadium"] = self.mapper_o.get_nhl_elite_stadium_mapper()
        mappers["look_ups"] = self.mapper_o.get_look_ups()
        mappers["first_name"] = self.mapper_o.get_firstname_mapper()
        season_name_player_id, normalized_season_name_player_id = self.mapper_o.get_player_id_team_season_mapper_dicts([season])
        mappers["season_name_player_id"] = season_name_player_id
        mappers["normalized_season_name_player_id"] = normalized_season_name_player_id
        logger.info("All mappers succesfully accessed.")

        return mappers

            
    @time_execution
    def scrape_and_input_game_into_db(
        self, game_dict: dict, season: str, mappers: dict) -> int:
        try:
            report_dict = self.scrape_game_data(
                game_dict, season)
            updated_dict, match_player_mapper = self.update_game_data(
                game_data=report_dict, mappers=mappers, season=season)
            self.input_game_data(
                updated_data=updated_dict, 
                match_player_mapper=match_player_mapper, 
                mappers=mappers
                )
        except:
            cf.log_and_raise(
                None, GameDataError, game_id=game_dict["id"], season=season
                )

        return report_dict['id']


    def scrape_game_data(
            self, game_dict: dict, season: str) -> dict:
        get_report_data = report_getter.GetReportData(
            game_dict=game_dict,
            season=season)
        report_dict = get_report_data.get_all_report_data()

        return report_dict
    

    def update_game_data(
            self, game_data: dict, mappers: dict, season: str) -> dict:
        ugo = update_game.UpdateGameData(mappers=mappers, season=season)
        updated_game_data = ugo.update_game_data(game_data=game_data)

        return updated_game_data, ugo.match_player_mapper
    

    def input_game_data(
            self, updated_data: dict, match_player_mapper: dict, 
            mappers: dict) -> None:
        input_o = input_game.InputGameInfo(
            db_session=self.db_session, 
            match_player_mapper=match_player_mapper, 
            mappers=mappers, 
            update_on_conflict=self.update_on_conflict
            )
        input_o.input_game_dict(updated_data)









           

