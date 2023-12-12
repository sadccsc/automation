#!/bin/bash
#
# script to call python script that pre-processes CHIRPS data
#
# P.Wolski
# June 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
scriptdir=$(dirname $ABSPATH)
source $scriptdir/csisEnv

var=pr
#rootdir devined in csisEnv
#directory with incoming data, this should not change even in root dir changes
prelimdir=$rootdir/data/observed/CHIRPS-v2.0-p05-prelim/day/
chirpsdir=$rootdir/data/observed/CHIRPS-v2.0-p05/day/
#directory where processed data will be stored. this should not change even if root dir changes
mergeddir=$rootdir/data/observed/CHIRPS-v2.0-p05-merged/day/

#this is relatie to prelim and chirps dir
prelimdirlink=../../../../CHIRPS-v2.0-p05-prelim/day
chirpsdirlink=../../../../CHIRPS-v2.0-p05/day

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
    # has to be back to 60 days because it merges chirps with chirps-prelim, and chirps gets updated with the latency of 45 days
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
    for domain in sadc ; do
        chirpsfile=pr_day_CHIRPS-v2.0-p05_${domain}_${year}${month}${day}.nc
        prelimfile=pr_day_CHIRPS-v2.0-p05-prelim_${domain}_${year}${month}${day}.nc
        mergedfile=pr_day_CHIRPS-v2.0-p05-merged_${domain}_${year}${month}${day}.nc

        #checking if source file exists
        if [ -f $chirpsdir/${domain}/$var/${chirpsfile} ]; then
            echo found final file $chirpsdir/${domain}/$var/${chirpsfile}
            #checking if outputdirectory exists
            [[ ! -e $mergeddir/$domain/$var ]] && mkdir -p $mergeddir/$domain/$var

            echo checking symlink in mergeddir 
            if [ -L $mergeddir/${domain}/$var/${mergedfile} ]; then
                target=`readlink -s $mergeddir/${domain}/$var/${mergedfile}`
                echo target: $target
                if [ $target == $prelimdirlink/${domain}/$var/${prelimfile} ]; then
                    echo "overwriting link to prelim file"
                    `ln -sf $chirpsdirlink/${domain}/$var/${chirpsfile} $mergeddir/${domain}/$var/${mergedfile}`
                    else
                    echo link already exists. skipping...
                fi
            else
                echo "link does not exsit. creating link to final file"
                #`ln -sf $chirpsdir/${domain}/$var/${chirpsfile} $mergeddir/${domain}/$var/${mergedfile}`
                `ln -sf $chirpsdirlink/${domain}/$var/${chirpsfile} $mergeddir/${domain}/$var/${mergedfile}`
            fi
        elif [ -f $prelimdir/${domain}/$var/${prelimfile} ]; then
            echo found prelim file $prelimdir/${domain}/$var/${prelimfile}
            #checking if outputdirectory exists
            [[ ! -e $mergeddir/$domain/$var ]] && mkdir -p $mergeddir/$domain/$var

            echo checking symlink in mergeddir 
            if [ -L $mergeddir/${domain}/$var/${mergedfile} ]; then
                target=`readlink -s $mergeddir/${domain}/$var/${mergedfile}`
                echo target: $target
                if [ $target == $chirpsdirlink/${domain}/$var/${chirpsfile} ]; then
                    echo "link is to final file, so not overwriting..."
                 elif [ $target == $prelimdirlink/${domain}/$var/${prelimfile} ]; then
                    echo "link is to prelim file, so not overwriting..."
                fi
            else
                echo "link does not exsit. creating link to prelim file"
                #`ln -sf $prelimdir/${domain}/$var/${prelimfile} $mergeddir/${domain}/$var/${mergedfile}`
                `ln -sf $prelimdirlink/${domain}/$var/${prelimfile} $mergeddir/${domain}/$var/${mergedfile}`
            fi
        else
            echo neither $chirpsdir/${domain}/$var/${chirpsfile}
            echo nor $prelimdir/${domain}/$var/${prelimfile}
            echo exist. skipping...
        fi
    done

    cdate=$(date +"%Y%m%d" -d "$cdate + 1 day")
done
