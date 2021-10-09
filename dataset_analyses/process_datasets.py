# analyze datalad datasets
# store results to mongodb

from pathlib import Path
import bids
from bids import BIDSLayout
import pymongo
from mongo import (
    add_info_to_db,
    ds_from_database,
    delete_ds_from_db)
import pickle

bids.config.set_option('extension_initial_dot', True)


def get_dataset_info(ds):
    info = {}
    try:
        layout = BIDSLayout(ds)
    except:  # catch any errors
        print('error for', ds.stem)
        return(info)
    info['dsnum'] = ds.stem
    info['tasks'] = layout.get_tasks()
    info['sessions'] = layout.get_sessions()
    info['subjects'] = layout.get_subjects()
    # get metadata for all files with json sidecars
    files = layout.get_files()
    info['metadata'] = {}
    info['tasknames'] = []
    for filename, fileobj in files.items():
        filename_fixed = filename.replace('.', ':')
        try:
            info['metadata'][filename_fixed] = fileobj.get_metadata()
        except (TypeError, OSError):
            info['metadata'][filename_fixed] = None
        # if there are tasks then get the task names from the json files
        if 'TaskName' in info['metadata'][filename_fixed]:
            info['tasknames'].append(
                info['metadata'][filename_fixed]['TaskName'])
    return(info)


if __name__ == "__main__":
    metadata_file = '../data/openneuro/metadata_sheet.csv'
    datadir = Path('/data/openneuro')
    clobber = False

    datasets = [i for i in datadir.glob('ds*')]
    datasets.sort()

    problem_ds = []
    all_info = {}
    for ds in datasets:
        info = ds_from_database(ds.stem)
        if info is not None and not clobber:
            print(ds.stem, 'found in database')
            continue

        if clobber:
            delete_ds_from_db(ds.stem)

        print('reading info for', ds.stem)
        try:
            info = get_dataset_info(ds)
        except TypeError:
            print('problem loading', ds.stem)
            continue
        all_info[ds.stem] = info
        try:
            add_info_to_db(info)
            print("saved metadata for", ds.stem)
        except pymongo.errors.InvalidDocument:
            problem_ds.append(ds.stem)
            print('problem saving', ds.stem)
        # print(info)

with open('../data/openneuro/metadata.pkl', 'wb') as f:
    pickle.dump(all_info, f)
