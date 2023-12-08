#!/bin/bash
rootdir=/home/sadc/data/products/RCC
outdir=$rootdir/incoming/CHIRPS-2.0/global/p05/day

startdate="19801231"
enddate=$(date +"%Y%m%d")

cdate=$startdate
echo $startdate $cdate $enddate

while [ "$cdate" != $enddate ]; do
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
    year=$(date +"%Y" -d "$cdate")
    month=$(date +"%m" -d "$cdate")
    day=$(date +"%d" -d "$cdate")
    echo
    echo $cdate

    outfile=chirps-v2.0.${year}.${month}.${day}.tif.gz
    outtiffile=chirps-v2.0.${year}.${month}.${day}.tif
    remotedir=https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/$year/
    remotefile=$outfile

    echo checking if tif file exists
    if [ -f $outdir/$outtiffile ]; then
        echo $outdir/$outtiffile exists. no need to download again.
    else
        echo unzipping...
        gunzip $outdir/$outfile
    fi
done

