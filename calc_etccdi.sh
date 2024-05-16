#!/bin/bash
#
# script to call python script that derives product based on etccdi
#
# P.Wolski
# June 2023
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
   echo calc_etccdi.sh lstfile.lst [startdate] [enddate] 
   exit
else
    lstfile=$1
    if [ ! -f $lstfile ]; then
        echo "ERROR. lst file $lstfile does not exist. Stopping execution..."
        exit
    fi 
fi

#if two or more arguments - set start date
if [ $# -ge 2 ]; then
    startdate=$2
else
    startdate=$(date +"%Y%m%d" -d "$enddate - 1 months")
fi

#if script receives three arguments - set end date
if [ $# == 3 ]; then
    enddate=$3
else
    enddate=$(date +"%Y%m%d")
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
    datatype=${item[1]} #observed, reanalysis
    domain=${item[2]} #sadc
    var=${item[3]} #pr
    basetime=${item[4]} #year,seas,mon,dek,pent,day
    index=${item[5]} #PRCPTOT onsetstatus onsetdate PRCPTOT
    attribute=${item[6]} #obs relanom percanom absanom clim
    climstartyear=${item[7]} #1991
    climendyear=${item[8]} #2010
    fracmissing=${item[9]} #0 o 0.1
    overwrite=${item[10]} #0 or 1

    #composing input directory
    indir=$rootdir/data/$datatype/$dataset/day/$domain/$var

    #climatology will be written into here, but it will be read from here if needed
    climdir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index
    #directory where processed data will be stored. this should not change even if root dir changes
    #some cheating there - in case clim or obs are requested, anomdir will be wrongly named, but then - it is not used when calculating these
    anomdir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index
    #this is the output directory
    indexdir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index

    #current date, i.e. date being processed
    cdate=$startdate

    #iterating through dates
    while [ "$cdate" -le $enddate ]; do
        year=$(date +"%Y" -d "$cdate")
        month=$(date +"%m" -d "$cdate")
        day=$(date +"%d" -d "$cdate")
        
        echo
        echo
        echo "************************************************************"
        echo dataset $dataset
        echo domain $domain
        echo basetime $basetime
        echo index $index
        echo attribute $attribute
        echo current date: $cdate
        echo "--------------------"

        # arguments to pass to the python script
        args="$dataset $domain $var $cdate $basetime $index $attribute $climstartyear $climendyear $fracmissing $overwrite"


        echo calling:
	echo python $scriptdir/calc_etccdi.py $indir $climdir $anomdir $indexdir $args
        echo "--------------------"
        python3 $scriptdir/calc_etccdi.py $indir $climdir $anomdir $indexdir $args
	#progressing dates
        cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
        #this one steps by month, because shorter baseline indices are all calculated for all periods for which data are available in a given month
    done
    echo
    echo
    #exit
done

