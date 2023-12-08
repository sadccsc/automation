import xarray as xr
import glob, os,sys
import netCDF4

ds=xr.open_dataset("incoming/ERA5/hr/tas_hr_ECMWF_ERA5_africa_arc.20231001.nc")

print(ds)

