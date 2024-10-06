import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json
import pandas as pd
from climate_indices import indices, compute
from rasterio.enums import Resampling

inputdir=sys.argv[1]
outputdir=sys.argv[2]
dataset=sys.argv[3]
domain=sys.argv[4]
var=sys.argv[5]
date=sys.argv[6]
basetime=sys.argv[7]
index=sys.argv[8]
scale=int(sys.argv[9])
attribute=sys.argv[10]
climstartyear=sys.argv[11]
climendyear=sys.argv[12]
fracmissing=float(sys.argv[13])
overwrite=bool(int(sys.argv[14]))

if index=="spei":
    petinputdir=sys.argv[15]
    petdataset=sys.argv[16]
    petvar=sys.argv[17]

#these are criteria for resampling to lower resolution
minres=0.25
maxngrid=500000

currentdate=datetime.datetime.strptime(date, "%Y%m%d")
day=str(currentdate.day).zfill(2)
month=str(currentdate.month).zfill(2)
year=str(currentdate.year)

def calcspei(_prec, _pet,_scale,_dist,_freq,_fyear,_cfyear,_ceyear):
    dist={"gamma":indices.Distribution.gamma, "pearson":indices.Distribution.pearson}
    freq={"monthly":compute.Periodicity.monthly, "daily":compute.Periodicity.daily}
    _spei = indices.spei(_prec, _pet,_scale, dist[_dist],freq[_freq], _fyear, _cfyear, _ceyear)
    return(_spei)

def calcspi(_prec, _scale,_dist,_freq,_fyear,_cfyear,_ceyear):
    dist={"gamma":indices.Distribution.gamma, "pearson":indices.Distribution.pearson}
    freq={"monthly":compute.Periodicity.monthly, "daily":compute.Periodicity.daily}
    _spi = indices.spi(_prec,  _scale, dist[_dist], _fyear, _cfyear, _ceyear,freq[_freq])
    return(_spi)


def get_spei(_prdata,_petdata,_scale,_fdatay,_frefy,_lrefy):
    if np.sum(np.isnan(_prdata))==0:
        _temp=calcspei(_prdata,_petdata,_scale,"gamma","monthly",_fdatay,_frefy,_lrefy)
    else:
        _temp=_prdata.copy()
        _temp[:]=np.nan
    return _temp

def get_spi(_data,_scale,_fdatay,_frefy,_lrefy):
#    print(_data)
    if np.sum(np.isnan(_data))==0:
        _temp=calcspi(_data,_scale,"gamma","monthly",_fdatay,_frefy,_lrefy)
    else:
        _temp=_data.copy()
        _temp[:]=np.nan
    return _temp

##################################################################
#


#first things first

if basetime!="mon":
   print("calculating drought indices only possible on monthly data. Requested basetime: {}. Exiting...".format(basetime))
   sys.exit()

if index not in ["spi","spei"]:
   print("only spi and spei possible at the moment. Requested: {}. Exiting...".format(index))
   sys.exit()

print("Requested: {} \nCalculating {} with scale {}".format(index, attribute, scale))




if index=="spi":

    if attribute in ["index", "indexall"]:
        #this sets up output directory for all basetimes
        
        outvar="spi{}".format(scale)

        if attribute=="index":
            #when index requested - then check for outputfile is done prior to calculations.
            outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
            print(outputfile)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
                sys.exit()
            else:
                print("outputfile does not exist. processing...")


        #this will be common to index and indexall
        inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
        ds=xr.open_mfdataset(inputfiles)
        prmon=ds[var]
        prmon["time"]=pd.to_datetime(prmon.time.data)+pd.offsets.MonthEnd()

        firstdate=pd.to_datetime("{}-{}-{}".format(climstartyear,month,1))-pd.offsets.DateOffset(months=scale)-pd.offsets.YearBegin()

        lastdate=pd.to_datetime("{}-{}-{}".format(climendyear,month,1))
        lastdate=lastdate+pd.offsets.MonthEnd()

        currentdate=pd.to_datetime("{}-{}".format(year,str(month).zfill(2)))+pd.offsets.MonthEnd()

        if ~(pd.to_datetime(prmon.time.data)==currentdate).any():
            print("Data not available for {}. Exiting...".format(currentdate))
            print(prmon.time.data[-1])
            sys.exit()

        test=prmon.sel(time=slice(firstdate, currentdate))
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
        
        prmon=prmon.sel(time=slice(firstdate,currentdate))
        prmon=prmon.rio.write_crs("epsg:4326")
        prmon.rio.set_spatial_dims("lon", "lat", inplace=True)

        #resampling to lower resolution if needed
        res=np.abs(prmon.rio.resolution())
        ngrid=prmon.shape[1]*prmon.shape[2]

        #resampling...
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

        #only last time step is used if index is requestested. The entire time series if indexall is requestes
        if attribute=="index":
            output=output[-1:]

        #output=output.expand_dims({"time":1})
        output=output.to_dataset()
        
        #iterating through time steps in output to accomodate indexall request
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

                units="-"
                comment="reference period {}-{}".format(climstartyear,climendyear)
                
                history="{}    {}: {} calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), outvar, os.path.basename(sys.argv[0])),
                output.attrs=ds.attrs

                output[outvar].attrs['units']=units
                output[outvar].attrs['comment']=comment
                output.attrs["history"]=history
                output.attrs["contributor_role"]="{}; calculated {}".format(ds.contributor_role, outvar)
                output.to_netcdf(outputfile)
                print("written {}".format(outputfile))
                ds.close()
    else:
        print("requested attribute {}, but only index possible. exiting...".format(attribute))



if index=="spei":
    if attribute in ["index", "indexall"]:
        #this sets up output directory for all basetimes
        
        outvar="spei{}".format(scale)

        if attribute=="index":
            #when index requested - then check for outputfile is done prior to calculations.
            outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
            print(outputfile)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
                sys.exit()
            else:
                print("outputfile does not exist. processing...")


        #this will be common to index and indexall

        print("reading rainfall data...")
        inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
        ds=xr.open_mfdataset(inputfiles)
        prmon=ds[var]
        prmon["time"]=(pd.to_datetime(prmon.time.data)+pd.offsets.MonthEnd()).normalize()

        firstdate=pd.to_datetime("{}-{}-{}".format(climstartyear,month,1))-pd.offsets.DateOffset(months=scale)-pd.offsets.YearBegin()

        lastdate=pd.to_datetime("{}-{}-{}".format(climendyear,month,1))
        lastdate=lastdate+pd.offsets.MonthEnd()

        currentdate=pd.to_datetime("{}-{}".format(year,str(month).zfill(2)))+pd.offsets.MonthEnd()
        
        if ~(pd.to_datetime(prmon.time.data)==currentdate).any():
            print("Data not available for {}. Exiting...".format(currentdate))
            print(prmon.time.data[-1])
            sys.exit()

        test=prmon.sel(time=slice(firstdate, currentdate))
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
        
        prmon=prmon.sel(time=slice(firstdate,currentdate))
        prmon=prmon.rio.write_crs("epsg:4326")
        prmon.rio.set_spatial_dims("lon", "lat", inplace=True)



        print("reading pet data...")
        petinputfiles="{}/{}_{}_{}_{}_*.nc".format(petinputdir,petvar,basetime,petdataset,domain)
        petds=xr.open_mfdataset(petinputfiles)
        petmon=petds[petvar]
        petmon["time"]=(pd.to_datetime(petmon.time.data)+pd.offsets.MonthEnd()).normalize()

        if ~(pd.to_datetime(petmon.time.data)==currentdate).any():
            print("PET data not available for {}. Exiting...".format(currentdate))
            print(petmon.time.data[-1])
            sys.exit()

        test=prmon.sel(time=slice(firstdate, currentdate))
        ndates=test.shape[0]

        if ndates!=expected:
            print("Missing dates in pet input data. got {}, expected {}. Cannot calculate. exiting...".format(ndates,expected))
            print(firstdate,lastdate,currentdate)
            sys.exit()
        else:
            print("Got {} months of data, expected {}. Proceeding...".format(ndates,expected))
            print(firstdate,lastdate,currentdate)
        
        petmon=petmon.sel(time=slice(firstdate,currentdate))
        petmon=petmon.rio.write_crs("epsg:4326")
        petmon.rio.set_spatial_dims("lon", "lat", inplace=True)

        print("checking dimensions")
        print("pr",prmon["time"])
        print("pet",petmon["time"])
        if prmon.shape[0]!=petmon.shape[0]:
            print("pr",prmon.shape)
            print("pet",petmon.shape)
            print("Numbers of time steps differ. They should not. Exiting..")
            sys.exit()

        print("resampling to lower resolution - assuming pet is lower res than rainfall")
        prmon = prmon.rio.reproject_match(petmon)
        prmon=prmon.rename({"x":"lon","y":"lat"})

        #print("pr")
        #print(prmon)

        #print("pet")
        #print(petmon)

        fdatay=prmon.time[0].dt.year.data

        print("Calculating spei...")
        temp=xr.apply_ufunc(
            get_spei,
            prmon.load(),
            petmon.load(),
            [scale],
            [fdatay],
            [int(climstartyear)],
            [int(climendyear)],
            input_core_dims=[["time"],["time"],[],[],[],[]],
            output_core_dims=[["time"]],
            vectorize=True
        )
        output=temp.transpose("time","lat","lon")
        output=output.astype("float32")
        output.name=outvar

        #only last time step is used if index is requestested. The entire time series if indexall is requestes
        if attribute=="index":
            output=output[-1:,:]

        #output=output.expand_dims({"time":1})
        output=output.to_dataset()
        
        #iterating through time steps in output to accomodate indexall request
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

                units="-"
                comment="reference period {}-{}".format(climstartyear,climendyear)
                
                history="{}    {}: {} calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), outvar, os.path.basename(sys.argv[0])),
                tsoutput.attrs=ds.attrs

                tsoutput[outvar].attrs['units']=units
                tsoutput[outvar].attrs['comment']=comment
                tsoutput.attrs["history"]=history
                tsoutput.attrs["contributor_role"]="{}; calculated {}".format(ds.contributor_role, outvar)
                tsoutput.to_netcdf(outputfile)
                print("written {}".format(outputfile))
        ds.close()
        petds.close()
    else:
        print("requested attribute {}, but only index possible. exiting...".format(attribute))

