import common_functions as cf
import gamedata.input_dict.input_game_dict as input_game
import gamedata.report_getter as report_getter
import gamedata.update_dict.update_game as update_game
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

from sqlalchemy.orm import  Session


class ManagePlayer():


    def __init__(
            self, done_folder_path: str, links_folder_path: str, 
            session: Session):
        self.players_done_path = done_folder_path + "/done_players.json"
        self.url_list_path = links_folder_path + "/players.json"
        self.players_done = None
        self.players_urls = None
        self.session = session
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_player.UpdatePlayer()
        self.input_dict = input_player_dict.InputPlayerDict(
            db_session=self.session)
        self.get_urls = get_url.LeagueUrlDownload(
            page=self.playwright_session.page)


    def add_players_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {league_uids} started")
        self.set_up_manage_player()
        for league_uid in league_uids:
            self.add_players_from_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {league_uids} finished")
        

    def set_up_manage_player(self) -> None:
        self.load_players_done_file()
        self.load_players_url_file()


    def load_players_done_file(self) -> None:
        if os.path.exists(self.players_done_path)==False:
            logger.info(f"Opening players_done file at path:" 
                        f"{self.players_done_path}")
            self.players_done = self.create_players_done_file()
        else:
            with open(self.players_done_path) as f:
                self.players_done = json.load(f)


    def create_players_done_file(self) -> list:
        logger.info(f"Creating and opening players_done file at path:" 
                    f"{self.players_done_path}")
        players_done = {'players_done': []}
        with open(self.players_done_path, 'w') as f:
            json.dump(players_done, f)

        return players_done


    def load_players_url_file(self) -> None:
        if os.path.exists(self.url_list_path)==False:
            logger.info(f"Opening players_urls file at path:" 
                        f"{self.url_list_path}")
            self.players_urls = self.create_player_url_file()
        else:
            with open(self.url_list_path) as f:
                self.players_urls = json.load(f)


    def create_player_url_file(self) -> None:
        players_urls = {}
        logger.info(f"Creating players_urls file at path:" 
                        f"{self.url_list_path}")
        with open(self.url_list_path, 'w') as f:
            json.dump(players_urls, f)

        return players_urls


    @repeat_request_until_success
    def scrape_player(self, url: str) -> dict:
        player_o = player_scraper.PlayerScraper(
                url=url, page=self.playwright_session.page)
        dict_player = player_o.get_info_all()

        return dict_player


    @time_execution
    def scrape_and_input_player_into_db(self, url: str) -> None:
            dict_player = self.scrape_player(url)
            dict_player_updated = (self.update_dict
                                   .update_player_dict(dict_player))
            self.input_dict.input_player_dict(player_dict=dict_player_updated)


    def scrap_input_player_into_db_wrapper(self, url: str) -> None:
        uid = re.findall('([0-9]+)', url)[0]
        if uid in self.players_done["players_done"]:
            logger.debug(f'Team with url {url} is already in the db')

            return
        self.scrape_and_input_player_into_db(url=url)
        self.players_done["players_done"].append(uid)


    def get_player_urls_in_league(self, league_uid: str) -> None:
        if league_uid in self.players_urls:

            return self.players_urls[league_uid] 
        url_list = self.get_urls.get_player_refs(league=league_uid,
                                                 years=None)
        if url_list != {}:
            self.players_urls[league_uid] = url_list
            with open(self.url_list_path, 'w') as f:
                json.dump(self.players_urls, f)

        return url_list
    

    def add_players_from_league_to_db(self, league_uid: str) -> None:
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} started")
        if league_uid not in self.players_urls:
            url_dict = self.get_player_urls_in_league(
                            league_uid=league_uid)
        else:
            url_dict =  self.players_urls[league_uid]
        for season in url_dict:
            try:
                season_dict = url_dict[season]
                self.add_one_season_in_db(
                    season_dict=season_dict, season=season,
                    league_uid=league_uid)
            except Exception as e:
                logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} was disrupted")
                with open(self.players_done_path, 'w') as f:
                    json.dump(self.players_done, f)
                logger.info(f"List of uids of players already in the db was"
                            " written to a file")
                raise e
            with open(self.players_done_path, 'w') as f:
                json.dump(self.players_done, f)
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} finished")


    def add_one_season_in_db(
            self, season_dict: dict, season: str, league_uid: str) -> None:
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} for season {season}"
                    f" started")
        for type_ in season_dict:
            type_list = season_dict[type_]
            self.add_one_type_in_db(types_=type_list)
        logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} for season {season}"
                    f" finished")

    def add_one_type_in_db(self, types_: list) -> None:
        for url in types_:
            self.scrap_input_player_into_db_wrapper(url=url)


class ManageTeam():


    def __init__(
            self, done_folder_path: str, links_folder_path: str, 
            session: Session):
        self.teams_done_path = done_folder_path + "/done_teams.json"
        self.url_list_path = links_folder_path + "/teams.json"
        self.teams_done = None
        self.teams_urls = None
        self.session = session
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_team.UpdateTeamDict()
        self.input_dict = input_team_dict.InputTeamDict(
            db_session=self.session)
        self.get_urls = get_url.LeagueUrlDownload()


    @time_execution
    def add_teams_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} started")
        self.set_up_manage_team()
        for league_uid in league_uids:
            self.add_teams_from_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} finished")
        

    def set_up_manage_team(self) -> None:
        self.load_teams_done_file()
        self.load_teams_url_file()


    def load_teams_done_file(self) -> None:
        if os.path.exists(self.teams_done_path)==False:
            logger.info(f"Opening teams_done file at path:" 
                        f"{self.teams_done_path}")
            self.teams_done = self.create_teams_done_file()
        else:
            with open(self.teams_done_path) as f:
                self.teams_done = json.load(f)


    def create_teams_done_file(self) -> dict:
        logger.info(f"Creating teams_done file at path:" 
                    f"{self.teams_done_path}")
        teams_done = {'teams_done': []}
        with open(self.teams_done_path, 'w') as f:
            json.dump(teams_done, f)

        return teams_done
    

    def load_teams_url_file(self) -> None:
        if os.path.exists(self.url_list_path)==False:
            logger.info(f"Opening teams_url file at path:" 
                        f"{self.url_list_path}")
            self.teams_urls = self.create_team_url_file()
        else:
            with open(self.url_list_path) as f:
                self.teams_urls = json.load(f)


    def create_team_url_file(self) -> list:
        teams_urls = {}
        logger.info(f"Creating teams_url file at path:" 
                    f"{self.url_list_path}")
        with open(self.url_list_path, 'w') as f:
            json.dump(teams_urls, f)
            
        return teams_urls


    @time_execution
    def scrape_and_input_team_into_db(self, url: str) -> None:
            dict_team = self.scrape_team(url=url)
            dict_team_updated = (self.update_dict
                                .update_team_dict(dict_team))
            self.input_dict.input_team_dict(team_dict=dict_team_updated)
    

    @repeat_request_until_success
    def scrape_team(self, url: str) -> dict:
        team_o = team_scraper.TeamScraper(
            url=url, page=self.playwright_session.page)
        dict_team = team_o.get_info()

        return dict_team


    def scrap_input_team_into_db_wrapper(self, url: str) -> None:
        uid = re.findall("team\/([0-9]+)\/", url)[0]
        if uid in self.teams_done["teams_done"]:
            logger.debug(f'Team with url: {url} is already in the db')

            return
        try:
            self.scrape_and_input_team_into_db(url=url)
        except Exception as e:
            with open(self.teams_done_path, 'w') as f:
                json.dump(self.teams_done, f)
            raise e
        self.teams_done["teams_done"].append(uid)


    def get_team_urls_in_league(self, league_uid: str) -> list:
        if league_uid in self.teams_urls:

            return  self.teams_urls[league_uid] 
        url_list = self.get_urls.get_team_refs(league=league_uid)
        if url_list != []:
            self.teams_urls[league_uid] = url_list
            with open(self.url_list_path, 'w') as f:
                json.dump(self.teams_urls, f)

        return url_list
    

    def add_teams_from_league_to_db(self, league_uid: str) -> None:
        logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} started")
        url_list = self.get_team_urls_in_league(
            league_uid=league_uid)
        try:
            for url in url_list:
                self.scrap_input_team_into_db_wrapper(url=url)
        except Exception as e:
            logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} was disrupted")
            with open(self.teams_done_path, 'w') as f:
                json.dump(self.teams_done, f)
            logger.info(f"List of uids of teams already in the db was"
                        f" written to a file")
            raise e
        with open(self.teams_done_path, 'w') as f:
            json.dump(self.teams_done, f)
        logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} finished")
       

class ManageLeague():


    def __init__(self, done_folder_path: str, session: Session):
        self.leagues_done_path = done_folder_path + "/done_leagues.json"
        self.leagues_done = None
        self.session = session
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_league.UpdateLeagueDict()
        self.input_dict = input_league_dict.InputLeagueDict(
            db_session=self.session)


    @time_execution
    def add_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} started")
        self.set_up_manage_league()
        for league_uid in league_uids:
            self.add_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} finished")
        

    def set_up_manage_league(self) -> None:
        self.load_leagues_done_file()


    def load_leagues_done_file(self) -> None:
        if os.path.exists(self.leagues_done_path)==False:
            self.leagues_done = self.create_leagues_done_file()
        else:
            logger.info(f"Opening leagues_done file at path:" 
                        f"{self.leagues_done_path}")
            with open(self.leagues_done_path) as f:
                self.leagues_done = json.load(f)


    def create_leagues_done_file(self) -> dict:
        logger.info(f"Creating and opening leagues_done file at path:" 
                    f"{self.leagues_done_path}")
        leagues_done = {'leagues_done': []}
        with open(self.leagues_done_path, 'w') as f:
            json.dump(leagues_done, f)

        return leagues_done
    
        
    def add_league_to_db(self, league_uid: str) -> None:
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db started")
        self.scrape_input_league_into_db_wrapper(league_uid=league_uid)
        with open(self.leagues_done_path, 'w') as f:
            json.dump(self.leagues_done, f)
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db finished")
        

    def scrape_input_league_into_db_wrapper(self, league_uid: str) -> None:
        if league_uid in self.leagues_done["leagues_done"]:
            logger.info(f'League ({league_uid}) is already in the db')

            return
        url = ELITE_URL + LEAGUE_URLS[league_uid]
        self.scrape_and_input_league_into_db(url=url)
        self.leagues_done["leagues_done"].append(league_uid)
        

    @time_execution
    def scrape_and_input_league_into_db(self, url: str) -> None:
            dict_league = self.scrape_league(url=url)
            dict_league_updated = (self.update_dict
                                   .update_league_dict(dict_league))
            self.input_dict.input_league_dict(league_dict=dict_league_updated)


    @repeat_request_until_success
    def scrape_league(self, url: str) -> None:
            league_o = league_scraper.LeagueScrapper(
                url=url, page=self.playwright_session.page)
            dict_league = league_o.get_info()

            return dict_league


class ManageGame():


    def __init__(
            self, done_folder_path: str, links_folder_path: str, 
            session: Session, update_on_conflict: bool):
        self.games_done_path = done_folder_path + "/done_games.json"
        self.games_done = None
        self.game_data_path = links_folder_path + "/games.json"
        self.game_data = None
        self.season_ranges_path = links_folder_path + "/season_ranges.json"
        self.season_ranges = None
        self.session = session
        self.report_id_getter_o = report_getter.ReportIDGetter()
        self.mapper_o = db_mapper.GetDBID(self.session)
        self.input_mapper_o = input_game.InputEliteNHLmapper(self.session)
        self.update_on_conflict = update_on_conflict


    @time_execution
    def add_games_from_seasons_to_db(self, seasons: list) -> None:
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} started")
        self.set_up_manage_game()
        for season in seasons:
            self.add_one_season_in_db(season=season)
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} finished")
        

    def set_up_manage_game(self) -> None:
        self.load_games_done_file()
        self.load_games_url_file()
        self.load_season_ranges()


    def load_games_done_file(self) -> None:
        if os.path.exists(self.games_done_path)==False:
            self.games_done = self.create_games_done_file()
        else:
            logger.info(f"Opening games_done file at path:" 
                        f"{self.games_done_path}")
            with open(self.games_done_path) as f:
                self.games_done = json.load(f)


    def create_games_done_file(self) -> dict:
        logger.info(f"Creating and opening games_done file at path:" 
                    f"{self.games_done_path}")
        games_done  = {'games_done': {}}
        with open(self.games_done_path, 'w') as f:
            json.dump(games_done, f)
        
        return games_done
    

    def load_games_url_file(self) -> None:
        if os.path.exists(self.game_data_path)==False:
            self.game_data = self.create_game_dates_file()
        else:
            logger.info(f"Opening game_dates file at path:" 
                        f"{self.game_data_path}")
            with open(self.game_data_path) as f:
                self.game_data = json.load(f)


    def load_season_ranges(self) -> None:
        try: 
            with open(self.season_ranges_path) as f:
                self.season_ranges = json.load(f)
        except Exception as e:
            logger.error(f"Season ranges file not found in specified "
                        f"location ({self.season_ranges_path})")
            raise e


    def create_game_dates_file(self) -> None:
        game_dates = {}
        logger.info(f"Creating game_dates file at path:" 
                        f"{self.game_data_path}")
        with open(self.game_data_path, 'w') as f:
            json.dump(game_dates, f)
        
        return game_dates
    

    def add_one_season_in_db(self, season: str) -> None:
        logger.info(f"Process of obtaining data of NHL games from"
                    f" season {season} started")
        if season not in self.game_data:
            season_dict = self.get_season_report_ids(season=season)
        else:
            season_dict = self.game_data[season]
        self.get_season_data(season_dict=season_dict,
                             season=season)
        logger.info(f"Process of obtaining data of games"
                    f" from season {season} finished")
        

    def get_season_report_ids(self, season: str) -> dict:
        try:
            season_dict = self.report_id_getter_o.get_season_ids(
                season_ranges_dict=self.season_ranges[season],
                season=season, scraped_dates=self.game_data[season])
            self.game_data[season] = season_dict
        except Exception as e:
            logger.error(f"Downloading of game report ids failed: {e}")
            logger.info("Downloading of game report ids failed..."
                        "Saving scraped IDs to file...")
            with open(self.game_data_path, "w") as f:
                json.dump(self.game_data, f)
            logger.debug("Scraped report IDs saved to a file.")
            raise e
        logger.info("Scraping of season report IDs finished.")
        with open(self.game_data_path, "w") as f:
                json.dump(self.game_data, f)
        logger.debug("Dates from which IDs of reports were already scraped"
                    " saved to a file")

        return season_dict
    
    
    def get_season_data(self, season: str, season_dict: dict) -> None:
        if season not in self.games_done:
            self.games_done[season] = []
        try:
            self.scrape_and_input_season_games_into_db(season, season_dict)
        except Exception as e:
            logger.info(f"Scraping of game report data for "
                        f"season {season} failed."
                        f"Saving scraped IDs to file...")
            with open(self.games_done_path, "w") as f:
                json.dump(self.games_done, f)
            logger.info(f"IDs of reports already in the database saved to"
                         f" a file")
            raise e
        logger.info(f"Scraping and inputting game data for season {season} "
                    "finished.")
        with open(self.games_done_path, "w") as f:
                json.dump(self.games_done, f)
        logger.debug("IDs of scraped report saved to a file.")
    
    
    def scrape_and_input_season_games_into_db(
            self, season: str, season_dict: dict) -> None:
        team_players = self.mapper_o.get_player_id_team_season_mapper_dict(
                [season])
        elite_nhl_mapper_detail = self.mapper_o.get_elite_nhl_mapper(
            [season])
        elite_nhl_mapper = self.mapper_o.get_elite_nhl_names()
        stadium_mapper = self.mapper_o.get_nhl_elite_stadium_mapper()
        reference_tables = self.mapper_o.get_reference_table_mappers()
        try:
            for game in season_dict["report_data"]:
                if game['id'] in self.games_done[season]:
                    continue
                report_id = self.scrape_and_input_game_into_db(
                    game, season_dict["season_long"], team_players[season], 
                    elite_nhl_mapper_detail[season], elite_nhl_mapper, stadium_mapper, reference_tables)
                self.games_done[season].append(report_id)
            self.input_mapper_o.input_all_mappers(
                elite_nhl_mapper_detail, stadium_mapper, reference_tables)
            self.session.close()
        except Exception as e:
            self.input_mapper_o.input_all_mappers(
                elite_nhl_mapper_detail, stadium_mapper, reference_tables)
            self.session.close()
            raise e
        
            
    @time_execution
    def scrape_and_input_game_into_db(
        self, game_dict: dict, season_long: str, team_players: dict, 
        elite_nhl_mapper_detail: dict, elite_nhl_mapper: dict, 
        stadium_mapper: dict, reference_tables: dict) -> int:
        try:
            report_dict = self.scrape_game_data(
                game_dict, season_long)
            updated_dict, player_mapper = self.update_game_data(
                report_dict, team_players, elite_nhl_mapper_detail, elite_nhl_mapper, reference_tables)
            self.input_game_data(
                updated_dict, player_mapper, stadium_mapper, reference_tables
                )
        except:
            cf.log_and_raise(
                None, GameDataError, game_id=game_dict["id"], season=season_long
                )

        return report_dict['id']


    def scrape_game_data(
            self, game_dict: dict, season_long: str) -> dict:
        get_report_data = report_getter.GetReportData(
            game_dict=game_dict,
            season_long=season_long)
        report_dict = get_report_data.get_all_report_data()

        return report_dict
    

    def update_game_data(
            self, game_data: dict, team_players: dict, 
            elite_nhl_mapper_detail: dict, elite_nhl_mapper: dict,
            reference_tables: str) -> dict:
        ugo = update_game.UpdateGameData(
            team_players, elite_nhl_mapper_detail, elite_nhl_mapper, reference_tables
            )
        updated_game_data = ugo.update_game_data(game_data)

        return updated_game_data, ugo.player_mapper
    

    def input_game_data(
            self, updated_data: dict, player_mapper: dict, 
            stadium_mapper: dict, reference_tables: dict) -> None:
        input_o = input_game.InputGameInfo(
            self.session, player_mapper, stadium_mapper, reference_tables, self.update_on_conflict)
        input_o.input_game_dict(updated_data)









           

