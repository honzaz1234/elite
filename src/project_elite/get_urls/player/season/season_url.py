import requests
import scrapy
import re
 


class SeasonUrlDownload:
    
    paths = {"main": "https://www.eliteprospects.com",
            "player_ref": "//table[@id='export-skater-stats-table']//td[@class='player']//a/@href", 
             "goalie_ref": "//table[@id='export-goalie-stats-table']//td[@class='player']//a/@href",
             "last_page_players": "//span[@class = 'hidden-xs']/a/@href",
             "last_page_goalies": "//span[@class = 'hidden-xs']/a/@href",
             "team_url": "//td[@class='team']//@href"
             }


                           
    def __init__(self):
        pass

    def _page_player(self, path, index):

        """downloads urls of player profiles from 1 page of seasonal statistic board"""

        subpage_path = path + "?page=" + str(index)
        subpage_html = requests.get(subpage_path).content
        selector_subpage = scrapy.Selector(text=subpage_html)
        player_refs = selector_subpage.xpath(SeasonUrlDownload.paths["player_ref"]).getall()
        return player_refs
        

    def _page_goalie(self, path, index):

        """downloads urls of goalie profiles from 1 page of seasonal statistic board"""

        subpage_path = path + "?sort-goalie-stats=svp&page-goalie=" + str(index)
        subpage_html = requests.get(subpage_path).content
        selector_subpage = scrapy.Selector(text=subpage_html)
        goalies_refs = selector_subpage.xpath(SeasonUrlDownload.paths["goalie_ref"]).getall()
        return goalies_refs


    def get_player_season_refs(self, league_stats_path, season):

        """downloads urls of player profiles for one season of one league from the webpage with statistics
            output dictionary: (players-goalies) -> urls"""
        dict_season = {}
        page_html = requests.get(league_stats_path).content
        selector_players = scrapy.Selector(text=page_html)
        ref_last_page = selector_players.xpath(SeasonUrlDownload.paths["last_page_players"]).getall()
        number_of_pages_players = [re.findall( "([0-9]+)$", string) for string in ref_last_page if re.search("[0-9]+$", string)]
        number_of_pages_goalies = [re.findall("([0-9]+)#goalies$", string) for string in ref_last_page if re.search("[0-9]+#goalies$", string)]
        sublist_players = []
        if number_of_pages_players == []:
            number_of_pages_players = 1
        else:
            number_of_pages_players = number_of_pages_players[0][0]
        for index in range(1, int(number_of_pages_players) + 1):
            player_refs = self._page_player(league_stats_path, index)
            sublist_players = sublist_players + player_refs
        if number_of_pages_goalies == []:
            number_of_pages_goalies = 1
        else:
            number_of_pages_goalies = number_of_pages_goalies[0][0]
        sublist_goalies = []
        for index in range(1, int(number_of_pages_goalies) + 1):
            goalies_refs = self._page_goalie(league_stats_path, index)
            sublist_goalies = sublist_goalies + goalies_refs
        dict_season["goalies"] = sublist_goalies
        dict_season["players"] = sublist_players
        return dict_season
    

    def get_team_season_refs(self, url_season, league_team_refs):
        season_html = requests.get(url_season).content
        sel_season = scrapy.Selector(text=season_html)
        team_refs = sel_season.xpath(SeasonUrlDownload.paths["team_url"]).getall()
        for team_ref in team_refs:
            team_ref_wo_season = re.findall("(.+)\/[0-9]{4}\-[0-9]{4}$", team_ref)[0]
            print(team_ref_wo_season)
            if team_ref_wo_season not in league_team_refs:
                league_team_refs.append(team_ref_wo_season)
        return league_team_refs








