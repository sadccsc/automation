
echo "---------------------------------------------------------"
echo daily

for dset in ARC2/africa  CHIRPS-v2.0-p05/global  CHIRPS-v2.0-p05-prelim/global CHIRPS-v2.0-p05-merged/global TAMSAT-v3.1/africa ;do
:
echo
echo $dset
if [ -e incoming/${dset} ]; then
    file=`ls -t incoming/${dset}/day/ |head -1`
    echo incoming:
    echo `ls -lst incoming/${dset}/day/$file`
fi

dset=(${dset/\// })
dset=${dset[0]}

file=`ls -lst data/observed/${dset}/day/sadc/pr/ |head -1`
echo daily data: $file

done

