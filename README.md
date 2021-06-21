## Analyses of OpenNeuro metadata

This repo contains analyses of metadata from the [OpenNeuro](http://openneuro.org) data archive, prepared for a paper describing the project (to be linked here once submitted)..


### Requirements:

To run the code you need the following:

- [Datalad](https://www.datalad.org/)
- [mongodb](https://www.mongodb.com) server installed and running with a database called `openneuro` containing an empty collection called `datasets`
- [Cognitive Atlas python package](https://github.com/CognitiveAtlas/cogat-python)


Code has only been tested using Python 3.8.

### Preparing the metadata

Running `make all` within the `metadata_prep` directory will:
- download metadata from openneuro database API
  - you will first need to generate an API key from your openneuro account and save it to `metadata_prep/api_key.txt`
  - results are saved to data/openneuro/db_metadata.json
- parse the metadata to identify NIH/NSF grants mentioned in metadata
  - results are printed to stdout

Running `make all` within the `dataset_analyses` directory will:
- download the metdata for all datasets using datalad
  - This will require > 20 GB of available disk space
  - note: some datasets are currently empty, working to fix this
- Extract dataset and task info
  - dataset info saved to data/openneuro/ds_info.csv
  - task info saved to data/openneuro/task_info.csv

Running `make all` within the `metadata_analyses` directory will:
- load all terms from the cognitiveatlas api
- find all matches in the readme/title text associated with each dataset:
- results saved to data/openneuro/cogatlas_matches.json

### Analysis notebooks

The main analyses are implemented in a set of Jupyter notebooks.

- *`metadata_analyses/DatabaseAndPublicationAnalyses.ipynb`* implements a set of analyses of the datasets, and generates a set of figures included in the preprint.
- *`metadata_analyses/UsageFigures.ipynb`* generates some additional figures on database usage.
- *`reuse_analyses/reuse_analysis.ipynb`* implements analyses of published reuses (based on data in `data/reuse/reuse_mappings.csv` and `data/reuse/reuse_papers.csv` generated using the scripts found in `reuse_anlayses/reuse_identification`)

