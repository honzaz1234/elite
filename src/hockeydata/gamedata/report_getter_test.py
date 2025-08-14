from gamedata.report_getter import ReportIDGetter

import json

SEASON_LIST = ['2022–23']

getter_o = ReportIDGetter()

data = getter_o.get_selected_season_ids(SEASON_LIST)

with open('season_ids.json', 'w') as f:
    json.dump(data, f)
