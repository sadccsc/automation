import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='This script performs harmonization of hourly era files')
parser.add_argument('inputfile', help='full path to input1 file')
parser.add_argument('outputfiletasmin', help='full path to output netcdf file tasmin')
parser.add_argument('outputfiletasmax', help='full path to output netcdf file tasmax')
parser.add_argument('outputfiletas', help='full path to output netcdf file tas')
parser.add_argument('datestr', help='date in string format. Should be for example: 20200131')
parser.add_argument('domain', help='domain for which subset is created and data are harmonized')
args = parser.parse_args()

inputfile=args.inputfile
outputfiletasmin=args.outputfiletasmin
outputfiletasmax=args.outputfiletasmax
outputfiletas=args.outputfiletas
datestr=args.datestr
domain=args.domain


#this is format string to parse teh datestr
dateformat="%Y%m%d"
overwrite=False

#this finds absolute path to this script
abspath=os.path.dirname(os.path.abspath(__file__))
domainsfile="{}/dictionaries/domains.json".format(abspath)


##################################################################
#processing code below, no need to edit anything normally
#

#opening domains file and reading domain info
try:
    with open(domainsfile, "r") as jsonfile:
        domains=json.load(jsonfile)
except:
    print("domains file {} either does not exist, or cannot be read. Exiting...".format(domainsfile))
    sys.exit()


lonmin,lonmax,latmin,latmax=domains[domain]

#stripping directory from file name
inputfilename=os.path.basename(inputfile)
inputdirname=os.path.dirname(inputfile)

#creating datetime object from date string
filedate=datetime.datetime.strptime(datestr, dateformat)
if not os.path.exists(inputfile):
    print("inputfile {} does not exist. Exiting...".format(inputfile))
    sys.exit()

vars=["tasmin","tasmax"]
longnames=["minimum daily temperature","maximum daily temperature","mean daily temperature"]


print("processing tasmin and tasmax...")
if os.path.exists(outputfiletasmin) and overwrite==False:
    print("{} exists, and overwrite is off. skipping...".format(outputfiletasmin))
else:
    print("processing {}...".format(inputfile))
    #reading mfdataset. 
    #this was used formerly, but now era5 has time dimension as valid_time, and this messes things up
    #ds=xr.open_mfdataset([inputfile1,inputfile2])
    #new code - from August 2024
    ds=xr.open_dataset(inputfile)
    if "valid_time" in ds.coords:
        ds=ds.rename({"valid_time":"time"})
    if "expver" in ds.variables:
        ds=ds.drop("expver")
    if "number" in ds.variables:
        ds=ds.drop("number")

    #renaming dimensions for them to be CF complaiant for saving in netcdf format
    ds=ds.rename({"longitude":"lon","latitude":"lat"})
    #African subset processed here has 0.05deg resolution, which is a bit of overkill for regional level analyses
    #adding attributes to lat lon dimensions for CF compliance
    ds.lat.attrs={"units":"degrees_north", "long_name":"latitude","standard_name":"latitude","axis":"Y"}
    ds.lon.attrs={"units":"degrees_east", "long_name":"longitude","standard_name":"longitude","axis":"X"}
    #naming the variable
    #adding variable's attributes
    ds=ds.sel(lon=slice(lonmin,lonmax), lat=slice(latmin,latmax))

    da=ds["t2m"]-273.15


    tasmin=da.resample(time="D").min().sel(time=slice(datestr,datestr))
    tasmax=da.resample(time="D").max().sel(time=slice(datestr,datestr))
    alldata=[tasmin,tasmax]

    #adding general attributes
    for i, outputfile in enumerate([outputfiletasmin, outputfiletasmax]):
        var=vars[i]
        ds=alldata[i].to_dataset(name=var)
        
        varattrs=ds[var].attrs
        varattrs["units"]="degC"
        varattrs["long_name"]=longnames[i]
        ds[var].attrs=varattrs

        ds.attrs={"description":"ERA5 {} dataset for {} domain obtained by subsetting and converting hourly tas data downloaded from https://cds.climate.copernicus.eu".format(var, domain), "history":sys.argv[0]}

        ds.attrs={"title": "ERA5 reanalysis {} data".format(var), 
    "summary":"ERA5 reanalysis data downloaded from cds.climate.copernicus.eu", 
    "history":"{}: converted from hourly to daily and harmonized using {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    "contributor_name":"SADC Climate Services Centre (CSC)",
    "contributor_role": "downloaded and harmonized data"}
     
        outputdir=os.path.dirname(outputfile)
        if not os.path.exists(outputdir):
            print("output directory {} does not exist. Exiting...".format(outputdir))
            sys.exit()
        #writing netcdf file
        ds.to_netcdf(outputfile)
        print("written {}".format(outputfile))

        da.close()


print("\nprocessing tas...")
if os.path.exists(outputfiletas) and overwrite==False:
    print("{} exists, and overwrite is off. skipping...".format(outputfiletas))
else:
    if not os.path.exists(outputfiletasmin):
        print("{} does not exists, cannot calculate tas, skipping...".format(outputfiletasmin))
    else:
        ds=xr.open_mfdataset([outputfiletasmin,outputfiletasmax])
        da=(ds["tasmin"]+ds["tasmax"])/2
        var="tas"
        ds=da.to_dataset(name=var)

        varattrs={}
        varattrs["units"]="degC"
        varattrs["long_name"]=longnames[2]
        ds[var].attrs=varattrs

        ds.attrs={"description":"ERA5 {} dataset for {} domain obtained by subsetting and converting hourly tas data downloaded from https://cds.climate.copernicus.eu".format(var, domain), "history":sys.argv[0]}

        ds.attrs={"title": "ERA5 reanalysis {} data".format(var), 
    "summary":"ERA5 reanalysis data downloaded from cds.climate.copernicus.eu", 
    "history":"{}: converted from hourly to daily and harmonized using {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    "contributor_name":"SADC Climate Services Centre (CSC)",
    "contributor_role": "downloaded and harmonized data"}
     
        outputdir=os.path.dirname(outputfiletas)
        if not os.path.exists(outputdir):
            print("output directory {} does not exist. Exiting...".format(outputdir))
            sys.exit()
        #writing netcdf file
        ds.to_netcdf(outputfiletas)
        print("written {}".format(outputfiletas))
        da.close()


    #sys.exit()
