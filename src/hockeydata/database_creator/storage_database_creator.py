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
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    scrape_type_id = Column(
        Integer, 
        ForeignKey('scrape_types.id'), 
        nullable=False
        )


    def __init__(
            self, scrape_type_id: int, start_datetime: datetime, end_datetime: datetime
            ):
        self.start_datetime = start_datetime or datetime.now()
        self.end_datetime = end_datetime
        self.scrape_type_id = scrape_type_id


    def __repr__(self):
        return "<Scrape(id=%s, start='%s', end='%s', scrape_type_id='%s')>" % (
            self.id, 
            self.start_datetime, 
            self.end_datetime, 
            self.scrape_type_id
        )
    

class ScrapeType(Base):

    __tablename__ = 'scrape_types'

    id = Column(Integer, primary_key=True)
    scrape_type = Column(String, nullable=False, unique=True)


    def __init__(self, scrape_type: str):
        self.scrape_type = scrape_type


    def __repr__(self):
        return "<Scrape(id=%s, scrape_type='%s')>" % (
            self.id, 
            self.scrape_type
        )
    
    

class PlayerURL(Base):


    __tablename__ = 'player_urls'


    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False, unique=True)
    scrape_id = Column(Integer, ForeignKey('scrapes.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    league_id = Column(Integer, ForeignKey('league_infos.id'), nullable=False)


    def __init__(
            self, url: str, scrape_id: int, season_id: int, league_id: int):
        self.url = url
        self.scrape_id = scrape_id
        self.season_id = season_id
        self.league_id = league_id


    def __repr__(self):
        return "<PlayerURL(id=%s, url='%s', scrape_id='%s', season_id=%s, league_id=%s)>" % (
            self.id, 
            self.url,
            self.scrape_id,
            self.season_id,
            self.league_id
        )
    

class PlayerLog(Base):

    __tablename__ = 'playerlogs'


    id = Column(Integer, primary_key=True)
    uid = Column(Integer, nullable=False)
    scrape_id = Column(Integer, ForeignKey('scrapes.id'), nullable=False)
    is_goalie = Column(Boolean, nullable=False)
    time_scraped = Column(DateTime, nullable=False)
    time_inserted = Column(
        DateTime, 
        default=lambda: datetime.now(), 
        nullable=False
        )


    __table_args__ = (
        UniqueConstraint('scrape_id', 'uid', name='uq_playerlogs_scrape_id_uid'),
    )


    def __init__(
            self, uid: int, scrape_id: int, is_goalie: bool, 
            time_scraped: datetime):
        self.uid = uid
        self.scrape_id = scrape_id
        self.is_goalie = is_goalie
        self.time_scraped = time_scraped
        self.time_inserted = None


    def __repr__(self):
        return (
            "<Player(id=%s, uid='%s', scrape_id='%s', is_goalie=%s, "
            "time_scraped=%s, time_inserted=%s)>" % (
                self.id, 
                self.uid, 
                self.scrape_id, 
                self.is_goalie, 
                self.time_scraped,
                self.time_inserted
                )
        )
    
    
class SkaterStats(Base, HtmlPreviewMixin):

    __tablename__ = 'skater_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('playerlogs.id'), nullable=False)
    competition_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False)


    def __init__(
            self, player_id: int, competition_type: str, html_data: bytes):
        self.player_id = player_id
        self.competition_type = competition_type
        self.html_data = html_data


    def __repr__(self):
        return (
            "<SkaterStats(id=%s, player_id=%s, competition_type=%s, "
            "html_data=%s)>" % (
                self.id, 
                self.player_id, 
                self.competition_type, 
             self.html_preview()
             )
        )
    

class GoalieStats(Base, HtmlPreviewMixin):

    __tablename__ = 'goalie_stats'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('playerlogs.id'), nullable=False)
    competition_type = Column(String, nullable=False)
    season_type = Column(String, nullable=False)
    html_data = Column(LargeBinary, nullable=False)


    def __init__(
            self, player_id: int, competition_type: str, season_type: str, html_data: bytes):
        self.player_id = player_id
        self.competition_type = competition_type
        self.season_type = season_type
        self.html_data = html_data


    def __repr__(self):
        return "<GoalieStats(id=%s, player_id=%s, competition_type=%s, season_type=%s, html_data=%s)>" % (
            self.id,
            self.player_id,
            self.competition_type,
            self.season_type,
            self.html_preview(),
        )
    

class PlayerFacts(Base):

    __tablename__ = 'player_facts'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('playerlogs.id'), nullable=False)
    html_data = Column(LargeBinary)  


    def __init__(self, player_id: int, html_data: bytes):
        self.player_id = player_id
        self.html_data = html_data


    def __repr__(self):
        preview = self.html_data[:50] + b"..." if len(self.html_data) > 50 else self.html_data
        return "<PlayerFacts(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, 
            self.player_id, 
            preview
        )


class PlayerAchievements(Base, HtmlPreviewMixin):

    __tablename__ = 'player_achievements'


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('playerlogs.id'), nullable=False)
    html_data = Column(LargeBinary)


    def __init__(self, player_id: int, html_data: bytes):
        self.player_id = player_id
        self.html_data = html_data


    def __repr__(self):
        return "<Achievements(id=%s, player_id=%s, html_data=%s)>" % (
            self.id, 
            self.player_id, 
            self.html_preview()
        )
    

class PlayerMissingDataLog(Base):

    __tablename__ = "player_missing_data_logs"


    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("playerlogs.id"), nullable=False)
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
            self.id, 
            self.player_id, 
            self.data_type
        )
    

class LeagueLog(Base):

    __tablename__ = 'league_logs'


    id = Column(Integer, primary_key=True)
    scrape_id = Column(Integer, ForeignKey('scrapes.id'), nullable=False)
    league_id = Column(Integer, ForeignKey('league_infos.id'), nullable=False)
    time_scraped = Column(DateTime, nullable=False)
    time_inserted = Column(
        DateTime, 
        default=lambda: datetime.now(), 
        nullable=False
        )


    __table_args__ = (
        UniqueConstraint('scrape_id', 'league_id', name='uq_playerlogs_scrape_id_league_id'),
    )


    def __init__(
            self, league_id: int, scrape_id: int, time_scraped: datetime):
        self.league_id = league_id
        self.scrape_id = scrape_id
        self.time_scraped = time_scraped
        self.time_inserted = None


    def __repr__(self):
        return (
            "<Player(id=%s, league_id='%s', scrape_id='%s', "
            "time_scraped=%s, time_inserted=%s)>" % (
                self.id, 
                self.league_id, 
                self.scrape_id, 
                self.time_scraped,
                self.time_inserted
                )
        )
    

class LeagueInfo(Base):

    __tablename__ = "league_infos"


    id = Column(Integer, primary_key=True)
    elite_name = Column(String, nullable=False)
    uid = Column(String, nullable=False, unique=True)
    first_season = Column(String)
    last_season = Column(String)
    last_update = Column(DateTime, nullable=False)


    def __init__(
            self, elite_name: str, uid: str, last_update: datetime, first_season: str|None = None, last_season: str|None = None):
        self.elite_name = elite_name
        self.uid = uid
        self.first_season = first_season
        self.last_season = last_season
        self.last_update = last_update


    def __repr__(self):
        return "<PlayerMissingDataLog(id=%s, elite_name=%s, uid='%s', first_season='%s', last_season='%s', last_update=%s)>" % (
            self.id, 
            self.elite_name, 
            self.uid,
            self.first_season,
            self.last_season,
            self.last_update
        )
    

class Season(Base):

    __tablename__ = "seasons"

    id = Column("id", Integer, primary_key=True)
    season = Column("season", String, nullable=False, unique=True)

    def __init__(self, season: str):
        self.season = season


    def __repr__(self):
        return "<Season(id=%s, season=%s)>" % (
            self.id, 
            self.season
        )
    

class LeagueName(Base):


    __tablename__ = "league_names"


    id = Column("id", Integer, primary_key=True)
    html_data = Column("html_data", String, nullable=False, unique=True)


    def __init__(self, html_data):
        self.html_data = html_data


    def __repr__(self):
        return "<LeagueName(id=%s, html_data=%s)>" % (
            self.id, 
            self.html_data
        )
    

class LeagueAchievement(Base):


    __tablename__ = "league_achievements"


    id = Column("id", Integer, primary_key=True)
    html_data = Column("html_data", String, nullable=False, unique=True)


    def __init__(self, html_data):
        self.html_data = html_data


    def __repr__(self):
        return "<LeagueAchievement(id=%s, html_data=%s)>" % (
            self.id, 
            self.html_data
        )
    

class LeagueSeason(Base):


    __tablename__ = "league_seasons"


    id = Column("id", Integer, primary_key=True)
    html_data = Column("html_data", String, nullable=False, unique=True)


    def __init__(self, html_data):
        self.html_data = html_data


    def __repr__(self):
        return "<LeagueSeason(id=%s, html_data=%s)>" % (
            self.id, 
            self.html_data
        )
    

class LeagueMissingDataLog(Base):

    __tablename__ = "league_missing_data_logs"


    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey("league_infos.id"), nullable=False)
    data_type = Column(String, nullable=False)


    __table_args__ = (
        UniqueConstraint(
            'league_id', 'data_type',
            name='uq_league_missing_data_logs_all_columns'
        ),
    )


    def __init__(self, league_id: int, data_type: str):
        self.league_id = league_id
        self.data_type = data_type


    def __repr__(self):
        return "<LeagueMissingDataLog(id=%s, league_id=%s, data_type='%s')>" % (
            self.id, 
            self.league_id, 
            self.data_type
        )