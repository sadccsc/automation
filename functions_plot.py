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

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
seasons=["JFM","FMA","MAM","AMJ","MJJ","JJA","JAS","ASO","SON","OND","NDJ","DJF"]

def get_catcmap(_xrdata, _cmap, _vmin,_vmax,_ncat,_centre):
    #this generates categorical colormap
    if _vmax=="auto":
        #if vmax is to be calculated automatically
        _vmax=np.nanquantile(_xrdata.data, 0.95)
        _vmax=neat_vmax(_vmax)
    if _vmin=="auto":
        #vmin will be symmetrical around 0 to vmax
        _vmin=-_vmax
    
    _catwidth=(_vmax-_vmin)/_ncat
    _levels = list(np.arange(_vmin,_vmax,_catwidth))+[_vmax]
    
    _smax=100
    if _centre is None:
        _smin=0
    else:
        _smin=50*(1-((_centre-_vmin)/(_vmax-_vmin)))
    _step=(_smax-_smin)/_ncat
    _seq=np.arange(_smin,_smax,_step)
    _cmap=colors.ListedColormap([plt.get_cmap(_cmap, 100)(int(x)) for x in _seq])

    return({"cmap":_cmap, "levels":_levels, "vmin":_vmin, "vmax":_vmax,"ticklabels":None})


def neat_vmax(_value):
    if _value>0:
        _order=np.floor(np.log10(_value))
        _x=_value/(10**_order)
        _output=np.ceil(_x)*10**_order
    else:
       _output=0
    return _output



def plot_map(_data,_cmap,_levels,_vmin,_vmax, _title, _annotation,_cbar_label,_ticklabels, _mask, _filename, _overlayfile, _logofile, _norm=None, _extend="neither",_plotbackground=False):
    overlay = geopandas.read_file(_overlayfile)
    fig=plt.figure(figsize=(5,5))
    pl=fig.add_subplot(1,1,1, projection=ccrs.PlateCarree())
    if _mask is not None:
        _sign,_val=_mask
        if _sign=="above":
            _data=_data.where(_data<_val)
        else:
            _data=_data.where(_data>_val)
    if _plotbackground:
        overlay.plot(ax=pl, color="0.7")

    m=_data.plot(cmap=_cmap, vmin=_vmin,vmax=_vmax, add_colorbar=False, norm=_norm)
    #m=_data.plot()

    overlay.boundary.plot(ax=pl, linewidth=0.3, color="0.1")

    plt.title(_title, fontsize=9)

    ax=fig.add_axes([0.82,0.25,0.02,0.5])

    if _levels is None:
        cont=True
        cbar = fig.colorbar(m, cax=ax, label=_cbar_label, extend=_extend)
    else:
        cont=True
        cbar = fig.colorbar(m, cax=ax,ticks=_levels, label=_cbar_label, extend=_extend)

    if _ticklabels is not None:
        cbar.ax.set_yticklabels(_ticklabels)
        cbar.ax.tick_params(labelsize=7)
        cbar.ax.tick_params(size=0)   
        cbar.set_label(_cbar_label, labelpad=-10)

    logoimg = plt.imread(_logofile)
    im = OffsetImage(logoimg, zoom=0.3)
    ab = AnnotationBbox(im, (0.99, 0.99), xycoords=pl.transAxes, box_alignment=(1,1), frameon=False)
    pl.add_artist(ab)

    pl.text(0,-0.01,_annotation,fontsize=6, transform=pl.transAxes, va="top")

    plt.subplots_adjust(bottom=0.1,top=0.9,right=0.8,left=0.05)
    if _filename:
        plt.savefig(_filename, dpi=300)
#    plt.show()


def get_timeexpr(year,month,day,basetime,flimy,lclimy,attr,var,varcat):

    if attr=="clim":
        year=""
        
    if basetime=="seas":
        if attr=="clim":
            yearexpr=""
            lastmonth=month
        else:
            if month>=11:
                print(year)
                yearexpr="{}-{}".format(year,int(year)+1)
                year=int(year)+1
                lastmonth=month-11+1
            else:
                yearexpr=str(year)
                lastmonth=month+2
        timeexpr="{} {}".format(seasons[month-1],yearexpr)
        print(lastmonth)
        #lastday=(pd.DatetimeIndex([str(year)+str(lastmonth).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day
        #month=lastmonth

    if basetime=="mon":
        timeexpr="{} {}".format(months[month-1],year)
        #lastday=(pd.DatetimeIndex([str(year)+str(month).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day

    if basetime=="dek":
        if day==21:
            #this should find the last day of the month
            if attr=="clim":
                fakeyear=2024
                lastday=(pd.DatetimeIndex([str(fakeyear)+str(month).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day
            else:
                lastday=(pd.DatetimeIndex([str(year)+str(month).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day
        else:
            lastday=int(day)+9
        timeexpr="{} to {} {} {}".format(day,lastday,months[month-1],year)

    if basetime=="pent":
        if day==26:
            if attr=="clim":
                fakeyear=2024
                lastday=(pd.DatetimeIndex([str(fakeyear)+str(month).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day
            else:
                lastday=(pd.DatetimeIndex([str(year)+str(month).zfill(2)+str(day).zfill(2)])+pd.offsets.MonthEnd())[0].day
        else:
            lastday=int(day)+4
        timeexpr="{} to {} {} {}".format(day,lastday,months[month-1],year)

    if varcat=="onset":
        timeexpr="by {} {} {}".format(lastday,months[month-1],year)

    print("timeexpr", timeexpr)
    return timeexpr


