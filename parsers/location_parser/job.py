from parsers.location_parser.parser import LocationParser
from parsers.helpers import get_cookies, setup_logger

def run():
    LocationParser(cookies=get_cookies(), logger=setup_logger()).run()

if __name__ == "__main__":
    run()