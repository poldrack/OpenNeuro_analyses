#!/bin/bash

for paper_name in papers/page*/*pdf; do
	output="$(file -b "$paper_name")"
	if [[ "$output" != *"PDF"* ]]; then
		echo "$paper_name"
		read -p "If you know the url of the paper, enter it here. Otherwise, just hit 'return': " url </dev/tty
		if [ -n "$url" ]; then
			curl "$url" -o "$paper_name"
			line="$(echo "$line" | awk -F',' 'BEGIN { OFS="," } $10="manual download"')"
		fi
	fi
done