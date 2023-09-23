import hockeydata.get_urls.get_urls as get_url
import hockeydata.scraper.league_scraper as league_scraper
import hockeydata.update_dict.update_league as update_dict
import hockeydata.input_dict.input_league_dict as input_dict_2
from hockeydata.constants import *
from  hockeydata.database_creator.create_session import session
import re
import json
import time

get_url_o = get_url.LeagueUrlDownload()

league_dict = LEAGUE_URLS
league_list = ['AHL', 'WHL',
               'OHL', 'QMJHL', 'SHL', 'Liiga', 'NL', 'DEL']
url_elite = "https://www.eliteprospects.com"

dict_data_path = "./data/data_dict/done_leagues.json"


lu_o = update_dict.UpdateLeagueDict()
insert_league_data = input_dict_2.InputLeagueDict(db_session=session)

f = open(dict_data_path)
u_id_done_dict = json.load(f)
u_id_done_list = u_id_done_dict["leagues_done"]

for league in league_list:
    league_url = league_dict[league]
    url = ELITE_URL + league_url
    time_start = time.time()
    u_id = re.findall("league\/(.+)$", url)[0]
    print(u_id)
    if u_id in u_id_done_list:
        continue
    ls_o = league_scraper.LeagueScrapper(url)
    league_data = ls_o.get_league_data()
    league_dict_updated = lu_o.update_league_dict(league_data)
    print(league_dict_updated)
    insert_league_data.input_league_dict(league_dict=league_dict_updated)
    u_id_done_list.append(u_id)
    time_end = time.time()
    time_difference = time_end - time_start
    print("duration: " + str(time_difference))
    u_id_done_dict["leagues_done"] = u_id_done_list
    with open(dict_data_path, "w") as fp:
        json.dump(u_id_done_dict, fp)
    time.sleep(120)
print("all leagues downloaded")
u_id_done_dict["leagues_done"] = u_id_done_list
with open(dict_data_path, "w") as fp:
    json.dump(u_id_done_dict, fp)
