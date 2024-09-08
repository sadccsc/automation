#! /bin/bash

#
# master script to call processing scripts for individual datasets
#
# P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv

#processing onset listfile. It's only one file, because there are relatively few onset indices, so all datasets can be processed at the same time
$ABSDIR/calc_heatwave.sh calc_heatwave_operational.lst

