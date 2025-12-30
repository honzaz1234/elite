import requests
from hockeydata.gamedata import pbp_parser

URL = "https://www.nhl.com/scores/htmlreports/20242025/PL020560.HTM"


htm = requests.get(URL).content
htm_scraper = pbp_parser.PBPParser(htm=htm)
data = htm_scraper.parse_htm_file()
list_events = []
for item in data:
    list_events.append(item["play_type"])
list_events = list(set(list_events))
list_events
