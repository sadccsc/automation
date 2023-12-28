#!/bin/bash

wbsgas=192.168.203.4

if [ $# -ne 0 ] ; then
  today=$1
else
  today=$(date +"%Y%m%d" -u)
fi
echo $today

#sync seasonal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/seas/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/seas/sadc/R*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/seas/sadc/C*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog maps/reanalysis/ERA5/seas/sadc/T*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal
rsync -avog maps/reanalysis/ERA5/seas/sadc/h*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/seasonal

# sync monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/R*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/SDII/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/C*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/spi*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/onset*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/mon/sadc/seasaccum/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog  maps/observed/ARC2/mon/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog  maps/observed/TAMSAT-v3.1/mon/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog maps/reanalysis/ERA5/mon/sadc/T*/*_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
#rsync -avog --size-only maps/reanalysis/ERA5/mon/sadc/T*/*_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly
rsync -avog  maps/reanalysis/ERA5/mon/sadc/hw*/*_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/monthly


# sync dekadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/R*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/SDII/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/dek/sadc/C*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
#rsync -avog  maps/observed/ARC2/dek/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
#rsync -avog  maps/observed/TAMSAT-v3.1/dek/sadc/PRCPTOT/PRCPTOT_* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal

rsync -avog  maps/reanalysis/ERA5/dek/sadc/T*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal
rsync -avog  maps/reanalysis/ERA5/dek/sadc/hw*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/dekadal

# sync pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/PRCPTOT/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/R*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/SDII/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/C*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/onset*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/observed/CHIRPS-v2.0-p05-merged/pent/sadc/seasaccum/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/reanalysis/ERA5/pent/sadc/T*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
rsync -avog  maps/reanalysis/ERA5/pent/sadc/hw*/* ftpdatapush@${wbsgas}:/var/www/html/media/data/rccsadc/csc/pentadal
