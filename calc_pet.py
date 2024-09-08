import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json
import pandas as pd
from rasterio.enums import Resampling
import functions_pet as fun



inputdir=sys.argv[1]
outputdir=sys.argv[2]
dataset=sys.argv[3]
domain=sys.argv[4]
var=sys.argv[5]
date=sys.argv[6]
basetime=sys.argv[7]
index=sys.argv[8]
attribute=sys.argv[9]
climstartyear=sys.argv[10]
climendyear=sys.argv[11]
fracmissing=float(sys.argv[12])
overwrite=bool(int(sys.argv[13]))


currentdate=datetime.datetime.strptime(date, "%Y%m%d")
day=str(currentdate.day).zfill(2)
month=str(currentdate.month).zfill(2)
year=str(currentdate.year)


##################################################################
#



#first things first

if basetime!="mon":
   print("calculating pet only possible on monthly data. Requested basetime: {}. Exiting...".format(basetime))
   sys.exit()

if index not in ["pet-har","pet-tho"]:
   print("only pet-har and pet-tho  possible at the moment. Requested: {}. Exiting...".format(index))
   sys.exit()

print("Requested: {} \nCalculating {}".format(index, attribute))




if attribute=="index":
    #this sets up output directory for all basetimes
    
    outvar=index
    outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
    print(outputfile)
    if os.path.exists(outputfile) and overwrite==False:
        print("{} exists, and overwrite is off. skipping...".format(outputfile))
        sys.exit()
    else:
        print("outputfile does not exist. processing...")


    inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
    ds=xr.open_mfdataset(inputfiles)
    tgmon=ds[var]
    tgmon["time"]=pd.to_datetime(tgmon.time.data)+pd.offsets.MonthEnd()

    firstdate=pd.to_datetime("{}-{}-{}".format(climstartyear,month,1))-pd.offsets.YearBegin()
    lastdate=pd.to_datetime("{}-{}-{}".format(climendyear,month,1))

    lastdate=lastdate+pd.offsets.MonthEnd()

    currentdate=pd.to_datetime("{}-{}".format(year,str(month).zfill(2)))+pd.offsets.MonthEnd()

    if ~(pd.to_datetime(tgmon.time.data)==currentdate).any():
        print("Data not available for {}. Exiting...".format(currentdate))
        print(tgmon.time.data[-1])
        sys.exit()

    test=tgmon.sel(time=slice(firstdate, currentdate))
    ndates=test.shape[0]

    expecteddates=pd.date_range(firstdate,currentdate, freq="M")
    expected=expecteddates.shape[0]
    if ndates!=expected:
        print("Missing dates in input data. got {}, expected {}. Cannot calculate. exiting...".format(ndates,expected))
        print(firstdate,lastdate,currentdate)
        sys.exit()
    else:
        print("Got {} months of data, expected {}. Proceeding...".format(ndates,expected))
        print(firstdate,lastdate,currentdate)
    
    tgmon=tgmon.sel(time=slice(firstdate,currentdate))
    tdmon=tgmon.rio.write_crs("epsg:4326")
    tgmon.rio.set_spatial_dims("lon", "lat", inplace=True)



    print("Calculating pet...")

    if index=="pet-tho":
        dates=tgmon["time"]
        
        day_of_year=dates.dt.dayofyear-15
        days_in_month=dates.dt.days_in_month                
        month_index=dates.dt.month
                                                    
        temp=xr.apply_ufunc(
            fun.do_thornthwaite,
            tgmon.load(),
            tgmon["lat"],
            month_index,
            day_of_year,
            days_in_month,
            input_core_dims=[["time"],[],["time"],["time"],["time"]],
            output_core_dims=[["time"]],
            vectorize=True
        )

        comment="PET calculated using Thornthwaite method"


    output=temp.transpose("time","lat","lon")
    output.name=outvar
    output=output[-1:]
    #output=output.expand_dims({"time":1})
    output=output.to_dataset()
    
    units="mm/month"
     
    if "history" in ds.attrs:
         history=ds.attrs["history"]
    else:
         history=""

    if "contributor_role" in ds.attrs:
         contributor_role=ds.attrs["contributor_role"]
    else:
         contributor_role=""



    history="{}    {}: {} calculated using {}".format(history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), outvar, os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs

    output[outvar].attrs['units']=units
    output[outvar].attrs['comment']=comment
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated {}".format(contributor_role, outvar)
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()





if attribute=="indexall":
    #this sets up output directory for all basetimes
    
    outvar="spi{}".format(scale)

    inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
    ds=xr.open_mfdataset(inputfiles)
    prmon=ds[var]
    firstdate=pd.to_datetime(prmon.time[0].data)
    lastdate=pd.to_datetime(prmon.time[-1].data)+pd.offsets.MonthEnd()

    ndates=prmon.shape[0]
    expecteddates=pd.date_range(firstdate,lastdate, freq="M")
    expected=expecteddates.shape[0]
    print(expecteddates)
    print(firstdate,lastdate)
    if ndates!=expected:
        print("Missing dates in input data. got {}, expected {}. Cannot calculate. exiting...".format(ndates,expected))
        print(firstdate,lastdate)
        sys.exit()
    else:
        print("Got {} months of data, expected {}. Proceeding...".format(ndates,expected))

    prmon=prmon.rio.write_crs("epsg:4326")
    prmon.rio.set_spatial_dims("lon", "lat", inplace=True)

    #resampling to lower resolution if needed
    res=np.abs(prmon.rio.resolution())
    ngrid=prmon.shape[1]*prmon.shape[2]
 
    if np.min(res)<minres and ngrid>maxngrid:
        print("resampling to coarser grid...")
        new_height=prmon.rio.height*res[1]/0.25
        new_width=prmon.rio.width*res[1]/0.25
        prmon = prmon.rio.reproject(prmon.rio.crs, shape=(int(new_height), int(new_width)), resampling=Resampling.bilinear)
        prmon=prmon.rename({"x":"lon","y":"lat"})

    fdatay=prmon.time[0].dt.year.data

    print("Calculating spi...")

    temp=xr.apply_ufunc(
        get_spi,
        prmon.load(),
        [scale],
        [fdatay],
        [int(climstartyear)],
        [int(climendyear)],
        input_core_dims=[["time"],[],[],[],[]],
        output_core_dims=[["time"]],
        vectorize=True
    )
    output=temp.transpose("time","lat","lon")
    output.name=outvar


    output=output.to_dataset()

    units="-"
    comment="reference period {}-{}".format(climstartyear,climendyear)

    for date in output.time[scale:]:
        month=date.dt.strftime("%m").data 
        year=date.dt.strftime("%Y").data 
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")
       
        history="{}    {}: {} calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), outvar, os.path.basename(sys.argv[0])),

        outputmon=output.sel(time=date)

        outputmon[outvar]=outputmon[outvar].expand_dims({"time":1})
    
        outputmon.attrs=ds.attrs
        outputmon[outvar].attrs['units']=units
        outputmon[outvar].attrs['comment']=comment
        outputmon.attrs["history"]=history
        outputmon.attrs["contributor_role"]="{}; calculated {}".format(ds.contributor_role, outvar)
        outputmon.to_netcdf(outputfile)
        print("written {}".format(outputfile))
        ds.close()


