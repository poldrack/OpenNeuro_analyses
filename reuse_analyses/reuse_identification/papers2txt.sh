#!/bin/bash

for f in papers/*/*pdf; do 
  pdf2txt.py "$f" > papers_txt/"$(basename "$f")".txt
done
