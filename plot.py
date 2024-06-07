import xarray as xr
import geopandas
import matplotlib.colors as colors
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geojson
import os, sys, glob
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from functions_plot import *
import datetime


inputdir=sys.argv[1]
outputdir=sys.argv[2]
dataset=sys.argv[3]
domain=sys.argv[4]
date=sys.argv[5]
basetime=sys.argv[6]
var=sys.argv[7]
attr=sys.argv[8]
climstartyear=sys.argv[9]
climendyear=sys.argv[10]
overwrite=bool(int(sys.argv[11]))

currentdate=datetime.datetime.strptime(date, "%Y%m%d")
day=str(currentdate.day).zfill(2)
monthval=currentdate.month
month=str(currentdate.month).zfill(2)
year=str(currentdate.year)
yearval=currentdate.year



months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
seasons=["JFM","FMA","MAM","AMJ","MJJ","JJA","JAS","ASO","SON","OND","NDJ","DJF"]

varnames={
    "TNn":"lowest minimum daily temperature",
    "TXx":"highest maximum daily temperature",
    "TN":"mean of minimum daily temperature",
    "TX":"mean of maximum daily temperature",
    "PRCPTOT":"total precipitation",
    "Rx1day": "maximum 1 day rainfall",
    "Rx5day": "maximum 5 day rainfall",
    "SDII": "mean daily rainfall intensity",
    "spi1": "1-month Standard Precipitation Index (SPI)",
    "spi3": "3-month Standard Precipitation Index (SPI)",
    "spi6": "6-month Standard Precipitation Index (SPI)",
    "spi12": "12-month Standard Precipitation Index (SPI)",
    "spi36": "36-month Standard Precipitation Index (SPI)",
    "CDD": "maximum consecutive dry days",
    "CWD": "maximum consecutive wet days",
    "R1mm": "number of days with rainfall > 1mm",
    "R10mm": "number of days with rainfall > 10mm",
    "R20mm": "number of days with rainfall > 20mm",
    "hwTX95": "daytime heat wave days",
    "hwTN95": "nighttime heat wave days",
    "seasaccum": "total rainfall in climatological year",
    "onsetD": "onset of the rainy season"
}

attrnames={
    "index":"Recorded",
    "clim":"Climatology of",
    "relanom":"Relative anomaly of",
    "percnormanom":"Anomaly of",
    "absanom":"Absolute anomaly of",
    "quantanom":"Percentile anomaly of",
}

varcategories={
    "PRCPTOT":"precipitation",
    "Rx1day": "precipitation",
    "Rx5day": "precipitation",
    "CDD": "precipitation",
    "SDII": "precipitation",
    "CWD": "precipitation",
    "R1mm": "precipitation",
    "R10mm": "precipitation",
    "R20mm": "precipitation",
    "onsetD": "onset",
    "spi1": "spi",
    "spi3": "spi",
    "spi6": "spi",
    "spi12": "spi",
    "spi36": "spi",
    "TNn": "temperature",
    "TN": "temperature",
    "TX": "temperature",
    "TXx": "temperature",
    "hwTX95": "heat wave",
    "hwTN95": "heat wave",
    "seasaccum": "seasaccum"
}

datasetnames={
    "ERA5": "ERA5",
    "TAMSAT-v3.1": "TAMSAT v3.1",
    "ARC2": "ARC2",
    "CHIRPS-v2.0-p05-merged": "CHIRPS v2.0"
}

domainoverlays={
    "sadc":"./gis/sadc_continental.geojson",
    "maur":"./gis/maur.geojson",
    "como":"./gis/como.geojson",
    "seyc":"./gis/seyc.geojson",
}

onsetdefs={
    "onsetA":["25 mm of accumulated rainfall in 10 days","Tadross et al. 2007"],
    "onsetB":["25 mm of accumulated rainfall in 10 days, \nnot followed by a period of 10 consecutive days with observed rainfall < 2 mm in the following 20 days","??"],
    "onsetC":["45 mm of accumulated rainfall in 4 days","??"],
    "onsetD":["20mm threshold over 3 days and no dry spell in the next 10 days","??"]
}

heatwavedefs={
    "hwTX95":{"definition":"at least 3 consecutive days exceeding 95th percentile of maximum daily temperature","climvar":"TX95"},
    "hwTX90":{"definition":"at least 3 consecutive days exceeding 90th percentile of maximum daily temperature","climvar":"TX90"},
    "hwTN95":{"definition":"at least 3 consecutive days exceeding 95th percentile of minimum daily temperature","climvar":"TN95"},
    "hwTN95":{"definition":"at least 3 consecutive days exceeding 90th percentile of minimum daily temperature","climvar":"TN90"}
}


accumdefs={
        "seasaccum":{"summer":"Accumulation since the 1st of July"},
        "onset":{"summer": "Calculated after the 1st of September"}
    }

#this is a temporary solution. ultimately, one would need to build the regime into lst file and onset and seasaccum calculation scripts
regime="summer"

varcat=varcategories[var]

datasetname=datasetnames[dataset]

annotation="Data source: {}".format(datasetname)

if attr in ["relanom","clim","quantanom","absanom","percnormanom"]: 
    attrfilecode="-{}".format(attr)
    annotation="{}\nClimatological period: {}-{}".format(annotation,climstartyear,climendyear)
else:
    attrfilecode=""

if varcat in ["spi", "heat wave"]:
    annotation="{}\nClimatological period: {}-{}".format(annotation,climstartyear,climendyear)

if varcat=="onset":
    annotation="{}\nDefinition: {}\n{}".format(annotation, onsetdefs[var][0], accumdefs[varcat][regime])

if varcat=="heat wave":
    annotation="{}\nDefinition: {}".format(annotation, heatwavedefs[var]["definition"])

if varcat=="seasaccum":
    annotation="{}\nDefinition: {}".format(annotation, accumdefs[varcat][regime])


datafiles=[]

if attr=="clim":
    if basetime=="seas":
        datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
        #datafile="{}/{}{}_{}_{}_{}_{}{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain,year,str(month).zfill(2))
        datafiles.append([day,datafile])
    if basetime=="mon":
        datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
        #datafile="{}/{}{}_{}_{}_{}_{}{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain,year,str(month).zfill(2))
        datafiles.append([day,datafile])
    if basetime=="dek":
        for firstday in [1,11,21]:
            datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
           # datafile="{}/{}{}_{}_{}_{}_{}{}{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2))
            datafiles.append([firstday,datafile])
    if basetime=="pent":
        for firstday in [1,6,11,16,21,26]:
            datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
            #datafile="{}/{}{}_{}_{}_{}_{}{}{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2))
            datafiles.append([firstday,datafile])


elif attr=="index":
    if basetime=="seas":
        datafile="{}/{}{}_{}_{}_{}_{}{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain,year,str(month).zfill(2))
        datafiles.append([day,datafile])
    if basetime=="mon":
        datafile="{}/{}{}_{}_{}_{}_{}{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain,year,str(month).zfill(2))
        datafiles.append([day,datafile])
    if basetime=="dek":
        for firstday in [1,11,21]:
            datafile="{}/{}{}_{}_{}_{}_{}{}{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2))
            datafiles.append([firstday,datafile])
    if basetime=="pent":
        for firstday in [1,6,11,16,21,26]:
            datafile="{}/{}{}_{}_{}_{}_{}{}{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2))
            datafiles.append([firstday,datafile])

else:
    #this is for anomalies
    if basetime=="seas":
        datafile="{}/{}{}_{}_{}_{}_{}{}_{}-{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain, year,str(month).zfill(2),climstartyear,climendyear)
        datafiles.append([day,datafile])
    elif basetime=="mon":
        datafile="{}/{}{}_{}_{}_{}_{}{}_{}-{}.nc".format(inputdir,var,attrfilecode, basetime,dataset,domain, year,str(month).zfill(2),climstartyear,climendyear)
        datafiles.append([day,datafile])
    elif basetime=="dek":
        for firstday in [1,11,21]:
            datafile="{}/{}{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2),climstartyear,climendyear)
            datafiles.append([firstday,datafile])
    elif basetime=="pent":
        for firstday in [1,6,11,16,21,26]:
            datafile="{}/{}{}_{}_{}_{}_{}{}{}_{}-{}.nc".format(inputdir,var,attrfilecode,basetime, dataset,domain, year,str(month).zfill(2),str(firstday).zfill(2),climstartyear,climendyear)
            datafiles.append([firstday,datafile])
    else:
        print("ERROR. Requested basetime {} cannot be processed. exiting...".format(basetim))
        sys.exit()


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#checking if files exist

overlayfile=domainoverlays[domain]
print("Using overlay file:",overlayfile)

if not os.path.exists(overlayfile):
    print("ERROR! Overlay file does not exist: {}".format(overlayfile))
    sys.exit()
overlayvector = geopandas.read_file(overlayfile)


logofile="./img/sadclogo-small.png"
print("Using logo file:",logofile)

if not os.path.exists(logofile):
    print("ERROR! Logo file does not exist: {}".format(logofile))
    sys.exit()


for day,datafile in datafiles:
    if not os.path.exists(datafile):
        print("Skipping. Required data file does not exist: {}".format(datafile))
    else:
        print("Found datafile:",day,datafile)
        if attr in ["relanom","quantanom","absanom","percnormanom"]: 
            filename=os.path.basename(datafile)
            filename="_".join(filename.split("_")[:-1])
            mapfile="{}/{}.{}".format(outputdir,filename,"png")
        elif attr in ["clim"]: 
            mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc","_{}.png".format(month)))
        else:
            mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc",".png"))
        elems=mapfile.split("_")
        mapfile="_".join(["-".join(elems[0:3]),"_".join(elems[3:])])
        #sys.exit()

        if os.path.exists(mapfile) and overwrite==False:
            print("Skipping. Map file exists and overwrite is off. {}".format(mapfile))
        else:
            print("Processing. Output map file does not exist. {}...".format(mapfile))


            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #reading data

            ds=xr.open_mfdataset(datafile)
            ds=ds.rio.write_crs("epsg:4326") #adding crs
            ds.rio.set_spatial_dims("lon","lat")


            if attr=="clim":
                data=ds[var].load()
                data=data.sel(month=monthval)
            else:
                data=ds[var].load()

            if var=="spi3":
                data=ds[var]
                data=data.where(~np.isnan(data),-4)
                ds[var]=data
                
            if var=="CDD":
                data=ds[var]
                data=data.where(~np.isnan(data),31)
                ds[var]=data

            if var=="CWD":
                data=ds[var]
                data=data.where(~np.isnan(data),0)
                ds[var]=data

            if var=="PRCPTOT-percnormanom":
                data=ds[var]
                data=data.where(~np.isnan(data),0)
                ds[var]=data

            ds=ds.rio.clip(overlayvector.geometry.values, "epsg:4326") #clipping to geojson
            data=ds[var]

            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #preparing for plotting


            attrname=attrnames[attr]
            varname=varnames[var]
            timeexpr=get_timeexpr(year,monthval,day,basetime,climstartyear,climendyear,attr,var,varcat)
            title="{} {} \n{}".format(attrname, varname, timeexpr)
            mask=None
            plotbackground=False

            #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #colormaps

            if varcat=="precipitation":

                if attr=="relanom":
                    vmin=10
                    vmax=190
                    levels = [10,30,50,70,90,110,130,150,170,190]
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cols[5]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    units="% of long-term mean"
                    extend="both"

                elif attr=="absanom":
                    vmin=-100
                    vmax=100
                    levels = np.linspace(vmin,vmax,11)    
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cols[5]=(1,1,1,1)
                    cols[6]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                    levels=None
                    ticklabels=None
                    units="mm"
                    extend="both"

                elif attr=="percnormanom":
                    vmin=10
                    vmax=190
                    levels = [10,30,50,70,90,110,130,150,170,190]
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cols[5]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    units="% of long-term mean"
                    extend="both"

                elif attr=="quantanom":
                    #custom color map for quantile anomaly
                    seq=[10]*10+[20]*10+[30]*13+[50]*34+[70]*13+[80]*10+[90]*10
                    levels = [0,10,20,30,70,80,90,100]
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                    cols[5]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="none")
                    ticklevels=None
                    ticklabels=None
                    units="percentile"
                    extend="neither"

                else:
                    if var=="PRCPTOT":
                        vmin=0
                        vmax=300
                        levels = [0,1,10,25,50,75,150,225,300]
                        #original CSC
                        cols=["#FFFFFF","#C6C618","#FEFE00","#00FF00","#10FAF7","#0F17FF","#F273E4","#841F89","#590059"]
                        #original BOM
                        #cols=["#FFFFFF","#FEBE59","#FEAC00","#FEFE00","#B2FE00","#4CFE00","#00E499","#00A4FE","#3E3EFE","#B200FE","#FE00FE","#FE4C9B"]
                        #reduced BOM
                        #cols=["#FFFFFF","#FEFE00","#B2FE00","#4CFE00","#00E499","#00A4FE","#3E3EFE","#B200FE","#FE4C9B"]
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=None
                        ticklabels=None 
                        units="mm"
                        extend="max"

                    if var=="Rx1day":
                        vmin=0
                        vmax=100
                        levels = [0,25,50,70,80,90,100]
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0, 1, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=None
                        ticklabels=None 
                        units="mm/day"
                        extend="max"

                    if var=="Rx5day":
                        vmin=0
                        vmax=200
                        levels = [0,25,50,70,80,90,100,200]
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0, 1, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=None
                        ticklabels=None 
                        units="mm/day"
                        extend="max"


                    params={"mon":[30,np.arange(0,31,3)],"dek":[10,range(11)],"pent":[5,range(6)],"seas":[90, np.arange(0,90,10)]}
                    if var=="CDD":
                        vmax=params[basetime][0]
                        vmin=0
                        mx=np.nanmax(data)
                        if basetime=="mon":
                            vmax=30
                            levels=np.arange(0,31,3)
                        elif basetime=="dek":
                            vmax=10
                            levels=np.arange(0,11,2)
                        elif basetime=="pent":
                            vmax=5
                            levels=np.arange(0,6,1)
                        else:
                            vmax=90
                            levels=np.arange(0,91,10)

                        cmap_rb = plt.get_cmap('turbo')
                        cols = cmap_rb(np.linspace(0.3, 0.8, len(levels)))
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=levels
                        ticklabels=None 
                        units="days"
                        extend="max"

                    if var=="CWD":
                        vmax=params[basetime][0]
                        vmin=0
                        mx=np.nanmax(data)
                        if basetime=="mon":
                            vmax=20
                            levels=np.arange(0,21,2)
                        elif basetime=="dek":
                            vmax=10
                            levels=np.arange(0,11,1)
                        elif basetime=="pent":
                            vmax=5
                            levels=np.arange(0,6,1)
                        else:
                            vmax=90
                            levels=np.arange(0,91,10)

                        cmap_rb = plt.get_cmap('turbo_r')
                        cols = cmap_rb(np.linspace(0.2, 0.7, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=levels
                        ticklabels=None 
                        units="days"
                        extend="max"

                    if var in ["R10mm","R20mm"]:
                        vmax=10
                        levels=range(11)
                        vmin=0
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.2, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=None
                        ticklabels=None 
                        units="days"
                        extend="max"

                    if var == "R1mm":
                        maxdays={"mon":[30,[0,3,6,9,12,15,18,21,24,27,30]],"dek":[10,range(11)],"pent":[5,range(6)],"seas":[90, np.arange(0,91,10)]}
                        vmax=maxdays[basetime][0]
                        levels=maxdays[basetime][1]
                        vmin=0
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.2, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=None
                        ticklabels=None 
                        units="days"
                        extend="max"

                    if var=="SDII":
                        mx=np.nanmean(data)
                        print("mx",mx)
                        vmax=20
                        levels=np.arange(0,21,2)
                        vmin=0
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.2, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                        ticklevels=levels
                        ticklabels=levels
                        units="mm/day"
                        extend="max"




                        
            if varcat=="onset":
                if attr[-4:]=="anom":
                    seq=np.linspace(10,90,10).astype(int)
                    colorlist=[plt.get_cmap('BrBG_r', 100)(x) for x in seq]
                    colorlist[4]="white"
                    colorlist=["0.7","lightyellow"]+colorlist
                    vmin,vmax=-200,5
                    uneven_levels = [-200,-100,-5,-4,-3,-2,-1,0,1,2,3,4,5]
                    cmap, norm = colors.from_levels_and_colors(uneven_levels, colorlist, extend="neither")
                    ticklevels = [-150,-50,-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5]
                    ticklabels=["not\nanalysed","not started", '-4', '-3', '-2', '-1',"0","1","2","3","4","5"]
                    units="    dekads early     dekads late"
                    extend="neither"
                    plotbackground=True
                else:
                    vmin,vmax=-100,180
                    cols=["#EEEEEE","#224E96","#2E67AF","#4284C4","#59A3D7","#73BAE5","#8ECFF0","#8BBD9F","#A3C38F","#CBE0B7","#EAEFAA","#FBE884","#FDD76D","#FAB446","#F3692A","#E95029","#DE3828", "#C91E26","#B01A20","#921519"]
                    levels = [-100,0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180]
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                    ticklevels = [-100,0,30,60,90,120,150]
                    ticklabels=["not started", 'Sep', 'Oct', 'Nov', 'Dec', 'Jan',"Feb"]
                    units="dekad"
                    extend="neither"

            if varcat=="temperature":
                units="deg C"
                q1,q99=np.nanquantile(data,[0.05,0.95])
                rnge=q99-q1

                if attr=="index":
                    vmax=20
                    if q99>40:
                        vmax=45
                    elif q99>35:
                        vmax=40
                    elif q99>30:
                        vmax=35
                    elif q99>25:
                        vmax=30
                    elif q99>20:
                        vmax=25
                    
                    span=20
                    ncat=11
                    if rnge>20:
                        span=30
                        ncat=16 
                    vmin=vmax-span

                    levels = np.linspace(vmin,vmax,ncat)
                    cmap_rb = plt.get_cmap('RdBu_r')
                    cols = cmap_rb(np.linspace(0, 1, len(levels)+1))
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    extend="both"

                if attr=="absanom":
                    #absolute anomaly
                    if q1<-1 or q99>4:
                        vmin=-4
                        vmax=4
                        ncat=9
                        blank=[4,5]
                    else:
                        vmin=-3
                        vmax=3
                        ncat=7
                        blank=[3,4]

                    uneven_levels = np.linspace(vmin,vmax,ncat)
                    cmap_rb = plt.get_cmap('RdBu_r')
                    cols = cmap_rb(np.linspace(0, 1, len(uneven_levels)+1))
                    for b in blank:
                        cols[b]=(1,1,1,1)            
                    cmap, norm = colors.from_levels_and_colors(uneven_levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    extend="both"

            if varcat=="spi":
                vmin=-4
                vmax=4      
                levels = [-4,-3,-2,-1,1,2,3,4]        
                cmap_rb = plt.get_cmap('BrBG')
                cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                cols[4]=(1,1,1,1)
                cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                ticklevels = [-3.5,-2.5,-1.5,0,1.5,2.5,3.5]        
                ticklabels=["extremely \ndry (< -3)",
                        "very dry \n(-2 to -3)",
                        "moderately \ndry (-1 to -2)",
                        "near normal \n(1 to -1)",
                        "moderately \nwet (1 to 2)",
                        "very wet \n(2 to 3)",
                        "extremely \nwet (>3)"]
                units="SPI [-]"
                extend="both"

            if varcat=="heat wave":
                print(varcat)
                vmin=3
                mx=np.nanmax(data)
                print("hw",mx, np.nanmin(data), np.mean(data))

                if mx>30:
                    vmax=30
                    ncat=10
                elif mx>20:
                    vmax=25
                    ncat=12
                elif mx>10:
                    vmax=15
                    ncat=13
                else:
                    vmax=10
                    ncat=8
                levels = np.linspace(3,vmax,ncat)
                cmap_rb = plt.get_cmap('Reds')
                cols = cmap_rb(np.linspace(0.1, 1, len(levels)))
                cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                ticklevels=None
                ticklabels=None
                units="days"
                extend="max"
                
            if var=="seasaccum":
                print(varcat)
                vmin=0
                vmax=500    
                levels = np.linspace(vmin,vmax,11)
                cmap_rb = plt.get_cmap('YlGnBu')
                cols = cmap_rb(np.linspace(0, 1, len(levels)))
                cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                ticklevels=None
                ticklabels=None
                units="mm"
                extend="max"


            plot_map(data,
                     cmap,
                     ticklevels,
                     vmin,
                     vmax,
                     title,
                     annotation,
                     units,
                     ticklabels,
                     mask, 
                     mapfile, 
                     overlayfile, 
                     logofile,
                     norm,
                     extend,
                     plotbackground
                     )

            print("written {}".format(mapfile))
            print("done")


