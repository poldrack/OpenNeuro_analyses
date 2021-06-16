for i in {47..47}; do 
  dl_dir="/Users/jbwexler/cs/poldracklab/openneuro_scholar/papers/page-${i}"
  mkdir "$dl_dir"
  python -m PyPaperBot --query="openneuro" --scholar-pages=${i}-${i} --dwn-dir="$dl_dir"
done
