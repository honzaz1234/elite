import requests
from gamedata import ts_parser

URL_SHIFT = "https://www.nhl.com/scores/htmlreports/20242025/TV020878.HTM"

htm = requests.get(URL_SHIFT).content
htm_scraper = ts_parser.TSParser(htm=htm, report_id="TV020878")
data = htm_scraper.parse_htm_file()

