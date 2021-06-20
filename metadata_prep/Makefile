all: clean get parse

clean:
	-rm ../data/openneuro/db_metadata.json

get:
	python get_metadata.py

parse:
	python parse_metadata.py

test:
	python -m pytest
