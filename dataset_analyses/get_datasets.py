# grab all datalad datasets

import pandas as pd
import subprocess


def run_shell_cmd(cmd,cwd=[]):
    """ run a command in the shell using Popen
    """
    stdout_holder = []
    if cwd:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,cwd=cwd)
    else:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        print(line.strip())
        stdout_holder.append(line.strip())
    process.wait()
    return stdout_holder


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
    metadata_file = '../data/openneuro/metadata_06182021.csv'
    datadir = '/home/poldrack/data/openneuro'
    dsnums = get_accession_numbers(metadata_file)
    download_datalad_datasets(dsnums, datadir)
