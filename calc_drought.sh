
#!/bin/bash
#
# script to call python script that derives product based on etccdi
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
    lstfile=$scriptdir/calc_drought.lst
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

    for item in ${indices[@]}; do
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

	indir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$var
	#directory where processed data will be stored. this should not change even if root dir changes
	outdir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$index$scale
	
	if [ ! -e $outdir ]; then
	    mkdir -p $outdir
	fi

        args="$dataset $domain $var $cdate $basetime $index $scale $attribute $climstartyear $climendyear $fracmissing $overwrite"
        echo
        echo "*********************************"
        echo calling calc_drought.py with $args


        echo python $scriptdir/calc_drought.py $indir $outdir $args
        python $scriptdir/calc_drought.py $indir $outdir $args
    done
    cdate=$(date +"%Y%m%d" -d "$cdate + 1 month")
    #exit
done

