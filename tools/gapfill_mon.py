import xarray as xr
import os, sys
import pandas as pd


year=1990
month=2
var="PRCPTOT"


climfile="data/observed/ARC2/mon/sadc/PRCPTOT/PRCPTOT_mon-clim_ARC2_sadc_1991-2020.nc"

outputfile="data/observed/ARC2/mon/sadc/PRCPTOT/PRCPTOT_mon_ARC2_sadc_{}{}.nc".format(year,str(month).zfill(2))

if not os.path.exists(climfile):
    print("{} not exist".format(climfile))
    sys.exit()

if os.path.exists(outputfile):
    print("{} exists".format(outputfile))
else:
    print("does not exist {}".format(outputfile))

    ds=xr.open_dataset(climfile)
    da=ds[var].sel(month=month)
    time=pd.to_datetime("{}-{}-01".format(year, str(month).zfill(2)))+pd.offsets.MonthEnd()
    da=da.expand_dims({"time":[time]})
    da=da.drop("month")
    print(da) 
    ds=da.to_dataset(name=var)
    ds.to_netcdf(outputfile)
