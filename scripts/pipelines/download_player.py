import json
import os
import re
import time
import scraper.player as player
import get_urls.player.season.season_url as season_url
import get_urls.player.league as league_url
import update_dict.wraper as update_dict_wraper
import database.entry_data.input_dict as input_dict

url_links = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/links/players/"
dict_data = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/"
file_name_done = "done_players.json"


season_url_scraper = season_url.SeasonUrlDownload()
update_dict1 = update_dict_wraper.UpdateDictWraper()
input_database = input_dict.InputPlayerDict()
league_url_scraper = league_url.LeagueUrlDownload()

list_seasons_nhl = league_url_scraper.create_season_list(1917, 2023)



dict_input = {"NHL": list_seasons_nhl, "Czechia": list_seasons_nhl, "AHL": list_seasons_nhl}
print(list_seasons_nhl)

links_list = os.listdir(url_links)
data_list = os.listdir(dict_data)


for league1 in dict_input:
    season_list = dict_input[league1]
    for season_1 in season_list:
        file_name = league1 + "_" + season_1 + ".json"
        if file_name in links_list:
            continue
        url_season = league_url_scraper.get_player_refs(league=league1, season=season_1)
        print(url_season)
        file_name = league1 + "_" + season_1 + ".json"
        file_path = url_links + file_name
        with open(file_path, "w") as fp:
            json.dump(url_season, fp)
try:
    for league in dict_input:
        season_list = dict_input[league]
        print(season_list)
        for season_1 in season_list:
            print(season_1)
            file_name = league + "_" + season_1 + ".json"
            file_path_links = url_links + file_name
            f = open(file_path_links)
            season_links = json.load(f)
            all_links = []
            for key in  season_links:
                all_links = season_links[key] + all_links
            to_download = []
            file_path_data = dict_data + file_name_done
            if file_name_done not in data_list:
                season_data={}
                season_data["players_done"] = []
                to_download = all_links.copy()
            else:
                f2 = open(file_path_data)
                season_data = json.load(f2)
            for link in all_links:
                print("link:")
                print(link)
                uid = re.findall('([0-9]+)', link)[0]
                print(uid)
                if uid not in season_data["players_done"]:
                    print("not downloaded:")
                    print(uid)
                    to_download.append(link)
            print(to_download)
            for link in to_download:
                uid = re.findall('([0-9]+)', link)[0]
                print(link)
                if "depth-chart" in link:
                    continue
                time_start = time.time()
                player_o = player.PlayerScraper(url=link)
                time_end=time.time()
                print(time_end - time_start)
                dict_player = player_o.get_info_all()
                dict_player_updated = update_dict1.update_player_dict(dict_player)
                input_database.input_player_dict(dict=dict_player_updated)
                season_data["players_done"].append(uid)
                time_end = time.time()
                print("one player duration:")
                print(str(time_end-time_start))
                print(len(season_data["players_done"]))
            with open(file_path_data, "w") as fp:
                json.dump(season_data, fp)
except:
    with open(file_path_data, "w") as fp:
        json.dump(season_data, fp)

    
    
        

        
