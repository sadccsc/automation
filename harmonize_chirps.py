import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json

import argparse
parser = argparse.ArgumentParser(description='This script performs harmonization')
parser.add_argument('inputfile', help='full path to input file')
parser.add_argument('outputfile', help='full path to output netcdf file')
parser.add_argument('datestr', help='date in string format. Should be for example: 20200131')
parser.add_argument('domain', help='domain for which subset is created and data are harmonized')
args = parser.parse_args()

inputfile=args.inputfile
outputfile=args.outputfile
datestr=args.datestr
domain=args.domain


#this is format string to parse teh datestr
dateformat="%Y%m%d"
overwrite=False

#this finds absolute path to this script
abspath=os.path.dirname(os.path.abspath(__file__))
domainsfile="{}/domains.json".format(abspath)


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



if os.path.exists(outputfile) and overwrite==False:
    print("{} exists, and overwrite is off. skipping...".format(outputfile))
else:
    print("processing {}...".format(inputfile))
    #reading tif file with rasterio. 
    #Tif file does not have date stored internally, thus date dimension is added to the dataarray
    da=rioxarray.open_rasterio(inputfile).expand_dims(time=[filedate])
    # after adding date, file has 4 dimensions, as the dataarray keeps "band" dimension inherited from tif file.
    # this removes that dimension
    da=da[:,0,:,:]
    da=da.drop("band",dim=None)
    #this substitures missing values 
    da=da.where(da>=0)
    #renaming dimensions for them to be CF complaiant for saving in netcdf format
    da=da.rename({"x":"lon","y":"lat"})
    #African subset processed here has 0.05deg resolution, which is a bit of overkill for regional level analyses
    #adding attributes to lat lon dimensions for CF compliance
    da.lat.attrs={"units":"degrees_north", "long_name":"latitude","standard_name":"latitude","axis":"Y"}
    da.lon.attrs={"units":"degrees_east", "long_name":"longitude","standard_name":"longitude","axis":"X"}
    #naming the variable
    #adding variable's attributes 
    da.attrs={"units":"mm/day"}
    da=da.sel(lon=slice(lonmin,lonmax), lat=slice(latmin,latmax))
    #adding general attributes
    ds=da.to_dataset(name="pr")
    ds.attrs={"description":"CHIRPS 2.0 dataset for {} domain obtained by subseting and converting daily tif files downloaded from https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/ to netcdf format".format(domain), "history":sys.argv[0]}

    ds.attrs={"title": "CHIRPS v2.0 rainfall data", 
"summary":"CHIRPS v2.0 rainfall data downloaded from https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05", 
"history":"{}: converted from original tif format to netcdf and harmonized using {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
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
    #sys.exit()
