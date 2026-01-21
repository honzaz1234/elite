import json

import database_session.database_session as ds


from database_session.database_session import ScrapeDBSession
from hockeydata.entity_data.input_html import PlayerHTMLInputter
from hockeydata.entity_data.scrapers import GoalieScraper, SkaterScraper

#path to folder with files with already downloaded entities (league, team, #player) must be specified

done_folder_path = "./data/data_dict/"

#path to folder with links to entities must be specified

links_folder_path = "./data/links/"

#path to database must be specifed

db_path = "./database/test_storage_db.db"


session_o = ds.DatabaseSession(db_path=db_path)

session_o.set_up_connection()


