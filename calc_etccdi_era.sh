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
#this activates python environment
source /home/sadc/csc/bin/activate

#if script receives two arguments - set end date
if [ $# -ge 2 ]; then
    enddate=$2
else
    enddate=$(date +"%Y%m%d")
fi

#if at leaset one argument - set start date
if [ $# -ge 1 ]; then
    startdate=$1
else
    # this is done for seasonal, monthly, dekadal and pentadal products
    # 2 months back time is needed to retro update chirps
    startdate=$(date +"%Y%m%d" -d "$enddate - 1 months")
fi

if [ $# == 3 ]; then
    lstfile=$scriptdir/$3
else
    lstfile=$scriptdir/calc_etccdi_era.lst
fi




#reading members list (i.e. list of models to be processed. These are stored in members.txt file
echo reading $lstfile
indices=()
while read -r line; do
    if [ ! ${line:0:1} == "#" ];then
        indices+=($line)
    fi
done < $lstfile
echo read ${#indices[@]} entries


echo startdate: $startdate
echo enddate: $enddate


for item in ${indices[@]}; do
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
    echo dataset $dataset
    echo datatype $datatype
    echo domain $domain
    echo var $var
    echo basetime $basetime
    echo index $index
    echo attribute $attribute
    echo $climstartyear
    echo $climendyear
    echo fracmissing $fracmissing
    echo overwrite $overwrite
    echo 

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
    echo start date: $cdate 
    echo end date: $enddate



    #iterating through dates
    while [ "$cdate" -le $enddate ]; do
        year=$(date +"%Y" -d "$cdate")
        month=$(date +"%m" -d "$cdate")
        day=$(date +"%d" -d "$cdate")
        
        echo
        echo
        echo "************************************************************"
        echo current date: $cdate

        args="$dataset $domain $var $cdate $basetime $index $attribute $climstartyear $climendyear $fracmissing $overwrite"
        echo
        echo "*********************************"
        echo calling calc_etccdi.py with $args


        echo python $scriptdir/calc_etccdi.py $indir $climdir $anomdir $indexdir $args
        python $scriptdir/calc_etccdi.py $indir $climdir $anomdir $indexdir $args
        cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
    done
    #this one steps by month, because shorter baseline indices are all calculated for all periods for which data are available in a given month
    #exit
done

