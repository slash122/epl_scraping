from parser import LocationParser
from parsers.helpers import get_cookies, setup_logger

def main():
    LocationParser(cookies=get_cookies(), logger=setup_logger()).run()

if __name__ == "__main__":
    main()