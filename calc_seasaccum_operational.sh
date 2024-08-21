#! /bin/bash

#
# master script to call processing scripts
#
# P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv

$ABSDIR/calc_seasaccum.sh calc_seasaccum_operational.lst

