import scrapy

import common_functions as cf

from logger.logging_config import logger


class TSParser():


    XPATHS = {
        "table_row": "//div[@class='pageBreakAfter' ]/table//tr/td"
                     "/table[.//td[contains(@class, 'playerHeading')]]//tr",
    }


    def __init__(self, htm, report_id: int):
        self.htm = htm
        self.sel = scrapy.Selector(text=self.htm)
        self.report_id = report_id


    def parse_htm_file(self) -> list:
        logger.info(
            "Scraping of player shift data from report %s started", 
            self.report_id
            )
        parsed_players = []
        sel_rows = self.sel.xpath(self.XPATHS["table_row"])
        player_index_ranges = self.get_list_with_player_index_ranges(
            sel_rows=sel_rows)
        player_idx = 0
        for ind in range(len(player_index_ranges)):
            player_idx += 1
            player_dict = self.get_player_dict(
                sel_rows=sel_rows, 
                index_range=player_index_ranges[ind], 
                player_idx=player_idx)
            parsed_players.append(player_dict)
        if not parsed_players:
            error_message = f"No data was scraped for match: {self.report_id}"
            cf.log_and_raise(error_message, ValueError)
        logger.info(
            "Scraping of player shift data from report %s finished", 
            self.report_id
            )

        return parsed_players
    
    
    def get_list_with_player_index_ranges(self, sel_rows) -> list:
        player_header_idx = [
            index for index, element 
            in enumerate(sel_rows)
            if element.xpath("./td[contains(@class, 'playerHeading')]")
            ]
        player_end_idx = [
            index for index, element 
            in enumerate(sel_rows)
            if element.xpath(
            "./td[contains(@class, 'spacer + bborder + lborder + rborder')]")
        ]
        table_ranges = list(zip(player_header_idx, player_end_idx))

        return table_ranges
    
    
    def get_player_dict(
            self, sel_rows: list, index_range: tuple, 
            player_idx: int) -> dict:
        logger.debug(
            "Scraping of shift data for player n.: %s started", player_idx
            )
        player_name = self.get_player_name(sel_rows[index_range[0]])
        shift_selectors = sel_rows[index_range[0] + 2: index_range[1]]
        player_dict = {}
        player_dict[player_name] = self.get_player_shifts(shift_selectors)
        logger.debug(
            "Scraping of shift data for player n.: %s finished", player_idx
            )

        return player_dict


    def get_player_name(self, sel: scrapy.Selector) -> str:
        player_name = cf.get_single_xpath_value(
            sel=sel, xpath="./td/text()", optional=False)

        return player_name  


    def get_player_shifts(self, row_selectors: scrapy.Selector) -> list:
        player_shifts = []
        shift_idx = 0
        for shift_sel in row_selectors:
            shift_idx += 1
            shift_dict = self.get_player_shift(shift_sel=shift_sel,
                                               shift_idx=shift_idx)
            player_shifts.append(shift_dict)

        return player_shifts  


    def get_player_shift(
            self, shift_sel: scrapy.Selector, shift_idx: int) -> dict:
        shift_dict = {}
        shift_dict["period"]  = cf.get_single_xpath_value(
            sel=shift_sel, xpath="./td[2]/text()", optional=False)
        shift_dict["shift_start"]  = cf.get_single_xpath_value(
            sel=shift_sel, xpath="./td[3]/text()", optional=False)
        shift_dict["shift_end"]  = cf.get_single_xpath_value(
            sel=shift_sel, xpath="./td[4]/text()", optional=False)
        logger.debug("Shift n. %s: %s", shift_idx, shift_dict)

        return shift_dict