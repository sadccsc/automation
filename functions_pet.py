import numpy as np
import sys
import xarray as xr
import pandas as pd
import datetime


# solar constant [ MJ m-2 min-1]
_SOLAR_CONSTANT = 0.0820

    
def do_thornthwaite(_tmeandata, _lat, _month_index, _day_of_year, _days_in_month):

#    print(_lat)
#    print(_month_index)
#    print(_day_of_year)
#    print(_days_in_month)
    _pet=np.copy(_tmeandata)
    _tmean=np.copy(_tmeandata)
    _pet[:]=np.nan
    
    if not (np.isnan(_tmean[0])):
        
        _latitude_radians=_lat*np.pi/180

        #remove months with temp below 0
        _tmean[_tmean<0]=0

        # Calculate the heat index (I)                
        _I=0
        for _mi in np.unique(_month_index):
            _I=_I+(np.mean(_tmean[_month_index==_mi])/5)**1.514

        
        _a = (6.75e-07 * _I ** 3) - (7.71e-05 * _I ** 2) + (1.792e-02 * _I) + 0.49239

        _solar_declination=solar_declination(_day_of_year)
        _sunset_hour_angle = sunset_hour_angle(_latitude_radians, _solar_declination)
        _daylight_hours=daylight_hours(_latitude_radians, _sunset_hour_angle)
                
        _pet_uncor= 10*1.6*(10.0 * _tmean / _I) ** _a
        

        _pet[:]=_pet_uncor*_days_in_month/30*_daylight_hours/12
#    print(_pet.shape)
    return _pet



   

    
def extraterrestrial_radiation(_latitude_rad, _day_of_year):
    #formula based on equation 21 in Allen et al. 1998 - FAO-56
    #_latitude_rad in radians
    #_day_of_year integer in range 1-365
    #Ra is in MJ m-2 day-1. The corresponding equivalent evaporation in mm day-1 is obtained by multiplying Ra by 0.408
    #The latitude expressed in radians is positive for the northern hemisphere and negative for the southern hemisphere.
    
    _ird=inverse_relative_distance(_day_of_year)
#    print("ird", _ird)
    
    _sol_dec=solar_declination(_day_of_year)
#    print("sd", _sol_dec)

    _sha=sunset_hour_angle(_latitude_rad, _day_of_year)
#    print("sha", _sha)
    
    Ra=24*60/np.pi*_SOLAR_CONSTANT*_ird*(_sha*np.sin(_latitude_rad)*np.sin(_sol_dec)+np.cos(_latitude_rad)*np.cos(_sol_dec)*np.sin(_sha))
    
    return Ra

def inverse_relative_distance(_day_of_year):
    #formula based on equation 23 in Allen et al. 1998 - FAO-56
    #equation 23 in Allen et al. 1998
    _ird=1+0.033*np.cos(2*np.pi*_day_of_year/366)
    return _ird


def solar_declination(_day_of_year):
    #based on equation 24 in Allen et al (1998). FAO-56
    _sd=0.409 * np.sin(((2.0 * np.pi / 365.0) * _day_of_year - 1.39))    
    return _sd


def daylight_hours(_latitude_rad, _day_of_year):
    #based on equation 34 in Allen et al (1998). FAO-56
    _dh=(24.0 / np.pi) * sunset_hour_angle(_latitude_rad, _day_of_year)
    return _dh

def sunset_hour_angle(_latitude_rad, _day_of_year):
    #based on equation 25 in Allen et al (1998) - FAO-56
    
    _sol_dec=solar_declination(_day_of_year)
    
    _cos_sha = -np.tan(_latitude_rad) * np.tan(_sol_dec)
    # Domain of arccos is -1 <= x <= 1 radians (this is not mentioned in FAO-56!)
    _cos_sha[_cos_sha<-1]=-1
    _cos_sha[_cos_sha>1]=1
    _sha=np.arccos(_cos_sha)
    return _sha 
