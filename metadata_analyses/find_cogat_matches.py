# process readme for each dataset
# find cognitive atlas terms

import json
import pandas as pd
from collections import defaultdict
from cogat import load_cogat_terms, get_cogat_matches
from utils import split_on_uppercase


def get_accession_numbers(metadata_file):
    md = pd.read_csv(metadata_file, skiprows=1)
    return(md['Assession Number'].tolist())


def get_db_metadata():
    db_metadata_file = '../data/openneuro/db_metadata.json'
    with open(db_metadata_file) as f:
        metadata = json.load(f)
    return(metadata)


def get_latest_snapshot_id(ds, db_metadata):
    # all snapshots should have 'latestSnapshot' defined
    # so we just need to take the first
    ds_matches = [i for i in db_metadata.keys() if i.find(ds) > -1]
    return(db_metadata[ds_matches[0]]['latestSnapshot'])


def get_latest_snapshot_readme(ds, db_metadata):
    latest_snapshot_id = get_latest_snapshot_id(ds, db_metadata)
    latest_snapshot_md = db_metadata[latest_snapshot_id]
    retval = db_metadata[latest_snapshot_id]['data']['snapshot']['description']['Name']
    if latest_snapshot_md['readme'] is not None:
        readme = latest_snapshot_md['readme'].lower()
        readme = ' '.join(readme.split())
        retval = ' '.join([retval, readme])
    return(retval)


def cleanup_task_name(name):
    # split by capital letters
    name = ' '.join(split_on_uppercase(name)).lower()

    # get rid of any multiple spaces
    name = ' '.join(name.split())
    return(name)


def get_task_info():
    # create dict relating ds number to task names
    task_info_df = pd.read_csv('../data/openneuro/task_info.csv')
    task_info_dict = defaultdict(lambda: [])
    for idx in task_info_df.index:
        taskname_orig = task_info_df.loc[idx, 'taskname']
        taskname_clean = cleanup_task_name(taskname_orig)
        task_info_dict[task_info_df.loc[idx, 'dsnum']].append(taskname_clean)
    return(task_info_dict)


if __name__ == "__main__":
    metadata_file = '../data/openneuro/metadata_06182021.csv'
    db_metadata = get_db_metadata()

    # try to use saved version of terms, or download if not saved
    termdict = load_cogat_terms()

    datasets = get_accession_numbers(metadata_file)

    readme_data = {}
    cogat_matches = {}
    for ds in datasets:
        readme_data[ds] = get_latest_snapshot_readme(ds, db_metadata)
        cogat_matches[ds] = get_cogat_matches(readme_data[ds], termdict)

    # run same analysis on task names from metadata
    task_info = get_task_info()
    for ds in datasets:
        for task in task_info[ds]:
            # if it doesn't include "task" in the name then add
            # another entry that appends "task" at the end
            if 'task' not in task:
                task_info[ds].append(task + ' task')
        task_string = ' '.join(task_info[ds])
        for t in get_cogat_matches(task_string, termdict):
            cogat_matches[ds].append(t)
            print('appending', t)

    with open('../data/openneuro/cogatlas_matches.json', 'w') as f:
        json.dump(cogat_matches, f)
