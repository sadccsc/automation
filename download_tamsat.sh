#!/bin/bash

################################
# script to download Tamsat data
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
outdir=$rootdir/incoming/TAMSAT-v3.1/africa/day

#if script receives two arguments - set end date
if [ $# == 2 ]; then
    enddate=$2
else
    enddate=$(date +"%Y%m%d")
fi

#if at leaset one argument - set start date
if [ $# -ge 1 ]; then
    startdate=$1
else
    startdate=$(date +"%Y%m%d" -d "$enddate - 10 days")
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

    outfile=rfe${year}_${month}_${day}.v3.1.nc
    #http://www.tamsat.org.uk/public_data/data/v3.1/daily/2014/11/rfe2014_11_30.v3.1.nc
    #remotedir=http://www.tamsat.org.uk/public_data/data/v3.1/daily/$year/$month
    remotedir=https://gws-access.jasmin.ac.uk/public/tamsat/rfe/data/v3.1/daily/$year/$month
    remotefile=$outfile

    dodownload=false

    if [ -f $outdir/$outfile ]; then
        echo $outdir/$outfile exists. checking file size...
        localfilesize=$(stat --format=%s $outdir/$outfile)
        echo localfilesize: $localfilesize 
        remotefilesize=`wget --no-check-certificate --spider $remotedir/$remotefile --spider --server-response -O - 2>&1 | sed -ne '/Content-Length/{s/.*: //;p}'`
        wgetresponse=$?
        echo remotefilesize: $remotefilesize
        if [ $localfilesize -lt $remotefilesize ];then
            echo local file smaller. downloading again...
            dodownload=true
        else
            echo local file OK. skipping download...
        fi
    else
        dodownload=true
    fi
    if $dodownload; then
        echo downloading...
        wget --no-check-certificate $remotedir/$remotefile -O $outdir/$outfile
        wgetresponse=$?
        echo response: $wgetresponse
        echo
        echo wget --no-check-certificate https://gws-access.jasmin.ac.uk/public/tamsat/rfe/data/v3.1/daily/$year/$month/$outfile -O $outdir/$outfile
        if [ $wgetresponse -gt 0 ]; then
            echo error downloading $outfile... 
            rm $outdir/$outfile
        else
            echo done. saved to: $outdir/$outfile
        fi
    fi
done

