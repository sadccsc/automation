#!/bin/bash
#
# script to call python script to plot maps for individual products
#
# P.Wolski
# May 2024
#
echo "***********************************************************************************************************************"

#some housekeeping
ABSPATH=$(readlink -f $0)
scriptdir=$(dirname $ABSPATH)
source $scriptdir/csisEnv


#if script receives no arguments - stop execution
if [ $# == 0 ]; then
   echo ERROR. This script requires at least one argument - the name of the lst file. None provided. Stopping execution...
   echo Expected usage:
   echo plot.sh lstfile.lst [startdate] [enddate] 
   exit
else
    lstfile=$1
    if [ ! -f $lstfile ]; then
        echo "ERROR. lst file $lstfile does not exist. Stopping execution..."
        exit
    fi 
fi

#if script receives three arguments - set end date
if [ $# == 3 ]; then
    enddate=$3
else
    enddate=$(date +"%Y%m%d")
fi


#if two or more arguments - set start date
if [ $# -ge 2 ]; then
    startdate=$2
else
    startdate=$(date +"%Y%m%d" -d "$enddate - 1 months")
fi


echo listfile: $lstfile
echo startdate: $startdate
echo enddate: $enddate




#reading and parsing the listfile (i.e. list of entries to be processed)
echo reading $lstfile

parameters=()
while read -r line; do
    if [ ! ${line:0:1} == "#" ];then
        parameters+=($line)
    fi
done < $lstfile
echo read ${#parameters[@]} entries

for item in ${parameters[@]}; do
    item=(${item//,/ })
    dataset=${item[0]} #ARC2 TAMSAT-v3.1
    datatype=${item[1]} #sadc
    domain=${item[2]} #sadc
    basetime=${item[3]} #year,seas,mon,dek,pent,day
    index=${item[4]} #PRCPTOT onsetstatus onsetdate PRCPTOT
    attribute=${item[5]} #obs relanom percanom absanom clim
    climstartyear=${item[6]} #1991
    climendyear=${item[7]} #2010
    overwrite=${item[8]} #0 or 1

    #composing input directory
    indir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index

    #current date, i.e. date being processed
    cdate=$startdate

    #iterating through dates
    while [ "$cdate" -le $enddate ]; do
        year=$(date +"%Y" -d "$cdate")
        month=$(date +"%m" -d "$cdate")
        day=$(date +"%d" -d "$cdate")
        outdir=$rootdir/maps/$datatype/$dataset/$basetime/$domain/$index
	#date will be appended to this directory by the plotting script. that is because script has stride of 1 month, and pentads and dekads are plotted within that stride
        if [ ! -e $outdir ]; then
            mkdir -p $outdir
	fi
        echo
        echo "******************************************************************************************"
        echo dataset $dataset
        echo domain $domain
        echo basetime $basetime
        echo index $index
        echo attribute $attribute
        echo current date: $cdate
        echo "--------------------"
        # arguments to pass to the python script
        args="$dataset $domain $cdate $basetime $index $attribute $climstartyear $climendyear $overwrite"
	# entire python command to execute
        cmd="python3 $scriptdir/plot.py $indir $outdir $args"
        echo calling:
        echo $cmd
        echo "--------------------"
        $cmd
	#progressing date
        cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
        #this one steps by month, because shorter baseline indices are all calculated for all periods for which data are available in a given month
    done
    echo
    echo
done

