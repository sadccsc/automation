dataset=CHIRPS-v2.0-p05-merged
datatype=observed
basetime=mon
domain=sadc
var=PRCPTOT
index=mean
coarsen=5

rootdir="./"

#if script receives no arguments - stop execution
if [ $# == 0 ]; then
   echo ERROR. This script requires at least one argument - the name of the lst file. None provided. Stopping execution...
   echo Expected usage:
   echo compile_essential.sh lstfile.lst 
   exit
else
    lstfile=$1
    if [ ! -f $lstfile ]; then
        echo "ERROR. lst file $lstfile does not exist. Stopping execution..."
        exit
    fi 
fi


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
    coarsen=${item[5]} #e.g. 5

    indir=$rootdir/data/$datatype/$dataset/$basetime/$domain/$var
    outputdir=./data/essential/
   
    python compile_essential.py $indir $outputdir $datatype $dataset $domain $var $basetime $coarsen
done

