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
$ABSDIR/download_arc.sh
$ABSDIR/download_tamsat.sh
$ABSDIR/download_chirps.sh
$ABSDIR/download_chirps-prelim.sh
$ABSDIR/download_era.sh

