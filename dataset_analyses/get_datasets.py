## grab all datalad datasets

import os
import pandas as pd
from poldracklab.utils.run_shell_cmd import run_shell_cmd

def get_accession_numbers(metadata_file):
    md = pd.read_csv(metadata_file, skiprows=1)
    return(md['Assession Number'].tolist())

def download_datalad_datasets(dsnums, datadir):
    for ds in dsnums:
        download_datalad_dataset(ds, datadir)
    
def download_datalad_dataset(ds, datadir):
    cmd = f'datalad clone git@github.com:OpenNeuroDatasets/{ds}.git'
    print(cmd)
    run_shell_cmd(cmd, datadir)

if __name__ == "__main__":
    metadata_file = '../data/openneuro/metadata_06172021.csv'
    datadir = '/home/poldrack/data/openneuro'
    dsnums = get_accession_numbers(metadata_file)
    download_datalad_datasets(dsnums, datadir)