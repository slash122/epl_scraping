from datetime import datetime, timezone
import json
from parsers.helpers import setup_logger
from parsers.location_parser.job import run as run_location_job
from parsers.ranking_parser.job import run as run_ranking_job
from parsers.content_parser.job import run as run_content_job
from azure.storage.blob import BlobServiceClient
import os

AZURE_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), 'azure_config.json'))
RESULTS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'results'))

def main():
    logger = setup_logger(name="main_job")
    run_jobs(logger)
    save_to_azure(logger)

def run_jobs(logger):
    clear_results()
    logger.info("Started escort.pl scraping application")
    run_location_job()
    logger.info("Location scraping job completed")
    run_ranking_job()
    logger.info("Ranking scraping job completed")
    run_content_job()
    logger.info("Content scraping job completed")
    logger.info("DONE")

def save_to_azure(logger):
    try:
        azure_config = json.load(open(AZURE_CONFIG, 'r'))
        date = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M')
        send_results_to_azure(azure_config, date)
    except Exception as e:
        logger.error(f"Failed to write results to Azure Blob Storage: {e}")
        return
    logger.info("Successfully uploaded results to Azure Blob Storage")

def send_results_to_azure(azure_config, date):
    connection_string = f"{azure_config['connectionString']}{azure_config['accessKey']}"
    blob_container_client = BlobServiceClient.from_connection_string(connection_string).get_container_client(azure_config['containerName'])
    files = files_to_upload()
    for file_path, file_name in files:
        send_file_to_azure(blob_container_client, file_path, file_name, date)

def files_to_upload():
    files = []
    for root, dirs, file_names in os.walk(RESULTS_FOLDER):
        for file_name in file_names:
            if file_name.endswith('.json'):
                files.append((os.path.join(root, file_name), file_name))
    return files

def send_file_to_azure(blob_container_client, file_path, file_name, date):
    with open(file_path, "rb") as data:
        blob_container_client.upload_blob(f"{date}/{file_name}", data, overwrite=True)

def clear_results():
    results_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'results'))
    for root, dirs, files in os.walk(results_folder):
        for file in files:
            if file.endswith('.json'):
                os.remove(os.path.join(root, file))

if __name__ == "__main__":
    main()