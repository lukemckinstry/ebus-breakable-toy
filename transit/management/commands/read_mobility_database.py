import os
import csv
import urllib.request
import logging

from django.core.management.base import BaseCommand, CommandError

from transit.models import DataSource

logging.basicConfig()
LOG = logging.getLogger()


def read_sanitize_key(obj, key, size, default=None):
    return obj.get(key,"")[:size]


def write_data_source_to_db(obj):

    data_source_mdb_id = obj.get("mdb_source_id", "")
    if not data_source_mdb_id:
        return None

    if DataSource.objects.filter(mdb_source_id=data_source_mdb_id).exists():
        a = DataSource.objects.get(mdb_source_id=data_source_mdb_id)
        a_obj = a

    else:

        a = DataSource.objects.update_or_create(
            name = read_sanitize_key(obj,"provider",100, default="unknown"),
            mdb_source_id = read_sanitize_key(obj,"mdb_source_id", 32),
            location_country_code = read_sanitize_key(obj,"location.country_code", 32),
            location_subdivision_name = read_sanitize_key(obj,"location.subdivision_name", 100),
            location_municipality = read_sanitize_key(obj,"location.municipality", 100),
            provider = read_sanitize_key(obj,"provider", 250),
            urls_direct_download = read_sanitize_key(obj,"urls.direct_download", 250),
            urls_authentication_type = read_sanitize_key(obj,"urls.authentication_type", 100),
            urls_authentication_info = read_sanitize_key(obj,"urls.authentication_type", 100),
            urls_api_key_parameter_name = read_sanitize_key(obj,"urls.api_key_parameter_name", 100),
            urls_latest = read_sanitize_key(obj,"urls.latest", 250),
            urls_license = read_sanitize_key(obj,"urls.license", 100),
            status = read_sanitize_key(obj,"status", 100)
        )

        a_obj = a[0]

    return {"source id": a_obj.mdb_source_id, "provider": a_obj.provider}

def download_csv(url, save_path):
    urllib.request.urlretrieve(url, save_path)

def read_csv_line_by_line(file_path):
    d = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Process each row here
            write_data_source_to_db(row)
    

def gather_mobility_data():
    # Get the current working directory
    current_directory = os.getcwd()
    local_file_path = current_directory + "tmp_mobility_database.csv"
    # Print the current working directory
    print("Current Working Directory:", current_directory)
    # URL of the CSV file
    csv_url = "https://bit.ly/catalogs-csv"
    # Download the CSV file
    download_csv(csv_url, local_file_path)
    # Read the CSV file line by line
    read_csv_line_by_line(local_file_path)

class Command(BaseCommand):
    help = "Loads data from gtfs transit feed files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Set log level to debug",
        )

        parser.add_argument(
            "--sample",
            nargs="?",
            default=None,
            const="https://storage.googleapis.com/storage/v1/b/mdb-latest/o/us-pennsylvania-centre-county-transit-authority-cata-gtfs-1236.zip?alt=media",
            help="Download a sample gtfs file (option to provide a download url)",
        )

    def handle(self, *args, **options):

        if options["debug"]:
            LOG.setLevel(logging.DEBUG)
        else:
            LOG.setLevel(logging.INFO)
        LOG.info("Going to gather records from the mobility database")
        gather_mobility_data()

        return
