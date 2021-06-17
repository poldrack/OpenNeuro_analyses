#!/bin/bash

cat no_match.txt | while read line; do 
	file="$(echo "$line"| gsed 's/[^[:alnum:][:space:]]\+//g' | tr -s ' ' )"
	file_no_trailing_space="${file%% }.pdf"
	file_no_outer_spaces="${file_no_trailing_space## }"
	open "papers/all_papers/$file_no_outer_spaces"
	echo "$line"
	read -p "If you need to re-download the paper, enter the url here. Otherwise, just hit 'return': " url </dev/tty
	if [ -n "$url" ]; then
		rm "papers/all_papers/$paper_name"
		curl "$url" -o "papers/all_papers/$paper_name"
	fi
done