# HAM10000 data (local only)

Place your **HAM10000** extract here; this directory is **gitignored** because image archives are large.

Expected layout:

```
archive/
  HAM10000_metadata.csv
  HAM10000_images_part_1/*.jpg
  HAM10000_images_part_2/*.jpg
```

Obtain the dataset from the official source / challenge website (respect license terms). Training scripts assume `--data-root ../archive` from `models/`.
