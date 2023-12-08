import numpy as np


def get_seasaccum(_data,_climystart,_leapfirstyr,_leapsecondyr):
    if ~np.isnan(_climystart) and np.sum(np.isnan(_data))==0:
        _ydays=365
        if _leapfirstyr:
            _ydays=366
            
        if _leapsecondyr and _climystart>=60:
            _ydays=366

        if len(_data)>_ydays+_climystart:
            _fday=_ydays+_climystart-1
        else:
            _fday=_climystart-1
        _data=_data[int(_fday):]
        _output=np.sum(_data)

    else:
        _output=np.nan
    return _output


