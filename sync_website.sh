#!/bin/bash

wbsgas=192.168.203.4

if [ $# -ne 0 ] ; then
  today=$1
else
  today=$(date +"%Y%m%d" -u)
fi
echo $today




echo
echo ---------------------------------------------------------------------------------------------
echo syncing seasonal
# in the one below - the pattern has to be *_seas_* because otherwise climatology which has _seas-clim_ gets sent to wrong place
rsync -avog  --exclude '*clim*' maps/observed/CHIRPS-v2.0-p05-merged/seas/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged$dset/seas/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal_climatology
rsync -avog --exclude '*clim*' maps/reanalysis/ERA5/seas/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog  maps/reanalysis/ERA5/seas/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal_climatology


echo
echo ---------------------------------------------------------------------------------------------
echo syncing monthly
rsync -avog --exclude '*clim*' maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly_climatology
#rsync -avog --exclude '*clim*'  maps/observed/ARC2/mon/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog --exclude '*clim*' maps/observed/TAMSAT-v3.1/mon/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog --exclude '*clim*' maps/reanalysis/ERA5/mon/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog maps/reanalysis/ERA5/mon/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly_climatology

echo syncing dekadal
rsync -avog --exclude '*clim*' maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal_climatology
#rsync -avog --exclude '*clim*' maps/observed/ARC2/mon/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog --exclude '*clim*' maps/observed/TAMSAT-v3.1/mon/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog --exclude '*clim*' maps/reanalysis/ERA5/dek/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog maps/reanalysis/ERA5/dek/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal_climatology

echo syncing pentadal
rsync -avog --exclude '*clim*' maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal_climatology
#rsync -avog --exclude '*clim*' maps/observed/ARC2/mon/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog --exclude '*clim*' maps/observed/TAMSAT-v3.1/mon/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog --exclude '*clim*' maps/reanalysis/ERA5/pent/sadc/*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog maps/reanalysis/ERA5/pent/sadc/*/*clim* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal_climatology
exit


