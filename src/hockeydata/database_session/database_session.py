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
from hockeydata.database_creator.database_creator import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseSession():
    """class which purpose is to manage scraping of all available entities including establishing connection to the database
    """

    def __init__(self, db_path, done_folder_path, links_folder_path):

        self.database_path = db_path
        self.done_folder_path = done_folder_path
        self.links_folder_path = links_folder_path
        self.session = None

    def set_up_connection(self):
        self.start_session()
        are_seasons_filled = self.check_seasons_table()
        if are_seasons_filled==False:
            self.add_data_to_season_table()

    def start_session(self):
        engine = create_engine("sqlite:///" + self.database_path, echo=False)
        Base.metadata.create_all(bind=engine)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def check_seasons_table(self):
        check_data = self.session.query(Season).all()
        if check_data == []:
            return False
        return True
    
    def add_data_to_season_table(self):
        self.add_seasons_to_seasons_table()
        self.add_years_to_seasons_table()
    
    def add_seasons_to_seasons_table(self):
        league_getter = league_url.LeagueUrlDownload()
        season_list = league_getter.create_season_list(1886, 2024)
        for one_season in season_list:
            season_entry = Season(season=one_season)
            self.session.add(season_entry)
            self.session.commit()

    def add_years_to_seasons_table(self):
        years = [*range(1886, 2025, 1)]
        for year in years:
            season_entry = Season(season=year)
            self.session.add(season_entry)
            self.session.commit()

    def add_players_from_leagues_to_db(self, league_uid_list):
        manage_player = ManagePlayer(done_folder_path=self.done_folder_path,
                                     links_folder_path=self.links_folder_path,
                                     session=self.session)
        manage_player.set_up_manage_player()
        for league_uid in league_uid_list:
            manage_player.add_players_from_league_to_db(league_uid=league_uid)

    def add_teams_from_leagues_to_db(self, league_uid_list):
        manage_team = ManageTeam(done_folder_path=self.done_folder_path,
                                 links_folder_path=self.links_folder_path,
                                 session=self.session)
        manage_team.set_up_manage_team()
        for league_uid in league_uid_list:
            manage_team.add_teams_from_league_to_db(league_uid=league_uid)

    def add_leagues_to_db(self, league_uid_list):
        manage_league = ManageLeague(done_folder_path=self.done_folder_path,
                                    session=self.session)
        manage_league.set_up_manage_league()
        for league_uid in league_uid_list:
            manage_league.add_teams_from_league_to_db(league_uid=league_uid)


class ManagePlayer():

    def __init__(self, done_folder_path, links_folder_path, session):
        self.players_done_path = done_folder_path + "/done_players.json"
        self.url_list_path = links_folder_path + "/players.json"
        self.players_done = None
        self.players_urls = None
        self.session = session
        self.playwright_session = ps.PlaywrightSetUp()
        self.update_dict = update_player.UpdatePlayer()
        self.input_dict = input_player_dict.InputPlayerDict(
            db_session=self.session)
        self.get_urls = get_url.LeagueUrlDownload()

    def set_up_manage_player(self):
        self.load_players_done_file()
        self.load_players_url_file()

    def load_players_done_file(self):
        if os.path.exists(self.players_done_path)==False:
            self.players_done = self.create_players_done_file()
        else:
            with open(self.players_done_path) as file:
                self.players_done = json.load(file)

    def create_players_done_file(self):
        players_done = {'players_done': []}
        with open(self.players_done_path, 'w') as file:
            json.dump(players_done, file)
        return players_done

    def load_players_url_file(self):
        if os.path.exists(self.url_list_path)==False:
            self.players_urls = self.create_player_url_file()
        else:
            with open(self.url_list_path) as file:
                self.players_urls = json.load(file)

    def create_player_url_file(self):
        players_urls = {}
        with open(self.url_list_path, 'w') as file:
            json.dump(players_urls, file)
        return players_urls

    def scrape_and_input_player_into_db(self, url):
            player_o = player_scraper.PlayerScraper(
                url=url, page=self.playwright_session.page)
            dict_player = player_o.get_info_all()
            dict_player_updated = (self.update_dict
                                   .update_player_dict(dict_player))
            print(dict_player_updated['general_info']['player_name'])
            self.input_dict.input_player_dict(player_dict=dict_player_updated)

    def scrap_input_player_into_db_wrapper(self, url):
        uid = re.findall('([0-9]+)', url)[0]
        print(uid)
        if uid in self.players_done["players_done"]:
            return
        self.scrape_and_input_player_into_db(url=url)
        self.players_done["players_done"].append(uid)

    def get_player_urls_in_league(self, league_uid):
        if league_uid in self.players_urls:
            return self.players_urls[league_uid] 
        url_list = self.get_urls.get_player_refs(league=league_uid,
                                                 years=None)
        if url_list != {}:
            self.players_urls[league_uid] = url_list
            with open(self.url_list_path, 'w') as file:
                json.dump(self.players_urls, file)
        return url_list
    
    def add_players_from_league_to_db(self, league_uid):
        if league_uid not in self.players_urls:
            url_dict = self.get_player_urls_in_league(
                            league_uid=league_uid)
        else:
            url_dict =  self.players_urls[league_uid]
        for season in url_dict:
            try:
                season_dict = url_dict[season]
                self.add_one_season_in_db(season_dict=season_dict)
            except:
                with open(self.players_done_path, 'w') as file:
                    json.dump(self.players_done, file)
            with open(self.players_done_path, 'w') as file:
                json.dump(self.players_done, file)

    def add_one_season_in_db(self, season_dict):
        for type_ in season_dict:
            type_list = season_dict[type_]
            self.add_one_type_in_db(type_list=type_list)

    def add_one_type_in_db(self, type_list):
        for url in type_list:
            self.scrap_input_player_into_db_wrapper(url=url)


class ManageTeam():

    def __init__(self, done_folder_path, links_folder_path, session):
        self.teams_done_path = done_folder_path + "/done_teams.json"
        self.url_list_path = links_folder_path + "/teams.json"
        self.teams_done = None
        self.teams_urls = None
        self.session = session
        self.update_dict = update_team.UpdateTeamDict()
        self.input_dict = input_team_dict.InputTeamDict(
            session_db=self.session)
        self.get_urls = get_url.LeagueUrlDownload()

    def set_up_manage_team(self):
        self.load_teams_done_file()
        self.load_teams_url_file()

    def load_teams_done_file(self):
        if os.path.exists(self.teams_done_path)==False:
            self.teams_done = self.create_teams_done_file()
        else:
            with open(self.teams_done_path) as file:
                self.teams_done = json.load(file)

    def create_teams_done_file(self):
        teams_done = {'teams_done': []}
        with open(self.teams_done_path, 'w') as file:
            json.dump(teams_done, file)
        return teams_done
    
    def load_teams_url_file(self):
        if os.path.exists(self.url_list_path)==False:
            self.teams_urls = self.create_team_url_file()
        else:
            with open(self.url_list_path) as file:
                self.teams_urls = json.load(file)

    def create_team_url_file(self):
        teams_urls = {}
        with open(self.url_list_path, 'w') as file:
            json.dump(teams_urls, file)
        return teams_urls

    def scrape_and_input_team_into_db(self, url):
            team_o = team_scraper.TeamScraper(url=url)
            dict_team = team_o.get_info()
            dict_team_updated = (self.update_dict
                                   .update_team_dict(dict_team))
            print(dict_team_updated['general_info']['short_name'])
            self.input_dict.input_team_dict(team_dict=dict_team_updated)

    def scrap_input_team_into_db_wrapper(self, url):
        uid = re.findall("team\/([0-9]+)\/", url)[0]
        if uid in self.teams_done["teams_done"]:
            return
        try:
            self.scrape_and_input_team_into_db(url=url)
        except:
            with open(self.teams_done_path, 'w') as file:
                json.dump(self.teams_done, file)
        self.teams_done["teams_done"].append(uid)

    def get_team_urls_in_league(self, league_uid):
        if league_uid in self.teams_urls:
            return  self.teams_urls[league_uid] 
        url_list = self.get_urls.get_team_refs(league=league_uid)
        if url_list != []:
            self.teams_urls[league_uid] = url_list
            with open(self.url_list_path, 'w') as file:
                json.dump(self.teams_urls, file)
        return url_list
    
    def add_teams_from_league_to_db(self, league_uid):
        url_list = self.get_team_urls_in_league(
            league_uid=league_uid)
        try:
            for url in url_list:
                self.scrap_input_team_into_db_wrapper(url=url)
        except:
            with open(self.teams_done_path, 'w') as file:
                json.dump(self.teams_done, file)
        with open(self.teams_done_path, 'w') as file:
            json.dump(self.teams_done, file)
       

class ManageLeague():

    def __init__(self, done_folder_path, session):
        self.leagues_done_path = done_folder_path + "/done_leagues.json"
        self.leagues_done = None
        self.session = session
        self.update_dict = update_league.UpdateLeagueDict()
        self.input_dict = input_league_dict.InputLeagueDict(
            db_session=self.session)

    def set_up_manage_league(self):
        self.load_leagues_done_file()

    def load_leagues_done_file(self):
        if os.path.exists(self.leagues_done_path)==False:
            self.leagues_done = self.create_leagues_done_file()
        else:
            with open(self.leagues_done_path) as file:
                self.leagues_done = json.load(file)

    def create_leagues_done_file(self):
        leagues_done = {'leagues_done': []}
        with open(self.leagues_done_path, 'w') as file:
            json.dump(leagues_done, file)
        return leagues_done

    def scrape_and_input_league_into_db(self, url):
            league_o = league_scraper.LeagueScrapper(url=url)
            dict_league = league_o.get_league_data()
            dict_league_updated = (self.update_dict
                                   .update_league_dict(dict_league))
            print(dict_league_updated["league_name"])
            self.input_dict.input_league_dict(league_dict=dict_league_updated)

    def scrap_input_league_into_db_wrapper(self, league_uid):
        if league_uid in self.leagues_done["leagues_done"]:
            return
        url = ELITE_URL + LEAGUE_URLS[league_uid]
        self.scrape_and_input_league_into_db(url=url)
        with open(self.leagues_done_path, 'w') as file:
            json.dump(self.leagues_done, file)
        self.leagues_done["leagues_done"].append(league_uid)
 
    def add_teams_from_league_to_db(self, league_uid):
        self.scrap_input_league_into_db_wrapper(league_uid=league_uid)
        with open(self.leagues_done_path, 'w') as file:
            json.dump(self.leagues_done, file)            

