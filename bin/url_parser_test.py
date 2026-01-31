from hockeydata.management.parsing.management import PlayerURLSParseManager


DB_PATH = "./database/storage_db_test.db"
LEAGUE_UID = "wjc-20-d3b"
FILTERS = {
    "scrape_id": [2]
}


def main():
    parser_manager = PlayerURLSParseManager(
        storage_db_path=DB_PATH,
        filters=FILTERS, 
        )
    parser_manager.set_up()
    parsed_data = parser_manager.parse_data(max_workers=4)
    parser_manager._input_all_data(parsed_data=parsed_data)
    parser_manager.close_storage_session()


if __name__ == "__main__":
    main()

