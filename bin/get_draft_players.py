import json

import database_session.database_session as ds
import management.management as management


#path to folder with files with already downloaded entities (league, team, #player) must be specified

done_folder_path = "./data/data_dict/"

#path to folder with links to entities must be specified

links_folder_path = "./data/links/"

#path to database must be specifed

db_path = "./database/hockey_v16_test.db"

with open('./data/other/draft_urls.json', 'r') as f:
    urls = json.load(f)
urls = urls["players"]

session_o = ds.GetDatabaseSession(db_path=db_path)


session_o.set_up_connection()


manage_player = management.ManagePlayer(
        done_folder_path=done_folder_path,
        links_folder_path=links_folder_path,
        session_o=session_o
        )

manage_player.set_up_management()
for url in urls:
    try:
        manage_player.scrape_input_into_db_wrapper(url)
    except BaseException as e:
         if manage_player.done_file is None:
             raise e
         with open(manage_player.done_path, 'w') as f:
             json.dump(manage_player.done_file, f)
         raise e
