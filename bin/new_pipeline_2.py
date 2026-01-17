

import hockeydata.database_session.database_session as ds
import hockeydata.entity_data.parser.player_parser as pp
import hockeydata.entity_data.update_dict.update_player as up
import hockeydata.entity_data.storage_db_getter.storage_db_getter as sdg


DB_PATH = "./database/storage_db_test.db"
PLAYER_UID = 9096

session_o = ds.ScrapeDBSession(db_path=DB_PATH)
session_o.set_up_connection()


db_getter_o = sdg.StorageDBDataGetter(
    db_session=session_o.session, 
    scrape_ids=[1], 
    player_uids=[PLAYER_UID], 
    is_goalie=True
    )

db_data = db_getter_o.get_data()

pp_o = pp.PlayerParser(scraped_data=db_data[PLAYER_UID], player_uid=PLAYER_UID)
parsed_data = pp_o.get_info_all()
up_o = up.UpdatePlayer()
updated_data = up_o.update_dict(dict=parsed_data)
updated_data



