#/bin/bash -l

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
outdir=$rootdir/incoming/ERA5/hr/

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

    outfile=tas_hr_ERA5_saf_${year}${month}${day}.nc

    dodownload=false
    #things are a bit complicated becase remote file is a .zip file and it needs to be unzipped localy
    echo checking if nc file exists
    if [ -f $outdir/$outfile ]; then
        echo $outdir/$outfile exists. checking file size...
        localfilesize=$(stat --format=%s $outdir/$outfile)
        echo localfilesize: $localfilesize 
        if [ $localfilesize -gt 0 ];then
            echo local file small. downloading again...
            dodownload=true
        else
            echo local file OK. skipping download
        fi
    else
        dodownload=true
    fi

    #this is where downloading happens
    if $dodownload; then
        echo downloading...
        python3 download_era.py tas $year $month $day hour sadc $outdir/$outfile
    fi
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
done
echo done

