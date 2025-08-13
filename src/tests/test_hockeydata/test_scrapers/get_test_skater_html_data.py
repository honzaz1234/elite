from pathlib import Path

import hockeydata.playwright_setup.playwright_setup as ps

from  hockeydata.scrapers import * 


current_dir = Path(__file__).parent

FOLDER_PATH = current_dir / "data" 

URL_LIST_SKATERS = [
    ("howe", "https://www.eliteprospects.com/player/20605/gordie-howe"),
#    ("gretzky", "https://www.eliteprospects.com/player/9678/wayne-gretzky"),
 #   ("lemieux", "https://www.eliteprospects.com/player/9679/mario-lemieux"),
    ("mcdavid", "https://www.eliteprospects.com/player/183442/connor-mcdavid"),
]

URL_LIST_GOALIES = [
    ("hasek", "https://www.eliteprospects.com/player/8665/dominik-hasek"),
  #  ("roy", "https://www.eliteprospects.com/player/21308/patrick-roy"),
   # ("brodeur", "https://www.eliteprospects.com/player/9096/martin-brodeur"),
    ("dostal", "https://www.eliteprospects.com/player/236340/lukas-dostal"),
]

playwright_session = ps.PlaywrightSetUp()


def get_path(info_type, tuple_, data):
    file_name = tuple_[0] + "_" + info_type + ".html"
    file_path = FOLDER_PATH / file_name
    
    return file_path


for tuple_ in URL_LIST_GOALIES:
    goalie_scraper = GoalieScraper(
        url=tuple_[1], page=playwright_session.page,
        )
    goalie_scraper.go_to_page()
    goalie_scraper.get_data()
    for info_type in goalie_scraper.scraped_data:
        if "stats" in info_type:
            for sub_type in goalie_scraper.scraped_data[info_type]:
                name_ = info_type + "_" + sub_type
                path_ = get_path(name_, tuple_, goalie_scraper.scraped_data)
                file = goalie_scraper.scraped_data[info_type][sub_type]
                with open(path_, "w", encoding="utf-8") as f:
                    f.write(file)
        else:
            path_ = get_path(info_type, tuple_, goalie_scraper.scraped_data)
            file = goalie_scraper.scraped_data[info_type]
            with open(path_, "w", encoding="utf-8") as f:
                f.write(file)
        

for tuple_ in URL_LIST_SKATERS:
    skater_scraper = SkaterScraper(
        url=tuple_[1], page=playwright_session.page,
        )
    skater_scraper.go_to_page()
    skater_scraper.get_data()
    for info_type in skater_scraper.scraped_data:
        path_ = get_path(info_type, tuple_, skater_scraper.scraped_data)
        file = skater_scraper.scraped_data[info_type]
        with open(path_, "w", encoding="utf-8") as f:
            f.write(file)
    