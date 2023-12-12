#!/bin/bash

################################
# script to download CHIRPS v2.0 p05 global data
#
# P.Wolski
# June 2023
#
###############################

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv

#defining directories
#rootdir defined in csisEnv
outdir=$rootdir/incoming/CHIRPS-v2.0-p05/global/day

#if script receives two arguments - set end date, otherwise end date is today
if [ $# == 2 ]; then
    enddate=$2
else
    enddate=$(date +"%Y%m%d")
fi

#if at leaset one argument - set start date, otherwise start date is 30 days ago
if [ $# -ge 1 ]; then
    startdate=$1
else
    #chirps gets updated with latency of 45 days??
    startdate=$(date +"%Y%m%d" -d "$enddate - 60 days")
fi

cdate=$startdate
echo $startdate $cdate $enddate

while [ "$cdate" != $enddate ]; do
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
    year=$(date +"%Y" -d "$cdate")
    month=$(date +"%m" -d "$cdate")
    day=$(date +"%d" -d "$cdate")
    echo
    echo $cdate

    #defining directories and url
    outfile=chirps-v2.0.${year}.${month}.${day}.tif.gz
    outtiffile=chirps-v2.0.${year}.${month}.${day}.tif
    remotedir=https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/$year/
    remotefile=$outfile

    dodownload=false
    #things are a bit complicated becase remote file is a .gz file and it needs to be unzipped localy
    if [ -f $outdir/$outfile ]; then
        echo $outdir/$outfile exists. checking file size...
        localfilesize=$(stat --format=%s $outdir/$outfile)
        echo localfilesize: $localfilesize 
        remotefilesize=`wget --no-check-certificate --spider $remotedir/$remotefile --spider --server-response -O - 2>&1 | sed -ne '/Content-Length/{s/.*: //;p}'`
        echo remotefilesize: $remotefilesize
        if [ $localfilesize -lt $remotefilesize ];then
            echo local file smaller. downloading again...
            dodownload=true
        else
            echo local file OK. skipping download...
        fi
    else
        echo checking if tif file exists
        if [ -f $outdir/$outtiffile ]; then
            echo $outdir/$outtiffile exists. no need to download again.
        else
            dodownload=true
        fi
    fi
    if $dodownload; then
        echo downloading...
        wget --no-check-certificate $remotedir/$remotefile -O $outdir/$outfile
        wgetresponse=$?
        echo response: $wgetresponse
        echo
        echo wget --no-check-certificate $remotedir/$remotefile -O $outdir/$outfile
        if [ $wgetresponse -gt 0 ]; then
            echo error downloading $outfile... 
            rm $outdir/$outfile
        else
            echo done. saved to: $outdir/$outfile
            echo unzipping...
            gunzip $outdir/$outfile
        fi
    fi
done
echo done

