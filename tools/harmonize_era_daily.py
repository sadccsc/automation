import xarray as xr
import sys, os
import pandas as pd
import json, datetime


var="tasmax"
var="tasmin"

if var=="tasmax":
    longname="maximum daily temperature"
else:
    longname="minimum daily temperature"

domain="sadc"
outdir="./data/reanalysis/ERA5/day/{}/{}".format(domain,var)
infile="./incoming/ERA5/{}_day_ECMWF_ERA5_merged.nc".format(var)

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


ds=xr.open_dataset(infile)
da=ds[var]-273.15
da=da.rename({"longitude":"lon", "latitude":"lat"})
da.lat.attrs={"units":"degrees_north", "long_name":"latitude","standard_name":"latitude","axis":"Y"}
da.lon.attrs={"units":"degrees_east", "long_name":"longitude","standard_name":"longitude","axis":"X"}

da=da.sel(lon=slice(lonmin,lonmax), lat=slice(latmin,latmax))

print(da.shape)

for date in da.sel(time=slice("1981-01-01","2022-12-31")).time:
#for date in da.sel(time=slice("2023-07-01","2023-11-01")).time:
    date=pd.to_datetime(date.data)
    datestr=date.strftime("%Y%m%d")
    print(datestr)
    outfile="{}/{}_day_ERA5_{}_{}.nc".format(outdir,var,domain, datestr)
    if not os.path.exists(outfile):
        daydat=da.sel(time=slice(date,date))
        print(daydat.shape)

        ds=daydat.to_dataset(name=var)

        varattrs=ds[var].attrs
        varattrs["units"]="degC"
        varattrs["long_name"]=longname

        ds[var].attrs=varattrs

        ds.attrs={"title": "ERA5 reanalysis data", 
        "summary":"ERA5 reanalysis data downloaded from Copernicus Data Store", 
        "history":"{}: harmonized using {}".format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
        "contributor_name":"SADC Climate Services Centre (CSC)",
        "contributor_role": "downloaded and harmonized data"}

        ds.to_netcdf(outfile)
        print("written {}".format(outfile))
#    else:
#        print("outfile {} exists. skipping...".format(outfile))
#    sys.exit()
