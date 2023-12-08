#! /bin/bash

#
# master script to call download scripts for individual datasets
#
# P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv
#source /home/sadc/csc/bin/activate

#downloading individual datasets
$ABSDIR/plot_chirps.sh
$ABSDIR/plot_era.sh
#$ABSDIR/plot_arc.sh
#$ABSDIR/plot_tamsat.sh
