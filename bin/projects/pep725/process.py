import shutil

import os, argparse, uuid, re, csv

import pandas as pd

FILE_PREFIX = "pep725_"
HEADERS = ['record_id', 'observation_id', 'LAT', 'LON', 'ALT', 'NAME', 'YEAR', 'DAY', 'Source', 'scientificname',
           'genus', 'specificEpithet', 'description', 'lower_count' ]
COLUMNS_MAP = {
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

    count = 0
    #with open(output_dir + FILES['data'], 'w') as out_file:
    #print 'out_file = ' + out_file.name
    #writer = csv.writer(out_file)
    #writer.writerow(HEADERS)

    data = pd.read_csv(input_dir + FILES['data'], sep=';', header=0,
           usecols=['s_id', 'genus_id', 'species_id', 'phase_id', 'year', 'day'], chunksize=100000,
           skipinitialspace=True)

    for chunk in data:
        count = count + 100000
        # specify columns - 'record_id'. If leave 'record_id' in the columns, pandas will print an extra
        # empty column as 'record_id' is the dataFrame index, and pandas doesn't consider the index a column
        print "    processing 100000 of " + str(count)
        df = transform_data(frames, chunk)
        # get a list of unique genus names
        genera = df.genus.unique()
        # write files out by genus
        for genus in genera:
            print "       genus = " + genus
            output_filename_fullpath = output_dir + genus + '.csv'
            #df.to_csv(output_filename_fullpath,sep=',', mode='a', header=writeHeader)
            #df.loc[df['Genus'] == genus].to_csv(output_filename_fullpath,sep=',', mode='a', header=writeHeader)
            df.loc[df['genus'] == genus].to_csv(output_filename_fullpath, columns=HEADERS[1:], mode='a', header=False)


def transform_data(frames, data):
    joined_data = data \
        .merge(frames['species'], left_on='species_id', right_on='species_id', how='left') \
        .merge(frames['genus'], left_on='genus_id', right_on='genus_id', how='left') \
        .merge(frames['stations'], left_on='s_id', right_on='s_id', how='left') \
        .merge(frames['phase'], left_on='phase_id', right_on='phase_id', how='left')

    joined_data.fillna("", inplace=True)  # replace all null values

    # manually remove some data from set that we don't want to work with
    # need to come up with a better method for this in the future!
    exclude=[]
    exclude.append("Beginning of seed imbibition, P, V: Beginning of bud swelling")
    exclude.append("D: Hypocotyl with cotyledons growing towards soil surface, P, V: Shoot growing towards soil surface")
    exclude.append("Dry seed (seed dressing takes place at stage 00), P, V: Winter dormancy or resting period")
    exclude.append("Elongation of radicle, formation of root hairs and /or lateral roots")
    exclude.append("end of harvest")
    exclude.append("End of leaf fall, plants or above ground parts dead or dormant, P Plant resting or dormant")
    exclude.append("G: Coleoptile emerged from caryopsis, D, M: Hypocotyl with cotyledons or shoot breaking through seed coat, P, V: Beginning of sprouting or bud breaking")
    exclude.append("G: Emergence: Coleoptile breaks through soil surface, D, M: Emergence: Cotyledons break through soil surface(except hypogeal germination),D, V: Emergence: Shoot/leaf breaks through soil surface, P: Bud shows green tips")
    exclude.append("Grapevine bleeding, pruned grapes start to loss water from the cuts")
    exclude.append("Harvestable vegetative plant parts or vegetatively propagated organs begin to develop")
    exclude.append("Harvestable vegetative plant parts or vegetatively propagated organs have reached 30% of final size, G: Flag leaf sheath just visibly swollen (mid-boot)")
    exclude.append("Harvestable vegetative plant parts or vegetatively propagated organs have reached 50% of final size, G: Flag leaf sheath swollen (late-boot)")
    exclude.append("Harvestable vegetative plant parts or vegetatively propagated organs have reached 70% of final size, G: Flag leaf sheath opening")
    exclude.append("Harvestable vegetative plant parts or vegetatively propagated organs have reached final size, G: First awns visible, Skinset complete")
    exclude.append("Harvested product (post-harvest or storage treatment is applied at stage 99)")
    exclude.append("Maximum of total tuber mass reached, tubers detach easily from stolons, skin set not yet complete (skin easily removable with thumb)")
    exclude.append("P: Shoot development completed, foliage still green, grapevine: after harvest, end of wood maturation")
    exclude.append("Radicle (root) emerged from seed, P, V: Perennating organs forming roots")
    exclude.append("Seed imbibition complete, P, V: End of bud swelling")
    exclude.append("Sowing")
    exclude.append("start of harvest")

    joined_data=joined_data[~joined_data['description'].isin(exclude)]

    joined_data['observation_id'] = joined_data.apply(lambda x: uuid.uuid4(), axis=1)
    joined_data['specificEpithet'] = joined_data.apply(
        lambda row: re.sub('^%s' % row['genus'], "", row['species']).strip(), axis=1)
    joined_data['Source'] = 'PEP725'
    joined_data['lower_count'] = 1
    joined_data.index.name = 'record_id'

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
