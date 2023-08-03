import requests
import scrapy

class LeagueSeasonScraper():

    paths = {"table_section": "//table[@class = 'table standings table-sortable']//tbody[count(./tr/*)>1]",
             "table_section_names": "//table[@class = 'table standings table-sortable']//tr[@class='title']/td//text()",
            "table_row": "//table[@class = 'table standings table-sortable']//tr"}
    header_names = ["position", "team", "gp", "w", "t", "l", "otw", "otl", "gf", "ga", "plus_minus", "tp", "postseason"]

    def __init__(self, url):
        self.url = url 
        self.html = requests.get(self.url).content
        self.selector = scrapy.Selector(text=self.html)

    def get_section_standings(self, path_section):
        n_rows = len(self.selector.xpath(path_section).getall())
        print(n_rows)
        dict_section = {}
        for row_ind in range(1, n_rows + 1):
            dict_row = {}
            one_row_path = path_section + "[" + str(row_ind) + "]" + "/td//text()"
            row_data = self.selector.xpath(one_row_path).getall()
            row_data = [value.strip() for value in row_data if value.strip()!=""]
            for ind in range(1, len(row_data)):
                print(row_data[ind].strip())
                dict_row[LeagueSeasonScraper.header_names[ind]] = row_data[ind].strip()
            dict_section[row_data[0]] = dict_row
        return dict_section
    
    def get_season_standings(self):
        section_names = self.selector.xpath(LeagueSeasonScraper.paths["table_section_names"]).getall()
        section_names = [name.strip() for name in section_names]
        print(LeagueSeasonScraper.paths["table_section"])
        n_sections = len(self.selector.xpath(LeagueSeasonScraper.paths["table_section"]).getall())
        print(section_names)
        print(n_sections)
        if n_sections > len(section_names):
            section_names = ["main"] + section_names
        dict_season = {}
        for part_ind in range(1, n_sections + 1):
            path_section = LeagueSeasonScraper.paths["table_section"] + "[" + str(part_ind) + "]" + "/tr[not(@class = 'title')]"
            dict_section = self.get_section_standings(path_section=path_section)
            dict_season[section_names[part_ind - 1]] = dict_section
        return dict_season




    
