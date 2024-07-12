ELITE_URL = "https://www.eliteprospects.com"
TEAM_STANDINGS = "/standings"

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

##input player dict
NHL_RIGHTS_ID = "nhl_rights_id"
PLACE_BIRTH_ID = "place_birth_id"

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
PLUS_MINUS = "plus_minus"
TOTAL_POINTS = "tp"
POSTSEASON = "postseason"

#input league_dict
SECTION_TYPE = "section_type"
LEAGUE_ID = "league_id"



STANDINGS_URL = "/standings/"
NA_REGION_ABB = {
    "USA": ["NJ", "CA", "AZ", "OH", "MI", 
            "NY", "NE", "WI", "MA", "FL", "CO", "SC", "MO", "MN", "PA", "TX", "CT", "IN", "WA", "IL", "ME", "AL", "OK", "UT", "OR", "NC", "RI", "NH", "VA", "AK", "IA", "MS", "SD", "ND", "MD",	"DE", "NV", "MT", "TN", "VT", "DC", "GA", "ID", "KY", "LA"],
    "CAN": ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "ON", "ONT", 
            "PE", "QC", "SK", "YT", "NU", "WV"]}


#league pages references

LEAGUE_URLS = {
        'SHL': '/league/shl',
        'HockeyAllsvenskan': '/league/hockeyallsvenskan',
        'HockeyEttan': '/league/hockeyettan',
        'Division 2': '/league/france3',
        'Division 3': '/league/france4',
        'Division 4': '/league/division-4',
        'Division 5': '/league/division-5',
        'Division 6': '/league/division-6',
        'J20 Nationell': '/league/j20-nationell',
        'J20 Region': '/league/j20-region',
        'J20 Div.1': '/league/j20-div.1',
        'J20 Div.2': '/league/j20-div.2',
        'J18 Nationell': '/league/j18-nationell',
        'J18 Region': '/league/j18-region',
        'J18 Div.1': '/league/j18-div.1',
        'J18 Div.2': '/league/j18-div.2',
        'U16 SM': '/league/u16-sm',
        'U16 Region': '/league/u16-region',
        'U16 Div.1': '/league/u16-div.1',
        'U16 Div.2': '/league/u16-div.2',
        'TV-Pucken': '/league/tv-pucken',
        'Liiga': '/league/liiga',
        'Mestis': '/league/mestis',
        'Suomi-sarja': '/league/suomi-sarja',
        'II-divisioona': '/league/ii-divisioona',
        'III-divisioona': '/league/iii-divisioona',
        'U20 SM-sarja': '/league/u20-sm-sarja',
        'U20 Mestis': '/league/u20-mestis',
        'U18 SM-sarja': '/league/u18-sm-sarja',
        'U18 Mestis': '/league/u18-mestis',
        'U16 SM-sarja': '/league/u16-sm-sarja',
        'U16 Mestis': '/league/u16-mestis',
        'Metal Ligaen': '/league/denmark',
        '1. Division': '/league/denmark2',
        'Denmark U20': '/league/denmark-u20',
        'Denmark U17': '/league/denmark-u17',
        'Eliteserien': '/league/norway',
        '1. Divisjon': '/league/norway2',
        '2. Divisjon': '/league/norway3',
        '3. Divisjon': '/league/norway4',
        'Norway U20': '/league/norway-u20',
        'Norway U18': '/league/norway-u18',
        'Iceland': '/league/iceland',
        'NL': '/league/nl',
        'Czechia': '/league/czechia', 
        'SL': '/league/sl',
        'MyHL': '/league/myhl',
        '1. Liga': '/league/swissdiv1',
        'U20-Elit': '/league/u20-elit',
        'U20-Top': '/league/u20-top',
        'U17-Elit': '/league/u17-elit',
        'DEL': '/league/del',
        'DEL 2': '/league/del2',
        'Oberliga': '/league/germany3',
        'Regionalliga': '/league/germany4',
        'DNL U20 Div. I': '/league/dnl-u20',
        'DNL U20 Div. II': '/league/dnl-u20-2',
        'DNL U20 Div. III': '/league/dnl-u20-3',
        'Germany U17 Div. I': '/league/germany-u17',
        'Germany U17 Div. II': '/league/germany-u17-2',
        'ICEHL': '/league/icehl',
        'Alps Hockey League': '/league/alpshl',
        'ÖEL': '/league/austria3',
        'Austria U20': '/league/austria-u20',
        'Austria U18i': '/league/austria-u18i',
        'Austria U17': '/league/austria-u17',
        'Ligue Magnus': '/league/ligue-magnus',
        'Division 1': '/league/france2',
        'France U17': '/league/france-u17',
        'France U20': '/league/france-u20',
        'EIHL': '/league/eihl',
        'NIHL': '/league/nihl',
        'NIHL 1': '/league/nihl-1',
        'NIHL 2': '/league/nihl-2',
        'England U15': '/league/england-u15',
        'England U18': '/league/england-u18',
        'England U20': '/league/england-u20',
        'SNL': '/league/snl',
        'BeNeLiga': '/league/beneliga',
        'Netherlands2': '/league/netherlands2',
        'KHL': '/league/khl',
        'VHL': '/league/vhl',
        'Russia3': '/league/russia3',
        'MHL': '/league/mhl',
        'NMHL': '/league/nmhl',
        'Russia U16': '/league/russia-u16',
        'Russia U17': '/league/russia-u17',
        'Russia U18': '/league/russia-u18',
        'Extraliga': '/league/slovakia',
        '1. liga': '/league/slovakia2',
        '2. liga': '/league/czechia3',
        'Czechia U17': '/league/czechia-u17',
        'Czechia U20': '/league/czechia-u20',
        'Slovakia U16': '/league/slovakia-u16',
        'Slovakia U18': '/league/slovakia-u18',
        'Slovakia U20': '/league/slovakia-u20',
        'Latvia': '/league/latvia',
        'Latvia2': '/league/latvia2',
        'Latvia U17': '/league/latvia-u17',
        'Erste Liga': '/league/erste-liga',
        'Hungary': '/league/hungary',
        'Hungary U18': '/league/hungary-u18',
        'Hungary U21': '/league/hungary-u21',
        'Belarus': '/league/belarus',
        'Belarus Vysshaya': '/league/belarus-vysshaya',
        'Ukraine': '/league/ukraine',
        'UHSL': '/league/uhsl',
        'Ukraine U19': '/league/ukraine-u19',
        'Kazakhstan': '/league/kazakhstan',
        'PHL': '/league/poland',
        'Poland2': '/league/poland2',
        'Poland U20': '/league/poland-u20',
        'Bulgaria': '/league/bulgaria',
        'Estonia': '/league/estonia',
        'Lithuania': '/league/lithuania',
        'Romania': '/league/romania',
        'IHL Elite': '/league/italy',
        'Italian HL': '/league/italy2',
        'IHL Division 1': '/league/italy3',
        'Junior League': '/league/italy-u19',
        'Italy U17': '/league/italy-u17',
        'Croatia': '/league/croatia',
        'Serbia': '/league/serbia',
        'Slovenia': '/league/slovenia',
        'Slovenia U19': '/league/slovenia-u19',
        'IntHL': '/league/inthl',
        'IntHL U19': '/league/inthl-u19',
        'Bosnia': '/league/bosnia',
        'Spain': '/league/spain',
        'Turkey': '/league/turkey',
        'Asia League': '/league/asia-league',
        'CIHL HK': '/league/cihl-hk',
        'China': '/league/china',
        'Japan': '/league/japan',
        'Korea College': '/league/korea-college',
        'AIHL': '/league/aihl',
        'AIJHL': '/league/ajihl',
        'ECSL': '/league/ecsl',
        'IHSA Premier': '/league/ihsa-premier',
        'IHV Premier': '/league/ihv-premier',
        'WASL': '/league/ihwa-premier',
        'NZIHL': '/league/nzihl',
        'GPHL': '/league/gphl',
        'WPIHL': '/league/wpihl',
        'Israel': '/league/israel',
        'UAE': '/league/uae',
        'EUHL': '/league/euhl',
        'MSHL1': '/league/mshl1',
        'MSHL2': '/league/mshl2',
        'MSHL3': '/league/mshl3',
        'RSHL1': '/league/rshl1',
        'RSHL2': '/league/rshl2',
        'SHLSPB1': '/league/shlspb1',
        'SHLSPB2': '/league/shlspb2',
        'NHL': '/league/nhl',
        'AHL': '/league/ahl',
        'ECHL': '/league/echl',
        'SPHL': '/league/sphl',
        'LNAH': '/league/lnah',
        'FPHL': '/league/fphl',
        'ACH': '/league/ach',
        'Chinook HL': '/league/chinook-hl',
        'WOAA': '/league/woaa',
        'NCAA': '/league/ncaa',
        'NCAA III': '/league/ncaa-iii',
        'ACHA': '/league/acha',
        'ACHA II': '/league/acha-ii',
        'ACHA III': '/league/acha-iii',
        'CHF': '/league/chf',
        'BCIHL': '/league/bcihl',
        'USports': '/league/usports',
        'ACAC': '/league/acac',
        'QCHL': '/league/qchl',
        'BSHL': '/league/bshl',
        'CarillonSHL': '/league/carillonshl',
        'CIHL': '/league/cihl',
        'CRL': '/league/crl',
        'EastCSHL': '/league/eastcshl',
        'ECSHL': '/league/aeshl',
        'EOSHL': '/league/eoshl',
        'GLHL': '/league/glhl',
        'HHL': '/league/hhl',
        'LHSAAAQ': '/league/lhsaaaq',
        'LHSAO': '/league/lhsao',
        'LHSLF': '/league/lhslf',
        'LHSR': '/league/lhse',
        'LLHL': '/league/llhl',
        'LRH': '/league/lrh',
        'MIHL': '/league/mihl',
        'MWHL': '/league/mwhl',
        'NCHL-AB': '/league/nchl-ab',
        'NCHL-MB': '/league/nchl-mb',
        'NorthPHL': '/league/northphl',
        'NoteHL': '/league/notehl',
        'QVHHL': '/league/qvhhl',
        'RHL': '/league/rhl',
        'SASHL': '/league/sashl',
        'SaskEHL': '/league/saskehl',
        'SaskPHL': '/league/saskphl',
        'SEMHL': '/league/semhl',
        'SVHL': '/league/svhl',
        'SSHL-Sr.': '/league/sshl-sr.',
        'SWHL': '/league/swhl',
        'THHL': '/league/thhl',
        'THL': '/league/thl',
        'TRHL': '/league/trhl',
        'WheatlandSHL': '/league/wheatlandshl',
        'WMHL': '/league/wmhl',
        'WOSHL': '/league/woshl',
        'EP Invitational': '/league/ep-invitational',
        'EP Cup Series 14U': '/league/ep-cup-series-14u',
        'EP Cup Series 15O': '/league/ep-cup-series-15o',
        'EP Cup Series 16U': '/league/ep-cup-series-16u',
        'EP Cup Series 18U': '/league/ep-cup-series-18u',
        'USHL': '/league/ushl',
        'NAHL': '/league/nahl',
        'NCDC': '/league/ncdc',
        'EHL': '/league/ehl',
        'EHLP': '/league/ehlp',
        'NA3HL': '/league/na3hl',
        'USPHL Premier': '/league/usphl-premier',
        'USPHL Elite': '/league/usphl-elite',
        'AYHL 18U': '/league/ayhl-18u',
        'BEAST 18U': '/league/beast-18u',
        'CSDHL 18U': '/league/csdhl-18u',
        'ECEL 18U': '/league/ecel-18u',
        'EJEPL 18U': '/league/ejepl-18u',
        'MNHP 18U': '/league/mnhp-18u',
        'NAPHL 18U': '/league/naphl-18u',
        'NJPHL 18U': '/league/njphl-18u',
        'T1EHL 18U': '/league/t1ehl-18u',
        'THF 18U': '/league/thf-18u',
        'AYHL 16U': '/league/ayhl-16u',
        'BEAST 16U': '/league/beast-16u',
        'CSDHL 16U': '/league/csdhl-16u',
        'ECEL 16U': '/league/ecel-16u',
        'EJEPL 16U': '/league/ejepl-16u',
        'MNHP 16U': '/league/mnhp-16u',
        'NAPHL 16U': '/league/naphl-16u',
        'NJPHL 16U': '/league/njphl-16u',
        'T1EHL 16U': '/league/t1ehl-16u',
        'THF 16U': '/league/thf-16u',
        'AYHL 15U': '/league/ayhl-15u',
        'BEAST 15U': '/league/beast-15u',
        'CSDHL 15U': '/league/csdhl-15u',
        'MNHP 15O': '/league/mnhp-15o',
        'NAPHL 15U': '/league/naphl-15u',
        'T1EHL 15U': '/league/t1ehl-15u',
        'THF 15U': '/league/thf-15u',
        'AYHL 14U': '/league/ayhl-14u',
        'BEAST 14U': '/league/beast-14u',
        'MNHP 14U': '/league/mnhp-14u',
        'MNBEL 14U': '/league/mnbel-15u',
        'T1EHL 14U': '/league/t1ehl-14u',
        'THF 14U': '/league/thf-14u',
        'NTDP': '/league/ntdp',
        'USHS-Prep': '/league/ushs-prep',
        'USHS-MN': '/league/ushs-mn',
        'USHS-MI': '/league/ushs-mi',
        'USHS-NY': '/league/ushs-ny',
        'MPHL': '/league/mphl',
        'USHS-MA': '/league/ushs-ma',
        'NAPrepHL U14': '/league/naprephl-u14',
        'NAPrepHL U16': '/league/naprephl-u16',
        'NAPrepHL U18': '/league/naprephl-u18',
        'WHL': '/league/whl',
        'AJHL': '/league/ajhl',
        'BCHL': '/league/bchl',
        'MJHL': '/league/mjhl',
        'SIJHL': '/league/sijhl',
        'SJHL': '/league/sjhl',
        'CapJHL': '/league/capjhl',
        'HJHL': '/league/hjhl',
        'KJHL': '/league/kjhl',
        'KIJHL': '/league/kijhl',
        'NEAJBHL': '/league/neajbhl',
        'NWJHL': '/league/nwjhl',
        'PJHL': '/league/pjhl',
        'PIJHL': '/league/pijhl',
        'VIJHL': '/league/vijhl',
        'CalJCHL': '/league/hc-u21c',
        'HTJHL': '/league/htjhl',
        'NorJHL': '/league/norjhl',
        'QVJHL': '/league/qvjhl',
        'AEHL U18': '/league/aehl-u18',
        'AEHL U17': '/league/aehl-u17',
        'BCEHL U18': '/league/bcehl-u18',
        'BCEHL U17': '/league/bcehl-u17',
        'CSSHL U18': '/league/csshl-u18',
        'CSSHL U17': '/league/csshl-u17',
        'CSSHL U16': '/league/csshl-u16',
        'MU18HL': '/league/mu18hl',
        'HSL U18': '/league/hsl-u18',
        'JPHL U18': '/league/jphl-u18',
        'NAHL U18': '/league/nahl-u18',
        'SAAHL U18': '/league/saahl-u18',
        'SMAAAHL': '/league/smaaahl',
        'WAAA U17': '/league/waaa-u17',
        'AEHL U15': '/league/aehl-u15',
        'BCEHL U15': '/league/bcehl-u15',
        'CSSHL U15': '/league/csshl-u15',
        'CSSHLV U15': '/league/csshlv-u15',
        'HSL U14': '/league/hsl-u14',
        'HSL U15': '/league/hsl-u15',
        'JPHL U14': '/league/jphl-u14',
        'JPHL U15': '/league/jphl-u15',
        'NAHL U15': '/league/nahl-u15',
        'PCAHA U15': '/league/pcbhl',
        'SAAHL U15': '/league/saahl-u15',
        'WAAA U15': '/league/waaa-u15',
        'WAAA U14': '/league/waaa-u14',
        'MMJHL': '/league/mmjhl',
        'CAJHL': '/league/cajhl',
        'OHL': '/league/ohl',
        'CCHL': '/league/cchl',
        'NOJHL': '/league/nojhl',
        'OJHL': '/league/ojhl',
        'EOJHL': '/league/eojhl',
        'GOJHL': '/league/gojhl',
        'LJHL': '/league/ljhl',
        'NCJHL': '/league/ncjhl',
        'PJCHL': '/league/pjchl',
        'OMHA U18': '/league/omha-u18',
        'ALLIANCE U18': '/league/alliance-u18',
        'GNML': '/league/gnml',
        'GTHL U18': '/league/gthl-u18',
        'HEO U18': '/league/heo-u18',
        'OMHA U16': '/league/omha-u16',
        'ALLIANCE U16': '/league/alliance-u16',
        'GTHL U16': '/league/gthl-u16',
        'ALLIANCE U15': '/league/alliance-u15',
        'OMHA U15': '/league/omha-u15',
        'GTHL U15': '/league/gthl-u15',
        'NOHL U15': '/league/nohl-u15',
        'HEO U15': '/league/heo-u15',
        'CAHS': '/league/cahs',
        'CISAA': '/league/cisaa',
        'GMHL': '/league/gmhl',
        'QMJHL': '/league/qmjhl',
        'MJAHL': '/league/mjahl',
        'QJHL': '/league/qjhl',
        'CAJAAHL': '/league/cajaahl',
        'IsJHL': '/league/isjhl',
        'LHC': '/league/lhc',
        'LHJSLSJ': '/league/lhjslsj',
        'LHMJAA': '/league/lhmjaa',
        'NSJHL': '/league/nsjhl',
        'SJJHL': '/league/sjjhl',
        'NBJHL': '/league/nbjhl',
        'NSRJHL': '/league/nsrjhl',
        'PEIJCHL': '/league/peijchl',
        'NBPEIMU18HL': '/league/nbpeimu18hl',
        'NLMMHL': '/league/nlu18mhl',
        'NSU18MHL': '/league/nsu18mhl',
        'PEI U18': '/league/pei-u18',
        'QM18AAA': '/league/qm18aaa',
        'QM18AA': '/league/qm18aa',
        'QM17AAA': '/league/qm17aaa',
        'RSEQ M18 D1': '/league/rseq-m18-d1',
        'NBU15MHL': '/league/nbu15mhl',
        'NLAAAHL U15': '/league/nlaaahl-u15',
        'NSU15MHL': '/league/nsu15mhl',
        'PEI U15': '/league/pei-u15',
        'QM15AAA E': '/league/qm15aaa-e',
        'QM15AAA': '/league/qm15aaa',
        'RSEQ M15 D1': '/league/rseq-m15-d1',
        'World Cup 2016': '/league/wcup',
        'WC': '/league/wc',
        'WC D1A': '/league/wc-d1a',
        'WC D1B': '/league/wc-d1b',
        'WC D2A': '/league/wc-d2a',
        'WC D2B': '/league/wc-d2b',
        'WC D3': '/league/wc-d3',
        'WC D3A': '/league/wc-d3a',
        'WC D3B': '/league/wc-d3b',
        'WC D3Q': '/league/wc-d3q',
        'WC D4': '/league/wc-d4',
        'Olympics': '/league/og',
        'OGQ': '/league/ogq',
        'U20 WJC': '/league/wjc-20',
        'U20 WJC D1A': '/league/wjc-20-d1a',
        'U20 WJC D1B': '/league/wjc-20-d1b',
        'U20 WJC D2A': '/league/wjc-20-d2a',
        'U20 WJC D2B': '/league/wjc-20-d2b',
        'U20 WJC D3': '/league/wjc-20-d3',
        'U18 WJC': '/league/wjc-18',
        'U18 WJC D1A': '/league/wjc-18-d1a',
        'U18 WJC D1B': '/league/wjc-18-d1b',
        'U18 WJC D2A': '/league/wjc-18-d2a',
        'U18 WJC D2B': '/league/wjc-18-d2b',
        'U18 WJC D3A': '/league/wjc-18-d3a',
        'U18 WJC D3B': '/league/wjc-18-d3b',
        'Hlinka Gretzky Cup': '/league/hlinka-gretzky-cup',
        'YOG': '/league/yog',
        'U17 WHC': '/league/whc-17',
        'CCOA': '/league/ccoa',
        'CCOA D1': '/league/ccoa-d1',
        'CCOA U20': '/league/ccoa-u20',
        'CCOA U18': '/league/ccoa-u18',
        'Champions HL': '/league/champions-hl',
        'Continental Cup': '/league/continental-cup'
}

SEASON_DATE_RANGES = {
    
        '1917–18': ['1917-12-19', '1918-03-13'],
        '1918–19': ['1918-12-19', '1919-03-06'],
        '1919–20': ['1919-12-23', '1920-03-10'],
        '1920–21': ['1920-12-22', '1921-03-15'],
        '1921–22': ['1921-12-17', '1922-03-13'],
        '1922–23': ['1922-12-16', '1923-03-09'],
        '1923–24': ['1923-12-15', '1924-03-11'],
        '1924–25': ['1924-11-29', '1925-03-13'],
        '1925–26': ['1925-11-28', '1926-03-27'],
        '1926–27': ['1926-11-18', '1927-04-13'],
        '1927–28': ['1927-11-15', '1928-04-14'],
        '1928–29': ['1928-11-15', '1929-03-29'],
        '1929–30': ['1929-11-14', '1930-04-03'],
        '1930–31': ['1930-11-11', '1931-04-14'],
        '1931–32': ['1931-11-12', '1932-04-09'],
        '1932–33': ['1932-11-10', '1933-04-13'],
        '1933–34': ['1933-11-09', '1934-04-10'],
        '1934–35': ['1934-11-08', '1935-04-09'],
        '1935–36': ['1935-11-07', '1936-04-11'],
        '1936–37': ['1936-11-05', '1937-04-15'],
        '1937–38': ['1937-11-04', '1938-04-12'],
        '1938–39': ['1938-11-03', '1939-04-16'],
        '1939–40': ['1939-11-02', '1940-04-13'],
        '1940–41': ['1940-11-03', '1941-04-12'],
        '1941–42': ['1941-11-01', '1942-04-18'],
        '1967–68': ['1967-10-11', '1968-05-11'],
        '1968–69': ['1968-10-11', '1969-05-04'],
        '1969–70': ['1969-10-11', '1970-05-10'],
        '1970–71': ['1970-10-09', '1971-05-18'],
        '1971–72': ['1971-10-08', '1972-05-11'],
        '1972–73': ['1972-10-07', '1973-05-10'],
        '1973–74': ['1973-10-10', '1974-05-19'],
        '1974–75': ['1974-10-09', '1975-05-27'],
        '1975–76': ['1975-10-07', '1976-05-16'],
        '1976–77': ['1976-10-05', '1977-05-14'],
        '1977–78': ['1977-10-12', '1978-05-25'],
        '1978–79': ['1978-10-11', '1979-05-21'],
        '1979–80': ['1979-10-09', '1980-05-24'],
        '1980–81': ['1980-10-09', '1981-05-21'],
        '1981–82': ['1981-10-06', '1982-05-16'],
        '1982–83': ['1982-10-05', '1983-05-17'],
        '1983–84': ['1983-10-04', '1984-05-19'],
        '1984–85': ['1984-10-11', '1985-05-30'],
        '1985–86': ['1985-10-10', '1986-05-24'],
        '1986–87': ['1986-10-09', '1987-05-31'],
        '1987–88': ['1987-10-08', '1988-05-26'],
        '1988–89': ['1988-10-06', '1989-05-25'],
        '1989–90': ['1989-10-05', '1990-05-24'],
        '1990–91': ['1990-10-04', '1991-05-25'],
        '1991–92': ['1991-10-03', '1992-06-01'],
        '1992–93': ['1992-10-06', '1993-06-09'],
        '1993–94': ['1993-10-05', '1994-06-14'],
        '1994–95': ['1994-01-20', '1995-06-24'],
        '1995–96': ['1995-10-06', '1996-06-10'],
        '1996–97': ['1996-10-04', '1997-06-07'],
        '1997–98': ['1997-10-01', '1998-06-16'],
        '1998–99': ['1998-10-09', '1999-06-19'],
        '1999–00': ['1999-10-01', '200-06-10'],
        '2000–01': ['2000-10-04', '2001-06-09'],
        '2001–02': ['2001-10-03', '2002-06-13'],
        '2002–03': ['2002-10-09', '2003-06-09'],
        '2003–04': ['2003-10-08', '2004-06-07'],
        '2005–06': ['2005-10-05', '2006-06-19'],
        '2006–07': ['2006-10-04', '2007-06-06'],
        '2007–08': ['2007-09-29', '2008-06-04'],
        '2008–09': ['2008-10-04', '2009-06-12'],
        '2009–10': ['2009-10-01', '2010-06-09'],
        '2010–11': ['2010-10-07', '2011-06-15'],
        '2011–12': ['2011-10-06', '2012-06-11'],
        '2012–13': ['2012-01-19', '2013-06-24'],
        '2013–14': ['2013-10-01', '2014-06-13'],
        '2014–15': ['2014-10-08', '2015-06-15'],
        '2015–16': ['2015-10-07', '2016-06-12'],
        '2016–17': ['2016-10-12', '2017-06-11'],
        '2017–18': ['2017-10-04', '2018-06-07'],
        '2018–19': ['2018-10-03', '2019-06-12'],
        '2019–20': ['2019-10-02', '2020-09-28'],
        '2020–21': ['2020-01-13', '2021-07-07'],
        '2021–22': ['2021-10-12', '2022-06-26'],
        '2022–23': ['2022-10-07', '2023-06-13'],
        '2023–24': ['2023-10-10', 'TBD']
}