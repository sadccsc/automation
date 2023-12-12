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


def get_dekad(_date):
    _month=_date.month
    _day=_date.day
    dekad=np.ceil(_day/10).astype(int)
    if dekad==4:
        dekad=3
    dekad=dekad+(_month-1)*3
    return(dekad)


def get_pentad(_date):
    _month=_date.month
    _day=_date.day
    pentad=np.ceil(_day/5).astype(int)
    if pentad==7:
        pentad=6
    pentad=pentad+(_month-1)*6
    return(pentad)


def val_to_quantanom(_val,_obs):
    _out=np.copy(_val)
    if np.sum(np.isnan(_val))==0:
        _val=_val[np.invert(np.isnan(_val))]
        _out=(_obs <= _val).mean().reshape(-1)
    return(_out)
