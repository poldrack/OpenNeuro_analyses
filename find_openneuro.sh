#!/bin/bash

cat "$1" | while read line; do
	file="$(echo "$line" | gsed 's/[^[:alnum:][:space:]]\+//g' | tr -s ' ' )"
	file_no_trailing_space="${file%% }.txt"
	file_no_outer_spaces="${file_no_trailing_space## }"
	ds_list="$(grep -ioP "*openneuro*" "papers_txt/$file_no_outer_spaces" | sort -uf )" 
	echo "$file_no_outer_spaces","$ds_list"
	
done