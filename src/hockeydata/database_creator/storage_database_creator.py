from sqlalchemy import Boolean, Column, Integer, LargeBinary, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class Scrape(Base):

    __tablename__ = 'scrapes'

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    description = Column(String, nullable=False)


    def __init__(
            self, description=None, start_datetime=None, end_datetime=None
            ):
        self.start_datetime = start_datetime or datetime.utcnow()
        self.end_datetime = end_datetime
        self.description = description


    def __repr__(self):
        return "<Scrape(id=%s, start='%s', end='%s', description='%s')>" % (
            self.id, self.start_datetime, self.end_datetime, self.description
        )
    

class Player(Base):

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    player_uid = Column(Integer, nullable=False)
    scrape_id = Column(Integer, ForeignKey('scraped.id'), nullable=False)
    is_goalie = Column(Boolean, nullable=False)
    time = Column(DateTime, default=datetime.utcnow, nullable=False)


    def __init__(
            self, player_uid: int, scrape_id: int):
        self.player_uid = player_uid
        self.scrape_id = scrape_id
        self.time =  datetime.utcnow()


    def __repr__(self):
        return "<Player(id=%s, player_uid='%s', scrape_id='%s', time=%s)>" % (
            self.id, self.player_uid, self.scrape_id, self.time
        )
    
    
class SkaterStats(Base):

    __tablename__ = 'skater_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    league_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False) 


    def __repr__(self):
        return "<PlayerStats(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id, self.html_data
            )
    

class GoalieStats(Base):

    __tablename__ = 'goalie_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    league_type = Column(String, nullable=False)
    season_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False) 


    def __repr__(self):
        return "<PlayerStats(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id, self.html_data
            )


class PlayerFacts(Base):

    __tablename__ = 'player_facts'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    html_data = Column(LargeBinary)  


    def __repr__(self):
        return "<PlayerInfos(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id)


class Achievements(Base):

    __tablename__ = 'achievements'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    html_data = Column(LargeBinary) 


    def __repr__(self):
        return "<Achievements(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id)