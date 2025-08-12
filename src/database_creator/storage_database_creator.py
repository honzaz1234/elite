from sqlalchemy import Column, Integer, LargeBinary, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class Scrape(Base):

    __tablename__ = 'scrapes'

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, default=datetime.utcnow)
    end_datetime = Column(DateTime, nullable=True)
    description = Column(String)


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
    player_id = Column(Integer)
    scrape_id = Column(Integer, ForeignKey('scraped.id'))
    time = Column(DateTime, default=datetime.utcnow)


    def __init__(
            self, player_id: int, scrape_id: int):
        self.player_id = player_id
        self.scrape_id = scrape_id
        self.time =  datetime.utcnow()


    def __repr__(self):
        return "<Player(id=%s, player_id='%s', scrape_id='%s', time=%s)>" % (
            self.id, self.player_id, self.scrape_id, self.time
        )
    
    
class PlayerStats(Base):

    __tablename__ = 'player_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    html_data = Column(LargeBinary) 


    def __repr__(self):
        return "<PlayerStats(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id, self.html_data
            )


class PlayerInfos(Base):

    __tablename__ = 'player_infos'


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