#! /bin/bash

set -f

infile=data/observed/CHIRPS-v2.0-p05-merged/day/sadc/pr/pr_day_CHIRPS-v2.0-p05-merged_sadc_*
outfile=pr_day_CHIRPS-v2.0-p05-merged_sadc_19810101-20231005.nc
python merge.py $infile $outfile
