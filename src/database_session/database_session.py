import common_functions
import database_queries.database_query as db_query
import management.input_data as input_data

from hockeydata.constants import *
from decorators import time_execution
from logger.logging_config import logger
from database_creator.database_creator import *

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class DatabaseSession():
    """class which purpose is to manage scraping of all available entities including establishing connection to the database
    """

    def __init__(self, db_path: str):

        self.database_path = db_path
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
            error_message = (
                f"Data deletion is not allowed on the" 
                f"database  as {self.database_path}' does not"
                f" contain 'test'."
                )
            common_functions.log_and_raise(error_message, ValueError)
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


class InsertDataSession(DatabaseSession):


    def __init__(
            self, db_path: str, done_folder_path: str, links_folder_path: str):
        super.__init__(db_path=db_path)
        self.done_folder_path = done_folder_path
        self.links_folder_path = links_folder_path


    @time_execution
    def add_players_from_leagues_to_db(self, league_uids: list) -> None:
        logger.info(f"Process of obtaining data of players from following"
                    f" leagues: {league_uids} started")
        manage_player = input_data.ManagePlayer(
            done_folder_path=self.done_folder_path,
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
        manage_team = input_data.ManageTeam(
            done_folder_path=self.done_folder_path,
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
        manage_league = input_data.ManageLeague(
            done_folder_path=self.done_folder_path,
                                    session=self.session)
        manage_league.set_up_manage_league()
        for league_uid in league_uids:
            manage_league.add_league_to_db(league_uid=league_uid)
        logger.info(f"Process of obtaining data of leagues from following"
                    f" list: {league_uids} finished")
        

    @time_execution
    def add_games_from_seasons_to_db(self, seasons: list) -> None:
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} started")
        manage_game = input_data.ManageGame(
            done_folder_path=self.done_folder_path,
                                 links_folder_path=self.links_folder_path,
                                 session=self.session)
        manage_game.set_up_manage_game()
        for season in seasons:
            manage_game.add_one_season_in_db(season=season)
        logger.info(f"Process of obtaining data of games from following"
                    f" list: {seasons} finished")
        

class GetDataSession(DatabaseSession):


    def get_db_query(
            self, query_name: str, filters: str=None, distinct=False) -> list:
        query_o = db_query.DbDataGetter(session=self.session)
        data = query_o.get_db_query_result(
            query_name=query_name,
            filters=filters,
            distinct=distinct)
        logger.debug(f"Executed query returned {len(data)} rows of data")

        return data


        





           

