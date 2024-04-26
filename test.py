import xarray as xr

ds=xr.open_dataset("incoming/ERA5/hr/tas_hr_ERA5_saf_20240102.nc")
print(ds)

ds2=ds.resample(time="D").sum()
print(ds2)

