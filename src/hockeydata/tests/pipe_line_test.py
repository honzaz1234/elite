import hockeydata.scraper.player_scraper as player_scraper
import hockeydata.update_dict.update_player as player_updater
import hockeydata.playwright_setup.playwright_setup as ps
import hockeydata.input_dict.input_player_dict as input_dict_2
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

def player_pipeline_test(player_url, session):
    pst_o = ps.PlaywrightSetUp()
    ps_o = player_scraper.PlayerScraper(url=player_url, page=pst_o.page)
    player_dict = ps_o.get_info_all()
    with open('mccdavid_test.json', "w") as json_file:
        json.dump(player_dict, json_file, indent=4)
    pst_o.p.stop()
    dict_updater = player_updater.UpdatePlayer()
    dict_updated = dict_updater.update_player_dict(player_dict)
    dict_updated
    insert_player_data = input_dict_2.InputPlayerDict(db_session=session)
    insert_player_data.input_player_dict(player_dict=dict_updated)

def team_pipeline_test():
    pass

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


if __name__ == "__main__":
    main()