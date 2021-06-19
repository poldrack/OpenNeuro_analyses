

from get_datasets import get_accession_numbers
from pathlib import Path
from mongo import ds_from_database
from collections import namedtuple
import pandas as pd


def check_datasets(dsnums, verbose=False):
    datasets = {'missing': [], 'empty': [], 'good': []}

    for ds in dsnums:
        dspath = datadir / ds
        if not dspath.exists():
            if verbose:
                print('missing', ds)
            datasets['missing'].append(ds)
            continue

        info = ds_from_database(ds)
        if info is None:
            if verbose:
                print('empty', ds)
            datasets['empty'].append(ds)
        else:
            datasets['good'].append(ds)
    return(datasets)


def get_ds_info(ds):
    info = ds_from_database(ds)
    Result = namedtuple("Result", "dsnum, ntasks, nsessions, nsubs, tasknames")
    if info['sessions'] == []:
        info['sessions'] = ['1']
    tasknames = set(info['tasknames']) if 'tasknames' in info else None
    return Result(
        dsnum=ds,
        ntasks=len(info['tasks']),
        nsessions=len(info['sessions']),
        nsubs=len(info['subjects']),
        tasknames=tasknames)


if __name__ == "__main__":

    metadata_file = '../data/openneuro/metadata_06182021.csv'
    datadir = Path('/home/poldrack/data/openneuro')
    dsnums = get_accession_numbers(metadata_file)

    datasets = check_datasets(dsnums)
    print(f"found {len(datasets['good'])} good datasets")

    ds_info = []
    task_info = []

    for ds in datasets['good']:
        result = get_ds_info(ds)
        ds_info.append(result)
        for t in result.tasknames:
            task_info.append([ds, t])

    ds_info_df = pd.DataFrame(ds_info)
    ds_info_df.to_csv('../data/openneuro/ds_info.csv')

    task_info_df = pd.DataFrame(task_info,
                                columns=['dsnum', 'taskname'])
    task_info_df.to_csv('../data/openneuro/task_info.csv')
