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

#downloading individual datasets
$ABSDIR/plot.sh plot_chirps.lst
$ABSDIR/plot.sh plot_era.lst
#$ABSDIR/plot_arc.sh
#$ABSDIR/plot_tamsat.sh
