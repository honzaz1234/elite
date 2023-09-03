import json
import os
import re
import time
import scraper.player as player
import get_urls.player.season.season_url as season_url
import get_urls.player.league as league_url
import update_dict.wraper as update_dict_wraper
import database.entry_data.input_dict as input_dict

url_links = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/links/players.json"
dict_data = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/"
done_players_path = "C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/data/data_dict/update_players.json"
file_name_done = "done_players.json"


season_url_scraper = season_url.SeasonUrlDownload()
update_dict1 = update_dict_wraper.UpdateDictWraper()
input_database = input_dict.InputPlayerDict()
league_url_scraper = league_url.LeagueUrlDownload()

list_seasons_whl = league_url_scraper.create_season_list(1966, 2023)
list_seasons_ohl = league_url_scraper.create_season_list(1974, 2023)
list_seasons_qmjhl = league_url_scraper.create_season_list(1975, 2023)


dict_input = {"WHL": list_seasons_whl,
              "OHL": list_seasons_ohl, "QMJHL": list_seasons_qmjhl}

data_list = os.listdir(dict_data)

pd_f = open(url_links)
player_links = json.load(pd_f)

help_list = []

for league_ in dict_input:
    print(league_)
    season_list = dict_input[league_]
    for season_ in season_list:
        if (season_ not in player_links[league_]
            or len(player_links[league_]["goalies"])==0
            or len(player_links[league_]["goalies"])==0
            ):
            url_season = season_url_scraper.get_player_season_refs(
                league=league_, season=season_)
            print(url_season)
            player_links[league_][season_] = url_season
    with open(url_links, "w") as fp:
        json.dump(url_season, fp)


f = open(url_links)
player_links = json.load(f)

for league_ in dict_input:
    season_list = dict_input[league_]
    for season_ in season_list:
        start_season = time.time()
        all_links = []
        season_links = player_links[league_][season_]
        for key in season_links:
            all_links = season_links[key] + all_links
        to_download = []
        f2 = open(done_players_path)
        players_done = json.load(f2)
        for link in all_links:
            uid = re.findall('([0-9]+)', link)[0]
            if uid not in players_done["players_done"]:
                to_download.append(link)
        print(to_download)
        for link in to_download:
            uid = re.findall('([0-9]+)', link)[0]
            print(link)
            if "depth-chart" in link:
                continue
            time_start = time.time()
            player_o = player.PlayerScraper(url=link)
            dict_player = player_o.get_info_all()
            dict_player_updated = update_dict1.update_player_dict(dict_player)
            input_database.input_player_dict(dict=dict_player_updated)
            players_done["players_done"].append(uid)
            time_end = time.time()
            print("one player duration:")
            print(str(time_end-time_start))
            print(len(players_done["players_done"]))
            time.sleep(0.5)
        with open(done_players_path, "w") as fp:
            json.dump(players_done, fp)
        end_season = time.time()
        season_duration = end_season - start_season
        print("Duration Season: " + str(season_duration))
        print("n_players: " + str(len(to_download)))
    print("all players downloaded")
with open(done_players_path, "w") as fp:
    json.dump(players_done, fp)
