from csv import DictWriter
from utilities import listFields,getShp, parseFieldType
from sqlite3 import Connection
from os.path import splitext, split

def prepareCSV(outJSON,featureClass,fileType,includeGeometry):
    shp=getShp(featureClass)[0]
    fields=listFields(featureClass)
    fieldNames = []
    out = open(outJSON,"wb")
    for field in fields:
        if (fields[field] != u'OID') and field.lower() !=shp.lower():
            fieldNames.append(field)
    if includeGeometry!="none":
        fieldNames.append("geometry")
    outCSV=DictWriter(out,fieldNames,extrasaction='ignore')
    fieldObject = {}
    for fieldName in fieldNames:
        fieldObject[fieldName]=fieldName
    outCSV.writerow(fieldObject)
    return [outCSV,out]
    
def prepareSqlite(out,featureClass,fileType,includeGeometry):
    [shp,shpType]=getShp(featureClass)
    if shpType == "point":
        gType = 1
    elif shpType == "multipoint":
        gType = 4
    elif shpType == "polyline":
        gType = 5
    elif shpType == "polygon":
        gType = 6
    fields=listFields(featureClass)
    fieldNames = []
    fieldNames.append("OGC_FID INTEGER PRIMARY KEY")
    if includeGeometry:
        fieldNames.append("GEOMETRY blob")
    for field in fields:
        if (fields[field] != u'OID') and field.lower() !=shp.lower():
            fieldNames.append(parseFieldType(field,fields[field]))

    conn=Connection(out)
    c=conn.cursor()
    name = splitext(split(out)[1])[0]
    c.execute("""CREATE TABLE geometry_columns (     f_table_name VARCHAR,      f_geometry_column VARCHAR,      geometry_type INTEGER,      coord_dimension INTEGER,      srid INTEGER,     geometry_format VARCHAR )""")
    c.execute("""insert into geometry_columns( f_table_name, f_geometry_column, geometry_type, coord_dimension, srid, geometry_format) values(?,?,?,?,?,?)""",(name,"GEOMETRY",gType,2,4326,"WKB"))
    c.execute("""CREATE TABLE spatial_ref_sys        (     srid INTEGER UNIQUE,     auth_name TEXT,     auth_srid TEXT,     srtext TEXT)""")
    c.execute("insert into spatial_ref_sys(srid ,auth_name ,auth_srid ,srtext) values(?,?,?,?)",(4326, u'EPSG', 4326, u'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'))
    c.execute("create table {0}({1})".format(name,", ".join(fieldNames)))
    return [name,c,conn]
def prepareGeoJSON(outJSON,*args):
    out = open(outJSON,"wb")
    out.write("""{"type":"FeatureCollection","features":[""")
    return out
    
def prepareJSON(outJSON,*args):
    out = open(outJSON,"wb")
    out.write("""{"rows":[""")
    return out

def prepareFile(outJSON,featureClass,fileType,includeGeometry):
    if fileType == "geojson":    
        return prepareGeoJSON(outJSON,featureClass,fileType,includeGeometry)
    elif fileType == "csv":    
        return prepareCSV(outJSON,featureClass,fileType,includeGeometry)
    elif fileType == "json":    
        return prepareJSON(outJSON,featureClass,fileType,includeGeometry)
    elif fileType == "sqlite": 
        return prepareSqlite(outJSON,featureClass,fileType,includeGeometry)
    else:
        return False