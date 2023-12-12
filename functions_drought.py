from climate_indices import indices, compute

def calcspi(_prec, _scale,_dist,_freq,_fyear,_cfyear,_ceyear):
    dist={"gamma":indices.Distribution.gamma, "pearson":indices.Distribution.pearson}
    freq={"monthly":compute.Periodicity.monthly, "daily":compute.Periodicity.daily}
    _spi = indices.spi(_prec,  _scale, dist[_dist], _fyear, _cfyear, _ceyear,freq[_freq])
    return(_spi)

def spionpandas(_prec, _scale,_fyear,_cfyear,_ceyear,_freq="monthly",_dist="gamma"):
    _spipd=_prec.copy()
    for i in range(_spipd.shape[1]):
        _spipd.iloc[:,i]=calcspi(_prec.iloc[:,i].values,_scale,_dist,_freq,_fyear,_cfyear,_ceyear)
    return(_spipd)

def petonpandas(_tas, _fyear,_lat=7):
    _petpd=_tas.copy()
    for i in range(_petpd.shape[1]):
        _petpd.iloc[:,i]=calcpet(_tas.iloc[:,i].values,_lat,_fyear)
    return(_petpd)

def calcspei(_prec,_temp, _lat, _scale,_dist,_freq,_fyear,_cfyear,_ceyear):
    _pet=calcpet(_temp,_lat,_fyear)
    dist={"gamma":indices.Distribution.gamma, "pearson":indices.Distribution.pearson}
    freq={"monthly":compute.Periodicity.monthly, "daily":compute.Periodicity.daily}
    _spei = indices.spei(_prec, _pet, _scale, dist[_dist], freq[_freq], _fyear, _cfyear, _ceyear)
    return(_spei)

def speionpandas(_prec,_tas, _scale,_fyear,_cfyear,_ceyear,_freq="monthly",_dist="gamma",_lat=7):
    _speipd=_prec.copy()
    for i in range(_speipd.shape[1]):
        _speipd.iloc[:,i]=calcspei(_prec.iloc[:,i].values,_tas.iloc[:,i].values,_lat,_scale,_dist,_freq,_fyear,_cfyear,_ceyear)
    return(_speipd)

def calcpet(_data,_lat,_fyear):
    _pet=indices.pet(_data, _lat, _fyear)
    #print(_pet)
    return(_pet)


