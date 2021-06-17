#!/bin/bash

for f in papers/page*/result_new.csv; do
	tail -n +2 "$f" >> papers/all_result.csv
done