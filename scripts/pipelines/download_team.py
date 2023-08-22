import get_urls.player.league as get_url
import scraper.team as team_scraper
import update_dict.sections.team_info as team_updater
import database.entry_data.input_dict as input_dict_2
import re
import json
import os
import time

get_url_o = get_url.LeagueUrlDownload()

league_list = ['NHL', 'Czechia', 'AHL', 'WHL', 'OHL', 'QMJHL', 'SHL', 'Liiga', 'NL', 'KHL', 'ECHL', 'WC', 'Olympics', 'U20 WJC']
#league_list = get_url_o.leagues_paths.keys()

url_links = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/links/teams/"
dict_data_path = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/done_teams.json"
file_name_done = "done_teams.json"

print(league_list)

tu_o = team_updater.UpdateTeamDict()
insert_team_data = input_dict_2.InputTeamDict()

links_list = os.listdir(url_links)
f =  open(dict_data_path)
u_id_done_dict = json.load(f)
u_id_done_list = u_id_done_dict["teams_done"]

is_created = False

for league in league_list:
    print(league)
    dict_league = {}
    file_name = league + ".json"
    file_path = url_links + file_name
    if file_name not in links_list:
        url_list = get_url_o.get_team_refs(league=league)
        if url_list ==[]:
            print("no data downloaded")
            break
        time.sleep(60)
        dict_league[league] = url_list
        with open(file_path, "w") as fp:
            json.dump(dict_league, fp)
        is_created = True
    f = open(file_path)
    dict_league = json.load(f)
    print(dict_league)
    print(type(dict_league))
    url_list = dict_league[league]
    count_requests = 0      
    for url in url_list:
        print(url)
        time_start = time.time()
        u_id = re.findall("team\/([0-9]+)\/", url)[0]
        if u_id in u_id_done_list:
            continue
        count_requests += 1
        ts_o = team_scraper.TeamScraper(url)
        team_data = ts_o.get_info()
        team_dict_updated = tu_o.update_team_dict_wrap(team_data)
        print("b")
        insert_team_data.input_team_dict(team_dict=team_dict_updated)
        print("c")
        u_id_done_list.append(u_id)
        time_end = time.time()
        time_difference = time_end - time_start
        print("duration: " + str(time_difference))
    u_id_done_dict["teams_done"] = u_id_done_list
    with open(dict_data_path, "w") as fp:
        json.dump(u_id_done_dict, fp)
    if count_requests > 10:
        time.sleep(120)
print("all teams downloaded")





