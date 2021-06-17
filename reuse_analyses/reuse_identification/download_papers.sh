for i in {47..47}; do 
  dl_dir="papers/page-${i}"
  mkdir "$dl_dir"
  python -m PyPaperBot --query="openneuro" --scholar-pages=${i}-${i} --dwn-dir="$dl_dir"
done
