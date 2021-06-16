#!/bin/bash

for f in *txt; do 
  echo "$f"
  cat "$f" | grep -P -a5 "\bds[0-9]{6}\b"
  echo "Enter 'o' for original, 'r' for reuse, or 'd' for don't know"
  read user_code
  echo "$f"	"$user_code" >> user_codes.tsv
  echo "---------------------------"
  echo
done
