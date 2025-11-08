import argparse
import json
import os
from parsers.ranking_parser.parser import RankingParser
from parsers.helpers import get_cookies, setup_logger

LOCATION_RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../results/location_results'))

def run(location_file=None):
    location_data = get_location_data(location_file)
    RankingParser(location_data=location_data, cookies=get_cookies(), logger=setup_logger()).run()

def main():
    args = cli_args()
    run(location_file=args.location_file)

def get_location_data(location_file=None):
    if not location_file:
        location_file = os.path.join(LOCATION_RESULTS_FOLDER, sorted(os.listdir(LOCATION_RESULTS_FOLDER))[-1])

    with open(location_file, 'r') as f:
        location_data = json.load(f)
    return location_data

def cli_args():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--location-file', type=str, required=False, help='Path to the location JSON file')
    return cli_parser.parse_args()

if __name__ == "__main__":
    main()