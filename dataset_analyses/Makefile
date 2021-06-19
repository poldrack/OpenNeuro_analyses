all: get process analyze

clean:
	-rm ../data/openneuro/ds_info.csv
	-rm ../data/openneuro/metadata.pkl

get:
	python get_datasets.py

process:
	python process_datasets.py

analyze:
	python analyze_datasets.py


