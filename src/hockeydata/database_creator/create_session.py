import hockeydata.get_urls.get_urls as league_url
from hockeydata.database_creator.database_creator import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

league_getter = league_url.LeagueUrlDownload()

database_location = input('Database path: ')
if database_location == '': 
    database_location = "./database/hockey_v8.db"

engine = create_engine("sqlite:///" + database_location, echo=False)
Base.metadata.create_all(bind=engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

check_data = session.query(Season).all()
if check_data == []:
    season_list = league_getter.create_season_list(1886, 2024)
    for one_season in season_list:
        season_entry = Season(season=one_season)
        session.add(season_entry)
        session.commit()
    years = [*range(1886, 2025, 1)]
    for year in years:
        season_entry = Season(season=year)
        session.add(season_entry)
        session.commit()