from sqlalchemy.orm import Session

import database_creator.storage_database_creator as db

from database_insert.db_insert import DatabaseMethods


class HTMLInputter():
    """Parent class for handling inputting downloaded html files into storage  
       DB
    """


    def __init__(
            self, db_session: Session, scraped_data: dict, scrape_id: int):
        self.insert_db = DatabaseMethods(db_session=db_session)
        self.scraped_data = scraped_data
        self.scrape_id = scrape_id


    def input_data(self):
        pass


class PlayerHTMLInputter(HTMLInputter):


    def __init__(
            self, db_session: Session, scraped_data: dict, scrape_id: int):
        super().__init__(
            db_session=db_session, scraped_data=scraped_data, scrape_id=scrape_id
            )
        self.is_goalie = None
        self.player_uid = None 
        self.player_id = None


    def _input_data(self):
        self._set_is_goalie()
        self._set_player_uid()
        self._input_player()
        self._input_player_facts_html()
        self._input_achievements_html()
        self._input_stats_htmls()
    

    def _set_is_goalie(self) -> None:

        """method for establishing if the player is goalie or field player; important because of different structure of downloaded html
        """

        position = self.scraped_data["player_type"]
        if position == "G":
            self.is_goalie =  True
        else:
            self.is_goalie = False


    def _set_player_uid(self) -> None:
        self.player_uid = self.scraped_data["player_uid"]


    def _input_player(self):
        self.player_id = self.insert_db._input_data(
            table=db.Player, player_uid=self.player_uid,
            is_goalie=self.is_goalie,
            scrape_id=self.scrape_id
            )


    def _input_player_facts_html(self):
        self.insert_db._input_data(
            table=db.PlayerFacts, player_id=self.player_id,
            html_data=self.scraped_data["player_facts"]
            )
        

    def _input_achievements_html(self):
        self.insert_db._input_data(
            table=db.Achievements, player_id=self.player_id,
            html_data=self.scraped_data["achievements"]
            )
        

    def _input_stats_htmls(self):
        if self.is_goalie:
            stats_class = InputGoalieStatsHtml(
                scraped_data=self.scraped_data, insert_db=self.insert_db,
                player_id=self.player_id
                ) 
        else:
            stats_class = InputSkaterStatsHtml(
                scraped_data=self.scraped_data, insert_db=self.insert_db
                ) 
        stats_class._input_data()


class InputStatsHtml():


    def __init__(
            self, scraped_data: dict, insert_db: DatabaseMethods, 
            player_id: int):
        self.scraped_data = scraped_data
        self.insert_db = insert_db
        self.player_id = player_id


    def _input_data(self):
        pass


class InputGoalieStatsHtml(InputStatsHtml):
    

    def _input_data(self):
        self.insert_db._input_data(
            table=db.GoalieStats, player_id=self.player_id,
            league_type="league", season_type="regular", html_data=self.scraped_data["stats_league"]["regular"]
            )
        self.insert_db._input_data(
            table=db.GoalieStats, player_id=self.player_id,
            league_type="league", season_type="play_off", html_data=self.scraped_data["stats_league"]["play_off"]
            )
        self.insert_db._input_data(
            table=db.GoalieStats, player_id=self.player_id,
            league_type="tournament", season_type="regular", html_data=self.scraped_data["stats_tournament"]["regular"]
            )
        self.insert_db._input_data(
            table=db.GoalieStats, player_id=self.player_id,
            league_type="tournament", season_type="play_off", html_data=self.scraped_data["stats_tournament"]["play_off"]
            )
        

class InputSkaterStatsHtml(InputStatsHtml):
    

    def _input_data(self):
        self.insert_db._input_data(
            table=db.SkaterStats, player_id=self.player_id,
            league_type="league", season_type="regular", 
            html_data=self.scraped_data["stats_league"]
            )
        self.insert_db._input_data(
            table=db.SkaterStats, player_id=self.player_id,
            league_type="tournament", season_type="play_off", 
            html_data=self.scraped_data["stats_tournament"]
            )




        