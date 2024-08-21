#! /bin/bash

#
# master script to call preprocessing scripts for individual datasets
# preprocess scripts organize incoming data into consistent format
# this involves changing, if necessary, file format to netcdf, file name, variable names and dimension names
#
# by P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv


#harmonizing individual datasets

$ABSDIR/harmonize_arc.sh
$ABSDIR/harmonize_tamsat.sh
$ABSDIR/harmonize_chirps.sh
$ABSDIR/harmonize_chirps-prelim.sh
$ABSDIR/harmonize_chirps-merged.sh
$ABSDIR/harmonize_era.sh

