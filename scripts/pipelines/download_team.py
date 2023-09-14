import hockeydata.get_urls.get_urls as get_url
import hockeydata.scraper.team_scraper as scraper_team
import hockeydata.update_dict.update_team as team_updater
import hockeydata.input_dict.input_team_dict as input_dict_2
import hockeydata.database_creator.database_creator as db
import re
import json
import time

get_url_o = get_url.LeagueUrlDownload()

league_list = ['USHL']
#league_list = get_url_o.leagues_paths.keys()

url_links_path = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/links/teams.json"
dict_data_path = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/done_teams.json"

print(league_list)

tu_o = team_updater.UpdateTeamDict()
insert_team_data = input_dict_2.InputTeamDict(session_db=db.session)

f =  open(dict_data_path)
u_id_done_dict = json.load(f)
u_id_done_list = u_id_done_dict["teams_done"]
f = open(url_links_path)
links_dict = json.load(f)

is_created = False

for league_ in league_list:
    print(league_)
    dict_league = {}
    if (league_ not in links_dict
        or len(links_dict[league_])==0
        ):
        url_list = get_url_o.get_team_refs(league=league_)
        if url_list ==[]:
            print("no data downloaded")
            break
        links_dict[league_] = url_list
        with open(url_links_path, "w") as fp:
            json.dump(links_dict, fp)
        is_created = True
        time.sleep(60)
    f = open(url_links_path)
    links_dict = json.load(f)
    url_list = links_dict[league_]
    print(dict_league)
    print(type(dict_league))
    count_requests = 0      
    for url in url_list:
        print(url)
        time_start = time.time()
        u_id = re.findall("team\/([0-9]+)\/", url)[0]
        if u_id in u_id_done_list:
            continue
        count_requests += 1
        ts_o = scraper_team.TeamScraper(url)
        team_data = ts_o.get_info()
        team_dict_updated = tu_o.update_team_dict(team_data)
        print(team_dict_updated)
        print("b")
        insert_team_data.input_team_dict(team_dict=team_dict_updated)
        print("c")
        u_id_done_list.append(u_id)
        time_end = time.time()
        time_difference = time_end - time_start
        print("duration: " + str(time_difference))
        time.sleep(2)
    u_id_done_dict["teams_done"] = u_id_done_list
    with open(dict_data_path, "w") as fp:
        json.dump(u_id_done_dict, fp)
    if count_requests > 10:
        time.sleep(120)
print("all teams downloaded")





