import database_session.database_session as ds
import management.input_data as management

#path to folder with files with already downloaded entities (league, team, #player) must be specified

done_folder_path = "./data/data_dict/"

#path to folder with links to entities must be specified

links_folder_path = "./data/links/"

#path to database must be specifed

db_path = "./database/hockey_v12.db"

#connection to database is managed by class GetDatabaseSession
#which takes one parameter with the path to the existing DB
#or path where the new DB should be created in case that it does not
#already exist at a given location

session_o = ds.GetDatabaseSession(db_path=db_path)

management_o = management.ManageLeague(
    done_folder_path=done_folder_path,
    session=session_o.session
)

league_list = ['Czechia', 'NHL', 'SHL', 'AHL']

#before scraping itself method set_up_connection must be called which sets up
#db session and loads data in table seasons in case the set up of database
#is established for the first time

session_o.set_up_connection()


#scraping, updating and inputing data into DB is administred by #Manage**DataType** classes.These classes load data from several files:
#a) done_file (done_folder_path) - dict with already scraped data
#   - in case that the name of the object (league, team, player) is in the #     done file, the script does not download this object again,
#   - on the other hand if the data for the object is already in the DB but 
#     but the league's name is not noted in the done file, it does not 
#     create duplicated values in the DB
     
#links_folder_path - dict with links of objects (Teams, Players) to be 
#                    downloaded 

#method for downloading data then always takes only one parameter - league_ids
#denoting leagues for which the data should be downloaded
#the names of leagues must be given as specified in module constants in keys #of dictionary LEAGUE_URLS in hockeydata package


type_to_scrape = input("Select one of the following options: player, team"
                       "league to decide which type of object for given"
                       " league_list should be downloaded.")

#PLAYER SCRAPER

if type_to_scrape=="player":
    manage_player = management.ManagePlayer(
        done_folder_path=done_folder_path,
        links_folder_path=links_folder_path,
        session=session_o.session
        )
    manage_player.add_players_from_leagues_to_db(league_uids=league_list)

#TEAM SCRAPER

if type_to_scrape=="team":
    manage_team = management.ManageTeam(
        done_folder_path=done_folder_path,
        links_folder_path=links_folder_path,
        session=session_o.session
        )
    manage_team.add_teams_from_leagues_to_db(league_uids=league_list)


#LEAGUE SCRAPER

if type_to_scrape=="league":
    manage_league = management.ManageLeague(
        done_folder_path=done_folder_path,
        session=session_o.session
        )
    manage_league.add_leagues_to_db(league_uids=league_list)