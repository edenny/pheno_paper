import os, argparse, csv, shutil, uuid
import pandas as pd

ASU_DATA_DIR = 'ASU_Phenology_DWCA'
HEADERS = ['uid', 'occurrenceID', 'scientificName', 'genus', 'specificEpithet', 'year', 'startDayOfYear',
           'latitude', 'longitude', 'source', 'phenophaseName', 'lower_count', 'upper_count',
           'lower_percent', 'upper_percent']

COLUMNS_MAP = {
    'measurementValue': 'phenophaseName',
    'decimalLatitude': 'latitude',
    'decimalLongitude': 'longitude'
}

FILES = {
    'data': 'data.csv',
    'occurrences': os.path.join(ASU_DATA_DIR, 'occurrences.csv'),
    'identifications': os.path.join(ASU_DATA_DIR, 'identifications.csv'),
    'measurements': os.path.join(ASU_DATA_DIR, 'measurementOrFact.csv')
}

INVALID_RECORDS = pd.DataFrame()


def process(input_dir, output_dir):
    clean(output_dir)

    out_file = open(os.path.join(output_dir, 'data.csv'), 'w')
    writer = csv.writer(out_file)
    writer.writerow(HEADERS)

    occurrences = pd.read_csv(input_dir + FILES['occurrences'], header=0, skipinitialspace=True,
                              usecols=['occurrenceID', 'scientificName', 'genus', 'specificEpithet', 'year',
                                       'startDayOfYear', 'decimalLatitude', 'decimalLongitude', 'id'])

    count = 0
    with open(os.path.join(output_dir, FILES['data']), 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(HEADERS)

        data = pd.read_csv(input_dir + FILES['measurements'], header=0, skipinitialspace=True, chunksize=100000,
                           usecols=['coreid', 'measurementValue'])

        for chunk in data:
            count += len(chunk)
            print "    processing 100000 of " + str(count)
            transform_data(occurrences, chunk).to_csv(out_file, columns=HEADERS, mode='a', header=False, index=False)

    out_file.close()

    # write invalid records to file
    with open(os.path.join(output_dir, 'invalid_data.csv'), 'w') as i_file:
        INVALID_RECORDS.to_csv(i_file, columns=HEADERS, header=True, index=False)


def transform_data(occurrences, base_data):
    global INVALID_RECORDS

    data = base_data \
        .merge(occurrences, left_on='coreid', right_on='id', how='left')

    data['uid'] = data.apply(lambda x: uuid.uuid4(), axis=1)
    # data = data.replace(r'\s+', pd.np.nan, regex=True)

    # remove invalid records to write to a separate file later
    INVALID_RECORDS = INVALID_RECORDS.append(data[data.decimalLatitude.isnull()])
    data = data.dropna(subset=['decimalLatitude'])
    INVALID_RECORDS = INVALID_RECORDS.append(data[data.decimalLongitude.isnull()])
    data = data.dropna(subset=['decimalLongitude'])
    INVALID_RECORDS = INVALID_RECORDS.append(data[data.year.isnull()])
    data = data.dropna(subset=['year'])
    INVALID_RECORDS = INVALID_RECORDS.append(data[data.startDayOfYear.isnull()])
    data = data.dropna(subset=['startDayOfYear'])

    data.fillna("", inplace=True)  # replace all null values

    data['source'] = 'ASU'
    data['lower_count'] = 1
    data["year"] = data["year"].astype(int)
    data["startDayOfYear"] = data["startDayOfYear"].astype(int)

    return data.rename(columns=COLUMNS_MAP)


def clean(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NEON Parser')
    parser.add_argument('input_dir', help='the input directory')
    parser.add_argument('output_dir', help='the output directory to store CSV results')

    args = parser.parse_args()
    input_dir = args.input_dir.strip()
    output_dir = args.output_dir.strip()

    process(input_dir, output_dir)
