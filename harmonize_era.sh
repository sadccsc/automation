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
var3=tas
#defining directories
#rootdir defined in csisEnv
#directory with incoming data, this should not change even in root dir changes
indir=$rootdir/incoming/ERA5/africa/hr
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
    year=$(date +"%Y" -d "$cdate")
    month=$(date +"%m" -d "$cdate")
    day=$(date +"%d" -d "$cdate")
    echo
    echo processing $cdate

    #source file
    infile=tas_hr_ERA5_saf_${year}${month}${day}.nc

    #checking if source file exists
    if [ -f $indir/${infile} ] ; then
        echo found input files $indir/${infile}
        #if exists - iterating through domains
        for domain in sadc; do

            #just in case directory does not exist
            if [ ! -e $outdir/$domain/$var1 ]; then
                mkdir -p $outdir/$domain/$var1
            fi
            if [ ! -e $outdir/$domain/$var2 ]; then
                mkdir -p $outdir/$domain/$var2
            fi
            if [ ! -e $outdir/$domain/$var3 ]; then
                mkdir -p $outdir/$domain/$var3
            fi
            echo processing domain: $domain
            #outfile name
            outfile1=tasmin_day_ERA5_${domain}_${year}${month}${day}.nc
            outfile2=tasmax_day_ERA5_${domain}_${year}${month}${day}.nc
            outfile3=tas_day_ERA5_${domain}_${year}${month}${day}.nc

            #checking if outfile exists
            if [ -f $outdir/$domain/$var3/$outfile3 ]; then
                echo $outdir/$domain/$var3/$outfile3 exists. skipping...
            else
                #processing if does not exist
                echo output file $outdir/$domain/$var3/$outfile3 does not exist. calling python script...

                cmd="python3 $scriptdir/harmonize_era.py $indir/$infile $outdir/$domain/$var1/$outfile1 $outdir/$domain/$var2/$outfile2 $outdir/$domain/$var3/$outfile3 $cdate $domain"
                echo executing: 
                echo $cmd
                $cmd
                echo done
                #exit
            fi
        done
    else
        echo input file $indir/${infile} missing. skipping...
    fi
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
done
echo done
