from datetime import datetime

from sqlalchemy import desc

import hockeydata.database_session.database_session as ds
import hockeydata.entity_data.input_html as ih
import hockeydata.entity_data.scrapers as ps
import entity_data.storage_db_getter.storage_db_getter as sdg
import hockeydata.entity_data.playwright_setup.playwright_setup as pls


DB_PATH = "./database/storage_db_test.db"
PLAYER_URL = "https://www.eliteprospects.com/player/183442/connor-mcdavid"


session_o = ds.GetScrapeDBSession(db_path=DB_PATH)
session_o.set_up_connection()
session_o.clear_all_tables()
session_o.close_session()
session_o.set_up_connection()
start_scrape = datetime.now()
pl_o = pls.PlaywrightSetUp()
ps_o = ps.SkaterScraper(url=PLAYER_URL, page=pl_o.page)

ps_o.go_to_page()
ps_o.get_data()

end_scrape = datetime.now()

input_log_db = ih.LogInputter(db_session=session_o.session, scrape_id=1, start_time=start_scrape, 
                              end_time=end_scrape, scrape_type="player")
input_log_db._input_log()

input_db = ih.PlayerHTMLInputter(db_session=session_o.session, scraped_data=ps_o.scraped_data, scrape_id=1)
input_db.input_data()

stg_o = sdg.StorageDBDataGetter(db_session=session_o.session, scrape_ids=[1], player_uids=[183442], is_goalie=False)
stg_o.get_data()