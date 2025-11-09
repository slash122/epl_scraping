import json
import os
import argparse
from parsers.content_parser.parser import ContentParser
from parsers.helpers import get_cookies, setup_logger
from threading import Thread

RANKINGS_RESULTS_FOLDER = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../results/ranking_results")
)


# For running from cli
def main():
    cli_arguments = cli_args()
    run(rankings_file=cli_arguments.rankings_file, threads=cli_arguments.threads)


def run(rankings_file=None, threads=16):
    threads_num = get_threads_num(threads)
    rankings_batches = prepare_rankings(rankings_file, threads_num)
    threads = []
    for thread_idx in range(threads_num):
        thread = Thread(
            target=thread_worker, args=(rankings_batches[thread_idx], thread_idx)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def thread_worker(urls, batch_idx):
    ContentParser(
        advertisement_urls=urls,
        cookies=get_cookies(),
        logger=setup_logger(),
        batch_num=batch_idx,
    ).run()


def prepare_rankings(rankings_file, threads_num=1):
    rankings_data = get_rankings_data(rankings_file)
    flattened_urls = [
        advertisement["url"]
        for province in rankings_data
        for city in province["cities"]
        for advertisement in city["rankings"]
    ]
    if threads_num == 1:
        return [flattened_urls]
    return [flattened_urls[i::threads_num] for i in range(threads_num)]


def get_rankings_data(rankings_file):
    if not rankings_file:
        rankings_file = os.path.join(
            RANKINGS_RESULTS_FOLDER, sorted(os.listdir(RANKINGS_RESULTS_FOLDER))[-1]
        )

    with open(rankings_file, "r") as f:
        rankings_data = json.load(f)

    return rankings_data


def get_threads_num(threads):
    return int(threads) if threads else 1


def cli_args():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument(
        "--threads", type=str, required=False, help="Number of threads to use"
    )
    cli_parser.add_argument(
        "--rankings-file",
        type=str,
        required=False,
        help="Path to the rankings JSON file",
    )

    return cli_parser.parse_args()


if __name__ == "__main__":
    main()
