#! /bin/bash

#
# master script to call etccdi calculation scripts
#
# P.Wolski
# March 2023
#

#some housekeeping
ABSPATH=$(readlink -f $0)
ABSDIR=$(dirname $ABSPATH)
source $ABSDIR/csisEnv

#calculating etccdi
$ABSDIR/calc_etccdi.sh calc_etccdi_operational.lst

