import sys
import xarray as xr
import glob
import pandas as pd


inputdir=sys.argv[1]
outputdir=sys.argv[2]
datatype=sys.argv[3]
dataset=sys.argv[4]
domain=sys.argv[5]
var=sys.argv[6]
basetime=sys.argv[7]
coarsen=int(sys.argv[8])

searchpattern="{}/{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset)
files=glob.glob(searchpattern)
print("found {} files".format(len(files)))

if len(files)==0:
    print(searchpattern)
    print("too few files. exiting...")
    sys.exit()

print("opening files...")
ds=xr.open_mfdataset(searchpattern)

print("compiling files...")
firstdate=pd.to_datetime(ds.time.data)[0].strftime("%Y%m%d")
lastdate=pd.to_datetime(ds.time.data)[-1].strftime("%Y%m%d")

outputfile="{}/{}_{}_{}_{}-{}.nc".format(outputdir,var,basetime,dataset,firstdate,lastdate)

if coarsen>1:
    print("coarsening...")
    ds=ds.coarsen(lat=coarsen).mean().coarsen(lon=coarsen).mean()

print("writing outfile {}".format(outputfile))
ds.to_netcdf(outputfile)
print("done")
ds.close

