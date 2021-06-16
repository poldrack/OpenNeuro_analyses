#!/bin/bash

cat reuses.txt | while read line; do
	file="$(echo "$line"| gsed 's/[^[:alnum:][:space:]]\+//g' | tr -s ' ' )"
	file_no_trailing_space="${file%% }.txt"
	file_no_outer_spaces="${file_no_trailing_space## }"
	cat "papers_txt/$file_no_outer_spaces" | grep -i doi
	while : ; do
		read -p "If you know the DOI, enter it here. Otherwise, just hit 'return' to open the pdf: " doi </dev/tty
		if [ -n "$doi" ]; then
			break
		else
			open "papers/all_papers/$(echo "$file_no_outer_spaces" | sed 's/\.txt/.pdf/g' )"
		fi
	done
	
	echo "$line 	$doi" >> reuse_dois.tsv
	
done
	