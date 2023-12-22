import xarray as xr
import sys

searchpattern=sys.argv[1]
outfile=sys.argv[2]

ds=xr.open_mfdataset(searchpattern)

ds=ds.coarsen(lat=5).mean().coarsen(lon=5).mean()

print("wiring outfile {}".format(outfile))
ds.to_netcdf(outfile)
print("done")
ds.close

