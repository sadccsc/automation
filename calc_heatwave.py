import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import pandas as pd

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

heatwavedefs={
    "hwTX95":{"definition":"3 consecutive days exceeding 95th percentile of maximum daily temperature","climvar":"TX95"},
    "hwTX90":{"definition":"3 consecutive days exceeding 90th percentile of maximum daily temperature","climvar":"TX90"},
    "hwTN95":{"definition":"3 consecutive days exceeding 95th percentile of minimum daily temperature","climvar":"TN95"},
    "hwTN90":{"definition":"3 consecutive days exceeding 90th percentile of minimum daily temperature","climvar":"TN90"}
}

quantdefs={
    "TN90":[0.90,"minimum daily temperature"],
    "TN95":[0.95,"minimum daily temperature"],
    "TX90":[0.90,"minimum daily temperature"],
    "TX95":[0.95,"minimum daily temperature"]
}

#these are parametes for calculatying seasons
seasparams={
        1:[9,-1,12,-1],
        2:[9,-1,12,-1],
        3:[12,-1,2,0],
        4:[12,-1,2,0],
        5:[12,-1,2,0],
        6:[3,0,5,0],
        7:[3,0,5,0],
        8:[3,0,5,0],
        9:[6,0,8,0],
        10:[6,0,8,0],
        11:[6,0,8,0],
        12:[9,0,11,0]
        }

#these are parametes for calculating all seasons
# first_month,year_of_first_month,last_month,year_of_last_month
seasparams={
        1:[10,-1,12,-1],
        2:[11,-1,1,0],
        3:[12,-1,2,0],
        4:[1,0,3,0],
        5:[2,0,4,0],
        6:[3,0,5,0],
        7:[4,0,6,0],
        8:[5,0,7,0],
        9:[6,0,8,0],
        10:[7,0,9,0],
        11:[8,0,10,0],
        12:[9,0,11,0]
        }



def write_output():
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    output[index].attrs['units']=units
    output[index].attrs['comment']=comment
    history="{}    {}: anomaly calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated anomaly".format(ds.contributor_role)
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()


def get_spells(_data, _thresh,_spell):
#    print(_distrib.shape, _data.shape)
    _temp=np.copy(_data)
    if np.isnan(_data[0])==False:
        _temp[_temp<_thresh]=0
        _temp[_temp>=_thresh]=1
        
        n=len(_temp)
        y = _temp[1:] != _temp[:-1]               # pairwise unequal (string safe)
        i = np.append(np.where(y), n - 1)   # positions of change. must include last element posi
        z = np.diff(np.append(-1, i))       # run lengths
        p = np.cumsum(np.append(0, z))[:-1] # positions
        _runs=np.copy(_temp)
        _runs[:]=0
        _runs[i]=z
        if _spell=="below":
            _runs[_temp>0]=0
        else:
            _runs[_temp==0]=0
        return(_runs)
    else:
        return(_temp)
#

###############################################
#
#  calculating actual indices
#
###############################################



if attribute=="index":

    climvar=heatwavedefs[index]["climvar"]
    #this sets up output directory for all basetimes
    outputdir=indexdir

##############################################
#  reading data

    climfile="{}/{}_day-clim_{}_{}_{}-{}.nc".format(inputdir.replace(var,climvar).replace(basetime,"day"),climvar,dataset,domain,climstartyear,climendyear)
    if not os.path.exists(climfile):
        print("{} does not exists, exiting...".format(climfile))
        sys.exit()
    else:
        print("found {}, proceeding...".format(climfile))
     

    datadict={}
    if basetime=="seas":
        seasstartmonth,seasstartoffset,seasendmonth,seasendoffset=seasparams[int(month)]
        seasstartyear=int(year)+seasstartoffset
        seasendyear=int(year)+seasendoffset
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,index,basetime,dataset,domain,seasstartyear,str(seasstartmonth).zfill(2))

        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")


        firstofmonth=pd.to_datetime("{}-{}-01".format(seasstartyear,seasstartmonth))
        firstdate=firstofmonth-pd.offsets.DateOffset(days=2)
        lastdate=pd.to_datetime("{}-{}-01".format(seasendyear,seasendmonth))+pd.offsets.MonthEnd()
        days=pd.date_range(firstdate,lastdate)
        ndays=len(days)
        files=[]
        for date in days:
            filedate=date.strftime("%Y%m%d")
            searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
            dayfiles=glob.glob(searchpath)
            if len(dayfiles)>0:
                files=files+[dayfiles[0]]
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles<ndays*(1-fracmissing):
            print("too few. need {}. exiting...".format(ndays))
        else:
            datadict[outputfile]=[files,firstdate,lastdate]

    elif basetime=="mon":
        #processes only months with data for all days
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")
            
            firstofmonth=pd.to_datetime("{}-{}-01".format(year,month))
            lastdate=firstofmonth+pd.offsets.MonthEnd()
            firstdate=firstofmonth-pd.offsets.DateOffset(days=2)

            days=pd.date_range(firstdate,lastdate)
            ndays=len(days)
            files=[]
            for date in days:
                filedate=date.strftime("%Y%m%d")
                searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                dayfiles=glob.glob(searchpath)
                if len(dayfiles)>0:
                    files=files+[dayfiles[0]]
            nfiles=len(files)
            print("found {} files in {}-{}".format(nfiles,firstdate,lastdate))
            if nfiles<ndays*(1-fracmissing):
                print("too few. need {}. exiting...".format(ndays))
            else:
                datadict[outputfile]=[files,firstdate,lastdate]

    elif basetime=="dek":
        #processes dekades with data for all days
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,11,21]:
            outputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))

            else:
                print("outputfile does not exist. processing...")
                lastday=firstday+9
                if firstday==21:
                    lastday=lastdayofmonth
                firstdate=pd.to_datetime("{}-{}-{}".format(year,month,firstday))-pd.offsets.DateOffset(days=2)
                lastdate=pd.to_datetime("{}-{}-{}".format(year,month,lastday)) 
                days=pd.date_range(firstdate,lastdate)
                ndays=len(days)
                files=[]
                for date in days:
                    filedate=date.strftime("%Y%m%d")
                    searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+[dayfiles[0]]
                nfiles=len(files)
                print("found {} files in {}-{}".format(nfiles,firstdate,lastdate))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=[files,firstdate,lastdate]


    elif basetime=="pent":
         #processes pentads with data for all days
        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,6,11,16,21,26]:
            outputfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))

            else:
                print("outputfile does not exist. processing...")
                lastday=firstday+4
                if firstday==26:
                    lastday=lastdayofmonth
                firstdate=pd.to_datetime("{}-{}-{}".format(year,month,firstday))-pd.offsets.DateOffset(days=2)
                lastdate=pd.to_datetime("{}-{}-{}".format(year,month,lastday)) 
                days=pd.date_range(firstdate,lastdate)
                ndays=len(days)
                files=[]
                for date in days:
                    filedate=date.strftime("%Y%m%d")
                    searchpath="{}/{}_*_{}*.nc".format(inputdir,var,filedate)
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+[dayfiles[0]]
                nfiles=len(files)
                print("found {} files in {}-{}".format(nfiles,firstdate,lastdate))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=[files,firstdate,lastdate]


    else:
        print("heatwaves processed only at seasonal,monthly,dekadal and pentadal  basetime. {} requested. exiting...".format(basetime))
        sys.exit()

#############################################
#    processing


    if len(datadict)>0:
        for outputfile in datadict.keys():
            files,firstdate,lastdate=datadict[outputfile]
            print("processing {} {}".format(index,outputfile))
            
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")
                climds=xr.open_dataset(climfile)
                climda=climds[climvar]

                ds=xr.open_mfdataset(files)
                da=ds[var]

                da2=da.assign_coords({"day":da.time.dt.dayofyear})
                da2=da2.swap_dims({'time': 'day'})
                anom=da2>(climda)
                anom=anom.swap_dims({'day': 'time'}).drop("day")

                temp=xr.apply_ufunc(
                    get_spells,
                    anom.load().astype(int),
                    1,
                    "above",
                    input_core_dims=[["time"],[],[]],
                    output_core_dims=[["time"]],
                    vectorize=True
                )
                hw=temp.transpose("time","lat","lon")
                hw.sel(time=slice(firstdate,lastdate))
                hw=hw.where(hw>=3)
                #heat wave frequency
                output=hw.sum("time")
                output=output.expand_dims(time=[ds.time[0].values])
                output.name=index
                units="none"
                comment="Heat wave frequency, calculated as the total number of days of heat wave days in the given period. Heat wave definition: {}".format(heatwavedefs[index]["definition"])           
#############################################
#    writing output

                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                output=output.to_dataset()
                output[index].attrs['units']=units
                output[index].attrs['comment']=comment
                history="{}    {}: index calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
                output.attrs=ds.attrs
                output.attrs["history"]=history
                output.attrs["contributor_role"]="{}; calculated index from downloaded data".format(ds.contributor_role)
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
    print("{} requested, but calculations of anomalies is not implemented. exiting...".format(attribute))
    sys.exit()
###############################################
#
#  calculating climatologies
#
###############################################

# this does not calculate climatologies of heatwaves, rather, it calculates percentiles


if attribute=="clim":
    if index not in ["TX90","TX95","TN90","TN95"]:
        print("Climatology calculations only possible for TX90, TX95, TN90 and TN95 . {} requested. exiting...".format(index))
        sys.exit()
    #width of window in days
    window=15

    quantile=quantdefs[index][0]
    varname=quantdefs[index][1]

    outputdir=indexdir

    nyears=int(climendyear)-int(climstartyear)+1
    outputfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(outputdir,index,basetime,dataset,domain,climstartyear,climendyear)
    if os.path.exists(outputfile) and overwrite==False:
        print("{} exists, and overwrite is off. skipping...".format(outputfile))
        sys.exit()
    else:
        print("outputfile does not exist. processing...")

    datadict={}

    if basetime=="day":
        searchpath="{}/{}_*{}_*.nc".format(inputdir,var,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
            sys.exit()

        ds=xr.open_mfdataset(searchpath)

        da=ds[var].sel(time=slice(climstartyear,climendyear))
        targetperiods=len(pd.date_range("{}-01-01".format(climstartyear), "{}-12-31".format(climendyear)))
        nperiods=da.shape[0]
        print("data for {} years available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
        if nperiods<targetperiods:
            print("exiting...")
            sys.exit()
        else:
            print("processing..")

        #preparing running windows
        n1=int(window/2)
        n2=window-n1
        seldaysarray=[]
        for jday in range(1,367):
            seldays=np.array(range(jday-n1,jday+n2,1))
            seldays[seldays<1]=seldays[seldays<1]+366
            seldata=da.time.dt.dayofyear.isin(seldays).data
            seldaysarray.append(seldata)
        seldaysarray=np.array(seldaysarray)

        #calculating percentiles
        output=[]
        for jday in range(366):
            sel=seldaysarray[jday,:]
            res=np.quantile(da.load().data[sel,:,:], quantile, axis=0)
            output.append(res)
        output=np.array(output)
        output=xr.DataArray(output, dims=["day", "lat", "lon"], coords={"day": range(1,367), "lat": da.lat, "lon":da.lon})
        output.name=index
        output=output.to_dataset()
    else:
        print("calculations of heatwaves is not intended to . {} requested. exiting...".format(basetime))
        sys.exit()

    output[index].attrs['units']="degC"
    output[index].attrs['long_name']="{} th percentile of {} over {}-day running window".format(quantile*100,varname,window)
    
    #saving output file 
    history="{}    {}: climatology calculated using {}".format(ds.history,datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(sys.argv[0])),
    output.attrs=ds.attrs
    output.attrs["history"]=history
    output.attrs["contributor_role"]="{}; calculated climatology".format(ds.contributor_role)

    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    output.to_netcdf(outputfile)
    print("written {}".format(outputfile))
    ds.close()
    #sys.exit()
