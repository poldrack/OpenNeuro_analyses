#!/bin/bash

cat paper_list.tsv | while read line; do
	column_1="$(echo "$line" | awk -F'	' '{ print $1 }')"
	file="$(echo "$column_1"| gsed 's/[^[:alnum:][:space:]]\+//g' | tr -s ' ' )"
	file_no_trailing_space="${file%% }.txt"
	file_no_outer_spaces="${file_no_trailing_space## }"
	echo "$file_no_outer_spaces"
	echo
	if [ -f "papers_txt/$file_no_outer_spaces" ]; then
		ds_list="$(cat "papers_txt/$file_no_outer_spaces" | tr -d " \t\n\r" | grep -ioP "ds[0-9]{6}" | sort -uf )"
		if [[ -z "${ds_list// }" ]]; then
			echo "$column_1"	"no match" >> mappings.tsv
		else
			echo "$ds_list"
			echo
			for ds in $ds_list; do
				paper_authors="$(echo "$line" | awk -F'	' '{ print $2 }' )"
				dataset_authors="$(grep -i "$ds" openneuro_authors.tsv | awk -F'	' '{ print $2 }' )"
				echo "${ds}: "
				echo "paper authors: $paper_authors"
				echo "dataset authors: $dataset_authors"
				echo "---"
				grep -a5 "$ds" "papers_txt/$file_no_outer_spaces"
				while : ; do
					echo "Enter 'o' for original, 'r' for reuse, 'u' for unsure, or 'open' to open the file"
					read user_code </dev/tty
					case "$user_code" in
					'o') use='original'; break;;
					'r') use='reuse'; break;;
					'u') use='unsure'; break;;
					'open') open "papers/all_papers/$(echo "$file_no_outer_spaces" | sed 's/txt$/pdf/g')";;
					esac
				done
			
				echo "$column_1"	"$ds"	"$use" >> mappings.tsv
				clear
			done
		fi
	else
		echo "papers_txt/$file_no_outer_spaces does not exist"
	fi
	clear
done
