import xarray as xr
import numpy as np
import glob, os,sys


basetime="mon"
tndir="data/reanalysis/ERA5/mon/sadc/TN"
tgdir=tndir.replace("TN","TG")
if not os.path.exists(tgdir):
    os.makedirs(tgdir)

for tnfile in glob.glob("{}/TN_{}_*.nc".format(tndir,basetime)):
    txfile=tnfile.replace("TN","TX")
    tgfile=tnfile.replace("TN","TG")
    if not os.path.exists(tgfile):
        tndset=xr.open_dataset(tnfile)
        txdset=xr.open_dataset(txfile)
        tndata=tndset["TN"]
        txdata=txdset["TX"]
        tgdata=(tndata+txdata)/2
        tgdset=tgdata.to_dataset(name="TG")
        print("saving {}".format(tgfile))
        tgdset.to_netcdf(tgfile)

