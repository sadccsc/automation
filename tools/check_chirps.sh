
echo "---------------------------------------------------------"
echo daily

for dset in CHIRPS-v2.0-p05-merged/global;do

    echo
    echo $dset
    if [ -e incoming/${dset} ]; then
        file=`ls -t incoming/${dset}/day/ |head -1`
        echo incoming: $file
    fi

    dset=(${dset/\// })
    dset=${dset[0]}

    file=`ls -t data/observed/${dset}/day/sadc/pr/ |head -1`
    echo daily data: $file

    for domain in sadc; do
        echo
        for basetime in mon seas dek pent; do
            echo
            for var in PRCPTOT CDD Rx1day; do
                file=`ls data/observed/${dset}/$basetime/$domain/$var/${var}_${basetime}_* |tail -1`
                echo $basetime $var: $file
               # file=`ls data/observed/${dset}/$basetime/$domain/$var/${var}-percnormanom_${basetime}_* |tail -1`
                #echo $basetime $var: $file
            done
        done
    done
done
