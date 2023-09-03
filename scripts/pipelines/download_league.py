import get_urls.player.league as get_url
import scraper.league as league_scraper
import update_dict.wraper as update_wraper
import database.entry_data.input_dict as input_dict_2
import re
import json
import os
import time

get_url_o = get_url.LeagueUrlDownload()

league_dict = get_url_o.league_refs
league_list = ['NHL', 'Czechia', 'AHL', 'WHL',
               'OHL', 'QMJHL', 'SHL', 'Liiga', 'NL']
url_elite = "https://www.eliteprospects.com"

dict_data_path = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/done_leagues.json"


lu_o = update_wraper.UpdateDictWraper()
insert_league_data = input_dict_2.InputLeagueDict()

f = open(dict_data_path)
u_id_done_dict = json.load(f)
u_id_done_list = u_id_done_dict["leagues_done"]

try:
    for league in league_list:
        league_url = league_dict[league]
        url = url_elite + league_url
        time_start = time.time()
        u_id = re.findall("league\/(.+)$", url)[0]
        print(u_id)
        if u_id in u_id_done_list:
            continue
        ls_o = league_scraper.LeagueScrapper(url)
        league_data = ls_o.get_league_data()
        team_dict_updated = lu_o.update_league_dict(league_data)
        print(team_dict_updated)
        insert_league_data.input_league_dict(league_dict=team_dict_updated)
        u_id_done_list.append(u_id)
        time_end = time.time()
        time_difference = time_end - time_start
        print("duration: " + str(time_difference))
        u_id_done_dict["leagues_done"] = u_id_done_list
        with open(dict_data_path, "w") as fp:
            json.dump(u_id_done_dict, fp)
        time.sleep(120)
    print("all leagues downloaded")
except:
    u_id_done_dict["leagues_done"] = u_id_done_list
    with open(dict_data_path, "w") as fp:
        json.dump(u_id_done_dict, fp)
