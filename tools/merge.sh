#! /bin/bash

set -f

infile=../data/observed/CHIRPS-v2.0-p05-merged/mon/sadc/PRCPTOT/PRCPTOT_mon_CHIRPS-v2.0-p05-merged_sadc_*
outfile=pr_mon_CHIRPS-v2.0-p05-merged_sadc_19810101-20231231.nc
python merge.py $infile $outfile
