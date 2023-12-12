import warnings
warnings.filterwarnings('ignore')
import sys,os,glob
import numpy as np
import xarray as xr
import datetime
import rioxarray
import json
import pandas as pd
import functions_etccdi as fun

inputdir=sys.argv[1]
climdir=sys.argv[2]
anomdir=sys.argv[3]
indexdir=sys.argv[4]
dataset=sys.argv[5]
domain=sys.argv[6]
var=sys.argv[7]
date=sys.argv[8]
basetime=sys.argv[9]
index=sys.argv[10]
attribute=sys.argv[11]
climstartyear=sys.argv[12]
climendyear=sys.argv[13]
fracmissing=float(sys.argv[14])
overwrite=bool(int(sys.argv[15]))

currentdate=datetime.datetime.strptime(date, "%Y%m%d")
day=str(currentdate.day).zfill(2)
month=str(currentdate.month).zfill(2)
year=str(currentdate.year)

##################################################################
#processing code below, no need to edit anything normally
#

#this defines threhold for wet day in mm/day
wetday=1

#these are parametes for calculatying seasons
seasparams={
        1:[9,-1,11,-1],
        2:[9,-1,11,-1],
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

#this function has to be here because it is using local variables of this script
#this is used to plot anomalies only, thus the history is "hard-coded"

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



###############################################
#
#  calculating actual indices
#
###############################################

if attribute=="index":

    #this sets up output directory for all basetimes
    outputdir=indexdir

##############################################
#  reading data

    datadict={}
    if basetime=="year":
        outputfile="{}/{}_{}_{}_{}_{}.nc".format(outputdir,index,basetime,dataset,domain,year)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")

        days=pd.date_range("{}-{}-{}".format(year,1,1),"{}-{}-{}".format(year,12,31))
        ndays=len(days)
        searchpath="{}/{}_*_{}*.nc".format(inputdir,var,year)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles<ndays*(1-fracmissing):
            print("too few. need {}. exiting...".format(ndays*(1-fracmissing)))
            sys.exit()
        else:
            print("processing...")

        datadict[outputfile]=files   


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

        lastdayofmonth=pd.Period("{}-{}-01".format(seasendyear,seasendmonth)).daysinmonth
        days=pd.date_range("{}-{}-{}".format(seasstartyear,seasstartmonth,1),"{}-{}-{}".format(seasendyear,seasendmonth,lastdayofmonth))
        ndays=len(days)
        files=[]
        print(seasstartyear,seasstartmonth,seasendyear, seasendmonth)
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
            datadict[outputfile]=files




    if basetime=="mon":
        #processes only months with data for all days
        outputfile="{}/{}_{}_{}_{}_{}{}.nc".format(outputdir,index,basetime,dataset,domain,year,month)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")
        ndays=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        searchpath="{}/{}_*_{}{}*.nc".format(inputdir,var,year,month)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles<ndays*(1-fracmissing):
            print("too few. need {}. exiting...".format(int(ndays*(1-fracmissing))))
            sys.exit()
        else:
            print("processing...")
        datadict[outputfile]=files   


    if basetime=="dek":
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
                days=pd.date_range("{}-{}-{}".format(year,month,firstday),"{}-{}-{}".format(year,month,lastday))
                ndays=len(days)
                files=[]
                for day in days.day.values:
                    searchpath="{}/{}_*_{}{}{}*.nc".format(inputdir,var,year,month,str(day).zfill(2))
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+[dayfiles[0]]
                nfiles=len(files)
                print("found {} files in {}".format(nfiles,searchpath))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=files


    if basetime=="pent":
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
                days=pd.date_range("{}-{}-{}".format(year,month,firstday),"{}-{}-{}".format(year,month,lastday))
                ndays=len(days)
                files=[]
                for day in days.day.values:
                    searchpath="{}/{}_*_{}{}{}*.nc".format(inputdir,var,year,month,str(day).zfill(2))
                    dayfiles=glob.glob(searchpath)
                    if len(dayfiles)>0:
                        files=files+[dayfiles[0]]
                nfiles=len(files)
                print("found {} files in {}".format(nfiles,searchpath))
                if nfiles<ndays*(1-fracmissing):
                    print("too few. need {}. exiting...".format(ndays))
                else:
                    datadict[outputfile]=files


#############################################
#    processing


    if len(datadict)>0:
        for outputfile in datadict.keys():
            files=datadict[outputfile]
            print("processing {} {}".format(index,outputfile))
            
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                ds=xr.open_mfdataset(files)
               
                if  index=="PRCPTOT":
                    print("calculating PRCPTOT")
                    temp=ds[var].copy()
                    output=temp.where(temp>=wetday).sum("time")
                    #sum over time wlll sum up nans to 0, we need to mask where nans are
                    mask=np.isnan(temp).sum("time")
                    output=output.where(mask==0)
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="mm"
                    comment="ETCCDI index"

                elif  index=="SDII":
                    print("calculating SDII")
                    temp=ds[var].copy()
                    temp=temp.where(temp>=wetday)
                    output=temp.sum("time")/temp.where(np.isnan(temp),1).sum("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="mm/day"
                    comment="ETCCDI index"

                elif index=="Rx1day":
                    print("calculating Rx1day")
                    output=ds[var].max("time")
                    print(np.nanmax(output))
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="mm"
                    comment="ETCCDI index"

                elif  index=="Rx5day":
                    print("calculating Rx5day")
                    output=ds[var].chunk({"time":None}).rolling(time=5).sum().max("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="mm"
                    comment="ETCCDI index"

                elif  index=="R20mm":
                    print("calculating R20mm")
                    temp=ds[var].copy()
                    temp=temp.where(temp>=20)
                    output=temp.where(np.isnan(temp),1).sum("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="day"
                    comment="ETCCDI index"
                elif  index=="R10mm":
                    print("calculating R10mm")
                    temp=ds[var].copy()
                    temp=temp.where(temp>=10)
                    output=temp.where(np.isnan(temp),1).sum("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="day"
                    comment="ETCCDI index"
                elif  index=="R1mm":
                    print("calculating R1mm")
                    temp=ds[var].copy()
                    temp=temp.where(temp>=1)
                    output=temp.where(np.isnan(temp),1).sum("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="day"
                    comment="ETCCDI index"
                elif  index=="CWD":
                    print("calculating CWD")
                    dlydata=ds[var]
                    temp=xr.apply_ufunc(
                        fun.get_spells,
                        dlydata.load(),
                        wetday,
                        "wet",
                        input_core_dims=[["time"],[],[]],
                        output_core_dims=[["time"]],
                        vectorize=True
                    )
                    
                    #that will be for target date
                    dlywetspell=temp.transpose("time","lat","lon")
                    output=dlywetspell.max("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="day"
                    comment="ETCCDI index"

                elif index=="CDD":
                    print("calculating CDD")
                    dlydata=ds[var]
                    temp=xr.apply_ufunc(
                        fun.get_spells,
                        dlydata.load(),
                        wetday,
                        "dry",
                        input_core_dims=[["time"],[],[]],
                        output_core_dims=[["time"]],
                        vectorize=True
                    )

                    #that will be for target date
                    dlywetspell=temp.transpose("time","lat","lon")
                    output=dlywetspell.max("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    output=xr.DataArray(output)
                    units="day"
                    comment="ETCCDI index"
                elif  index=="TNn":
                    print("calculating TNn")
                    output=ds[var].min("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="K"
                    comment="ETCCDI index"
                elif  index=="TXx":
                    print("calculating TXx")
                    output=ds[var].max("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="K"
                    comment="ETCCDI index"
                elif  index=="TN":
                    print("calculating TN")
                    output=ds[var].mean("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="K"
                    comment="ETCCDI index"
                elif  index=="TX":
                    print("calculating TX")
                    output=ds[var].mean("time")
                    output=output.expand_dims(time=[ds.time[0].values])
                    units="K"
                    comment="ETCCDI index"

                else:
                    print("index {} cannot be calculated. exiting..".format(index))
                    sys.exit()

#############################################
#    writing output

                if not os.path.exists(outputdir):
                    os.makedirs(outputdir)
                output=output.to_dataset()
                output=output.rename({var:index})
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

    outputdir=anomdir

#########################

    if basetime=="year":

        #    reading data

        outputfile="{}/{}-{}_{}_{}_{}_{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,climyearstart,climyearend)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")

        indexfile="{}/{}_{}_{}_{}_{}.nc".format(indexdir,index,basetime,dataset,domain,year)
        if os.path.exists(indexfile)==False:
             print("{}\n does not not exist.exiting...".format(indexfile))
             sys.exit()
        climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(climdir,index,basetime,dataset,domain,climstartyear,climendyear)
        if os.path.exists(climfile)==False:
             print("{}\n does not not exist.exiting...".format(climfile))
         
        ds=xr.open_dataset(inputfile)
        clim=xr.open_dataset(climfile)


        #    calculating anomalies
        
        if attribute=="absanom":
            output=ds-clim[index].data
            units=ds[index].units
            comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="quantanom":
            print("{} not implemented. exiting..".format(attribute))
            sys.exit()
            units="percentile"
            comment="quantile anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="relanom":
            climvalue=clim[index].data
            output=((ds-climvalue)/climvalue*100)
            units="% of mean"
            comment="relative anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="percnormanom":
            climvalue=clim[index].data
            output=(ds/climvalue)*100
            units="% of mean"
            comment="percent of normal wrt. {}-{} climatology".format(climstartyear,climendyear)
        else:
            print("cannot calculate {}. exiting..".format(attribute))
            sys.exit()

        write_output()

#########################

    if basetime=="seas":
        seasstartmonth,seasstartoffset,seasendmomnth,seasendoffset=seasparams[int(month)]
        seasstartyear=int(year)+seasstartoffset
        seasendyear=int(year)+seasendoffset
        #nominal date of the file is the first month of the season
        outputfile="{}/{}-{}_{}_{}_{}_{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,seasstartyear,str(seasstartmonth).zfill(2),climstartyear,climendyear)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")

        indexfile="{}/{}_{}_{}_{}_{}{}.nc".format(indexdir,index,basetime,dataset,domain,seasstartyear,str(seasstartmonth).zfill(2))
        if os.path.exists(indexfile)==False:
             print("{}\n does not exist.exiting...".format(indexfile))
             sys.exit()
        climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(climdir,index,basetime,dataset,domain,climstartyear,climendyear)
        if os.path.exists(climfile)==False:
             print("{}\n does not not exist.exiting...".format(climfile))
         
        ds=xr.open_dataset(indexfile)
        clim=xr.open_dataset(climfile)


        month=ds.time.dt.month

        #    calculating anomalies

        if attribute=="absanom":
            output=ds-clim[index].sel(month=month).data
            units=ds[index].units
            comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="quantanom":
            units="percentile"
            comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="relanom":
            climvalue=clim[index].sel(month=month).data
            output=(ds-climvalue)/climvalue*100
            units="% of mean"
            comment="relative anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="percnormanom":
            climvalue=clim[index].sel(month=month).data
            output=(ds/climvalue)*100
            units="% of mean"
            comment="percent of normal wrt. {}-{} climatology".format(climstartyear,climendyear)
        else:
            print("cannot calculate {}. exiting..".format(attribute))
            sys.exit()

        write_output()


    if basetime=="mon":

        outputfile="{}/{}-{}_{}_{}_{}_{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,climstartyear,climendyear)
        if os.path.exists(outputfile) and overwrite==False:
            print("{} exists, and overwrite is off. skipping...".format(outputfile))
            sys.exit()
        else:
            print("outputfile does not exist. processing...")


        indexfile="{}/{}_{}_{}_{}_{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month)
        if os.path.exists(indexfile)==False:
             print("{}\n does not not exist.exiting...".format(indexfile))
             sys.exit()
        climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(climdir,index,basetime,dataset,domain,climstartyear,climendyear)
        if os.path.exists(climfile)==False:
             print("{}\n does not not exist.exiting...".format(climfile))
         
        ds=xr.open_dataset(indexfile)
        clim=xr.open_dataset(climfile)

        month=ds.time.dt.month

        if attribute=="absanom":
            output=ds-clim[index].sel(month=month).data
            units=ds[index].units
            comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="quantanom":
            units="percentile"
            comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="relanom":
            climvalue=clim[index].sel(month=month).data
            output=((ds-climvalue)/climvalue*100)
            units="% of mean"
            comment="relative anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

        elif attribute=="percnormanom":
            climvalue=clim[index].sel(month=month).data
            output=(ds/climvalue)*100
            units="% of mean"
            comment="percent of normal wrt. {}-{} climatology".format(climstartyear,climendyear)

        else:
            print("cannot calculate {}. exiting..".format(attribute))
            sys.exit()

        write_output()


    if basetime=="dek":
        climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(climdir,index,basetime,dataset,domain,climstartyear,climendyear)
        if os.path.exists(climfile)==False:
            print("{}\n does not not exist.exiting...".format(climfile))
            sys.exit()

        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,11,21]:
            outputfile="{}/{}-{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,str(firstday).zfill(2),climstartyear,climendyear)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                indexfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
                if os.path.exists(indexfile)==False:
                     print("{}\n does not not exist. skipping...".format(indexfile))
                else:
                    ds=xr.open_dataset(indexfile)
                    clim=xr.open_dataset(climfile)

                    dekad=fun.get_dekad(pd.to_datetime(ds.time.data[0]))

                    if attribute=="absanom":
                        output=ds-clim[index].sel(dekad=dekad).data
                        units=ds[index].units
                        comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

                    elif attribute=="quantanom":
                        units="percentile"
                        comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

                    elif attribute=="relanom":
                        climvalue=clim[index].sel(dekad=dekad).data
                        output=((ds-climvalue)/climvalue*100)
                        units="% of mean"
                        comment="relative anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

                    elif attribute=="percnormanom":
                        climvalue=clim[index].sel(dekad=dekad).data
                        output=(ds/climvalue)*100
                        units="% of mean"
                        comment="percent of normal wrt. {}-{} climatology".format(climstartyear,climendyear)

                    else:
                        print("cannot calculate {}. exiting..".format(attribute))
                        sys.exit()
                    write_output()


    if basetime=="pent":

        climfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(climdir,index,basetime,dataset,domain,climstartyear,climendyear)
        if os.path.exists(climfile)==False:
            print("{}\n does not not exist.exiting...".format(climfile))
            sys.exit()

        lastdayofmonth=pd.Period("{}-{}-01".format(year,month)).daysinmonth
        for firstday in [1,6,11,16,21,26]:
            outputfile="{}/{}-{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(outputdir,index,attribute,basetime,dataset,domain,year,month,str(firstday).zfill(2),climstartyear,climendyear)
            if os.path.exists(outputfile) and overwrite==False:
                print("{} exists, and overwrite is off. skipping...".format(outputfile))
            else:
                print("outputfile does not exist. processing...")

                indexfile="{}/{}_{}_{}_{}_{}{}{}.nc".format(indexdir,index,basetime,dataset,domain,year,month,str(firstday).zfill(2))
                if os.path.exists(indexfile)==False:
                     print("{}\n does not not exist. skipping...".format(indexfile))
                else:
                    ds=xr.open_dataset(indexfile)
                    clim=xr.open_dataset(climfile)

                    pentad=fun.get_pentad(pd.to_datetime(ds.time.data[0]))

                    if attribute=="absanom":
                        output=ds-clim[index].sel(pentad=pentad).data
                        units=ds[index].units
                        comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

                    elif attribute=="quantanom":
                        units="percentile"
                        comment="absolute anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)
                        print("calculating quantanom is not ready yet. exiting")
                        sys.exit()
                    elif attribute=="relanom":
                        climvalue=clim[index].sel(pentad=pentad).data
                        output=((ds-climvalue)/climvalue*100)
                        units="%"
                        comment="relative anomaly wrt. {}-{} climatology".format(climstartyear,climendyear)

                    elif attribute=="percnormanom":
                        climvalue=clim[index].sel(pentad=pentad).data
                        output=(ds/climvalue)*100
                        units="% of mean"
                        comment="percent of normal wrt. {}-{} climatology".format(climstartyear,climendyear)

                    else:
                        print("cannot calculate {}. exiting..".format(attribute))
                        sys.exit()
                    write_output()





###############################################
#
#  calculating climatologies
#
###############################################

if attribute=="clim":

    outputdir=climdir

    nyears=int(climendyear)-int(climstartyear)+1

    outputfile="{}/{}_{}-clim_{}_{}_{}-{}.nc".format(outputdir,index,basetime,dataset,domain,climstartyear,climendyear)

    if os.path.exists(outputfile) and overwrite==False:
        print("{} exists, and overwrite is off. skipping...".format(outputfile))
        sys.exit()
    else:
        print("outputfile does not exist. processing...")


    datadict={}

    if basetime=="year":
        searchpath="{}/{}_*{}_*.nc".format(indexdir,index,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
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
            output=temp.groupby(temp.time.dt.month).mean()



    if basetime=="seas":
        searchpath="{}/{}_*{}_*.nc".format(indexdir,index,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
            sys.exit()

        ds=xr.open_mfdataset(searchpath)

        temp=ds.sel(time=slice(climstartyear,climendyear))
        targetperiods=int(nyears*4*(1-fracmissing))
        nperiods=temp[index].shape[0]
        print("data for {} seasons available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
        if nperiods<targetperiods:
            print("exiting...")
            sys.exit()
        else:
            print("processing..")
            output=temp.groupby(temp.time.dt.month).mean()


    if basetime=="mon":
        searchpath="{}/{}_*{}_*.nc".format(indexdir,index,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
            sys.exit()

        ds=xr.open_mfdataset(searchpath)

        temp=ds.sel(time=slice(climstartyear,climendyear))
        targetperiods=int(nyears*12*(1-fracmissing))
        nperiods=temp[index].shape[0]
        print("data for {} months available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
        if nperiods<targetperiods:
            print("exiting...")
            sys.exit()
        else:
            print("processing..")
            output=temp.groupby(temp.time.dt.month).mean()



    if basetime=="dek":
        searchpath="{}/{}_*{}_*.nc".format(indexdir,index,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
            sys.exit()

        ds=xr.open_mfdataset(searchpath)

        temp=ds.sel(time=slice(climstartyear,climendyear))

        targetperiods=int(nyears*12*3*(1-fracmissing))
        nperiods=temp[index].shape[0]
        print("data for {} dekades available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
        if nperiods<targetperiods:
            print("exiting...")
            sys.exit()
        else:
            print("processing..")

            dekads=[fun.get_dekad(x) for x in pd.to_datetime(temp.time.data)]
            temp=temp.assign_coords({"time": dekads})
            temp=temp.rename({"time":"dekad"})
            output=temp.groupby(temp.dekad).mean()


    if basetime=="pent":

        searchpath="{}/{}_*{}_*.nc".format(indexdir,index,basetime)
        files=glob.glob(searchpath)
        nfiles=len(files)
        print("found {} files in {}".format(nfiles,searchpath))
        if nfiles==0:
            print("no files found. exiting...")
            sys.exit()
        ds=xr.open_mfdataset(searchpath)

        temp=ds.sel(time=slice(climstartyear,climendyear))

        targetperiods=int(nyears*12*6*(1-fracmissing))
        nperiods=temp[index].shape[0]
        print("data for {} dekades available in {}-{} period. Should be at least {}".format(nperiods,climstartyear,climendyear,targetperiods))
        if nperiods<targetperiods:
            print("exiting...")
            sys.exit()
        else:
            print("processing..")

            pentads=[fun.get_pentad(x) for x in pd.to_datetime(temp.time.data)]
            temp=temp.assign_coords({"time": pentads})
            temp=temp.rename({"time":"pentad"})
            output=temp.groupby(temp.pentad).mean()


    units=ds[index].units
    output[index].attrs['units']=units
    
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
