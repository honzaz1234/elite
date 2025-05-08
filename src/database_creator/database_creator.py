import hockeydata.get_urls.get_urls as league_url

from sqlalchemy import Boolean, Column, Date, Index, Integer, ForeignKey, Float, String, UniqueConstraint
from sqlalchemy.orm import declarative_base


leauge_getter = league_url.LeagueUrlDownload()
Base = declarative_base()


class Player(Base):

    __tablename__ = "players"

    id = Column("id", Integer, primary_key=True)
    uid = Column("uid", Integer, nullable=False, unique=True)
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
        return (f"({self.id}, {self.uid}, {self.name}, {self.position}, {self.active}, "
        f"{self.age}, {self.shoots}, {self.catches}, {self.contract}, "
        f"{self.cap_hit}, {self.signed_nhl}, {self.date_birth}, {self.drafted}, "
        f"{self.height}, {self.weight}, {self.nhl_rights_id}, "
        f"{self.place_birth_id})")


class PlayerDraft(Base):

    __tablename__ = "players_draft"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", 
                       Integer, 
                       ForeignKey("players.id"), 
                       nullable=False)
    team_id = Column("team_id", 
                     Integer, 
                     ForeignKey("teams.id"), 
                     nullable=False)
    draft_round = Column("draft_round", Integer, nullable=False)
    draft_position = Column("draft_position", Integer, nullable=False)
    draft_year = Column("draft_year", Integer, index=True, nullable=False)

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
    stadium = Column("stadium", String, nullable=False)
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
    uid = Column("uid", Integer, nullable=False, unique=True)
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
    colour = Column("colour", String, nullable=False, unique=True)

    def __init__(self, colour):
        self.colour = colour

    def __repr__(self):
        return f"({self.id}, {self.colour})"


class TeamColour(Base):

    __tablename__ = "team_colours"

    id = Column("id", Integer, primary_key=True)
    team_id = Column("team_id", ForeignKey("teams.id"), nullable=False)
    colour_id = Column("colour_id", 
                       ForeignKey("colours.id"), 
                       index=True, 
                       nullable=False)

    def __init__(self, team_id, colour_id):
        self.team_id = team_id
        self.colour_id = colour_id

    def __repr__(self):
        return f"({self.id}, {self.team_id}, {self.colour_id})"


class AffiliatedTeam(Base):

    __tablename__ = "affiliated_teams"

    id = Column("id", Integer, primary_key=True)
    team_1_id = Column("team_1_id", ForeignKey("teams.id"), nullable=False)
    team_2_id = Column("team_2_id", ForeignKey("teams.id"), nullable=False)

    def __init__(self, team_1_id, team_2_id):
        self.team_1_id = team_1_id
        self.team_2_id = team_2_id

    def __repr__(self):
        return f"({self.id}, {self.team_1_id}, {self.team_2_id})"


class RetiredNumber(Base):

    __tablename__ = "retired_numbers"

    id = Column("id", Integer, primary_key=True)
    team_id = Column("team_id", ForeignKey("teams.id"), nullable=False)
    player_id = Column("player_id", ForeignKey("players.id"), nullable=False)
    number = Column("number", Integer, index=True, nullable=False)

    def __init__(self, team_id, player_id, number):
        self.team_id = team_id
        self.player_id = player_id
        self.number = number

    def __repr__(self):
        return f"({self.id}, {self.team_id}, {self.player_id}, {self.number})"


class League(Base):

    __tablename__ = "leagues"

    id = Column("id", Integer, primary_key=True)
    uid = Column("uid", String, nullable=False, unique=True)
    league = Column("league", String)

    def __init__(self,  uid, league):
        self.uid = uid
        self.league = league

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.league})"


class Nationality(Base):

    __tablename__ = "nationalities"

    id = Column("id", Integer, primary_key=True)
    nationality = Column("nationality", String, nullable=False, unique=True)

    def __init__(self, nationality):
        self.nationality = nationality

    def __repr__(self):
        return f"({self.id}, {self.nationality})"


class PlayerNationality(Base):

    __tablename__ = "players_nationalities"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", 
                       Integer, 
                       ForeignKey("players.id"), 
                       nullable=False)
    nationality_id = Column("nationality_id", 
                            Integer,
                            ForeignKey("nationalities.id"), 
                            index=True, 
                            nullable=False)

    def __init__(self, player_id, nationality_id):
        self.player_id = player_id
        self.nationality_id = nationality_id

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.nationality_id})"


class Relation(Base):

    __tablename__ = "relations"

    id = Column("id", Integer, primary_key=True)
    relation = Column("relation", String, nullable=False, unique=True)

    def __init__(self, relation):
        self.relation = relation

    def __repr__(self):
        return f"({self.id}, {self.relation})"


class PlayerRelation(Base):

    __tablename__ = "players_relations"

    id = Column("id", Integer, primary_key=True)
    player_from_id = Column("player_from_id", 
                            Integer,
                            ForeignKey("players.id"),
                            nullable=False)
    player_to_id = Column("player_to_id", 
                          Integer, 
                          ForeignKey("players.id"),
                          nullable=False)
    relation_id = Column("relation_id", 
                         Integer,
                         ForeignKey("relations.id"), 
                         index=True,
                         nullable=False)

    def __init__(self, player_from_id, player_to_id, relation_id):
        self.player_from_id = player_from_id
        self.player_to_id = player_to_id
        self.relation_id = relation_id

    def __repr__(self):
        return f"({self.id}, {self.player_from_id}, {self.player_to_id}, {self.relation_id})"


class Place(Base):

    __tablename__ = "places"

    id = Column("id", Integer, primary_key=True)
    place = Column("place", String, nullable=False)
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
    season = Column("season", String, nullable=False, unique=True)

    def __init__(self, season):
        self.season = season

    def __repr__(self):
        return f"({self.id, self.season})"


class TeamName(Base):

    __tablename__ = "team_names"

    id = Column("id", Integer, primary_key=True)
    team_name = Column("team_name", String, nullable=False)
    year_from = Column("year_from", 
                       Integer, 
                       ForeignKey("seasons.id"), 
                       nullable=False)
    year_to = Column("year_to", Integer, ForeignKey("seasons.id"))
    team_id = Column("team_id", 
                     Integer, 
                     ForeignKey("teams.id"), 
                     nullable=False)

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
    division = Column("division", String, nullable=False, unique=True)

    def __init__(self, division):
        self.division = division

    def __repr__(self):
        return f"({self.id}, {self.division})"


class TeamSeason(Base):

    __tablename__ = "team_seasons"

    id = Column("id", Integer, primary_key=True)
    position = Column("position", Integer)
    league_id = Column("league_id", 
                       Integer, 
                       ForeignKey("leagues.id"), 
                       nullable=False)
    team_id = Column("team_id", 
                     Integer, 
                     ForeignKey("teams.id"), 
                     index=True, 
                     nullable=False)
    division_id = Column("division_id", Integer, ForeignKey("divisions.id"))
    conference_id = Column("conference_id", Integer,
                           ForeignKey("divisions.id"))
    season_id = Column("season_id", Integer, ForeignKey("seasons.id"),
                        nullable=False)
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
        return f"({self.id}, {self.position}, {self.league_id}, {self.team_id}, {self.division_id}, {self.conference_id}, {self.season_id}, {self.gp}, {self.w}, {self.t}, {self.l}, {self.otw}, {self.otl}, {self.gf}, {self.ga}, {self.plus_minus}, {self.tp}, {self.postseason_type_id})"

Index('team_season_league_id_season_id_index',
      TeamSeason.league_id, TeamSeason.season_id)


class PostseasonType(Base):

    __tablename__ = "postseason_types"

    id = Column("id", Integer, primary_key=True)
    postseason_type = Column("postseason_type", 
                             String, 
                             nullable=False, 
                             unique=True)

    def __init__(self, postseason_type):
        self.postseason_type = postseason_type

    def __repr__(self):
        return f"({self.id}, {self.postseason_type})"


class Achievement(Base):

    __tablename__ = "achievements"

    id = Column("id", Integer, primary_key=True)
    uid = Column("achievement", String, nullable=False)
    league_id = Column("league_id", Integer, ForeignKey("leagues.id"))

    def __init__(self, uid, league_id):
        self.uid = uid
        self.league_id = league_id

    def __repr__(self):
        return f"({self.id}, {self.uid}, {self.league_id})"


class PlayerAchievement(Base):

    __tablename__ = "players_achievements"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", 
                       Integer, 
                       ForeignKey("players.id"), 
                       nullable=False)
    achievement_id = Column("achievement_id", 
                            Integer,
                            ForeignKey("achievements.id"), 
                            nullable=False)
    season_id = Column("season_id", 
                       Integer, 
                       ForeignKey("seasons.id"), 
                       nullable=False)

    def __init__(self, player_id, achievement_id, season_id):
        self.player_id = player_id
        self.achievement_id = achievement_id
        self.season_id = season_id

    def __repr__(self):
        return f"({self.id}, {self.player_id}, {self.achievement_id}, {self.season_id})"


class PlayerStats(Base):

    __tablename__ = "player_stats"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", 
                       Integer,
                       ForeignKey("players.id"), 
                       index=True,
                       nullable=False)
    regular_season = Column("regular_season", Boolean)
    season_id = Column("season_id", 
                       Integer, 
                       ForeignKey("seasons.id"),
                         nullable=False)
    league_id = Column("league_id", 
                       Integer, 
                       ForeignKey("leagues.id"), 
                       nullable=False)
    team_id = Column("team_id", 
                     Integer, 
                     ForeignKey("teams.id"),
                     nullable=False)
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
    player_id = Column("player_id", 
                       Integer,
                       ForeignKey("players.id"), 
                       index=True,
                       nullable=False)
    regular_season = Column("regular_season", Boolean)
    season_id = Column("season_id", 
                       ForeignKey("seasons.id"), 
                       nullable=False)
    league_id = Column("league_id", 
                       Integer, 
                       ForeignKey("leagues.id"),
                       nullable=False)
    team_id = Column("team_id", 
                     Integer, 
                     ForeignKey("teams.id"),
                     nullable=False)
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


class PlayType(Base):
    __tablename__ = 'play_types'
    id = Column(Integer, primary_key=True)
    play_type = Column(String, nullable=False, unique=True)

    def __init__(self, play_type):
        self.play_type = play_type

    def __repr__(self):
        return f"({self.id}, {self.play_type})"

class ShotType(Base):
    __tablename__ = 'shot_types'
    id = Column(Integer, primary_key=True)
    shot_type = Column(String, nullable=False, unique=True)

    def __init__(self, shot_type):
        self.shot_type = shot_type

    def __repr__(self):
        return f"({self.id}, {self.shot_type})"

class Zone(Base):

    __tablename__ = 'zones'

    id = Column(Integer, primary_key=True)
    zone = Column(String, nullable=False, unique=True)

    def __init__(self, zone):
        self.zone = zone

    def __repr__(self):
        return f"({self.id}, {self.zone})"

class ShotResult(Base):

    __tablename__ = 'shot_results'

    id = Column(Integer, primary_key=True)
    shot_result = Column(String, nullable=False, unique=True)

    def __init__(self, shot_result):
        self.shot_result = shot_result

    def __repr__(self):
        return f"({self.id}, {self.shot_result})"

class PenaltyType(Base):

    __tablename__ = 'penalty_types'

    id = Column(Integer, primary_key=True)
    penalty_type = Column(String, nullable=False, unique=True)

    def __init__(self, penalty_type):
        self.penalty_type = penalty_type

    def __repr__(self):
        return f"({self.id}, {self.penalty_type})"


class Match(Base):

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, nullable=False, unique=True)
    stadium_id = Column(Integer, ForeignKey('stadiums.id'), nullable=False)
    date = Column(String, nullable=False)
    time = Column(Integer)
    attendance = Column(Integer)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)

    def __init__(self, match_id, stadium_id, date, time, 
                 attendance, home_team_id, away_team_id):
        self.match_id = match_id
        self.stadium_id = stadium_id
        self.date = date
        self.time = time
        self.attendance = attendance
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id

    def __repr__(self):
        return (f"({self.id}, {self.match_id}, {self.stadium_id}, "
               f"{self.date}, {self.time}, {self.attendance}, "
               f"{self.home_team_id}, {self.away_team_id})")


class Play(Base):

    __tablename__ = 'plays'

    id = Column(Integer, primary_key=True)
    play_type_id = Column(Integer, ForeignKey('play_types.id'), nullable=False)
    match_id = Column(Integer, ForeignKey('matches.id'), nullable=False)
    period = Column(Integer, nullable=False)
    time = Column(Integer)

    def __init__(self, play_type_id, match_id, period, time):
        self.play_type_id = play_type_id
        self.match_id = match_id
        self.period = period
        self.time = time

    def __repr__(self):
        return (f"({self.id}, {self.play_type_id}, {self.match_id}, "
               f"{self.period}, {self.time})")


class GoalPlay(Base):

    __tablename__ = 'goal_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    distance = Column(Integer, nullable=False)
    penalty_shot = Column(Boolean, nullable=False)
    own_goal = Column(Boolean, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    shot_type_id = Column(Integer, ForeignKey('shot_types.id'), nullable=False)
    deflection_type_id = Column(Integer, ForeignKey('deflection_types.id'))
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)


    def __init__(self, play_id, distance, penalty_shot, own_goal, team_id, player_id, shot_type_id, deflection_type_id, zone_id):
        self.play_id = play_id
        self.distance = distance
        self.penalty_shot = penalty_shot
        self.own_goal = own_goal
        self.team_id = team_id
        self.player_id = player_id
        self.shot_type_id = shot_type_id
        self.deflection_type_id = deflection_type_id
        self.zone_id = zone_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.distance}," 
                f"{self.penalty_shot}, {self.own_goal}, "
                f"{self.team_id}, {self.player_id}, {self.shot_type_id}, "
                f"{self.deflection_type_id}, {self.zone_id})")
    

class AssistPlay(Base):

    __tablename__ = 'assist_plays'

    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goal_plays.id'), nullable=False)
    player_id = Column(Integer, primary_key=True, nullable=False)
    is_primary = Column(Boolean, nullable=False)

    def __init__(self, goal_id, player_id, is_primary):

        self.goal_id = goal_id
        self.player_id = player_id
        self.is_primary = is_primary

    def __repr__(self):
        return (f"({self.id}, {self.goal_id}, {self.player_id}, "
               f"{self.is_primary}")
    

class DeflectionType(Base):

    __tablename__ = 'deflection_types'

    id = Column(Integer, primary_key=True)
    deflection_type = Column(String, nullable=False)

    def __init__(self, deflection_type):

        self.deflection_type = deflection_type

    def __repr__(self):
        return (f"({self.id}, {self.deflection_type}")


class ShotPlay(Base):

    __tablename__ = 'shot_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    shot_type_id = Column(Integer, ForeignKey('shot_types.id'), nullable=False)
    distance = Column(Integer, nullable=False)
    penalty_shot = Column(Boolean, nullable=False)
    broken_stick = Column(Boolean, nullable=False)
    over_board = Column(Boolean, nullable=False)
    deflection_type_id = Column(Integer, ForeignKey('deflection_types.id'))

    def __init__(
            self, play_id, player_id, team_id, zone_id, shot_type_id,distance, penalty_shot, broken_stick, over_board, deflection_type_id):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id
        self.zone_id = zone_id
        self.shot_type_id = shot_type_id
        self.distance = distance
        self.penalty_shot = penalty_shot
        self.broken_stick = broken_stick
        self.over_board = over_board
        self.deflection_type_id = deflection_type_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.player_id},"
                f" {self.team_id}, {self.zone_id}, {self.shot_type_id}, "
                f"{self.distance}, {self.penalty_shot}, "
                f"{self.broken_stick}, {self.over_board}, "
                f"{self.deflection_type_id})")


class HitPlay(Base):

    __tablename__ = 'hit_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    hitter_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    hitter_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    victim_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    victim_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)

    def __init__(self, play_id, hitter_id, hitter_team_id, victim_id, 
                 victim_team_id, zone_id):
        self.play_id = play_id
        self.hitter_id = hitter_id
        self.hitter_team_id = hitter_team_id
        self.victim_id = victim_id
        self.victim_team_id = victim_team_id
        self.zone_id = zone_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.hitter_id}, "
               f"{self.hitter_team_id}, {self.victim_id}, "
               f"{self.victim_team_id}, {self.zone_id})")


class FaceoffPlay(Base):

    __tablename__ = 'faceoff_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    winner_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    loser_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    winner_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    loser_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)

    def __init__(self, play_id, winner_id, loser_id, winner_team_id, loser_team_id, zone_id):
        self.play_id = play_id
        self.winner_id = winner_id
        self.loser_id = loser_id
        self.winner_team_id = winner_team_id
        self.loser_team_id = loser_team_id
        self.zone_id = zone_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.winner_id}, "
               f"{self.loser_id}, {self.winner_team_id}, {self.loser_team_id},"
               f" {self.zone_id})")


class GiveawayPlay(Base):

    __tablename__ = 'giveaway_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)

    def __init__(self, play_id, player_id, team_id, zone_id):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id
        self.zone_id = zone_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.player_id}, "
               f"{self.team_id}, {self.zone_id})")


class TakeawayPlay(Base):

    __tablename__ = 'takeaway_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)

    def __init__(self, play_id, player_id, team_id, zone_id):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id
        self.zone_id = zone_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.player_id}, "
               f"{self.team_id}, {self.zone_id})")


class MissedShotPlay(Base):

    __tablename__ = 'missed_shot_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    shot_type_id = Column(Integer, ForeignKey('shot_types.id'), nullable=False)
    shot_result_id = Column(Integer, 
                            ForeignKey('shot_results.id'), 
                            nullable=False)
    distance = Column(Integer)
    broken_stick = Column(Boolean, nullable=False)
    over_board = Column(Boolean, nullable=False)

    def __init__(self, play_id, player_id, team_id, zone_id, shot_type_id,
              shot_result_id, distance, broken_stick, over_board):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id
        self.zone_id = zone_id
        self.shot_type_id = shot_type_id
        self.shot_result_id = shot_result_id
        self.distance = distance
        self.broken_stick = broken_stick
        self.over_board = over_board

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.player_id}, "
                f"{self.team_id}, {self.zone_id}, {self.shot_type_id}, "
                f"{self.shot_result_id}, {self.distance}, {self.broken_stick}, {self.over_board})")


class BlockedShotPlay(Base):

    __tablename__ = 'blocked_shot_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    shooter_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    shooter_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    blocker_type_id = Column(Integer, ForeignKey('blocker_types.id'))
    blocker_id = Column(Integer, ForeignKey('players.id'))
    blocker_team_id = Column(Integer, ForeignKey('teams.id'))
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    shot_type_id = Column(Integer, ForeignKey('shot_types.id'), nullable=False)
    broken_stick = Column(Boolean, nullable=False)
    over_board = Column(Boolean, nullable=False)

    def __init__(self, play_id, shooter_id,
                shooter_team_id, blocker_type_id, blocker_id, blocker_team_id, zone_id, shot_type_id, broken_stick, over_board):
        
        self.play_id = play_id
        self.shooter_id = shooter_id
        self.shooter_team_id = shooter_team_id
        self.blocker_type_id = blocker_type_id
        self.blocker_id = blocker_id
        self.blocker_team_id = blocker_team_id
        self.zone_id = zone_id
        self.shot_type_id = shot_type_id
        self.broken_stick = broken_stick
        self.over_board = over_board

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.shooter_id},"
               f"{self.shooter_team_id}, {self.blocker_type_id}, "
               f"{self.blocker_id}, {self.blocker_team_id}, "
               f"{self.zone_id}, {self.shot_type_id}, {self.broken_stick}, "
               f"{self.over_board})")


class BlockerType(Base):

    __tablename__ = 'blocker_types'

    id = Column(Integer, primary_key=True)
    blocker_type = Column(String, nullable=False)

    def __init__(self, blocker_type):
        self.blocker_type = blocker_type

    def __repr__(self):
        return (f"({self.id}, {self.blocker_type}")
    

class PenaltyPlay(Base):

    __tablename__ = 'penalty_plays'

    id = Column(Integer, primary_key=True)
    major_penalty = Column(Boolean, nullable=False)
    offender_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    offender_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    served_by_id = Column(Integer, ForeignKey('players.id'))
    victim_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    victim_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    penalty_type_id = Column(Integer, 
                             ForeignKey('penalty_types.id'), 
                             nullable=False)
    penalty_minutes = Column(Integer, nullable=False)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)

    def __init__(self, play_id, offender_id, 
                 offender_team_id, served_by_id, victim_id, victim_team_id, zone_id, penalty_type_id, penalty_minutes, major_penalty):
        
        self.play_id = play_id
        self.offender_id = offender_id
        self.offender_team_id = offender_team_id
        self.served_by_id = served_by_id
        self.victim_id = victim_id
        self.victim_team_id = victim_team_id
        self.zone_id = zone_id
        self.penalty_type_id = penalty_type_id
        self.penalty_minutes = penalty_minutes
        self.major_penalty = major_penalty

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, " 
                f"{self.offender_id}, {self.offender_team_id}, "
                f"{self.served_by_id}, {self.victim_id}, "
                f"{self.victim_team_id}, {self.zone_id}, "
                f"{self.penalty_type_id}, {self.penalty_minutes}, "  
                f"{self.major_penalty})")


class ChallengeReason(Base):

    __tablename__ = 'challenge_reasons'

    id = Column(Integer, primary_key=True)
    challenge_reason = Column("challenge_reason", String, nullable=False)

    def __init__(self, challenge_reason):
        self.challenge_reason = challenge_reason

    def __repr__(self):
        return f"({self.challenge_reason})"


class ChallengeResult(Base):

    __tablename__ = 'challenge_results'

    id = Column(Integer, primary_key=True)
    challenge_result = Column("challenge_result", String, nullable=False)

    def __init__(self, challenge_result):
        self.challenge_result = challenge_result

    def __repr__(self):
        return f"({self.challenge_result})"
    

class ChallengePlay(Base):
    __tablename__ = 'challenge_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    reason_id = Column(Integer, 
                        ForeignKey('challenge_reasons.id'),  
                        nullable=False)
    result_id = Column(Integer, 
                        ForeignKey('challenge_results.id'), 
                        nullable=False)
    league_challenge = Column(Boolean)

    def __init__(
            self, play_id, team_id, challenge_reason_id, challenge_result_id,
            league_challenge):
        self.play_id = play_id
        self.team_id = team_id
        self.challenge_reason_id = challenge_reason_id
        self.challenge_result_id = challenge_result_id
        self.league_challenge=league_challenge

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.challenge_reason_id}," 
                f"{self.challenge_result_id}, {self.league_challenge})")
    

class DelayedPenaltyPlay(Base):

    __tablename__ = 'delayed_penalty_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)

    def __init__(self, play_id, team_id):
        self.play_id = play_id
        self.team_id = team_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.team_id})")
    
    
class TimeZone(Base):

    __tablename__ = 'time_zones'

    id = Column(Integer, primary_key=True)
    time_zone = Column(String, nullable=False)

    def __init__(self, time_zone):
        self.time_zone = time_zone

    def __repr__(self):
        return (f"({self.id}, {self.time_zone}")
    

class PeriodType(Base):

    __tablename__ = 'period_types'

    id = Column(Integer, primary_key=True)
    period_type = Column(String, nullable=False)

    def __init__(self, period_type):
        self.period_type = period_type

    def __repr__(self):
        return (f"({self.id}, {self.period_type}")
    
    
class PeriodPlay(Base):

    __tablename__ = 'period_plays'

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    time = Column(String, nullable=False)
    time_zone_id = Column(Integer, ForeignKey('time_zones.id'), nullable=False)
    period_type_id = Column(Integer, 
                            ForeignKey('period_types.id'),
                             nullable=False)

    def __init__(self, play_id, time, time_zone_id, period_type_id):
        self.play_id = play_id
        self.time = time
        self.time_zone_id = time_zone_id
        self.period_type_id = period_type_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.time}, "
                f"{self.time_zone_id}), {self.period_type_id})")


class PlayerShift(Base):

    __tablename__ = "player_shifts"

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    period = Column(Integer, nullable=False)
    shift_start = Column(Integer, nullable=False)
    shift_end = Column(Integer, nullable=False)

    def __init__(
            self, play_id, player_id, team_id, period, shift_start, shift_end):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id
        self.period = period
        self.shift_start = shift_start
        self.shift_end = shift_end

    def __repr__(self):
        return (
            f"({self.id}, {self.play_id}, {self.player_id}, "
            f"{self.team_id}, {self.period}, {self.shift_start}, "
            f"{self.shift_end})"
            )


class PlayerOnIce(Base):

    __tablename__ = "on_ice_players"

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)

    def __init__(self, play_id, player_id, team_id):
        self.play_id = play_id
        self.player_id = player_id
        self.team_id = team_id

    def __repr__(self):
        return f"({self.id}, {self.play_id}, {self.player_id}, {self.team_id})"
    

class GameStopageType(Base):

    __tablename__ = "game_stopage_types"

    id = Column(Integer, primary_key=True)
    stopage_type = Column(String, nullable=False)

    def __init__(self, stopage_type):
        self.stopage_type = stopage_type

    def __repr__(self):
        return (f"({self.id}, {self.stopage_type}")
    

class GameStopagePlay(Base):

    __tablename__ = "game_stopages"

    id = Column(Integer, primary_key=True)
    play_id = Column(Integer, ForeignKey('plays.id'), nullable=False)
    stopage_type_id = Column(
        Integer, ForeignKey('game_stopage_types.id'), nullable=False)
    

    def __init__(self, play_id, stopage_type_id):
        self.play_id = play_id
        self.stopage_type_id = stopage_type_id

    def __repr__(self):
        return (f"({self.id}, {self.play_id}, {self.stopage_type_id})")
    

class NHLEliteNameMapper(Base):

    __tablename__ = "elite_nhl_name_mapper"

    id = Column("id", Integer, primary_key=True)
    player_id = Column("player_id", 
                       ForeignKey("players.id"), 
                       nullable=False)
    nhl_name = Column("nhl_name", String, nullable=False)
    elite_name = Column("elite_name", String, nullable=False)
    team_id = Column("team_id", ForeignKey("teams.id"), nullable=False)
    season_id = Column("season_id", ForeignKey("seasons.id"), nullable=False)
    player_number = Column("player_number", Integer,  nullable=False)

    def __init__(self, player_id,  elite_name, nhl_name, team_id, 
                 season_id, player_number):
        self.player_id = player_id
        self.elite_name = elite_name
        self.nhl_name = nhl_name
        self.team_id = team_id
        self.season_id = season_id
        self.player_number = player_number

        __table_args__ = (
            UniqueConstraint(
                'player_id', 'elite_name', 'nhl_name', 'team_id', 'season_id', 'player_number', name='uq_all_columns'
                ),
            )

    def __repr__(self):
        return (f"({self.id}, {self.player_id}, {self.elite_name}, "
                f"{self.nhl_name}, {self.team_id}, {self.season_id}"
                f" {self.player_number})")
    

class BrokenPBP(Base):

    __tablename__ = "broken_play"

    id = Column(Integer, primary_key=True)
    play_id = Column(ForeignKey("plays.id"), 
                     nullable=False)
    play_desc = Column(String, nullable=False)


    def __init__(self, play_id, play_desc):
        self.play_id = play_id
        self.play_desc = play_desc

    def __repr__(self):
        return (
            f"({self.id}, {self.play_id}, {self.play_desc})"
            )


class BrokenPOI(Base):

    __tablename__ = "broken_poi"

    id = Column(Integer, primary_key=True)
    play_id = Column(ForeignKey("plays.id"), 
                     nullable=False)
    team_id = Column("team_id", ForeignKey("teams.id"), nullable=False)
    poi = Column(String, nullable=False)
    error_type = Column(String, nullable=False)


    def __init__(self, play_id, team_id, poi, error_type):
        self.play_id = play_id
        self.team_id = team_id
        self.poi = poi
        self.error_type = error_type

    def __repr__(self):
        return (
            f"({self.id}, {self.play_id}, {self.team_id}, {self.poi}, "
            f"{self.error_type})"
            )


class StadiumMapper(Base):

    __tablename__ = "stadium_mappers"

    id = Column(Integer, primary_key=True)
    stadium_nhl = Column(String, nullable=False)
    stadium_elite = Column(String, nullable=False)


    def __init__(self, stadium_nhl, stadium_elite):
        self.stadium_nhl = stadium_nhl
        self.stadium_elite = stadium_elite

    def __repr__(self):
        return (
            f"({self.id}, {self.stadium_nhl}, {self.stadium_elite})"
            )
    
    

