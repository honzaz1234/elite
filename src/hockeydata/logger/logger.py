#code created by mCodingLLC github account, original code available at:
#https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/135_modern_logging

import json
import logging.config
import logging.handlers
import pathlib


CONFIG_PATH = './src/hockeydata/logger/logger_config.json'


def setup_logging():
    config_file = pathlib.Path(CONFIG_PATH)
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)


setup_logging()
logger = logging.getLogger("elite") 


def main():
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")


if __name__ == "__main__":
    main()