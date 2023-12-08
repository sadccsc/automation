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

lstfile=$scriptdir/plot_all.lst

#reading members list (i.e. list of models to be processed. These are stored in members.txt file
echo reading plot.lst
parameters=()
while read -r line; do
    if [ ! ${line:0:1} == "#" ];then
        parameters+=($line)
    fi
done < $lstfile
echo read ${#parameters[@]} entries

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
    startdate=$(date +"%Y%m%d" -d "$enddate - 1 months")
fi

echo startdate: $startdate
echo enddate: $enddate

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
    echo dataset $dataset
    echo domain $domain
    echo basetime $basetime
    echo index $index
    echo attribute $attribute
    echo $climstartyear
    echo $climendyear
    echo 

    indir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index

    #current date, i.e. date being processed
    cdate=$startdate
    echo start date: $cdate 
    echo end date: $enddate

    #iterating through dates
    while [ "$cdate" -le $enddate ]; do
        year=$(date +"%Y" -d "$cdate")
        month=$(date +"%m" -d "$cdate")
        day=$(date +"%d" -d "$cdate")

	#date will be appended to this directory by the plotting script. that is because script has stride of 1 month, and pentads and dekads are plotted within that stride
        outdir=$rootdir/maps/$datatype/$dataset/$basetime/$domain/$index
        if [ ! -e $outdir ]; then
            mkdir -p $outdir
	fi
	echo
        echo
        echo "************************************************************"
        echo current date: $cdate

        args="$dataset $domain $cdate $basetime $index $attribute $climstartyear $climendyear $overwrite"
        echo
        echo "*********************************"

        cmd="python3 $scriptdir/plot_all.py $indir $outdir $args"
        echo calling:
        echo $cmd
        $cmd
        cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
    done
    #this one steps by month, because shorter baseline indices are all calculated for all periods for which data are available in a given month
    #exit
done

