#!/bin/bash
#
# script to call python script that pre-processes ARC data
#
# P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
scriptdir=$(dirname $ABSPATH)
source $scriptdir/csisEnv


var=pr
#defining directories
#rootdir defined in csisEnv
#directory with incoming data, this should not change even in root dir changes
indir=$rootdir/incoming/TAMSAT-v3.1/africa/day
#directory where processed data will be stored. this should not change even if root dir changes
outdir=$rootdir/data/observed/TAMSAT-v3.1/day
#directory to store temporary data
tempdir=./tmp

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
    startdate=$(date +"%Y%m%d" -d "$enddate - 60 days")
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
    infile=rfe${year}_${month}_${day}.v3.1.nc

    #checking if source file exists
    if [ -f $indir/${infile} ]; then
        echo found input file $indir/${infile}
        #if exists - iterating through domains, Tamsat does cover neiter Mauritius nor Seychelles, so only SADC and Comorow are possible.
        #processing SADC only
        for domain in sadc; do
            echo processing domain: $domain

            #just in case directory does not exist
            if [ ! -e $outdir/$domain/$var ]; then
                mkdir -p $outdir/$domain/$var
            fi

            #outfile name
            outfile=pr_day_TAMSAT-v3.1_${domain}_${year}${month}${day}.nc

            #checking if outfile exists
            if [ -f $outdir/$domain/$var/$outfile ]; then
                echo $outdir/$domain/$var/$outfile exists. skipping...
            else
                #processing if does not exist
                echo output file $outdir/$domain/$var/$outfile does not exist. processing...

                cmd="python3 $scriptdir/harmonize_tamsat.py $indir/$infile $outdir/$domain/$var/$outfile $cdate $domain"
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
