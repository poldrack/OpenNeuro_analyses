all: terms match

terms:
	-rm ../data/cognitiveatlas/terms.json
	python cogat.py

test:
	python -m pytest cogat_test.py

match:
	-rm ../data/openneuro/cogatlas_matches.json
	python find_cogat_matches.py
