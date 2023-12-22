#!/bin/bash

################################
# script to download ARC2 data
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
outdir=$rootdir/incoming/ARC2/africa/day

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
    startdate=$(date +"%Y%m%d" -d "$enddate - 10 days")
fi


cdate=$startdate
echo $startdate $cdate $enddate

while [ "$cdate" -le  $enddate ]; do
    year=$(date +"%Y" -d "$cdate")
    month=$(date +"%m" -d "$cdate")
    day=$(date +"%d" -d "$cdate")
    echo
    echo $cdate

    #defining directories and url

    #https://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/geotiff/africa_arc.19830101.tif.zip
    remotedir=https://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/geotiff
    outfile=africa_arc.${year}${month}${day}.tif.zip
    outtiffile=africa_arc.${year}${month}${day}.tif
    remotefile=$outfile

    dodownload=false
    #things are a bit complicated becase remote file is a .zip file and it needs to be unzipped localy
    echo checking if tif file exists
    if [ -f $outdir/$outtiffile ]; then
        echo $outdir/$outtiffile exists. no need to download again.

    elif [ -f $outdir/$outfile ]; then
        echo $outdir/$outfile exists. checking file size...
        localfilesize=$(stat --format=%s $outdir/$outfile)
        echo localfilesize: $localfilesize 
        remotefilesize=`wget --no-check-certificate --spider $remotedir/$remotefile --spider --server-response -O - 2>&1 | sed -ne '/Content-Length/{s/.*: //;p}'`
        echo remotefilesize: $remotefilesize
        if [ $localfilesize -lt $remotefilesize ];then
            echo local file smaller. downloading again...
            dodownload=true
        else
            echo local file OK. skipping download, just unzipping
            unzip -d $outdir $outdir/$outfile
        fi
    else
        dodownload=true
    fi

    #this is where downloading happens
    if $dodownload; then
        echo downloading now...
	echo to $outdir/$outfile
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
            unzip -d $outdir $outdir/$outfile
            chgrp csis $outdir/$outfile
        fi
    fi
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
done
echo done

