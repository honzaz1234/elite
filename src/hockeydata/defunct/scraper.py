import get_urls.player.league as leagues
import scraper.player.player_scraper as player

class Scraper:

    
    def __init__(self):
        pass
    
    def get_player_refs(self, dict_info=None):

        """wraper function used to download urls of all players based on league and season played
           dict_info - dictionary, keys - names of leagues; values - list of years to be downloaded
            2011 = 2011-2012 season etc. 
            output: dictionary: leagues -> season -> (players-goalies) -> urls"""

        dict_player_ref = {}
        if dict_info is None:
            return
        leauge_getter = leagues.LeagueDownload()
        for league in dict_info:
            year_list = dict_info[league]
            league_dict = leauge_getter.get_league_refs(league=league, years=year_list)
            dict_player_ref[league]=league_dict
        return dict_player_ref

    
    def get_player_info_wrapper(self, url_dict):

        """"function used to download information on player based on dictionary of urls of player profiles
         attained from function  get_player_refs
         output: dictionary: names -> (general_info-stats-achievements)-> values"""

        dict_players = {}
        list_downloaded = []
        for league in url_dict:
            for season in url_dict[league]:
                for player_type in url_dict[league][season]:
                    list_players = url_dict[league][season][player_type]
                    sub_dict_players = {}
                    for url_player in list_players:
                        if url_player in list_downloaded:
                            continue
                        print(url_player)
                        player_object = player.PlayerScraper(url_player)
                        info_dict = player_object.get_info_all()
                        dict_players = {**dict_players, **info_dict}
                        list_downloaded.append(url_player)
        return dict_players
    



        







            
            

            

        
