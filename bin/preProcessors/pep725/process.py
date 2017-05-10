import shutil

import os, argparse, uuid, re, csv

import pandas as pd

FILE_PREFIX = "PEP725_"
HEADERS = ['record_id', 'observation_id', 'LAT', 'LON', 'ALT', 'NAME', 'YEAR', 'DAY', 'Source', 'scientificname',
           'genus', 'specificEpithet', 'description', 'lower_count', 'upper_count']
COLUMNS_MAP = {
    's_id': 'record_id',
    'lat': 'LAT',
    'lon': 'LON',
    'alt': 'ALT',
    'name': 'NAME',
    'year': 'YEAR',
    'day': 'DAY',
    'species': 'scientificname'
}
FILES = {
    'data': FILE_PREFIX + 'data.csv',
    'genus': FILE_PREFIX + 'genus.csv',
    'species': FILE_PREFIX + 'species.csv',
    'stations': FILE_PREFIX + 'stations.csv',
    'phase': FILE_PREFIX + 'phase.csv',
}


def process(input_dir, output_dir):
    clean(output_dir)

    frames = {}

    frames['genus'] = pd.read_csv(input_dir + FILES['genus'], sep=';', header=0, usecols=['genus_id', 'genus'],
                                  skipinitialspace=True)
    frames['species'] = pd.read_csv(input_dir + FILES['species'], sep=';', header=0, skipinitialspace=True,
                                    usecols=['species_id', 'species'])
    frames['stations'] = pd.read_csv(input_dir + FILES['stations'], sep=';', header=0, skipinitialspace=True,
                                     usecols=['s_id', 'lat', 'lon', 'alt', 'name'])
    frames['phase'] = pd.read_csv(input_dir + FILES['phase'], sep=';', header=0, usecols=['phase_id', 'description'],
                                  skipinitialspace=True)

    with open(output_dir + FILES['data'], 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(HEADERS)

        data = pd.read_csv(input_dir + FILES['data'], sep=';', header=0,
                           usecols=['s_id', 'genus_id', 'species_id', 'phase_id', 'year', 'day'], chunksize=100000,
                           skipinitialspace=True)

        for chunk in data:
            transform_data(frames, chunk).to_csv(out_file, columns=HEADERS, mode='a', header=False, index=False)


def transform_data(frames, data):
    joined_data = data \
        .merge(frames['species'], left_on='species_id', right_on='species_id', how='left') \
        .merge(frames['genus'], left_on='genus_id', right_on='genus_id', how='left') \
        .merge(frames['stations'], left_on='s_id', right_on='s_id', how='left') \
        .merge(frames['phase'], left_on='phase_id', right_on='phase_id', how='left')

    joined_data.fillna("", inplace=True)  # replace all null values

    joined_data['observation_id'] = joined_data.apply(lambda x: uuid.uuid4(), axis=1)
    joined_data['specificEpithet'] = joined_data.apply(
        lambda row: re.sub('^%s' % row['genus'], "", row['species']), axis=1)
    joined_data['Source'] = 'PEP725'
    joined_data['lower_count'] = 1
    joined_data['upper_count'] = 0

    return joined_data.rename(columns=COLUMNS_MAP)


def clean(dir):
    if (os.path.exists(dir)):
        shutil.rmtree(dir)
    os.makedirs(dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PEP725 Parser')
    parser.add_argument('input_dir', help='the input directory')
    parser.add_argument('output_dir', help='the output directory to store CSV results')

    args = parser.parse_args()
    input_dir = args.input_dir.strip()
    output_dir = args.output_dir.strip()

    if not input_dir.endswith('/'):
        input_dir = input_dir + '/'
    if not output_dir.endswith('/'):
        output_dir = output_dir + '/'

    process(input_dir, output_dir)
