import json
import os
import re
import time
import hockeydata.scraper.player_scraper as player
import hockeydata.get_urls.get_urls as get_url
import hockeydata.update_dict.update_player as update_player
import hockeydata.input_dict.input_player_dict as input_dict
from  hockeydata.database_creator.create_session import session

url_links = "./data/links/players.json"
dict_data = "./data/data_dict/"
done_players_path = "./data/data_dict/done_players.json"

season_url_scraper = get_url.SeasonUrlDownload()
update_dict = update_player.UpdatePlayer()
input_database = input_dict.InputPlayerDict(db_session=session)
league_url_scraper = get_url.LeagueUrlDownload()

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
            or len(player_links[league_]["players"])==0
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
            dict_player_updated = update_dict.update_player_dict(dict_player)
            print(dict_player_updated)
            input_database.input_player_dict(player_dict=dict_player_updated)
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
