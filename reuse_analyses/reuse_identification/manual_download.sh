#!/bin/bash

for d in papers/page*; do
  if [ ! -f "$d/result_new.csv" ]; then
	  tail -n +0 $d/result.csv | while read line; do
	    if [ "$(echo "$line" | cut -d, -f10)" == "False" ]; then
	      echo "$line"
	      read -p "If you know the url of the paper, enter it here. Otherwise, just hit 'return': " url </dev/tty
	      if [ -n "$url" ]; then
	        paper_name="$(echo "$line" | cut -d, -f1)".pdf
	        curl "$url" -o $d/"$paper_name"
#			read -p "If you know the DOI, enter it here. Otherwise, just hit 'return': " doi </dev/tty
#	        line="$(echo "$line" | awk -F',' 'BEGIN { OFS="," } $10="manual download", $3="'$doi'"')"
	        line="$(echo "$line" | awk -F',' 'BEGIN { OFS="," } $10="manual download"')"

	      fi
	    fi
	  echo "$line" >> $d/result_new.csv
      done
  fi
done
