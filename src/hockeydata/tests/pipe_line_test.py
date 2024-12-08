import hockeydata.scraper.player_scraper as player_scraper
import hockeydata.scraper.team_scraper as team_scraper
import hockeydata.update_dict.update_player as player_updater
import hockeydata.update_dict.update_team as team_updater
import hockeydata.playwright_setup.playwright_setup as ps
import hockeydata.input_dict.input_player_dict as input_dict_player
import hockeydata.input_dict.input_team_dict as input_dict_team
import hockeydata.database_session.database_session as ds

import json

#path to database must be specifed

DB_PATH = "./database/hockey_test.db"

league_list = ['Czechia', 'NHL', 'SHL', 'AHL']

PLAYER_URLS = [
   # "https://www.eliteprospects.com/player/8627/jaromir-jagr",
   # "https://www.eliteprospects.com/player/20605/gordie-howe",
    "https://www.eliteprospects.com/player/183442/connor-mcdavid",
    "https://www.eliteprospects.com/player/190526/radim-zohorna",
    "https://www.eliteprospects.com/player/19145/bobby-orr",
    "https://www.eliteprospects.com/player/8665/dominik-hasek",
    "https://www.eliteprospects.com/player/70424/andrei-vasilevsky"
               ]

TEAM_URLS = [
    #"https://www.eliteprospects.com/team/64/montreal-canadiens",
    "https://www.eliteprospects.com/team/162/hc-slavia-praha",
    "https://www.eliteprospects.com/team/3271/hc-junior-melnik"

]

def player_pipeline_test(player_url, session):
    pst_o = ps.PlaywrightSetUp()
    ps_o = player_scraper.PlayerScraper(url=player_url, page=pst_o.page)
    player_dict = ps_o.get_info_all()
    pst_o.p.stop()
    dict_updater = player_updater.UpdatePlayer()
    dict_updated = dict_updater.update_player_dict(player_dict)
    dict_updated
    insert_player_data = input_dict_player.InputPlayerDict(db_session=session)
    insert_player_data.input_player_dict(player_dict=dict_updated)


def team_pipeline_test(team_url, session):
    pst_o = ps.PlaywrightSetUp()
    ts_o = team_scraper.TeamScraper(team_url, page=pst_o.page)
    team_dict = ts_o.get_info()
    pst_o.p.stop()
    tu_o = team_updater.UpdateTeamDict()
    team_dict_updated = tu_o.update_team_dict(team_dict)
    insert_team_data = input_dict_team.InputTeamDict(session_db=session)
    insert_team_data.input_team_dict(team_dict=team_dict_updated)

def league_pipeline_test():
    pass


def main():
    session1 = ds.DatabaseSession(done_folder_path="",
                              links_folder_path="",
                              db_path=DB_PATH)
    session1.set_up_connection()
    to_test = input('Select pipelines to be tested: ')
    if 'player' in to_test:
        for player_url in PLAYER_URLS:
            player_pipeline_test(player_url, session1.session)
    if 'team' in to_test:
        for team_url in TEAM_URLS:
            team_pipeline_test(team_url, session1.session)


if __name__ == "__main__":
    main()