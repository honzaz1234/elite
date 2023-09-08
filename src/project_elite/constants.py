NA = "-"

#regexes
LEAGUE_UID_REGEX = "league\/(.+)$"
TEAM_UID_REGEX = "team\/([0-9]+)\/"
PLAYER_UID_REGEX = "player\/([0-9]+)\/"

#common key names
GENERAL_INFO = "general_info"
UID = "uid"
PLAYER_UID = "player_uid"
TEAM_UID = "team_uid"
LEAGUE_UID = "league_uid"

##places
COUNTRY = "country"
REGION = "region"
TOWN = "town"
PLACE_DICT = "place_dict"

# player dicitonary keys
ACHIEVEMENTS = "achievements"
SEASON_STATS = "season_stats"


## general info
PLAYER_NAME = "player_name"
RELATIONS = "relations"
BIRTH_DATE = "birth_date"
AGE = "age"
BIRTH_PLACE_STRING = "birth_string"
NATIONALITY = "nationality"
POSITION = "position"
HEIGHT = "height"
WEIGHT = "weight"
SHOOTS = "shoots"
CATCHES = "catches"
CONTRACT_END = "contract_end"
CAP_HIT = "cap_hit"
NHL_RIGHTS_UID = "nhl_rights_uid"
DRAFT_LIST = "draft_list"
DRAFTED = "drafted"
ACTIVE = "active"
NHL_RIGHTS = "nhl_rights"
DRAFTS = "drafts"
SIGNED_NHL = "signed_nhl"

##draft dict
DRAFT_YEAR = "draft_year"
DRAFT_ROUND = "draft_round"
DRAFT_POSITION = "draft_position"
DRAFT_TEAM = "draft_team"

##season stats
TEAM_URL = "team_url"
LEAGUE_URL = "league_url"
REGULAR_SEASON = "regular_season"
PLAY_OFF = "play_off"
LEADERSHIP = "leadership"

## input one season stats dict
PLAYER_ID = "player_id"
SEASON_NAME = "season_name"
LEAGUE_NAME = "league_name"
IS_GOALIE = "is_goalie"

##stat attributes
###common
GP = "gp"
###player
G = "g"
A = "a"
TP = "tp"
PIM = "PIM"
PLUS_MINUS = "plus_minus"
###goalie
GD = "gd"
GAA = "gaa"
SVP = "svp"
GA = "ga"
SVS = "svs"
SO = "so"
WLT = "wlt"
TOI = "toi"
G_W = "w"
G_L = "l"
G_T = "t"

## input one season dict




#team dictionary keys
STADIUM_INFO = "stadium_info"
AFFILIATED_TEAMS = "affiliated_teams"
RETIRED_NUMBERS = "retired_numbers"
HISTORIC_NAMES = "titles"
## general info
PLAYS_IN = "plays_in"
TEAM_COLOURS = "team_colours"
COLOUR_LIST = "colour_list"
PLACE = "place"
YEAR_FOUNDED = "year_founded"
LONG_NAME = "long_name"
SHORT_NAME = "short_name"
ACTIVE = "active"
##stadium info
ARENA_NAME = "arena_name"
LOCATION = "location"
CAPACITY = "capacity"
CONSTRUCTION_YEAR = "construction_year"
##input dict
STADIUM_ID = "stadium_id"

#league
##genral info
LEAGUE_NAME = "league_name"
LEAGUE_ACHIEVEMENTS = "league_achievements"
SEASON_STANDINGS = "season_standings"

##header names
LEAGUE_POSITION = "position"
TEAM = "team"
GP = "gp"
W = "w"
T = "t"
L = "l"
OTW = "otw"
OTL = "otl"
GOALS_FOR = "gf"
GOALS_AGAINST = "ga"
PLUS_MINUS = "plu_minus"
TOTAL_POINTS = "tp"
POSTSEASON = "postseason"

#input league_dict
SECTION_TYPE = "section_type"
LEAGUE_ID = "league_id"




NA_REGION_ABB = {
    "USA": ["NJ", "CA", "AZ", "OH", "MI", 
            "NY", "NE", "WI", "MA", "FL", "CO", "SC", "MO", "MN", "PA", "TX", "CT", "IN", "WA", "IL", "ME", "AL", "OK", "UT", "OR", "NC", "RI", "NH", "VA", "AK", "IA", "MS", "SD", "ND", "MD",	"DE", "NV", "MT", "TN", "VT", "DC", "GA", "ID", "KY", "LA"],
    "CAN": ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "ON", "ONT", 
            "PE", "QC", "SK", "YT", "NU", "WV"]}