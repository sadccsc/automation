#! /bin/bash


today=$(date +"%Y%m%d") #here too, has to be the first of the month
./calc_etccdi.sh $today $today calc_etccdi_clim.lst

