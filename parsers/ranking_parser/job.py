import argparse
import json
import os
from parser import RankingParser
from parsers.helpers import get_cookies, setup_logger

SELECTED_PROVINCE_IDS = [2]
LOCATION_RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../results/location_results'))

def main():
    location_data = get_location_data()
    RankingParser(location_data=location_data, cookies=get_cookies(), logger=setup_logger()).run()


def get_location_data():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--location-file', type=str, required=False, help='Path to the location JSON file')
    args = cli_parser.parse_args()
    location_file = args.location_file

    if not location_file:
        location_file = os.path.join(LOCATION_RESULTS_FOLDER, sorted(os.listdir(LOCATION_RESULTS_FOLDER))[-1])

    with open(location_file, 'r') as f:
        location_data = json.load(f)
    
    # return [province for province in location_data if int(province['id']) in SELECTED_PROVINCE_IDS]
    return location_data


if __name__ == "__main__":
    main()