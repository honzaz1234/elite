from gamedata import report_getter
import json
import time

#report__id_getter_o = report_getter.ReportIDGetter()
#dict_data = report__id_getter_o.get_selected_season_ids(['2023–24'])
#with open('test_report_data.json', 'w') as f:
#    json.dump(dict_data, f, indent=4)



with open('season_ids.json', 'r') as f:
    dict_data = json.load(f)

try:
    with open('all_report_data.json', 'r') as f:
        all_data = json.load(f)
except:
    all_data = {}

try:
    for season in dict_data:
        if season in all_data:
            all_data_season = all_data[season].copy()
            ids_season = [dict_['id'] for dict_ in all_data_season]
        else:
            all_data_season = []
            ids_season = []
        count = 0
        for game in dict_data[season]["report_data"]:
            count += 1
            if game['id'] in ids_season:
                continue
            report_getter_o = report_getter.GetReportData(
                game, dict_data[season]["season"])
            dict_ = report_getter_o.get_all_report_data()
            all_data_season.append(dict_)
            if count % 40 == 0:
                time.sleep(10)
                print(f"Saving data after {count} downloaded matches")
                with open('all_report_data.json', 'w') as f:
                    json.dump(all_data_season, f)

except Exception as e:
    print({e})
    all_data[season] = all_data_season
    with open('all_report_data.json', 'w') as f:
        json.dump(all_data, f)
all_data[season] = all_data_season
with open('all_report_data.json', 'w') as f:
    json.dump(all_data, f)



