import gamedata.report_getter as report_getter
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
import json
import os
import re

from hockeydata.constants import *
from decorators import repeat_request_until_success, time_execution
from logger.logger import logger
from database_creator.database_creator import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

class DatabaseSession():
    """class which purpose is to manage scraping of all available entities including establishing connection to the database
    """

    def __init__(
            self, db_path: str, done_folder_path: str, links_folder_path: str):

        self.database_path = db_path
        self.done_folder_path = done_folder_path
        self.links_folder_path = links_folder_path
        self.engine = None
        self.session = None
        self.meta_data = None

    def set_up_connection(self) -> None:
        logger.info('New scrapping session started')
        self.start_session()
        are_seasons_filled = self.check_seasons_table()
        if are_seasons_filled==False:
            self.add_data_to_season_table()

    def start_session(self) -> None:
        self.engine = create_engine("sqlite:///" + self.database_path, echo=False)
        Base.metadata.create_all(bind=self.engine)
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
        self.meta_data = Base.metadata
        logger.info(f"New DB session initiated with db at"
                    f" {self.database_path}")

    def clear_all_tables(self) -> None:
        if 'test' not in self.database_path.lower():
            logger.error(f"Data deletion is not allowed on the" 
                         f"database  as {self.database_path}' does not"
                         f" contain 'test'.")
            raise ValueError
        for table in self.meta_data.sorted_tables:
            self.session.execute(text(f"DELETE FROM {table.name};"))
        logger.info(f"Data from all tables in db {self.database_path}"
                    f" has been deleted")
        self.session.commit()

    def check_seasons_table(self) -> bool:
        check_data = self.session.query(Season).all()
        if check_data == []:
            return False
        return True
    
    def add_data_to_season_table(self) -> None:
        self.add_seasons_to_seasons_table()
        self.add_years_to_seasons_table()
        logger.debug('Season and year values added to the db')
    
    def add_seasons_to_seasons_table(self) -> None:
        league_getter = league_url.LeagueUrlDownload()
        season_list = league_getter.create_season_list(1886, 2024)
        for one_season in season_list:
            season_entry = Season(season=one_season)
            self.session.add(season_entry)
            self.session.commit()

    def add_years_to_seasons_table(self) -> None:
        years = [*range(1886, 2025, 1)]
        for year in years:
            season_entry = Season(season=year)
            self.session.add(season_entry)
            self.session.commit()

    @time_execution
    def add_players_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {league_uids} started")
        manage_player = ManagePlayer(done_folder_path=self.done_folder_path,
                                     links_folder_path=self.links_folder_path,
                                     session=self.session)
        manage_player.set_up_manage_player()
        for league_uid in league_uids:
            manage_player.add_players_from_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {league_uids} finished")
    
    @time_execution
    def add_teams_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} started")
        manage_team = ManageTeam(done_folder_path=self.done_folder_path,
                                 links_folder_path=self.links_folder_path,
                                 session=self.session)
        manage_team.set_up_manage_team()
        for league_uid in league_uids:
            manage_team.add_teams_from_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of teams from following"
                    f" leagues: {league_uids} finished")

    @time_execution
    def add_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} started")
        manage_league = ManageLeague(done_folder_path=self.done_folder_path,
                                    session=self.session)
        manage_league.set_up_manage_league()
        for league_uid in league_uids:
            manage_league.add_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} finished")


class ManagePlayer():

    def __init__(
            self, done_folder_path: str, links_folder_path: str, 
            session: Session):
        self.players_done_path = done_folder_path + "/done_players.json"
        self.url_list_path = links_folder_path + "/players.json"
        self.players_done = None
        self.players_urls = None
        self.session = session
        self.plawright_setup = ps.PlaywrightSetUp()
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_player.UpdatePlayer()
        self.input_dict = input_player_dict.InputPlayerDict(
            db_session=self.session)
        self.get_urls = get_url.LeagueUrlDownload(
            page=self.playwright_session.page)

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
                url=url, page=self.playwright_session)
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
            except:
                logger.info(f"Process of obtaining data of players from"
                    f" league {league_uid} was disrupted")
                with open(self.players_done_path, 'w') as f:
                    json.dump(self.players_done, f)
                logger.info(f"List of uids of players already in the db was"
                            " written to a file")
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
            self.add_one_type_in_db(type_list=type_list)
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
        self.update_dict = update_team.UpdateTeamDict()
        self.input_dict = input_team_dict.InputTeamDict(
            session_db=self.session)
        self.get_urls = get_url.LeagueUrlDownload()

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
        team_o = team_scraper.TeamScraper(url=url)
        dict_team = team_o.get_info()
        return dict_team

    def scrap_input_team_into_db_wrapper(self, url: str) -> None:
        uid = re.findall("team\/([0-9]+)\/", url)[0]
        if uid in self.teams_done["teams_done"]:
            logger.debug(f'Team with url: {url} is already in the db')
            return
        try:
            self.scrape_and_input_team_into_db(url=url)
        except:
            with open(self.teams_done_path, 'w') as f:
                json.dump(self.teams_done, f)
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
        except:
            logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} was disrupted")
            with open(self.teams_done_path, 'w') as f:
                json.dump(self.teams_done, f)
            logger.info(f"List of uids of teams already in the db was"
                        f" written to a file")
        with open(self.teams_done_path, 'w') as f:
            json.dump(self.teams_done, f)
        logger.info(f"Process of obtaining data of teams from"
                    f" league {league_uid} finished")
       

class ManageLeague():

    def __init__(self, done_folder_path: str, session: Session):
        self.leagues_done_path = done_folder_path + "/done_leagues.json"
        self.leagues_done = None
        self.session = session
        self.update_dict = update_league.UpdateLeagueDict()
        self.input_dict = input_league_dict.InputLeagueDict(
            db_session=self.session)

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

    @time_execution
    def scrape_and_input_league_into_db(self, url: str) -> None:
            dict_league = self.scrape_league(url=url)
            dict_league_updated = (self.update_dict
                                   .update_league_dict(dict_league))
            self.input_dict.input_league_dict(league_dict=dict_league_updated)


    @repeat_request_until_success
    def scrape_league(self, url: str) -> None:
            league_o = league_scraper.LeagueScrapper(url=url)
            dict_league = league_o.get_info()
            return dict_league


    def scrape_input_league_into_db_wrapper(self, league_uid: str) -> None:
        if league_uid in self.leagues_done["leagues_done"]:
            logger.debug(f'League ({league_uid}) is already in the db')
            return
        url = ELITE_URL + LEAGUE_URLS[league_uid]
        self.scrape_and_input_league_into_db(url=url)
        self.leagues_done["leagues_done"].append(league_uid)
 

    def add_league_to_db(self, league_uid: str) -> None:
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db started")
        self.scrape_input_league_into_db_wrapper(league_uid=league_uid)
        with open(self.leagues_done_path, 'w') as f:
            json.dump(self.leagues_done, f)
        logger.info(f"Process of adding league with uid {league_uid} "
                    f"to db finished")
        

class ManageGame():


    def __init__(
            self, done_folder_path: str, links_folder_path: str, 
            seeason_ranges_path: str, session: Session):
        self.games_done_path = done_folder_path + "/done_games.json"
        self.games_done = None
        self.game_data_path = links_folder_path + "/games.json"
        self.game_data = None
        self.season_ranges_path = seeason_ranges_path + "/season_ranges.json"
        self.season_ranges = None
        self.report_id_getter = report_getter.ReportIDGetter()
        self.session = session


    def set_up_manage_league(self) -> None:
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
        except:
            logger.error(f"Season ranges file not found in specified "
                        f"location ({self.season_ranges_path})")


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
            season_dict = self.report_id_getter.get_season_ids(
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
        logger.info("Scraping of season report IDs finished.")
        with open(self.game_data_path, "w") as f:
                json.dump(self.game_data, f)
        logger.debug("Dates from which IDs of reports were already scraped"
                    " saved to a file")

        return season_dict
    
    
    def get_season_data(self, season_dict: dict, season: str) -> None:
        try:
            for game in season_dict:
                if game['report_id'] in self.games_done[season]:
                    continue
                report_id = self.scrape_and_input_game_into_db(
                    game_dict=game, season_long=season_dict["season_long"])
                self.games_done[season].append(report_id)
        except Exception as e:
            logger.error(f"Scraping of game report data for "
                         f"season {season} failed: {e}") 
            logger.info(f"Scraping of game report data for "
                        f"season {season} failed."
                        f"Saving scraped IDs to file...")
            with open(self.games_done_path, "w") as f:
                json.dump(self.games_done, f)
            logger.debug(f"IDs of reports already in the database saved to"
                         f" a file")
        logger.info("Scraping and inputting game data finished.")
        with open(self.games_done_path, "w") as f:
                json.dump(self.games_done, f)
        logger.debug("IDs of scraped report saved to a file.")
    
    
    @time_execution
    def scrape_and_input_game_into_db(
        self, game_dict: dict, season_long: str) -> int:
        #methods for updating data and putting data into db must be added
        report_dict = self.scrape_game_data(
            game_dict=game_dict, season_long=season_long)

        return report_dict['id']


    def scrape_game_data(self, game_dict: dict, season_long: str) -> dict:
        get_report_data = report_getter.GetReportData(
            report_dict=game_dict["report_data"],
            season_long=season_long)
        report_dict = get_report_data.get_all_report_data()

        return report_dict







           

