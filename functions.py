import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import *
engine = create_engine("mysql://mesa:me5asadc@localhost/products", echo=False)
conn = engine.connect()

metadata = MetaData()
table_metadata = Table('metadata', metadata, autoload=True, autoload_with=engine)
table_paths = Table('paths', metadata, autoload=True, autoload_with=engine)
table_mapset = Table('mapset', metadata, autoload=True, autoload_with=engine)
table_colormap = Table('colormap', metadata, autoload=True, autoload_with=engine)

def get_id_mapset():
  s = select([table_metadata.c.id,table_metadata.c.mapset])
  try:
    return conn.execute(s).fetchall()
  except:
    return None


def get_name(prod):
  s = select([table_metadata.c.name]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_masked(prod):
  s = select([table_metadata.c.masked]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_postfix(prod):
  s = select([table_metadata.c.postfix]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_indir(prod):
  s = select([table_paths.c.input]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_outdir(prod):
  s = select([table_paths.c.output]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_source(prod):
  s = select([table_metadata.c.source]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_format(prod):
  s = select([table_metadata.c.img_format]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_colormap(prod):
  s = select([table_colormap.c.file]).where((table_colormap.c.id == prod) & (table_colormap.c.default == 1))
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_extent(mapset):
  s = select([table_mapset.c.xmin, table_mapset.c.xmax, table_mapset.c.ymin, table_mapset.c.ymax]).where(table_mapset.c.mapset == mapset)
  try:
    return conn.execute(s).fetchall()
  except:
    return None

def get_pathdated(prod):
  s = select([table_paths.c.dated]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_dateformat(prod):
  s = select([table_metadata.c.date_format]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_qmldir(prod):
  s = select([table_paths.c.colormap]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_mask(mapset):
  s = select([table_mapset.c.mask_layer,table_mapset.c.mask_attr]).where(table_mapset.c.mapset == mapset)
  try:
    return conn.execute(s).fetchall()
  except:
    return None

def get_inputregex(prod):
  s = select([table_paths.c.inputregex]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_date2col(prod):
  s = select([table_metadata.c.date2_col]).where(table_metadata.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_namedelim(prod):
  s = select([table_paths.c.name_delim]).where(table_paths.c.id == prod)
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_plotter(prod):
  s = select([table_colormap.c.plot]).where((table_colormap.c.id == prod) & (table_colormap.c.default == 1))
  try:
    return conn.execute(s).fetchall()[0][0]
  except:
    return None

def get_mapsets():
  s = select([table_mapset.c.mapset])
  try:
    return conn.execute(s).fetchall()
  except:
    return None



