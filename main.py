from gdelt.items import *
from gdelt.scrapper import *
import argparse
import logging


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    arg = parser.parse_args()

    if arg.verbose:
        logging.basicConfig(level=logging.INFO)

    scrapper_GDELT = GDELT_Scrapper(query = "war in Nigeria")
    GDELT_articles = scrapper_GDELT.run()
    Article.download_all(GDELT_articles)
