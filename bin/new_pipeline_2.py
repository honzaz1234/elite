

import hockeydata.database_session.database_session as ds
import hockeydata.entity_data.parser.player_parser as pp
import hockeydata.entity_data.storage_db_getter.storage_db_getter as sdg


DB_PATH = "./database/storage_db_test.db"

session_o = ds.GetScrapeDBSession(db_path=DB_PATH)
session_o.set_up_connection()


db_getter_o = sdg.StorageDBDataGetter(
    db_session=session_o.session, 
    scrape_ids=[1], 
    player_uids=[183442], 
    is_goalie=False
    )

db_data = db_getter_o.get_data()

pp_o = pp.PlayerParser(scraped_data=db_data[183442], player_uid=183442)
parsed_data = pp_o.get_info_all()
parsed_data



