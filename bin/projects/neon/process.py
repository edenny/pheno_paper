import shutil

from xml.etree import ElementTree
from zipfile import ZipFile

import os, argparse, uuid, re, csv, sys

import pandas as pd

NEON_DATA_DIR = 'NEON_obs-phenology-plant'
HEADERS = ['uid', 'Latitude', 'Longitude', 'Year', 'DayOfYear', 'Source', 'IndividualID', 'genus', 'specificEpithet',
           'scientificName', 'phenophaseName', 'lower_count', 'upper_count', 'lower_percent', 'upper_percent']

COLUMNS_MAP = {
    'individualID': 'IndividualID',
    'dayOfYear': 'DayOfYear',
}

INTENSITY_FILE = 'projects/neon/intensity_values.csv'
INTENSITY_VALUE_FRAME = pd.read_csv(INTENSITY_FILE, skipinitialspace=True, header=0) if os.path.exists(
    INTENSITY_FILE) else None

INTENSITY = 'intensity'
PHENO_DESC = 'phenophase descriptions'
GENERATE_DATA = 'generate data'


def process(input_dir, output_dir, action=GENERATE_DATA):
    if action == INTENSITY:
        generate_intensity_values()
    elif action == PHENO_DESC:
        generate_phen_descriptions()
    elif action == GENERATE_DATA:
        import ipdb
        #ipdb.set_trace()
        generate_data(input_dir, output_dir)
    else:
        raise RuntimeError('undefined action {}'.format(action))


def generate_data(input_dir, output_dir):
    clean(output_dir)

    out_file = open(os.path.join(output_dir, 'data.csv'), 'w')
    writer = csv.writer(out_file)
    writer.writerow(HEADERS)

    for root, dirs, files in os.walk(os.path.join(input_dir, NEON_DATA_DIR)):

        for file in files:
            if file.endswith(".zip"):
                process_zip(os.path.join(root, file), out_file)

    out_file.close()


def process_zip(input_zip_file, out_file):
    xml_file = None
    csv_file = None

    with ZipFile(input_zip_file) as zip_file:
        for filename in zip_file.namelist():

            if filename.endswith('phe_statusintensity.csv'):
                if csv_file:
                    raise RuntimeError('multiple csv files found in zip_file {}'.format(zip_file.filename))
                csv_file = zip_file.open(filename)

            elif filename.endswith('.xml'):
                if xml_file:
                    raise RuntimeError('multiple xml files found in zip_file {}'.format(zip_file.filename))
                xml_file = zip_file.open(filename)

    if not csv_file or not xml_file:
        raise RuntimeError('missing xml or csv file in zip_file {}'.format(zip_file.filename))

    lat, lng = parse_coordinates(xml_file)

    data = pd.read_csv(csv_file, header=0, chunksize=100000, skipinitialspace=True,
                       usecols=['uid', 'date', 'dayOfYear', 'individualID', 'scientificName', 'phenophaseName',
                                'phenophaseStatus', 'phenophaseIntensity'],
                       parse_dates=['date'])

    for chunk in data:
        transform_data(chunk, lat, lng).to_csv(out_file, columns=HEADERS, mode='a', header=False, index=False)

    csv_file.close()
    xml_file.close()


def parse_coordinates(xml_file):
    tree = ElementTree.parse(xml_file)
    w_bound = tree.find('./dataset/coverage/geographicCoverage/boundingCoordinates/westBoundingCoordinate')
    e_bound = tree.find('./dataset/coverage/geographicCoverage/boundingCoordinates/eastBoundingCoordinate')
    n_bound = tree.find('./dataset/coverage/geographicCoverage/boundingCoordinates/northBoundingCoordinate')
    s_bound = tree.find('./dataset/coverage/geographicCoverage/boundingCoordinates/southBoundingCoordinate')

    if (w_bound is not None and e_bound is not None and w_bound.text != e_bound.text) or (n_bound is not None and s_bound is not None and n_bound.text != s_bound.text):
        raise RuntimeError('bounding coordinates do not match for xml_file: {}'.format(xml_file.name))

    lat = n_bound.text if n_bound is not None else ""
    lng = w_bound.text if w_bound is not None else ""

    # if not lat or not lng:
    #     raise RuntimeError('missing bounding coordinates for xml_file: {}'.format(xml_file.name))

    return lat, lng


def transform_data(data, lat, lng):
    data['Source'] = 'NEON'
    data['Latitude'] = lat
    data['Longitude'] = lng

    data['genus'] = data.apply(lambda row: row.scientificName.split()[0] if pd.notnull(row.scientificName) else "",
                               axis=1)
    data['specificEpithet'] = data.apply(
        lambda row: row.scientificName.split()[1] if pd.notnull(row.scientificName) else "", axis=1)
    data['Year'] = data.apply(lambda row: row['date'].year, axis=1)

    data[list("lower_count")] = data[list("lower_count")].astype(int)
    data[list("upper_count")] = data[list("upper_count")].astype(int)

    df = data.merge(INTENSITY_VALUE_FRAME, left_on='phenophaseIntensity', right_on='value', how='left')

    # check that we have a 'value' value if we have a phenophaseIntensity value
    if not df.loc[df.phenophaseIntensity.notnull() & df.value.isnull()].empty:
        raise RuntimeError('found row with a phenophaseIntensity, but is missing the appropriate counts. may need to '
                           'regenerate the intensity_values.csv file. Re-run this script with the --intensity flag to '
                           'append and "values" that do not currently exist in the intensity_values.csv file. You will '
                           'need to manually insert the correct counts in the intensity_values.csv file.')

    # if phenophaseStatus is 'yes' and no phenophaseIntensity, set lower_count = 1
    df.loc[df.phenophaseIntensity.isnull() & df.phenophaseStatus.str.match('yes', case=False), 'lower_count'] = 1
    # if phenophaseStatus is 'yes' and no phenophaseIntensity, set lower_count = 1
    df.loc[df.phenophaseIntensity.isnull() & df.phenophaseStatus.str.match('no', case=False), 'upper_count'] = 0

    df.fillna('', inplace=True)  # replace all null values

    return df.rename(columns=COLUMNS_MAP)


def clean(dir):
    if (os.path.exists(dir)):
        shutil.rmtree(dir)
    os.makedirs(dir)


def generate_phen_descriptions():
    found_values = set()

    for root, dirs, files in os.walk(os.path.join(input_dir, NEON_DATA_DIR)):

        for file in files:
            if file.endswith(".zip"):

                csv_file = None

                with ZipFile(os.path.join(root, file)) as zip_file:

                    for filename in zip_file.namelist():
                        if filename.endswith('phe_statusintensity.csv'):
                            if csv_file:
                                raise RuntimeError('multiple csv files found in zip_file {}'.format(zip_file.filename))
                            csv_file = zip_file.open(filename)

                if not csv_file:
                    raise RuntimeError('didnt file csv file in zip_file {}'.format(zip_file))

                data = pd.read_csv(csv_file, header=0, chunksize=1000000, skipinitialspace=True,
                                   usecols=['phenophaseName'])

                for chunk in data:
                    found_values.update(chunk.phenophaseName.unique().tolist())

    with open('phenphase_names.csv', 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(['phenophaseName'])

        for value in found_values:
            writer.writerow([value])


def generate_intensity_values():
    if INTENSITY_VALUE_FRAME is None:
        intensity_frame = pd.DataFrame([], columns=['value', 'lower_count', 'upper_count', 'lower_percent',
                                                    'upper_percent'])
    else:
        intensity_frame = INTENSITY_VALUE_FRAME

    found_values = set()

    for root, dirs, files in os.walk(os.path.join(input_dir, NEON_DATA_DIR)):

        for file in files:
            if file.endswith(".zip"):

                csv_file = None

                with ZipFile(os.path.join(root, file)) as zip_file:

                    for filename in zip_file.namelist():
                        if filename.endswith('phe_statusintensity.csv'):
                            if csv_file:
                                raise RuntimeError('multiple csv files found in zip_file {}'.format(zip_file.filename))
                            csv_file = zip_file.open(filename)

                if not csv_file:
                    raise RuntimeError('didnt file csv file in zip_file {}'.format(zip_file))

                data = pd.read_csv(csv_file, header=0, chunksize=1000000, skipinitialspace=True,
                                   usecols=['phenophaseIntensity'])

                for chunk in data:
                    found_values.update(chunk.phenophaseIntensity.unique().tolist())

    found_values.difference_update(intensity_frame.index.tolist())

    intensity_frame = intensity_frame.append(
        pd.DataFrame.from_items([('value', list(found_values))])
    )

    intensity_frame.drop_duplicates('value', inplace=True)
    intensity_frame.set_index('value', inplace=True)

    intensity_frame.to_csv(INTENSITY_FILE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NEON Parser')
    parser.add_argument('input_dir', help='the input directory')
    parser.add_argument('output_dir', help='the output directory to store CSV results')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--intensity', dest='action', action='store_const',
                       const=INTENSITY,
                       help='generate a intensity_values.csv file with all phenophaseIntensity values found in the data')
    group.add_argument('--phenophase', dest='action', action='store_const',
                       const=PHENO_DESC,
                       help='generate a phenophase_names.csv file with all PhenophaseName values found in the data')

    args = parser.parse_args()
    input_dir = args.input_dir.strip()
    output_dir = args.output_dir.strip()

    process(input_dir, output_dir, args.action or GENERATE_DATA)
