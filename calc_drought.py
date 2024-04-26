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


#these are criteria for resampling to lower resolution
minres=0.25
maxngrid=500000

currentdate=datetime.datetime.strptime(date, "%Y%m%d")
day=str(currentdate.day).zfill(2)
month=str(currentdate.month).zfill(2)
year=str(currentdate.year)


def calcspi(_prec, _scale,_dist,_freq,_fyear,_cfyear,_ceyear):
    dist={"gamma":indices.Distribution.gamma, "pearson":indices.Distribution.pearson}
    freq={"monthly":compute.Periodicity.monthly, "daily":compute.Periodicity.daily}
    _spi = indices.spi(_prec,  _scale, dist[_dist], _fyear, _cfyear, _ceyear,freq[_freq])
    return(_spi)

def get_spi(_data,_scale,_fdatay,_frefy,_lrefy):
#    print(_data)
    if np.sum(np.isnan(_data))==0:
        _temp=calcspi(_data,_scale,"gamma","monthly",_fdatay,_frefy,_lrefy)
    else:
        _temp=_data
    return _temp

def get_spells(_data, _thresh,_spell):
#    print(_distrib.shape, _data.shape)
    _temp=np.copy(_data)
    if np.sum(np.isnan(_data))<len(_data):
#        print(_data)
        _temp[_temp>=_thresh]=1
        _temp[_temp<_thresh]=0
        
        n=len(_temp)
        y = _temp[1:] != _temp[:-1]               # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)   # positions of change. must include last element posi
        z = np.diff(np.append(-1, i))       # run lengths
        p = np.cumsum(np.append(0, z))[:-1] # positions
        _runs=np.copy(_temp)
        _runs[:]=0
        _runs[i]=z
#        print(_runs)
#        sys.exit()
        if _spell=="dry":
            _runs[_temp>0]=0
        else:
            _runs[_temp==0]=0
        return(_runs)
    else:
        return(_temp)

##################################################################
#

def write_output():
    output[outvar].attrs['units']=units
    output[outvar].attrs['comment']=comment
    history="{}    {}: {} calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), outvar, os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated {}".format(ds.contributor_role, outvar)
    
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()



#first things first

if basetime!="mon":
   print("calculating drought indices only possible on monthly data. Requested basetime: {}. Exiting...".format(basetime))
   sys.exit()

if index!="spi":
   print("only spi possible at the moment. Requested: {}. Exiting...".format(index))
   sys.exit()

print("Requested: {} \nCalculating {} with scale {}".format(index, attribute, scale))




if attribute=="index":
    #this sets up output directory for all basetimes
    
    outvar="spi{}".format(scale)
    outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,basetime,dataset,domain,year,month)
    print(outputfile)
    if os.path.exists(outputfile) and overwrite==False:
        print("{} exists, and overwrite is off. skipping...".format(outputfile))
        sys.exit()
    else:
        print("outputfile does not exist. processing...")


    inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
    ds=xr.open_mfdataset(inputfiles)
    prmon=ds[var]
    prmon["time"]=pd.to_datetime(prmon.time.data)+pd.offsets.MonthEnd()
#    firstdate=pd.to_datetime(prmon.time[0].data)
#    lastdate=pd.to_datetime(prmon.time[-1].data)+pd.offsets.MonthEnd()

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
    output=output[-1:]
    #output=output.expand_dims({"time":1})
    output=output.to_dataset()
    
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


severity={"mil":0,"mod":-1,"sev":-1.5,"ext":-2}



if attribute[-3:]=="dur":
    #this sets up output directory for all basetimes
    if attribute[:3] in severity.keys():
        sev=severity[attribute[:3]]
        outvar="spi{}".format(scale)
        outputfile="{}/{}-{}_{}_{}_{}_{}{}.nc".format(outputdir,outvar,attribute,basetime,dataset,domain,year,month)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")


        inputfiles="{}/{}_{}_{}_{}_*.nc".format(inputdir,var,basetime,dataset,domain)
        ds=xr.open_mfdataset(inputfiles)
        prmon=ds[var]
        firstdate=pd.to_datetime(prmon.time[0].data)
        lastdate=pd.to_datetime(prmon.time[-1].data)+pd.offsets.MonthEnd()

        firstdate=pd.to_datetime("{}-{}-{}".format(climyearstart,month,1))-pd.offsets.DateOffset(months=scale)
        firstdate=firstdate+pd.offsets.MonthEnd()

        lastdate=pd.to_datetime("{}-{}-{}".format(climyearend,month,1))
        lastdate=lastdate+pd.offsets.MonthEnd()
        test=prmon.sel(time=slice(firstdate, lastdate))

        ndates=test.shape[0]
        
        expecteddates=pd.date_range(firstdate,lastdate, freq="M")
        expected=expecteddates.shape[0]
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


        temp=xr.apply_ufunc(
            get_spells,
            output,
            sev,
            "dry",
            input_core_dims=[["time"],[],[]],
            output_core_dims=[["time"]],
            vectorize=True
        )

        #that will be for target date
        dur=temp.transpose("time","lat","lon")
        units="months"
        comment="{} {} drought duration".format(outvar,sev)

        output=output[-1].to_dataset()

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


