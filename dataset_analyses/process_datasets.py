# analyze datalad datasets
# store results to mongodb

import os
from pathlib import Path
import bids
from bids import BIDSLayout
from pymongo import MongoClient

bids.config.set_option('extension_initial_dot', True)

def get_dataset_info(ds):
    info = {}
    layout = BIDSLayout(ds)
    info['dsnum'] = ds.stem
    info['tasks'] = layout.get_tasks()
    info['sessions'] = layout.get_sessions()
    info['subjects'] = layout.get_subjects()
    return(info)

def get_db_collection():
    client = MongoClient()
    db = client.openneuro
    return(db.datasets)

def add_info_to_db(info):
    collection = get_db_collection()
    collection.insert_one(info)

def ds_from_database(dsnum):
    collection = get_db_collection()
    return(collection.find_one({'dsnum': dsnum}))

if __name__ == "__main__":
    metadata_file = '../data/openneuro/metadata_06172021.csv'
    datadir = Path('/home/poldrack/data/openneuro')

    datasets = [i for i in datadir.glob('ds*')]
    datasets.sort()
    for ds in datasets[:4]:
        info = ds_from_database(ds.stem)
        if info is not None:
            print(ds.stem, 'found in database')
        else:
            print('reading info for', ds.stem)
            info = get_dataset_info(ds)
            add_info_to_db(info)
        print(info)

