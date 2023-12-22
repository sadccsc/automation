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
$ABSDIR/calc_etccdi_arc.sh
$ABSDIR/calc_etccdi_tamsat.sh
$ABSDIR/calc_etccdi_chirps.sh
$ABSDIR/calc_etccdi_era.sh

