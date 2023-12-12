#!/usr/bin/env python
"""
download ERA5 air temperature data from the Copernicus Data Store

usage: python download_ecmwf.py variable year month basetime model domain rootdir

"""

import cdsapi, os, sys, json
import xarray as xr

#checking if arguments are OK
if len(sys.argv) !=8:

    print(__doc__)

    sys.exit()


c = cdsapi.Client()

#setting up
varname=sys.argv[1]
year=sys.argv[2]
month=int(sys.argv[3])
day=int(sys.argv[4])
basetime=sys.argv[5]
domainname=sys.argv[6]
outfile=sys.argv[7]

cds_dataset="reanalysis-era5-single-levels"
fileformat="netcdf"
if varname=="tas":
    cds_variable_name="2m_temperature"

if domainname=="sadc":
    domain="10/10/-40/60"
times=["00:00",
       "01:00",
       "02:00",
       "03:00",
       "04:00",
       "05:00",
       "06:00",
       "07:00",
       "08:00",
       "09:00",
       "10:00",
       "11:00",
       "12:00",
       "13:00",
       "14:00",
       "15:00",
       "16:00",
       "17:00",
       "18:00",
       "19:00",
       "20:00",
       "21:00",
       "22:00",
       "23:00"]

requestDict={
    'product_type':"reanalysis",
    'variable':cds_variable_name,
    'year':str(year),
    'month':str(month),
    'day':str(day),
    'area': domain,
    'time': times,
    'format':fileformat
}

print(requestDict)


if os.path.exists(outfile)==False:
    print (outfile, "does not exist. Downloading...")

    #sys.exit()
    print ("retriving", outfile)
    c.retrieve(
        cds_dataset,
        requestDict,
        outfile
    )


    print("checking time steps")
    ds=xr.open_dataset(outfile)
    nts=ds["t2m"].shape[0]
    if nts<24:
        print("file {} has only {} time steps. deleting...".format(outfile, nts))
        os.remove(outfile)
    ds.close()
else:
    print (outfile, "exists. Exiting...")
