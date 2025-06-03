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

wetday=1

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
    "spi1": "1-month Standardized Precipitation Index (SPI)",
    "spi3": "3-month Standardized Precipitation Index (SPI)",
    "spi6": "6-month Standardized Precipitation Index (SPI)",
    "spi12": "12-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
    "spi36": "36-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
    "spei1": "1-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
    "spei3": "3-month SPEI index",
    "spei6": "6-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
    "spei12": "12-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
    "spei36": "36-month Standardized Precipitation-Evapotranspiration Index (SPEI)",
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
    "spei1": "spi",
    "spei3": "spi",
    "spei6": "spi",
    "spei12": "spi",
    "spei36": "spi",
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
        datafiles.append([day,datafile])
    if basetime=="mon":
        datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
        datafiles.append([day,datafile])
    if basetime=="dek":
        for firstday in [1,11,21]:
            datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
            datafiles.append([firstday,datafile])
    if basetime=="pent":
        for firstday in [1,6,11,16,21,26]:
            datafile="{}/{}_{}{}_{}_{}_{}-{}.nc".format(inputdir,var, basetime,attrfilecode, dataset,domain,climstartyear,climendyear)
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
            #this just removes the climatology years from the file name
            filename="_".join(filename.split("_")[:-1])
            mapfile="{}/{}.{}".format(outputdir,filename,"png")
        elif attr in ["clim"]:
            if basetime in ["mon","seas"]:
                mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc","_{}.png".format(month)))
            elif basetime=="dek":
                dekadcodes={1:1,11:2,21:3}
                dekad=dekadcodes[day]
                mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc","_{}-{}.png".format(month,dekad)))
            elif basetime=="pent":
                pentadcodes={1:1,6:2,11:3,16:4,21:5,26:6}
                pentad=pentadcodes[day]
                mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc","_{}-{}.png".format(month,pentad)))
            else:
                print("basetime not available {}".format(basetime))
                sys.exit()
        else:
            #this will be index
            mapfile="{}/{}".format(outputdir,os.path.basename(datafile).replace(".nc",".png"))


        # this makes sure the mapfile format corresponds to what website can handle
        elems=mapfile.split("_")
        mapfile="_".join(["-".join(elems[0:3]),"_".join(elems[3:])])

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
                if basetime in ["mon","seas"]:
                    data=data.sel(month=monthval)
                elif basetime=="dek":
                    dekadval=(monthval-1)*3+dekad
                    data=data.sel(dekad=dekadval)
                elif basetime=="pent":
                    pentadval=(monthval-1)*6+pentad
                    data=data.sel(pentad=pentadval)

                ds[var]=data

            if var=="spi3":
                data=ds[var].load()
                data=data.where(~np.isnan(data),-4)
                ds[var]=data
                
            if var=="CDD":
                data=ds[var].load()
                data=data.where(~np.isnan(data),31)
                ds[var]=data

            if var=="CWD":
                data=ds[var].load()
                data=data.where(~np.isnan(data),0)
                ds[var]=data

            if var=="PRCPTOT-percnormanom":
                data=ds[var].load()
                data=data.where(~np.isnan(data),0)
                ds[var]=data

            #for some reason,clipping is done AFTER "preprocessing"
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
            #defined separately for different varcat value, attr values and var values

            if varcat=="precipitation":

                if attr=="relanom":
                    vmin=10
                    vmax=190
                    extend="both"
                    levels = [10,30,50,70,90,110,130,150,170,190]
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cols[5]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                    ticklevels=None
                    ticklabels=None
                    units="% of long-term mean"

                elif attr=="absanom":
                    vmin=-100
                    vmax=100
                    extend="both"
                    levels = np.linspace(vmin,vmax,21)    
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cols[10]=(1,1,1,1)
                    cols[11]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                    levels=None
                    ticklabels=None
                    units="mm"

                elif attr=="percnormanom":
                    if var=="PRCPTOT":
                        extend="max"
                        vmin,vmax=-10000,200
                        seq=np.arange(0,205,10).astype(int)
                        seq=[0,10,30,50,70,90,110,130,150,170,190,200]
                        cmap_rb = plt.get_cmap('BrBG')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(seq)))
                        colorlist=list(cols)

                        #colorlist=[plt.get_cmap('BrBG', 100)(x) for x in seq]
                        colorlist[5]="white"
                        colorlist=["lightyellow"]+colorlist
                        levels = [-10000]+list(seq)
                        cmap, norm = colors.from_levels_and_colors(levels, colorlist, extend=extend)
                        ticklevels = levels
                        ticklabels=["dry\nclimato-\nlogy"]+[str(x) for x in list(seq)]
                        units="% of long-term mean"
                        plotbackground=True
                        annotation="{}\nRegions where climatological rainfall is less than {}mm are masked out".format(annotation,wetday)

                    else:
                        vmin=10
                        vmax=190
                        extend="both"
                        levels = [10,30,50,70,90,110,130,150,170,190]
                        cmap_rb = plt.get_cmap('BrBG')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                        cols[5]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=None
                        ticklabels=None
                        units="% of long-term mean"


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
                    #this is when index is requested

                    if var=="PRCPTOT":
                        extend="max"
                        vmin=0
                        #this self-adjusts to the nearest 100
                        #high value
                        highval=np.nanpercentile(data, 95)
                        #vmax will be highest 100 that is less than the highval
                        vmax=int(highval/100)*100
                        #this just makes sure the max value is not 0, It has to be at least 100
                        if vmax<100:
                            vmax=100

                        levels = np.linspace(vmin,vmax,11)    
                        cmap_rb = plt.get_cmap("YlGnBu")
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels))) #ncolors is same as levels if extend is one sided, i.e. max or min 

                        #this is original CSC colour map
                        #levels = [0,1,10,25,50,75,150,225,300]
                        #cols=["#FFFFFF","#C6C618","#FEFE00","#00FF00","#10FAF7","#0F17FF","#F273E4","#841F89","#590059"]

                        #thisis original BOM colour map
                        #cols=["#FFFFFF","#FEBE59","#FEAC00","#FEFE00","#B2FE00","#4CFE00","#00E499","#00A4FE","#3E3EFE","#B200FE","#FE00FE","#FE4C9B"]

                        #this is a reduced BOM map that fits the csc categories
                        #cols=["#FFFFFF","#FEFE00","#B2FE00","#4CFE00","#00E499","#00A4FE","#3E3EFE","#B200FE","#FE4C9B"]

                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=None
                        ticklabels=None 
                        units="mm"

                    if var=="Rx1day":
                        vmin=0
                        vmax=150
                        levels = [0,25,50,70,80,90,100,150]
                        extend="max"
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0, 1, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=None
                        ticklabels=None 
                        units="mm/day"

                    if var=="Rx5day":
                        vmin=0
                        vmax=200
                        levels = [0,25,50,70,80,90,100,200]
                        extend="max"
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0, 1, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=None
                        ticklabels=None 
                        units="mm/day"


                    if var=="CDD":
                        vmin=0
                        extend="max"
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
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None 
                        units="days"

                    if var=="CWD":
                        vmin=0
                        extend="max"
                        #vmaxes are reduced for monthly and seasonal as wet days will never be entire month or season
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
                            vmax=30
                            levels=np.arange(0,31,3)

                        cmap_rb = plt.get_cmap('turbo_r')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None 
                        units="days"

                    if var =="R20mm":

                        vmin=0
                        extend="max"

                        if basetime=="mon":
                            vmax=10
                            levels=np.arange(0,11,2)
                        elif basetime=="dek":
                            vmax=10
                            levels=np.arange(0,11,1)
                        elif basetime=="pent":
                            vmax=5
                            levels=np.arange(0,6,1)
                        else:
                            vmax=20
                            levels=np.arange(0,21,2)

                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None 
                        units="days"

                    if var =="R10mm":

                        vmin=0
                        extend="max"

                        if basetime=="mon":
                            vmax=10
                            levels=np.arange(0,11,1)
                        elif basetime=="dek":
                            vmax=10
                            levels=np.arange(0,11,1)
                        elif basetime=="pent":
                            vmax=5
                            levels=np.arange(0,6,1)
                        else:
                            vmax=30
                            levels=np.arange(0,31,3)

                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None 
                        units="days"



                    if var == "R1mm":
                        vmin=0
                        extend="max"
                        if basetime=="mon":
                            vmax=30
                            levels=np.arange(0,31,3)
                        elif basetime=="dek":
                            vmax=10
                            levels=np.arange(0,11,1)
                        elif basetime=="pent":
                            vmax=5
                            levels=np.arange(0,6,1)
                        else:
                            vmax=50
                            levels=np.arange(0,51,5)

                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None 
                        units="days"

                    if var=="SDII":
                        vmin=0
                        extend="max"

                        highval=np.nanpercentile(data, 95)
                        #vmax will be highest 10 that is less than the highval
                        vmax=int(highval/10)*10
                        #this just makes sure the max value is not 0, It has to be at least 100
                        if vmax<10:
                            vmax=10

                        levels = np.linspace(vmin,vmax,11)    
                        cmap_rb = plt.get_cmap('YlGnBu')
                        cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)))
                        cols[0]=(1,1,1,1)
                        cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                        ticklevels=levels
                        ticklabels=None
                        units="mm/day"

                        
            if varcat=="onset":
                #this is for anomaly
                if attr[-4:]=="anom":
                    seq=np.linspace(10,90,10).astype(int)
                    colorlist=[plt.get_cmap('BrBG_r', 100)(x) for x in seq]
                    colorlist[4]="white"
                    colorlist=["0.7","lightyellow"]+colorlist
                    vmin,vmax=-200,5
                    uneven_levels = [-200,-100,-5,-4,-3,-2,-1,0,1,2,3,4,5]
                    cmap, norm = colors.from_levels_and_colors(uneven_levels, colorlist, extend="neither")
                    ticklevels = [-150,-50,-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5]
                    ticklabels=["not\nanalysed","not\nstarted", '-4', '-3', '-2', '-1',"0","1","2","3","4","5"]
                    units="    dekads early     dekads late"
                    extend="neither"
                    plotbackground=True
                else:
                #this is for index
                    vmin,vmax=-100,180
                    cols=["#EEEEEE","#224E96","#2E67AF","#4284C4","#59A3D7","#73BAE5","#8ECFF0","#8BBD9F","#A3C38F","#CBE0B7","#EAEFAA","#FBE884","#FDD76D","#FAB446","#F3692A","#E95029","#DE3828", "#C91E26","#B01A20","#921519"]
                    levels = [-100,0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180]
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                    ticklevels = [-100,0,30,60,90,120,150]
                    ticklabels=["not\nstarted", 'Sep', 'Oct', 'Nov', 'Dec', 'Jan',"Feb"]
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
                    ncat=21
                    if rnge>20:
                        span=30
                        ncat=16

                    vmin=vmax-span

                    levels = np.linspace(vmin,vmax,ncat)
                    cmap_rb = plt.get_cmap('RdBu_r')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(levels)+1))
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    extend="both"

                if attr=="absanom":
                    #absolute anomaly
                    vmin=-4
                    vmax=4
                    levels=np.arange(vmin,vmax+0.1,0.5)
                    extend="both"
                    cmap_rb = plt.get_cmap('RdBu_r')
                    cols = cmap_rb(np.linspace(0, 1, len(levels)+1))
                    cols[8]=(1,1,1,1)            
                    cols[9]=(1,1,1,1)
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend=extend)
                    ticklevels=None
                    ticklabels=None
                    extend="both"


                if attr=="clim":
                    if q1<10:
                        vmin=5
                        vmax=25
                    elif q1<15:
                        vmin=10
                        vmax=30
                    else:
                        vmin=15
                        vmax=35
                    ncat=21
                    uneven_levels = np.linspace(vmin,vmax,ncat)
                    cmap_rb = plt.get_cmap('RdBu_r')
                    cols = cmap_rb(np.linspace(0, 1, len(uneven_levels)+1))
                    cmap, norm = colors.from_levels_and_colors(uneven_levels, cols, extend="both")
                    ticklevels=None
                    ticklabels=None
                    extend="both"


            if varcat in ["spi","spei"]:
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
                vmin=3
                mx=np.nanmax(data)

                if mx>48:
                    vmax=48
                    ncat=10
                elif mx>39:
                    vmax=39
                    ncat=10
                elif mx>30:
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
                
            if varcat=="seasaccum":
                if attr=="index":
                    highval=np.nanpercentile(data, 95)
                    vmax=int(highval/100)*100
                    vmin=0
                    if vmax<100:
                        vmax=100
                    print(highval, vmax)

                    levels = np.linspace(vmin,vmax,11)
                    cmap_rb = plt.get_cmap('YlGnBu')
                    cols = cmap_rb(np.linspace(0, 1, len(levels)))
                    cmap, norm = colors.from_levels_and_colors(levels, cols, extend="max")
                    ticklevels=None
                    ticklabels=None
                    units="mm"
                    extend="max"

                elif attr=="relanom":
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
                    extend="max"
                    vmin,vmax=-100000,200
                    seq=np.arange(0,205,10).astype(int)
                    seq=[0,10,30,50,70,90,110,130,150,170,190,200]
                    cmap_rb = plt.get_cmap('BrBG')
                    cols = cmap_rb(np.linspace(0.1, 0.9, len(seq)))
                    colorlist=list(cols)

                    colorlist[5]="white"
                    colorlist=["0.7","lightyellow"]+colorlist
                    levels = [-100000,-10000]+list(seq)
                    cmap, norm = colors.from_levels_and_colors(levels, colorlist, extend=extend)
                    ticklevels = [-50000,-5000]+list(seq)
                    ticklabels=["not considered","normally dry"]+[str(x) for x in list(seq)]
                    units="% of long-term mean"
                    plotbackground=True
                    annotation="{}\nRegions where climatological rainfall is less than {}mm are masked out".format(annotation,wetday)
                    annotation="{}\nCalculated only for {} rainfall regime".format(annotation, regime)



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


