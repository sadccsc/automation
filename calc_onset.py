import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json
import pandas as pd
import geopandas as gpd
from geocube.api.core import make_geocube

from functions_onset import *

inputdir=sys.argv[1]
indexdir=sys.argv[2]
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
#processing code below, no need to edit anything normally
#

#this defines threhold for wet day in mm/day
wetday=1
regime="summer"

onsetclimmonth={"summer":3}

onsetdefs={
    "onsetA":[get_onsetA,"25 mm of accumulated rainfall in 10 days","Tadross et al. 2007"],
    "onsetB":[get_onsetB,"25 mm of accumulated rainfall in 10 days, not followed by a period of 10 consecutive days with observed rainfall < 2 mm in the following 20 days","??"],
    "onsetC":[get_onsetC,"45 mm of accumulated rainfall in 4 days","??"],
    "onsetD":[get_onsetD,"20mm threshold over 3 days and no dry spell in the next 10 days","??"]
}


#reading zones file
#this file contains polygons with julian day of the start of the season stored in the attribute table
gisdir="./gis"
zonesfile="{}/sadc_seasonality_zones_summer_sep.geojson".format(gisdir)
zones=gpd.read_file(zonesfile)




def write_output():
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    output[index].attrs['unit']=units
    output[index].attrs['comment']=comment
    history="{}    {}: anomaly calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated anomaly".format(ds.contributor_role)
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()


###############################################
#
#  calculating actual indices
#
###############################################

onsetfunc, onsetdef,source=onsetdefs[index]

if attribute=="index":

    #this sets up output directory for all basetimes
    outputdir=indexdir

##############################################
#  reading data

    datadict={}

    if basetime=="mon":
        #processes only months with data for all days
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month)
        print(outputfile)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")
            nominaldate=pd.to_datetime("{}-{}-{}".format(year,month,1))
            lastdate=pd.to_datetime(currentdate)+pd.offsets.MonthEnd()
            #finding first date on which analysis starts, i.e. first day of the previous calendar year
            firstdate=lastdate-pd.offsets.DateOffset(years=1)-pd.offsets.YearBegin()
            print("date range:",firstdate,lastdate)
            dates=pd.date_range(firstdate,lastdate)
            ndays=len(dates)
            files=[]
            for date in dates:
                filedate=date.strftime("%Y%m%d")
                searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                dayfiles=glob.glob(searchpath)
                if len(dayfiles)>0:
                    files=files+list(dayfiles)
            nfiles=len(files)
            print("found {} files in {}".format(nfiles,searchpath))
            if nfiles<ndays*(1-fracmissing):
                print("too few. need {}. exiting...".format(ndays))
            else:
                datadict[outputfile]=[files,firstdate,lastdate,nominaldate]

    elif basetime=="dek":
        #processes dekades with data for all days
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,11,21]:
            outputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            print(outputfile)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))

            else:
                print("outputfile does not exist. processing...")
                lastday=firstday+9
                if firstday==21:
                    lastday=lastdayofmonth

                nominaldate=pd.to_datetime("{}-{}-{}".format(year,month,firstday))
                lastdate=pd.to_datetime("{}-{}-{}".format(year,month,lastday))
                firstdate=lastdate-pd.offsets.DateOffset(years=1)-pd.offsets.YearBegin()
                days=pd.date_range(firstdate,lastdate)
                ndays=len(days)
                files=[]
                for date in days:
                    filedate=date.strftime("%Y%m%d")
                    searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+list(dayfiles)
                nfiles=len(files)
                print("found {} files in {}".format(nfiles,searchpath))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=[files,firstdate,lastdate,nominaldate]

    elif basetime=="pent":
        #processes dekades with data for all days
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,6,11,16,21,26]:
            outputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            print(outputfile)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))

            else:
                print("outputfile does not exist. processing...")
                lastday=firstday+4
                if firstday==26:
                    lastday=lastdayofmonth

                nominaldate=pd.to_datetime("{}-{}-{}".format(year,month,firstday))
                lastdate=pd.to_datetime("{}-{}-{}".format(year,month,lastday))
                firstdate=lastdate-pd.offsets.DateOffset(years=1)-pd.offsets.YearBegin()
                days=pd.date_range(firstdate,lastdate)
                ndays=len(days)
                files=[]
                for date in days:
                    filedate=date.strftime("%Y%m%d")
                    searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+list(dayfiles)
                nfiles=len(files)
                print("found {} files in {}".format(nfiles,searchpath))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=[files,firstdate,lastdate,nominaldate]

    else:
        print("onset processed only at monthly, dedakal and pentadal basetime. {} requested. exiting...".format(basetime))
        sys.exit()

#############################################
#    processing


    if len(datadict)>0:
        for outputfile in datadict.keys():
            files,firstdate,lastdate,nominaldate=datadict[outputfile]

            print("processing {} {}".format(index,outputfile))
            
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                ds=xr.open_mfdataset(files)
                ds=ds.chunk(-1,10,10)
                ds=ds.rio.write_crs("epsg:4326") #adding crs
                #rasterizing zones vector with raster corresponding to the extent and resolution of rainfall data
                zone_grid = make_geocube(
                    vector_data=zones,
                    like=ds
                )
                zone_grid=zone_grid.rename({"x":"lon","y":"lat"})
                data=ds[var]
                leapfirstyr=firstdate.is_leap_year
                leapsecondyr=lastdate.is_leap_year
                #calculating onset
                #returned is day of year

                temp=xr.apply_ufunc(
                    onsetfunc,
                    data.load(),
                    zone_grid.climystart,
                    leapfirstyr,
                    leapsecondyr,
                    input_core_dims=[["time"],[],[],[]],
                    output_core_dims=[[]],
                    vectorize=True
                )
                output=temp.transpose("lat","lon")
                output=output.expand_dims({"time":[nominaldate]})
                output=output.astype(np.float32)
                output.name=index
                output=output.rio.set_spatial_dims("lon","lat")
                #output=output.rio.write_crs("epsg:4326")
                #print(output)
                #sys.exit()

#############################################
#    writing output
                comment="value expressed in days since the start of climatological year, units attribute skipped because value of 'days' confuses xarray into interpreting data as timedelta"
                title=onsetdef
                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                output=output.to_dataset()
                #cannot have units attribute with name days, becasuse then xarray converts data frormat to timedelta
                output[index].attrs['units']="day of year"
                output[index].attrs['comment']=comment
                history="{}    {}: index calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
                output.attrs=ds.attrs
                output.attrs['title']=onsetdef
                output.attrs["history"]=history
                output.attrs["contributor_role"]="{}; calculated index from downloaded data".format(ds.contributor_role)

                output["climyearstart"]=zone_grid.climystart.astype(np.float32)
                output["climyearstart"].attrs['long_name']="start of climatological year"
                output["climyearstart"].attrs['comment']="day of year on which climatological year starts"
                output["climyearstart"].attrs['unit']="day of year"
                output.to_netcdf(outputfile)
                print("written {}".format(outputfile))
                ds.close()
                #sys.exit()




###############################################
#
#  calculating anomalies
#
###############################################



if attribute[-4:]=="anom":

    outputdir=indexdir

#########################
    if attribute=="absanom": 
        comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)
    else:
        print("calculations only possible for absanom, {} requested. exiting...".format(attribute))
        sys.exit()

    climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(indexdir,index,basetime,dataset,domain,climstartyear,climendyear)
    if os.path.exists(climfile)==False:
        print("{}\n does not not exist.exiting...".format(climfile))
        sys.exit()

    if basetime=="mon":
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        inputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month)
        outputfile="{}/{}-{}_{}_{}_{}_{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,climstartyear,climendyear)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
        else:
            print("outputfile does not exist. processing...")

            indexfile="{}/{}_{}_{}_{}_{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month)
            if os.path.exists(inputfile)==False:
                 print("{}\n does not not exist. skipping...".format(indexfile))
            else:
                ds=xr.open_dataset(indexfile)
                clim=xr.open_dataset(climfile)
                onset=ds[index]
                meanons=clim[index]
                temp=onset.where(onset>=0)-meanons
                temp=temp.where(onset>=0,-999)
                temp=(temp.where(~np.isnan(meanons))/10)
                output=temp.to_dataset(name=index)
                units="dekads"
                write_output()


    elif basetime=="dek":
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,11,21]:
            inputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            outputfile="{}/{}-{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,str(firstday).zfill(2),climstartyear,climendyear)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                indexfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
                if os.path.exists(inputfile)==False:
                     print("{}\n does not not exist. skipping...".format(indexfile))
                else:
                    ds=xr.open_dataset(indexfile)
                    clim=xr.open_dataset(climfile)
                    onset=ds[index]
                    meanons=clim[index]
                    temp=onset.where(onset>=0)-meanons
                    temp=temp.where(onset>=0,-999)
                    temp=(temp.where(~np.isnan(meanons))/10)
                    output=temp.to_dataset(name=index)
                    units="dekads"
                    write_output()

    elif basetime=="pent":
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,6,11,16,21,26]:
            inputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            outputfile="{}/{}-{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,str(firstday).zfill(2),climstartyear,climendyear)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                indexfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
                if os.path.exists(inputfile)==False:
                     print("{}\n does not not exist. skipping...".format(indexfile))
                else:
                    ds=xr.open_dataset(indexfile)
                    clim=xr.open_dataset(climfile)
                    onset=ds[index]
                    meanons=clim[index]
                    temp=onset.where(onset>=0)-meanons
                    temp=temp.where(onset>=0,-999)
                    temp=(temp.where(~np.isnan(meanons))/10)
                    output=temp.to_dataset(name=index)
                    units="dekads"
                    write_output()
    else:
        print("calculations only possible at monthly,dedadal and pentadal basetime, {} requested. exiting...".format(basetime))



###############################################
#
#  calculating climatologies
#
###############################################

if attribute=="clim":

    nyears=int(climendyear)-int(climstartyear)+1

    outputfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(indexdir,index,basetime,dataset,domain,climstartyear,climendyear)

    if os.path.exists(outputfile) and overwrite==False:
        print("{} exists, and overwrite is off. skipping...".format(outputfile))
        sys.exit()
    else:
        print("outputfile does not exist. processing...")

    datadict={}
    climdir=indexdir.replace(basetime,"mon")
    searchpath="{}/{}_*{}_*{}.nc".format(climdir,index,"mon", onsetclimmonth[regime])
    files=glob.glob(searchpath)
    nfiles=len(files)
    print("found {} files in {}".format(nfiles,searchpath))
    if nfiles==0:
        print("no files found. climatology is calculated using monthly files for {} month. exiting...".format(onsetclimmonth[regime]))
        sys.exit()

    ds=xr.open_mfdataset(searchpath)

    temp=ds.sel(time=slice(climstartyear,climendyear))
    targetperiods=int(nyears*(1-fracmissing))
    nperiods=temp[index].shape[0]
    print("data for {} years available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
    if nperiods<targetperiods:
        print("exiting...")
        sys.exit()
    else:
        print("processing..")
    onset=temp[index]
    meanons=onset.where(onset>0).mean("time")
    output=meanons.to_dataset(name=index)

    #saving output file 
    history="{}    {}: climatology calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated climatology".format(ds.contributor_role)

    if not os.path.exists(indexdir):
        os.makedirs(indexdir)
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()
    #sys.exit()
