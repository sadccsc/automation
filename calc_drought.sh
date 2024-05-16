
#!/bin/bash
#
# script to call python script that derives drought monitoring products
#
# P.Wolski
# June 2023
#
echo "***********************************************************************************************************************"

#finding path to this script
ABSPATH=$(readlink -f $0)
#this is when other scripts are in the same directory as this file, otherwise scriptdir will need to be defined here explicitly
scriptdir=$(dirname $ABSPATH)

source $scriptdir/csisEnv

#if script receives no arguments - stop execution
if [ $# == 0 ]; then
   echo ERROR. This script requires at least one argument - the name of the lst file. None provided. Stopping execution...
   echo Expected usage:
   echo calc_drought.sh lstfile.lst [startdate] [enddate] 
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

#reading members list (i.e. list of models to be processed. These are stored in members.txt file
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
    datatype=${item[1]} #ARC2 TAMSAT-v3.1
    domain=${item[2]} #sadc
    var=${item[3]} #PRCPTOT
    basetime=${item[4]} #mon
    index=${item[5]} #SPI
    scale=${item[6]} #1,3,6,12 etc months
    attribute=${item[7]} #index dur sev
    climstartyear=${item[8]} #1991
    climendyear=${item[9]} #2010
    fracmissing=${item[10]} #0 o 0.1
    overwrite=${item[11]} #0 or 1

    #composing intput directory
    indir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$var
    #directory where processed data will be stored. this should not change even if root dir changes
    outdir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index$scale
	
    if [ ! -e $outdir ]; then
	mkdir -p $outdir
    fi

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


        args="$dataset $domain $var $cdate $basetime $index $scale $attribute $climstartyear $climendyear $fracmissing $overwrite"
        echo calling:
        echo python $scriptdir/calc_drought.py $indir $outdir $args
        echo "--------------------"
        python3 $scriptdir/calc_drought.py $indir $outdir $args
    done
    #progressing dates
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
    #exit
done

