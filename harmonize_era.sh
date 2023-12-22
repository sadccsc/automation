#!/bin/bash
#
# script to call python script that pre-processes ERA data
#
# P.Wolski
# June 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
scriptdir=$(dirname $ABSPATH)
source $scriptdir/csisEnv

var1=tasmin
var2=tasmax
#defining directories
#rootdir defined in csisEnv
#directory with incoming data, this should not change even in root dir changes
indir=$rootdir/incoming/ERA5/hr
#directory where processed data will be stored. this should not change even if root dir changes
outdir=$rootdir/data/reanalysis/ERA5/day

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
    startdate=$(date +"%Y%m%d" -d "$enddate - 30 days")
fi

#current date, i.e. date being processed
cdate=$startdate

#iterating through dates
while [ "$cdate" -le $enddate ]; do
    year1=$(date +"%Y" -d "$cdate")
    month1=$(date +"%m" -d "$cdate")
    day1=$(date +"%d" -d "$cdate")
    year2=$(date +"%Y" -d "$cdate + 1 day")
    month2=$(date +"%m" -d "$cdate + 1 day")
    day2=$(date +"%d" -d "$cdate + 1 day")
    echo
    echo processing $cdate

    #source file
    infile1=tas_hr_ERA5_saf_${year1}${month1}${day1}.nc
    infile2=tas_hr_ERA5_saf_${year2}${month2}${day2}.nc

    #checking if source file exists
    if [ -f $indir/${infile1} ] && [ -f $indir/${infile2} ]; then
        echo found input files $indir/${infile1} and $indir/${infile2}
        #if exists - iterating through domains
        #chirps global covers seychelles, but does not generate data for them. so only three domains
        for domain in sadc; do

            #just in case directory does not exist
            if [ ! -e $outdir/$domain/$var1 ]; then
                mkdir -p $outdir/$domain/$var1
            fi
            if [ ! -e $outdir/$domain/$var2 ]; then
                mkdir -p $outdir/$domain/$var2
            fi
            echo processing domain: $domain
            #outfile name
            outfile1=tasmin_day_ERA5_${domain}_${year1}${month1}${day1}.nc
            outfile2=tasmax_day_ERA5_${domain}_${year1}${month1}${day1}.nc

            #checking if outfile exists
            if [ -f $outdir/$domain/$var1/$outfile1 ]; then
                echo $outdir/$domain/$var1/$outfile1 exists. skipping...
            else
                #processing if does not exist
                echo output file $outdir/$domain/$var1/$outfile1 does not exist. processing...

                cmd="python3 $scriptdir/harmonize_era.py $indir/$infile1 $indir/$infile2 $outdir/$domain/$var1/$outfile1 $outdir/$domain/$var2/$outfile2 $cdate $domain"
                echo executing: 
                echo $cmd
                $cmd
                echo done
                #exit
            fi
        done
    else
        echo input file $indir/${infile1} missing. skipping...
    fi
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
done
echo done
