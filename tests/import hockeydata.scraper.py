import hockeydata.scraper.player_scraper as player_scraper
import hockeydata.update_dict.update_player as player_updater
import hockeydata.playwright_setup.playwright_setup as ps
import json

pst_o = ps.PlaywrightSetUp()
player_url = "https://www.eliteprospects.com/player/8665/dominik-hasek"
ps_o = player_scraper.PlayerScraper(url=player_url, page=pst_o.page)
player_dict = ps_o.get_info_all()
pst_o.p.stop()
dict_updater = player_updater.UpdatePlayer()
dict_updated = dict_updater.update_player_dict(player_dict)
dict_updated
#with open("howe.json", "w") as f:
#    json.dump(player_dict, f)
#player_dict