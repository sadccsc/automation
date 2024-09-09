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




if attribute in ["index", "indexall"]:
    #this sets up output directory for all basetimes
    
    outvar=index


    if attribute=="index":
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

    if attribute=="index":
        output=output[-1:]

    output.name=outvar
    output=output.to_dataset()

    for date in output.time:
        print("date", date)
        tsoutput=output.sel(time=slice(date,date))
        date=pd.to_datetime(date.data)
        year=date.strftime("%Y")
        month=date.strftime("%m")
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
        print(outputfile)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            
        else:
            print("outputfile does not exist. processing...")


            
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
            tsoutput.attrs=ds.attrs

            tsoutput[outvar].attrs['units']=units
            tsoutput[outvar].attrs['comment']=comment
            tsoutput.attrs["history"]=history
            tsoutput.attrs["contributor_role"]="{}; calculated {}".format(contributor_role, outvar)
            tsoutput.to_netcdf(outputfile)
            print("written {}".format(outputfile))
        ds.close()






