from sqlalchemy import Boolean, Column, Integer, LargeBinary, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class HtmlPreviewMixin():


    def html_preview(self, length: int = 50) -> bytes:
        """Return a preview of html_data up to `length` bytes."""
        if hasattr(self, "html_data") and self.html_data:
            return self.html_data[:length] + b"..." if len(self.html_data) > length else self.html_data
        return b""


class Scrape(Base):

    __tablename__ = 'scrapes'

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
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
    

class PlayerURL(Base):

    __tablename__ = 'player_urls'


    id = Column(Integer, primary_key=True)
    player_url = Column(String, nullable=False)
    player_uid = Column(Integer, nullable=False)


    __table_args__ = (
        UniqueConstraint('player_url', 'player_uid', name='uq_player_urls_all_columns'),
    )


    def __init__(self, player_url: str, player_uid: int):
        self.player_url = player_url
        self.player_uid = player_uid


    def __repr__(self):
        return "<PlayerURL(id=%s, player_uid=%s, url='%s')>" % (
            self.id, self.player_uid, self.player_url
        )
    

class Player(Base):

    __tablename__ = 'players'


    id = Column(Integer, primary_key=True)
    player_uid = Column(Integer, nullable=False)
    scrape_id = Column(Integer, ForeignKey('scraped.id'), nullable=False)
    is_goalie = Column(Boolean, nullable=False)
    time = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)


    __table_args__ = (
        UniqueConstraint('scrape_id', 'player_uid', name='uq_players_scrape_id_player_uid'),
    )


    def __init__(self, player_uid: int, scrape_id: int, is_goalie: bool):
        self.player_uid = player_uid
        self.scrape_id = scrape_id
        self.is_goalie = is_goalie


    def __repr__(self):
        return (
            "<Player(id=%s, player_uid='%s', scrape_id='%s', is_goalie=%s, time=%s)>"
            % (self.id, self.player_uid, self.scrape_id, self.is_goalie, self.time)
        )
    
    
class SkaterStats(Base, HtmlPreviewMixin):

    __tablename__ = 'skater_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    league_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False)


    def __repr__(self):
        return (
            "<SkaterStats(id=%s, player_id=%s, league_type=%s, html_data=%s)>" %
            (self.id, self.player_id, self.league_type, self.html_preview())
        )
    

class GoalieStats(Base, HtmlPreviewMixin):

    __tablename__ = 'goalie_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    league_type = Column(String, nullable=False)
    season_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False)


    def __init__(self, player_id: int, html_data: bytes):
        self.player_id = player_id
        self.html_data = html_data


    def __repr__(self):
        return (
            "<GoalieStats(id=%s, player_id=%s, league_type=%s, "
            "season_type=%s, html_data=%s)>" %
            (self.id, self.player_id, self.league_type, self.season_type, self.html_preview())
        )


class PlayerFacts(Base):

    __tablename__ = 'player_facts'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    html_data = Column(LargeBinary)  


    def __init__(self, player_id: int, html_data: str):
        self.player_id = player_id
        self.html_data = html_data


    def __repr__(self):
        preview = self.html_data[:50] + b"..." if len(self.html_data) > 50 else self.html_data
        return "<PlayerFacts(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id, preview
        )


class Achievements(Base, HtmlPreviewMixin):

    __tablename__ = 'achievements'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    html_data = Column(LargeBinary)


    def __init__(self, player_id: int, html_data: bytes):
        self.player_id = player_id
        self.html_data = html_data


    def __repr__(self):
        return "<Achievements(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, self.player_id, self.html_preview()
        )
    

class PlayerMissingDataLog(Base):

    __tablename__ = "player_missing_data_logs"


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    data_type = Column(String, nullable=False)


    __table_args__ = (
        UniqueConstraint(
            'player_id', 'data_type',
            name='uq_player_missing_data_logs_all_columns'
        ),
    )


    def __init__(self, player_id: int, data_type: str):
        self.player_id = player_id
        self.data_type = data_type


    def __repr__(self):
        return "<PlayerMissingDataLog(id=%s, player_id=%s, data_type='%s')>" % (
            self.id, self.player_id, self.data_type
        )
    

class PlayerScrapeLog(Base):

    __tablename__ = "player_scrape_logs"


    id = Column(Integer, primary_key=True)
    scrape_id = Column(ForeignKey("scrapes.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)


    __table_args__ = (
        UniqueConstraint(
           'scrape_id', 'player_id',
           name='uq_player_scrape_logs_all_columns'
        ),
    )


    def __init__(self, scrape_id: int, player_id: int):
        self.scrape_id = scrape_id
        self.player_id = player_id


    def __repr__(self):
        return "<PlayerScrapeLog(id=%s, scrape_id=%s, player_id=%s)>" % (
            self.id, self.scrape_id, self.player_id
        )