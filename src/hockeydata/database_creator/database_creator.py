import hockeydata.get_urls.get_urls as league_url
from sqlalchemy import create_engine, Boolean, Column, Date, Index, Integer, ForeignKey, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


leauge_getter = league_url.LeagueUrlDownload()
Base = declarative_base()


class Player(Base):

    __tablename__ = "players"

    id = Column("id", Integer, primary_key=True)
    uid = Column("uid", Integer)
    name = Column("name", String)
    position = Column("position", String)
    active = Column("active", Boolean)
    age = Column("age", Integer)
    shoots = Column("handedness", String)
    catches = Column("catches", String)
    contract = Column("contract_end", String)
    cap_hit = Column("cap_hit", Integer)
    signed_nhl = Column("signed_nhl", Boolean)
    date_birth = Column("date_birth", Date)
    drafted = Column("drafted", Boolean)
    height = Column("height", Integer)
    weight = Column("weight", Integer)

    nhl_rights_id = Column("nhl_rights_id", Integer, ForeignKey("teams.id"))
    place_birth_id = Column("place_birth_id", Integer, ForeignKey("places.id"))

    def __init__(self, uid, name, position, active, age, shoots, 
                catches, contract, cap_hit, signed_nhl, date_birth, 
                drafted, height, weight, nhl_rights_id,
                place_birth_id):
        self.uid = uid
        self.name = name
        self.position = position
        self.active = active
        self.age = age
        self.shoots = shoots
        self.catches = catches
        self.contract = contract
        self.cap_hit = cap_hit
        self.signed_nhl = signed_nhl
        self.date_birth = date_birth
        self.drafted = drafted
        self.height = height
        self.weight = weight
        self.nhl_rights_id = nhl_rights_id
        self.place_birth_id = place_birth_id

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.name}, {self.position}, {self.active}, {self.age}, {self.shoots}, {self.catches}, {self.contract}, {self.cap_hit}, {self.signed_nhl}, {self.date_birth}, {self.drafted}, {self.height}, {self.weight}, {self.nhl_rights_id}, {self.place_birth_id})"


class PlayerDraft(Base):

    __tablename__ = "players_draft"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", Integer, ForeignKey("players.id"))
    team_id = Column("team_id", Integer, ForeignKey("teams.id"))
    draft_round = Column("draft_round", Integer)
    draft_position = Column("draft_position", Integer)
    draft_year = Column("draft_year", Integer, index=True)

    def __init__(self, player_id, team_id, draft_round, 
                draft_position, draft_year):
        self.player_id = player_id
        self.team_id = team_id
        self.draft_round = draft_round
        self.draft_position = draft_position
        self.draft_year = draft_year

    def __repr__(self):
        return f"({self.player_id}, {self.team_id}, {self.draft_round}, {self.draft_position}, {self.draft_year})"


class Stadium(Base):

    __tablename__ = "stadiums"

    id = Column("id", Integer, primary_key=True)
    stadium = Column("stadium", String)
    capacity = Column("capacity", Integer)
    construction_year = Column("construction_year", Integer)
    place_id = Column("place_id", ForeignKey("places.id"))

    def __init__(self, stadium, capacity, construction_year, place_id):
        self.stadium = stadium
        self.capacity = capacity
        self.construction_year = construction_year
        self.place_id = place_id

    def __repr__(self):
        return f"({self.id}, {self.stadium}, {self.capacity}, {self.construction_year}, {self.place_id})"


class Team(Base):

    __tablename__ = "teams"

    id = Column("id", Integer, primary_key=True)
    uid = Column("uid", Integer)
    team = Column("team", String)
    long_name = Column("long_name", String)
    active = Column("active", Integer)
    founded = Column("founded", Integer)
    place_id = Column("place_id", ForeignKey("places.id"))
    stadium_id = Column("stadium_id", ForeignKey("stadiums.id"))

    def __init__(self, uid,  team, long_name, active, 
                 founded, place_id, stadium_id):
        self.uid = uid
        self.team = team
        self.long_name = long_name
        self.active = active
        self.founded = founded
        self.place_id = place_id
        self.stadium_id = stadium_id

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.team}, {self.long_name}, {self.active}, {self.founded} {self.place_id}, {self.stadium_id})"


class Colour(Base):

    __tablename__ = "colours"

    id = Column("id", Integer, primary_key=True)
    colour = Column("colour", String)

    def __init__(self, colour):
        self.colour = colour

    def __repr__(self):
        return f"({self.id}, {self.colour})"


class TeamColour(Base):

    __tablename__ = "team_colours"

    id = Column("id", Integer, primary_key=True)
    team_id = Column("team_id", ForeignKey("teams.id"))
    colour_id = Column("colour_id", ForeignKey("colours.id"), index=True)

    def __init__(self, team_id, colour_id):
        self.team_id = team_id
        self.colour_id = colour_id

    def __repr__(self):
        return f"({self.id}, {self.team_id}, {self.colour_id})"


class AffiliatedTeam(Base):

    __tablename__ = "affiliated_teams"

    id = Column("id", Integer, primary_key=True)
    team_1_id = Column("team_1_id", ForeignKey("teams.id"))
    team_2_id = Column("team_2_id", ForeignKey("teams.id"))

    def __init__(self, team_1_id, team_2_id):
        self.team_1_id = team_1_id
        self.team_2_id = team_2_id

    def __repr__(self):
        return f"({self.id}, {self.team_1_id}, {self.team_2_id})"


class RetiredNumber(Base):

    __tablename__ = "retired_numbers"

    id = Column("id", Integer, primary_key=True)
    team_id = Column("team_id", ForeignKey("teams.id"))
    player_id = Column("player_id", ForeignKey("players.id"))
    number = Column("number", Integer, index=True)

    def __init__(self, team_id, player_id, number):
        self.team_id = team_id
        self.player_id = player_id
        self.number = number

    def __repr__(self):
        return f"({self.id}, {self.team_id}, {self.player_id}, {self.number})"


class League(Base):

    __tablename__ = "leagues"

    id = Column("id", Integer, primary_key=True)
    uid = Column("uid", String)
    league = Column("league", String)

    def __init__(self,  uid, league):
        self.uid = uid
        self.league = league

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.league})"


class Nationality(Base):

    __tablename__ = "nationalities"

    id = Column("id", Integer, primary_key=True)
    nationality = Column("nationality", String)

    def __init__(self, nationality):
        self.nationality = nationality

    def __repr__(self):
        return f"({self.id}, {self.nationality})"


class PlayerNationality(Base):

    __tablename__ = "players_nationalities"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", Integer, ForeignKey("players.id"))
    nationality_id = Column("nationality_id", Integer,
                            ForeignKey("nationalities.id"), index=True)

    def __init__(self, player_id, nationality_id):
        self.player_id = player_id
        self.nationality_id = nationality_id

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.nationality_id})"


class Relation(Base):

    __tablename__ = "relations"

    id = Column("id", Integer, primary_key=True)
    relation = Column("relation", String)

    def __init__(self, relation):
        self.relation = relation

    def __repr__(self):
        return f"({self.id}, {self.relation})"


class PlayerRelation(Base):

    __tablename__ = "players_relations"

    id = Column("id", Integer, primary_key=True)
    player_from_id = Column("player_from_id", Integer,
                            ForeignKey("players.id"))
    player_to_id = Column("player_to_id", Integer, ForeignKey("players.id"))
    relation_id = Column("relation_id", Integer,
                         ForeignKey("relations.id"), index=True)

    def __init__(self, player_from_id, player_to_id, relation_id):
        self.player_from_id = player_from_id
        self.player_to_id = player_to_id
        self.relation_id = relation_id

    def __repr__(self):
        return f"({self.id}, {self.player_from_id}, {self.player_to_id}, {self.relation_id})"


class Place(Base):

    __tablename__ = "places"

    id = Column("id", Integer, primary_key=True)
    place = Column("place", String)
    region = Column("region", String)
    country_s = Column("country_s", String, index=True)

    def __init__(self, place, region, country_s):
        self.place = place
        self.region = region
        self.country_s = country_s

    def __repr__(self):
        return f"({self.id}, {self.place}, {self.region}, {self.country_s})"


class Season(Base):

    __tablename__ = "seasons"

    id = Column("id", Integer, primary_key=True)
    season = Column("season", String)

    def __init__(self, season):
        self.season = season

    def __repr__(self):
        return f"({self.id, self.season})"


class TeamName(Base):

    __tablename__ = "team_names"

    id = Column("id", Integer, primary_key=True)
    team_name = Column("team_name", String)
    year_from = Column("year_from", Integer, ForeignKey("seasons.id"))
    year_to = Column("year_to", Integer, ForeignKey("seasons.id"))
    team_id = Column("team_id", Integer, ForeignKey("teams.id"))

    def __init__(self, team_name, year_from, year_to, team_id):
        self.team_name = team_name
        self.year_from = year_from
        self.year_to = year_to
        self.team_id = team_id

    def __repr__(self):
        return f"({self.id}, {self.team_name}, {self.year_from}, {self.year_to}, {self.team_id})"


class Divison(Base):

    __tablename__ = "divisions"

    id = Column("id", Integer, primary_key=True)
    division = Column("division", String)

    def __init__(self, division):
        self.division = division

    def __repr__(self):
        return f"({self.id}, {self.division})"


class TeamSeason(Base):

    __tablename__ = "team_seasons"

    id = Column("id", Integer, primary_key=True)
    position = Column("position", Integer)
    league_id = Column("league_id", Integer, ForeignKey("leagues.id"))
    team_id = Column("team_id", Integer, ForeignKey("teams.id"), index=True)
    division_id = Column("division_id", Integer, ForeignKey("divisions.id"))
    conference_id = Column("conference_id", Integer,
                           ForeignKey("divisions.id"))
    season_id = Column("season_id", Integer, ForeignKey("seasons.id"))
    gp = Column("gp", Integer)
    w = Column("w", Integer)
    t = Column("t", Integer)
    l = Column("l", Integer)
    otw = Column("otw", Integer)
    otl = Column("otl", Integer)
    gf = Column("gf", Integer)
    ga = Column("ga", Integer)
    plus_minus = Column("plus_minus", Integer)
    tp = Column("tp", Integer)
    postseason_type_id = Column(
        "postseason_type_id", Integer, ForeignKey("postseason_types.id"))

    def __init__(self, position, league_id, team_id, division_id, 
                conference_id, season_id, gp, w, t, l, otw, otl, gf, 
                ga, plus_minus, tp, postseason_type_id):

        self.position = position
        self.league_id = league_id
        self.team_id = team_id
        self.division_id = division_id
        self.conference_id = conference_id
        self.season_id = season_id
        self.gp = gp
        self.w = w
        self.t = t
        self.l = l
        self.otw = otw
        self.otl = otl
        self.gf = gf
        self.ga = ga
        self.plus_minus = plus_minus
        self.tp = tp
        self.postseason_type_id = postseason_type_id

    def __repr__(self):
        return f"({self.id}, {self.position}, {self.league_id}, {self.team_id}, {self.divison_id}, {self.conference_id}, {self.season_id}, {self.gp}, {self.w}, {self.t}, {self.l}, {self.otw}, {self.otl}, {self.gf}, {self.ga}, {self.plus_minus}, {self.tp}, {self.postseason_type_id})"


Index('team_season_league_id_season_id_index',
      TeamSeason.league_id, TeamSeason.season_id)


class PostseasonType(Base):

    __tablename__ = "postseason_types"

    id = Column("id", Integer, primary_key=True)
    postseason_type = Column("postseason_type", String)

    def __init__(self, postseason_type):
        self.postseason_type = postseason_type

    def __repr__(self):
        return f"({self.id}, {self.postseason_type})"


class Achievement(Base):

    __tablename__ = "achievements"

    id = Column("id", Integer, primary_key=True)
    uid = Column("achievement", String)
    league_id = Column("league_id", Integer, ForeignKey("leagues.id"))

    def __init__(self, uid, league_id):
        self.uid = uid
        self.league_id = league_id

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.league_id})"


class PlayerAchievement(Base):

    __tablename__ = "players_achievements"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", Integer, ForeignKey("players.id"))
    achievement_id = Column("achievement_id", Integer,
                            ForeignKey("achievements.id"))
    season_id = Column("season_id", Integer, ForeignKey("seasons.id"))

    def __init__(self, player_id, achievement_id, season_id):
        self.player_id = player_id
        self.achievement_id = achievement_id
        self.season_id = season_id

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.achievement_id}, {self.season_id})"


class PlayerStats(Base):

    __tablename__ = "player_stats"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", Integer,
                       ForeignKey("players.id"), index=True)
    regular_season = Column("regular_season", Boolean)
    season_id = Column("season_id", Integer, ForeignKey("seasons.id"))
    league_id = Column("league_id", Integer, ForeignKey("leagues.id"))
    team_id = Column("team_id", Integer, ForeignKey("teams.id"))
    captaincy = Column("captaincy", String)
    games_played = Column("gp", Integer)
    goals = Column("g", Integer)
    assists = Column("a", Integer)
    total_points = Column("tp", Integer)
    PM = Column("pm", Integer)
    plus_minus = Column("plus_minus", Float)

    def __init__(self,  player_id, regular_season, season_id, league_id, 
                 team_id, captaincy, games_played, goals, assists, total_points, PM, plus_minus):
        self.player_id = player_id
        self.regular_season = regular_season
        self.season_id = season_id
        self.league_id = league_id
        self.team_id = team_id
        self.captaincy = captaincy
        self.games_played = games_played
        self.goals = goals
        self.assists = assists
        self.total_points = total_points
        self.PM = PM
        self.plus_minus = plus_minus

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.regular_season}, {self.season_id}, {self.league_id}, {self.team_id}, {self.captaincy}, {self.games_played}, {self.goals}, {self.assists}, {self.total_points}, {self.PM}, {self.plus_minus})"


Index('player_stats_league_id_season_id_index',
      PlayerStats.league_id, PlayerStats.season_id)


class GoalieStats(Base):

    __tablename__ = "goalie_stats"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", Integer,
                       ForeignKey("players.id"), index=True)
    regular_season = Column("regular_season", Boolean)
    season_id = Column("season_id", ForeignKey("seasons.id"))
    league_id = Column("league_id", Integer, ForeignKey("leagues.id"))
    team_id = Column("team_id", Integer, ForeignKey("teams.id"))
    captaincy = Column("captaincy", String)
    games_played = Column("gp", Integer)
    gd = Column("gd", Integer)
    goal_against_average = Column("gaa", Integer)
    save_percentage = Column("svp", Integer)
    goal_against = Column("ga", Integer)
    shot_saved = Column("svs", Integer)
    shotouts = Column("so", Integer)
    wins = Column("w", Integer)
    looses = Column("l", Integer)
    ties = Column("t", Integer)
    toi = Column("toi", Integer)

    def __init__(self,  player_id, regular_season, season_id, league_id, 
                team_id, captaincy, games_played, gd, goal_against_average, save_percentage, goal_against, shot_saved, shotouts,
                wins, looses, ties, toi):
        self.player_id = player_id
        self.regular_season = regular_season
        self.season_id = season_id
        self.league_id = league_id
        self.team_id = team_id
        self.captaincy = captaincy
        self.games_played = games_played
        self.gd = gd
        self.goal_against_average = goal_against_average
        self.save_percentage = save_percentage
        self.goal_against = goal_against
        self.shot_saved = shot_saved
        self.shotouts = shotouts
        self.wins = wins
        self.looses = looses
        self.ties = ties
        self.toi = toi

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.regular_season}, {self.season_id}, {self.league_id}, {self.team_id}, {self.captaincy}, {self.games_played}, {self.gd}, {self.goal_against_average}, {self.save_percentage}, {self.goal_against}, {self.shot_saved}, {self.shotouts}, {self.wins}, {self.looses}, {self.ties}, {self.toi})"


Index('goalie_stats_league_id_season_id_index',
      GoalieStats.league_id, GoalieStats.season_id)

engine = create_engine(
    "sqlite:///C:/Users/jziac/OneDrive/Documents/programovani/projekty/elite/database/hockey_v8.db", echo=False)
Base.metadata.create_all(bind=engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

check_data = session.query(Season).all()
if check_data == []:
    season_list = leauge_getter.create_season_list(1886, 2024)
    for one_season in season_list:
        season_entry = Season(season=one_season)
        session.add(season_entry)
        session.commit()
    years = [*range(1886, 2025, 1)]
    for year in years:
        season_entry = Season(season=year)
        session.add(season_entry)
        session.commit()
