# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Analysis of publications related to OpenNeuro

# %%
import numpy as np
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as tkr
import requests
from datetime import datetime
import matplotlib
from collections import defaultdict

# %%
figdir = './'

# %%
# use metadata obtained from API - based on Joe's metadata_update.py

headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Origin': 'https://openneuro.org',
}

query = """
{
    edges {
        cursor,
        node {
            id,
            publishDate,
            latestSnapshot {
                tag, 
                dataset {
                    name, 
                    publishDate,
                    metadata {
                      trialCount,
                      studyDesign,
                      studyDomain,
                      studyLongitudinal,
                      dataProcessed,
                      species,
                      associatedPaperDOI,
                      openneuroPaperDOI
                      dxStatus
                    }
                }, 
                description {
                    SeniorAuthor
                },
                summary {
                    subjects,
                    modalities, 
                    secondaryModalities, 
                    subjectMetadata {
                        age
                    }, 
                    tasks,
                    dataProcessed
                }
            }
        }
    }
}
""".replace(
    '\n', ''
)
data = '{"query":"query testq{datasets ' + query + '}"}'


response = requests.post(
    'https://openneuro.org/crn/graphql', headers=headers, data=data
)
response = response.json()

datasets = {}

while True:
    for y in response['data']['datasets']['edges']:

        datasets[y['node']['id']] = y

    if len(response['data']['datasets']['edges']) < 25:
        break

    next_cur = y['cursor']
    data = (
        f'{{"query": "query testq{{datasets(after: \\"{next_cur}\\") '
        + query
        + '}"}'
    )
    response = requests.post(
        'https://openneuro.org/crn/graphql', headers=headers, data=data
    )
    response = response.json()

# %%
len(datasets)


# %%
# utility functions to clean things up - from metadata_update.py
def format_modalities(all_modalities):
    Modalities_available_list = []
    if any(('MRI_' in e for e in all_modalities)):
        all_modalities.remove('MRI')
        for m in all_modalities:
            if 'MRI' in m:
                scan_type = scan_dict[m.split('MRI_', 1)[1].lower()]
                new_m = 'MRI - ' + scan_type
                Modalities_available_list.append(new_m)
            else:
                Modalities_available_list.append(m)
    else:
        Modalities_available_list = all_modalities
    return ', '.join(Modalities_available_list)


def format_ages(raw_age_list):
    formatted_list = []
    if raw_age_list:
        age_list = sorted([x['age'] for x in raw_age_list if x['age']])
        for key, value in age_dict.items():
            if any(x for x in age_list if x >= key[0] and x <= key[1]):
                formatted_list.append(value)
        return ', '.join(formatted_list)
    else:
        return ''


def format_name(name):
    if not name:
        return ''
    elif ',' not in name:
        last = name.split(' ')[-1]
        first = ' '.join(name.split(' ')[0:-1])
        new_name = last + ', ' + first
        return new_name
    else:
        return name


# %%
# convert to named tuple for ultimate conversion into pd data frame
# this is converted pretty much directly from metadata_update.py

scan_dict = {
    'anatomical': 'anat',
    'structural': 'anat',
    'functional': 'func',
    'behavioral': 'beh',
    'diffusion': 'dwi',
    'perfusion': 'perf',
}
age_dict = {
    (0, 10): '0-10',
    (11, 17): '11-17',
    (18, 25): '18-25',
    (26, 34): '26-34',
    (35, 50): '35-50',
    (51, 65): '51-65',
    (66, 1000): '66+',
}
bool_dict = {True: 'yes', False: 'no', None: 'no'}
date_arg_format = '%m/%d/%Y'
date_input_format = '%Y-%m-%d'
date_output_format = '%-m/%-d/%Y'


output = []

for accession_Number, y in datasets.items():
    if y['node']['publishDate'] is None:
        print('No publish date for', accession_Number)
        continue
    Dataset_made_public_datetime = datetime.strptime(
        y['node']['publishDate'][:10], date_input_format
    )
    Dataset_URL = os.path.join(
        'https://openneuro.org/datasets/',
        accession_Number,
        'versions',
        y['node']['latestSnapshot']['tag'],
    )
    Dataset_name = y['node']['latestSnapshot']['dataset']['name']
    Dataset_made_public = Dataset_made_public_datetime.strftime(
        date_output_format
    )
    Most_recent_snapshot_date = datetime.strptime(
        y['node']['latestSnapshot']['dataset']['publishDate'][:10],
        date_input_format,
    ).strftime(date_output_format)
    if y['node']['latestSnapshot']['summary'] is not None:
        Number_of_subjects = len(
            y['node']['latestSnapshot']['summary']['subjects']
        )
        Modalities_available = format_modalities(
            y['node']['latestSnapshot']['summary']['secondaryModalities']
            + y['node']['latestSnapshot']['summary']['modalities']
        )
        Ages = format_ages(
            y['node']['latestSnapshot']['summary']['subjectMetadata']
        )
        Tasks_completed = ', '.join(
            y['node']['latestSnapshot']['summary']['tasks']
        )
    else:
        Number_of_subjects = None
        Modalities_available = None
        Ages = None
        Tasks_completed = None

    if y['node']['latestSnapshot']['dataset']['metadata'] is not None:
        DX_status = y['node']['latestSnapshot']['dataset']['metadata'][
            'dxStatus'
        ]
        Number_of_trials = y['node']['latestSnapshot']['dataset']['metadata'][
            'trialCount'
        ]
        Study_design = y['node']['latestSnapshot']['dataset']['metadata'][
            'studyDesign'
        ]
        Domain_studied = y['node']['latestSnapshot']['dataset']['metadata'][
            'studyDomain'
        ]
        Longitudinal = (
            'Yes'
            if y['node']['latestSnapshot']['dataset']['metadata'][
                'studyLongitudinal'
            ]
            == 'Longitudinal'
            else 'No'
        )
        Processed_data = (
            'Yes'
            if y['node']['latestSnapshot']['dataset']['metadata'][
                'dataProcessed'
            ]
            == True
            else 'No'
        )
        Species = y['node']['latestSnapshot']['dataset']['metadata']['species']
        DOI_of_paper_associated_with_DS = y['node']['latestSnapshot'][
            'dataset'
        ]['metadata']['associatedPaperDOI']
        DOI_of_paper_because_DS_on_OpenNeuro = y['node']['latestSnapshot'][
            'dataset'
        ]['metadata']['openneuroPaperDOI']
    else:
        DX_status = ''
        Number_of_trials = ''
        Study_design = ''
        Domain_studied = ''
        Longitudinal = ''
        Processed_data = ''
        Species = ''
        DOI_of_paper_associated_with_DS = ''
        DOI_of_paper_because_DS_on_OpenNeuro = ''

    Senior_Author = format_name(
        y['node']['latestSnapshot']['description']['SeniorAuthor']
    )
    line_raw = [
        accession_Number,
        Dataset_URL,
        Dataset_name,
        Dataset_made_public,
        Most_recent_snapshot_date,
        Number_of_subjects,
        Modalities_available,
        DX_status,
        Ages,
        Tasks_completed,
        Number_of_trials,
        Study_design,
        Domain_studied,
        Longitudinal,
        Processed_data,
        Species,
        DOI_of_paper_associated_with_DS,
        DOI_of_paper_because_DS_on_OpenNeuro,
        Senior_Author,
    ]
    line = [None if x == None else str(x) for x in line_raw]
    output.append(line)


# %%
colnames = [
    'AccessionNumber',
    'Dataset URL',
    'Dataset name',
    'ReleaseDate',
    'Most recent snapshot date (MM/DD/YYYY)',
    'NSubjects',
    'Modalities',
    'DX status(es)',
    'Ages (range)',
    'Tasks completed?',
    '# of trials (if applicable)',
    'Study design',
    'Domain studied',
    'Longitudinal?',
    'Processed data?',
    'Species',
    'DOI of paper associated with DS (from submitter lab)',
    'DOI of paper because DS on OpenNeuro',
    'Senior Author (lab that collected data) Last, First',
]

def int_none(x):
    try:
        return int(x)
    except:
        return None

metadata = pd.DataFrame(output, columns=colnames)
metadata['NSubjects'] = [int_none(i) for i in metadata['NSubjects']]
# metadata.to_csv('../data/openneuro/metadata_sheet.csv')

# %%
metadata['ReleaseDate'] = pd.to_datetime(metadata['ReleaseDate'])

# Collapse any dates prior to 07/17/2018 when OpenfMRI datasets were uploaded
# metadata.loc[metadata["ReleaseDate"] < "2018-07-17", "ReleaseDate"] = "2018-07-17"

# %% [markdown]
# ## Statistics on the database

# %%
print('Number of datasets:', len(metadata['Dataset name'].unique()))
print('Number of datasets:', len(metadata['AccessionNumber'].unique()))


# %%
print('Number of subjets:', metadata['NSubjects'].sum())


# %%
data_paper_dois = metadata[
    'DOI of paper associated with DS (from submitter lab)'
].unique()
print(f'Number of data paper DOIs: {data_paper_dois.shape[0]}')
print(
    f'Proportion of data paper DOIs: {data_paper_dois.shape[0]/metadata.shape[0]}'
)

# %%
user_paper_dois = metadata['DOI of paper because DS on OpenNeuro'].unique()
print(f'Number of user paper DOIs: {user_paper_dois.shape[0]}')

# %% [markdown]
# Clean up data to create plots

# %%
df_sorted = metadata.sort_values('ReleaseDate')
df_sorted['ones'] = 1
df_sorted['cumulative'] = df_sorted['ones'].cumsum()
df_sorted['cumulative_subjects'] = df_sorted['NSubjects'].cumsum()
dates = df_sorted['ReleaseDate'].unique()
print('Earliest dataset:', dates.min())
print('Latest dataset:', dates.max())

# fix dates to reflect fact that early datasets were all from openneuro
# df_sorted.loc[df_sorted['ReleaseDate'] < pd.Timestamp(2018,8,1), 'ReleaseDate'] = '2018-08-01'
df_sorted

# %%

datasets = defaultdict(lambda: 0)
subjects = defaultdict(lambda: 0)

for date, nsub in metadata[['ReleaseDate', 'NSubjects']].values:
    datasets[date.strftime('%Y-%m-%d')] += 1
    subjects[date.strftime('%Y-%m-%d')] += nsub

datadict = defaultdict(list)
for k in datasets.keys():
    datadict['ReleaseDate'].append(k)
    datadict['n_datasets'].append(datasets[k])
    datadict['n_subjects'].append(subjects[k])

df_plotting = pd.DataFrame(datadict)
df_plotting['ReleaseDate'] = pd.to_datetime(df_plotting['ReleaseDate'])
df_plotting = df_plotting.set_index('ReleaseDate').sort_values(
    by='ReleaseDate'
)

df_plotting['cumsum_datasets'] = df_plotting['n_datasets'].cumsum()
df_plotting['cumsum_subjects'] = df_plotting['n_subjects'].cumsum()

release_dates = df_plotting.index.astype(int)

df_plotting.to_csv('openneuro_growth.csv')

# %%
print(
    f"OpenNeuro surpassed the 1000 datasets on {df_plotting[df_plotting['cumsum_datasets'] >= 1000].index[0].strftime('%B %d, %Y')}"
)
print(
    f"The latest report from {df_plotting.index[-1].strftime('%B %d, %Y')} yields {df_plotting['cumsum_datasets'].iloc[-1]} datasets, and {df_plotting['cumsum_subjects'].iloc[-1]} subjects"
)

# %%
end_year = 25   # set to current year + 1
midyears = pd.to_datetime(
    [f'20{yr}-07-02' for yr in range(18, end_year)]
).astype(
    int
)  # July 2 is the midpoint of year
midyears

# %% [markdown]
# Plot # of datasets over time

# %%
plt.figure(figsize=(8, 6))
sns.set(font_scale=2)  # crazy big
sns.lineplot(x='ReleaseDate', y='cumsum_datasets', data=df_plotting)
plt.xticks(rotation=90)
plt.xlabel('Date')
plt.ylabel('Total # of datasets')
plt.tight_layout()
# plt.savefig(os.path.join(figdir, 'n_datasets.pdf'))

# %% [markdown]
# Plot # of subjects over time

# %%
plt.figure(figsize=(8, 6))
sns.set(font_scale=2)  # crazy big
sns.lineplot(x='ReleaseDate', y='cumsum_subjects', data=df_plotting)
plt.xticks(rotation=90)
plt.xlabel('Date')
plt.ylabel('Total # of subjects')
plt.tight_layout()
# plt.savefig(os.path.join(figdir, 'n_subjects.pdf'))

# %% [markdown]
# Plot both together

# %%
# plotting code from Oscar Esteban
# requires a bit of tweaking when years change

font_to_use = 'Arial'

# Edit general skin
sns.set_style('whitegrid')
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot Datasets
color = 'tab:green'
ax1.set_xlabel('Date', fontsize=20)
ax1 = sns.lineplot(
    x=release_dates,
    y=df_plotting['cumsum_datasets'],
    color=color,
    label='Datasets',
    linewidth=3.2,
)
# Plot Subjects
ax2 = ax1.twinx()
color = 'tab:red'
ax2 = sns.lineplot(
    x=release_dates,
    y=df_plotting['cumsum_subjects'],
    color=color,
    label='Subjects',
    linewidth=3.2,
)
# Grid & spines
ax1.grid(False)
ax2.grid(False)
ax1.spines.left.set_visible(False)
ax2.spines.left.set_visible(False)
ax1.spines.right.set_visible(False)
ax2.spines.right.set_visible(False)
ax1.spines.top.set_visible(False)
ax2.spines.top.set_visible(False)
ax1.spines.bottom.set_visible(False)
ax2.spines.bottom.set_visible(False)
# ax1.spines.bottom.set_position(('outward', 10))

# Manipulate axes
ax1.set_ylabel(None)
ax2.set_ylabel(None)
ax1.set_xlabel(None)
ax2.set_xlabel(None)
ax1.get_legend().remove()
ax2.get_legend().remove()

# Place year label at the middle of each year
ax1.set_xticks(midyears)
ax1.set_xticklabels(
    [f'20{yr}' for yr in range(18, end_year)], fontsize=20, color='darkgray'
)

# Annotate total datasets
x_lim = ax1.get_xlim()
y1_lim = ax1.get_ylim()
normalized_dates = (release_dates - x_lim[0]) / (x_lim[1] - x_lim[0])
num_ds = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200]
x_dates_norm = np.interp(
    num_ds, df_plotting['cumsum_datasets'], normalized_dates
)
x_dates = np.interp(num_ds, df_plotting['cumsum_datasets'], release_dates)
y1_norm = (np.array(num_ds) - y1_lim[0]) / (y1_lim[1] - y1_lim[0])

for y, x, y_norm in zip(num_ds, x_dates_norm, y1_norm):
    xorig = max(x - 0.2, 0)
    ax1.axhline(
        y=y, xmax=x, xmin=xorig, color='tab:green', alpha=0.4, linewidth=0.5
    )
    ax1.text(
        xorig,
        y_norm + 0.01,
        f'{y} datasets',
        transform=ax1.transAxes,
        verticalalignment='bottom',
        horizontalalignment='left',
        color='tab:green',
        fontsize=14,
    )

ax1.plot(
    x_dates,
    num_ds,
    marker='o',
    markeredgecolor='tab:green',
    markerfacecolor='white',
    color='white',
    ms=6,
    markeredgewidth=2.2,
    fillstyle='full',
    linestyle='None',
)

# Annotate total subjects
num_subj = np.arange(5000, metadata['NSubjects'].sum(), 5000)

x_subj_dates = np.interp(
    num_subj, df_plotting['cumsum_subjects'], normalized_dates
)
x2_dates = np.interp(num_subj, df_plotting['cumsum_subjects'], release_dates)
y2_lim = ax2.get_ylim()
y2_norm = (np.array(num_subj) - y2_lim[0]) / (y2_lim[1] - y2_lim[0])
for y, x, y_norm in zip(num_subj, x_subj_dates, y2_norm):
    xend = min(x + 0.2, 1.0)
    ax2.axhline(
        y=y, xmin=x, xmax=xend, color='tab:red', alpha=0.4, linewidth=0.5
    )
    ax2.text(
        xend,
        y_norm - 0.01,
        f'{y // 1000}k',
        transform=ax2.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        color='tab:red',
        fontsize=14,
    )

ax2.plot(
    np.interp(num_subj, df_plotting['cumsum_subjects'], release_dates),
    num_subj,
    marker='o',
    markeredgecolor='tab:red',
    markerfacecolor='white',
    color='white',
    ms=6,
    markeredgewidth=2.2,
    fillstyle='full',
    linestyle='None',
)

# Add Y-axis labels in the middle of the plot, linked by color
ax2.text(
    0.05,
    0.9,
    'Total number of datasets',
    verticalalignment='top',
    horizontalalignment='left',
    transform=ax2.transAxes,
    color='tab:green',
    fontsize=20,
)

ax2.text(
    0.95,
    0.05,
    'Total number of subjects',
    verticalalignment='bottom',
    horizontalalignment='right',
    transform=ax2.transAxes,
    color='tab:red',
    fontsize=20,
)

# Replace X-axis with a fancier timeline plot
years = (
    pd.to_datetime(
        [
            '2018-01-05',
            '2018-12-26',
            '2019-01-05',
            '2019-12-26',
            '2020-01-05',
            '2020-12-26',
            '2021-01-05',
            '2021-12-26',
            '2022-01-05',
            '2022-12-26',
            '2023-01-05',
            '2023-12-26',
            '2024-01-05',
            '2024-12-26',
        ]
    )
    .astype(int)
    .values
)
years_norm = (years - x_lim[0]) / (x_lim[1] - x_lim[0])
years_norm[0] = 0.0
years_norm[-1] = 1.0

for yr_start, yr_end in years_norm.reshape(-1, 2):
    ax1.axhline(
        y1_lim[0],
        xmin=yr_start,
        xmax=yr_end,
        clip_on=False,
        color='darkgray',
        linewidth=1,
    )

for yr in years[1:-1]:
    ax1.axvline(
        yr,
        ymin=0,
        ymax=0.02,
        clip_on=False,
        color='darkgray',
        linewidth=2,
    )

ax1.set_yticks([])
ax2.set_yticks([])

plt.tight_layout()
plt.savefig(os.path.join(figdir, 'combined_growth.png'))

