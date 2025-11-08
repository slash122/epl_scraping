from parsers.helpers import setup_logger
from parsers.location_parser.job import run as run_location_job
from parsers.ranking_parser.job import run as run_ranking_job
from parsers.content_parser.job import run as run_content_job
import os

def main():
    logger = setup_logger()
    clear_results()
    logger.info("Started escort.pl scraping application")
    run_location_job()
    logger.info("Location scraping job completed")
    run_ranking_job()
    logger.info("Ranking scraping job completed")
    run_content_job()
    logger.info("Content scraping job completed")
    logger.info("DONE")

def clear_results():
    results_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'results'))
    for root, dirs, files in os.walk(results_folder):
        for file in files:
            if file.endswith('.json'):
                os.remove(os.path.join(root, file))

if __name__ == "__main__":
    main()