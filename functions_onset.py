import numpy as np


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
        if _spell=="dry":
            _runs[_temp>0]=0
        else:
            _runs[_temp==0]=0
        return(_runs)
    else:
        return(_temp)
    
#In this study the onset of rains is defined as the last day starting from July each year in
#which rainfall of 25mm or above has been accumulated over the previous ten days and also
#at least 20mm has to be accumulated in the subsequent 20 days (Reason et al., 2005;
#Tadross et al., 2005). 

#The day considered to be rainy if observed at least 1 mm, 
#the accumulated rainfall total of 20 mm over 5 days with at least 3 rain days and dry 
#spell not exceeding 7 days in the next 21 days
#omay et al. 2023
#https://link.springer.com/article/10.1007/s00704-023-04433-0

def get_onsetA(_data,_climystart):
#A 25 mm of accumulated rainfall in 10 days - Tadross 2007
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data))==0:
        #moving sum
        _data=np.convolve(_data, np.ones(10), "same")
        if len(_data)>365+_climystart:
            fday=365+_climystart
        else:
            fday=_climystart
        _data=_data[int(fday):]
        if np.max(_data)>=25:
            _onset=np.where(_data>=25)[0][0]
        else:
            _onset=-99            
    else:
        _onset=np.nan
    return _onset

def get_onsetB(_data0,_climystart):
#B 25 mm of accumulated rainfall in 10 days, not
#followed by a period of 10 consecutive days with
#observed rainfall < 2 mm in the following 20 days
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data0))==0:
        #moving sum
        _data=np.convolve(_data0, np.ones(10), "same")
        if len(_data)>365+_climystart:
            fday=365+_climystart
        else:
            fday=_climystart
        _data=_data[int(fday):]
        if np.max(_data)>=25:
            _onset=-99
            _onsets=np.where(_data>=25)[0]
            for _onsetcandidate in _onsets:
                #next 20 days
                if _onsetcandidate+20<=len(_data):
                    _window=_data0[_onsetcandidate:_onsetcandidate+20]
                    _spell=get_spells(_window,1,"dry")
                    if max(_spell)<10:
                        _onset=(_onsetcandidate)
                        break
        else:
            _onset=-99
    else:
        _onset=np.nan
    return _onset


def get_onsetC(_data,_climystart):
#C 45 mm of accumulated rainfall in 4 days
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data))==0:
        #moving sum over 4 days, the first 3 values will be Nan
        _data=np.convolve(_data, np.ones(4), "same")
        if len(_data)>365+_climystart:
            fday=365+_climystart
        else:
            fday=_climystart
        _data=_data[int(fday):]
        if np.max(_data)>=45:
            _onset=np.where(_data>=45)[0][0]
        else:
            _onset=-99
    else:
        _onset=np.nan
    return _onset


def get_onsetD(_data,_climystart,_leapfirst,_leapsecond):
    _ydays=365
    if _leapfirst:
        _ydays=366
    _climystart=_climystart
    if _leapsecond and _climystart>=60:
        _ydays=366       
    #C 45 mm of accumulated rainfall in 4 days
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data))==0:
    #moving sum over 4 days, the first 3 values will be Nan
        _data=np.convolve(_data, np.ones(3), "same")
        if len(_data)>_ydays+_climystart-1:
            _fday=_ydays+_climystart-1
        else:
            _fday=_climystart-1
        _data=_data[int(_fday):]
        if np.max(_data)>=20:
            _onset=-99
            _onsets=np.where(_data>=20)[0]
            #print(_onsets)
            for _onsetcandidate in _onsets:
                #next 10 days
                if _onsetcandidate+10<=len(_data):
                    _window=_data[_onsetcandidate:_onsetcandidate+10]
                    _spell=get_spells(_window,1,"dry")
                    if max(_spell)<10:
                        _onset=(_onsetcandidate)
                        break
        else:
            _onset=-99
    else:
        _onset=np.nan
    return _onset

def get_onsetD_old(_data0,_climystart):
#D 20mm threshold over 3 days and no dry spell in the next 10 days
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data0))==0:
        #moving sum
        _data=np.convolve(_data0, np.ones(3), "same")
        if len(_data)>365+_climystart:
            fday=365+_climystart
        else:
            fday=_climystart
        _data=_data[int(fday):]
        if np.max(_data)>=20:
            _onset=-99
            _onsets=np.where(_data>=20)[0]
            #print(_onsets)
            #sys.exit()
            for _onsetcandidate in _onsets:
                #next 10 days
                if _onsetcandidate+10<=len(_data):
                    _window=_data0[_onsetcandidate:_onsetcandidate+10]
                    _spell=get_spells(_window,1,"dry")
                    if max(_spell)<10:
                        _onset=(_onsetcandidate)
                        break
        else:
            _onset=-99
    else:
        _onset=np.nan
    return _onset


