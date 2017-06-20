import argparse, csv, os, datetime

import elasticsearch.helpers
from elasticsearch import Elasticsearch

# This script assumes that the csv's have the following headers
# eventID
# materialSampleID
# startDayOfYear
# year
# latitude
# longitude
# genus
# specificEpithet
# scientificName
# lower_count
# upper_count
# lower_percent
# upper_percent
# source -- assumes that this is the same for each entry in each file in the data_dir. this is also used as the index name
# plantStructurePresenceTypes -- this is a '|' delimited field

ALIAS_NAME = 'ppo'
TYPE = 'record'


def load(data_dir, drop_existing=False):
    es = Elasticsearch()

    index_name = get_index_name(data_dir)

    if not es.indices.exists(index_name):
        create_index(es, index_name)
    elif drop_existing:
        es.indices.delete(index=index_name)
        create_index(es, index_name)

    doc_count = 0

    for file in get_files(data_dir):
        try:
            doc_count += load_file(es, file, index_name)
        except RuntimeError as e:
            print(e)
            print("Failed to load file {}".format(file))


    print("Indexed {} documents total".format(doc_count))


def load_file(es, file, index_name):
    doc_count = 0
    data = []

    with open(file) as f:
        print("Starting indexing on " + f.name)
        reader = csv.DictReader(f)

        for row in reader:
            row['plantStructurePresenceTypes'] = row['plantStructurePresenceTypes'].split("|")
            row['loaded_ts'] = datetime.datetime.now()
            data.append({k: v for k, v in row.items() if v})  # remove any empty values

        elasticsearch.helpers.bulk(client=es, index=index_name, actions=data, doc_type=TYPE, raise_on_error=True,
                                   chunk_size=10000, request_timeout=60)
        doc_count += len(data)
        print("Indexed {} documents in {}".format(doc_count, f.name))

    return doc_count


def get_index_name(data_dir):
    """
    finds the name for the elasticsearch index. The name is the 'source' column value in the data files.
    we assume that each record in each file in the data_dir has the same 'source' value.
    """

    for file in get_files(data_dir):
        with open(file) as f:
            reader = csv.DictReader(f)

            for row in reader:

                if row['source']:
                    return row['source'].lower()


def create_index(es, index_name):
    request_body = {
        "mappings": {
            TYPE: {
                "properties": {
                    "plantStructurePresenceTypes": {"type": "keyword"}
                }
            }
        }
    }
    es.indices.create(index=index_name, body=request_body)
    es.indices.put_alias(index=index_name, name=ALIAS_NAME)


def get_files(data_dir):
    for root, dirs, files in os.walk(data_dir):

        for file in files:
            if file.endswith(".csv"):
                yield os.path.join(root, file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to load local elasticsearch instance with reasoned data')
    parser.add_argument('data_dir', help='the directory containing the reasoned data to load')
    parser.add_argument('--drop-existing', dest='drop_existing', action='store_true',
                        help='this flag will drop all existing data with the same "source" value.')

    args = parser.parse_args()

    load(args.data_dir.strip(), args.drop_existing or False);
