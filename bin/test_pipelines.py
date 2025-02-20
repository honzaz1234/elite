import database_session.database_session as ds

#path to folder with files with already downloaded entities (league, team, #player) must be specified

done_folder_path = "./data/data_dict/"

#path to folder with links to entities must be specified

links_folder_path = "./data/links/"

#path to database must be specifed

db_path = "./database/hockey_v11.db"

#connection to database, downloading links, scrapping entities and loading #them into database is managed by one wrapper class DatabaseSession
#only 3 parameters are 3 paths described above

session1 = ds.DatabaseSession(done_folder_path=done_folder_path,
                              links_folder_path=links_folder_path,
                              db_path=db_path)

league_list = ['Czechia', 'NHL', 'SHL', 'AHL']

#before scraping itself method set_up_connection must be called which sets up
#db session and loads data in table seasons in case the set up of database
#is made for the first time

session1.set_up_connection()

#method for downloading info about players, takes only one paramater: list of #names of leagues from which players should be downloaded 
#the names must be given as specified in module constants in keys of #dictionary LEAGUE_URLS in hockeydata package

session1.add_players_from_leagues_to_db(league_uid_list=league_list)

#method for downloading info about teams, takes only one paramater: list of #names of leagues from which teams should be downloaded 
#the names must be given as specified in module constants in keys of #dictionary LEAGUE_URLS in hockeydata package

session1.add_teams_from_leagues_to_db(league_uid_list=league_list)

#method for downloading info about leagues, takes only one paramater: list of names of leagues for which the info should be downloaded
#the names must be given as specified in module constants in keys of #dictionary LEAGUE_URLS in hockeydata package

session1.add_leagues_to_db(league_uid_list=league_list)