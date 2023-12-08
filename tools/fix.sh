files=`ls incoming/ERA5/hr/tas_hr_ECMWF-ERA5_*.nc`
#tas_hr_ECMWF-ERA5_saf_20231107.nc
for file in $files; do

outfile=${file/_ECMWF-ERA5/_ERA5}

mv $file $outfile

done
