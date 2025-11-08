import json
import os
import argparse 
from parser import ContentParser
from parsers.helpers import get_cookies, setup_logger
from threading import Thread

RANKINGS_RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../results/ranking_results'))

def main():
    args = cli_args()
    threads_num = get_threads_num(args)
    rankings_batches = prepare_rankings(args, threads_num)
    threads = []
    for thread_idx in range(threads_num):
        thread = Thread(target=thread_worker, args=(rankings_batches[thread_idx], thread_idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def thread_worker(urls, batch_idx):
    ContentParser(advertisement_urls=urls, cookies=get_cookies(), logger=setup_logger(), batch_num=batch_idx).run()

def prepare_rankings(args, threads_num=1):
    rankings_data = get_rankings_data(args)
    flattened_urls = [advertisement['url'] for province in rankings_data for city in province['cities'] for advertisement in city['rankings']]
    if threads_num == 1: return [flattened_urls]
    return [flattened_urls[i::threads_num] for i in range(threads_num)]

def get_rankings_data(args):
    rankings_file = args.rankings_file
    if not rankings_file:
        rankings_file = os.path.join(RANKINGS_RESULTS_FOLDER, sorted(os.listdir(RANKINGS_RESULTS_FOLDER))[-1])

    with open(rankings_file, 'r') as f:
        rankings_data = json.load(f)

    return rankings_data

def cli_args():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('--threads', type=str, required=False, help='Number of threads to use')
    cli_parser.add_argument('--rankings-file', type=str, required=False, help='Path to the rankings JSON file')

    return cli_parser.parse_args()

def get_threads_num(args):
    threads_num = args.threads
    return int(threads_num) if threads_num else 1

if __name__ == "__main__":
    main()