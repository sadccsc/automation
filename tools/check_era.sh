
echo "---------------------------------------------------------"
echo daily

for dset in ERA5 ;do
:
    echo
    echo $dset
    if [ -e incoming/${dset} ]; then
        file=`ls -t incoming/${dset}/hr/ |head -1`
        echo incoming: $file
    fi

    dset=(${dset/\// })
    dset=${dset[0]}

    file=`ls -t data/reanalysis/${dset}/day/sadc/tasmin/ |head -1`
    echo daily data tasmin: $file

    file=`ls -t data/reanalysis/${dset}/day/sadc/tasmax/ |head -1`
    echo daily data tasmax: $file

    for basetime in mon dek pent; do
        for adir in `ls data/reanalysis/${dset}/$basetime/sadc/`;do
            var=`basename $adir`
            file=`ls -t data/reanalysis/${dset}/$basetime/sadc/$var/${var}_${basetime}_* |head -1`
            echo $basetime data $var: $file
            file=`ls -t data/reanalysis/${dset}/$basetime/sadc/$var/${var}-absanom_${basetime}_* |head -1`
            echo $basetime data $var: $file
        done
    done
done

