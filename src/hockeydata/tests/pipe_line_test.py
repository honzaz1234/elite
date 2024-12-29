import hockeydata.get_urls.get_urls as get_urls
import hockeydata.scraper.league_scraper as league_scraper
import hockeydata.scraper.player_scraper as player_scraper
import hockeydata.scraper.team_scraper as team_scraper
import hockeydata.update_dict.update_league as league_updater
import hockeydata.update_dict.update_player as player_updater
import hockeydata.update_dict.update_team as team_updater
import hockeydata.playwright_setup.playwright_setup as ps
import hockeydata.input_dict.input_league_dict as input_dict_league
import hockeydata.input_dict.input_player_dict as input_dict_player
import hockeydata.input_dict.input_team_dict as input_dict_team
import hockeydata.database_session.database_session as ds

import json
import re

#path to database must be specifed
DB_PATH = "./database/hockey_test.db"

PLAYER_URLS = [
    "https://www.eliteprospects.com/player/8627/jaromir-jagr",
    "https://www.eliteprospects.com/player/20605/gordie-howe",
    "https://www.eliteprospects.com/player/183442/connor-mcdavid",
    "https://www.eliteprospects.com/player/19456/daniel-goneau",
    "https://www.eliteprospects.com/player/190526/radim-zohorna",
    "https://www.eliteprospects.com/player/19145/bobby-orr",
    "https://www.eliteprospects.com/player/8665/dominik-hasek",
    "https://www.eliteprospects.com/player/70424/andrei-vasilevsky"
]

TEAM_URLS = [
    #"https://www.eliteprospects.com/team/64/montreal-canadiens",
    "https://www.eliteprospects.com/team/162/hc-slavia-praha",
    "https://www.eliteprospects.com/team/3271/hc-junior-melnik",
    "https://www.eliteprospects.com/team/8178/toronto-marlboros-u16-aaa",
    "https://www.eliteprospects.com/team/1392/zemgale"
]

LEAGUE_URLS = [
    "https://www.eliteprospects.com/league/czechia",
    "https://www.eliteprospects.com/league/liiga",
]


def player_pipeline_test(player_url, session):
    pst_o = ps.PlaywrightSetUp()
    ps_o = player_scraper.PlayerScraper(url=player_url, page=pst_o.page)
    player_dict = ps_o.get_info_all()
    name = re.findall('-([a-z]+)$', player_url)[0]
    file_name = name + '_new.json'
    with open(file_name, 'w') as file:
        json.dump(player_dict, file)
    pst_o.p.stop()
    dict_updater = player_updater.UpdatePlayer()
    dict_updated = dict_updater.update_player_dict(player_dict)
    insert_player_data = input_dict_player.InputPlayerDict(db_session=session)
    insert_player_data.input_player_dict(player_dict=dict_updated)

def team_pipeline_test(team_url, session):
    pst_o = ps.PlaywrightSetUp()
    ts_o = team_scraper.TeamScraper(team_url, page=pst_o.page)
    team_dict = ts_o.get_info()
    name = re.findall('([a-z0\-]+)$', team_url)[0]
    file_name = name + '_new.json'
    with open(file_name, 'w') as file:
        json.dump(team_dict, file)
    pst_o.p.stop()
    tu_o = team_updater.UpdateTeamDict()
    team_dict_updated = tu_o.update_team_dict(team_dict)
    insert_team_data = input_dict_team.InputTeamDict(session_db=session)
    insert_team_data.input_team_dict(team_dict=team_dict_updated)

def league_pipeline_test(league_url, session):
    pst_o = ps.PlaywrightSetUp()
    ls_o = league_scraper.LeagueScrapper(league_url, page=pst_o.page)
    league_dict = ls_o.get_info()
    name = re.findall('([a-z0\-]+)$', league_url)[0]
    file_name = name + '_new.json'
    with open(file_name, 'w') as file:
        json.dump(league_dict, file)
    pst_o.p.stop()
    lu_o = league_updater.UpdateLeagueDict()
    league_dict_updated = lu_o.update_league_dict(league_dict)
    insert_league_data = input_dict_league.InputLeagueDict(session_db=session)
    insert_league_data.input_league_dict(league_dict=league_dict_updated)

def player_urls_pipeline_test():
    pst_o = ps.PlaywrightSetUp()
    lu_o = get_urls.LeagueUrlDownload(page=pst_o.page)
    lu_o.get_player_refs(league='NHL')

def team_urls_pipeline_test():
    pst_o = ps.PlaywrightSetUp()
    lu_o = get_urls.LeagueUrlDownload(page=pst_o.page)
    lu_o.get_team_refs(league='NHL')
  

def main():
    session1 = ds.DatabaseSession(done_folder_path="",
                                 links_folder_path="",
                                 db_path=DB_PATH)
    session1.set_up_connection()
    session1.clear_all_tables()
    to_test = input('Select pipelines to be tested: ')
    if 'player' in to_test:
        for player_url in PLAYER_URLS:
            player_pipeline_test(player_url, session1.session)
    if 'team' in to_test:
        for team_url in TEAM_URLS:
            team_pipeline_test(team_url, session1.session)
    if 'league' in to_test:
        for league_url in LEAGUE_URLS:
            league_pipeline_test(league_url, session1.session)
    if 'url_p' in to_test:
        player_urls_pipeline_test()
    if 'url_t' in to_test:
        team_urls_pipeline_test()

if __name__ == "__main__":
    main()