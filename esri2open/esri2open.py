# ---------------------------------------------------------------------------
# esri2open.py
# Created on: March 11, 2013
# Created by: Michael Byrne
# Federal Communications Commission
# exports the feature classes for any feature class to
# a csv file, JSON file or geoJSON file 
# also adding edits from sgillies and Shaun Walbridge
# updates include using the python json.dumps method and indentation issues
# Edit by Calvin Metcalf to merge in improvments made for exporting
# Massachusetts Department Of Transportation Data
# edits made 4/8/2013
# ---------------------------------------------------------------------------
#imports
from arcpy import AddMessage, GetCount_management
from utilities import getExt, listFields,getShp, parseProp, parseFieldType
from parseRow import parse
from csv import DictWriter
from json import dump
from sqlite3 import Connection
from os.path import splitext, split

#----
#prepare files
#----
def prepareCSV(outJSON,featureClass,fileType,includeGeometry):
    shp=getShp(featureClass)[0]
    fields=listFields(featureClass)
    fieldNames = []
    out = open(outJSON,"wb")
    for field in fields:
        if (fields[field] != u'OID') and field.lower() not in ('shape_length','shape_area','shape.len','shape.length','shape_len','shape.area',shp.lower()):
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
    for field in fields:
        if (fields[field] != u'OID') and field.lower() not in ('shape_length','shape_area','shape.len','shape.length','shape_len','shape.area',shp.lower()):
            fieldNames.append(parseFieldType(field,fields[field]))
    if includeGeometry:
        fieldNames.append("GEOMETRY blob")
    conn=Connection(out.name)
    c=conn.cursor()
    c.execute("""CREATE TABLE spatial_ref_sys (
             srid INTEGER UNIQUE,
             auth_name TEXT,
             auth_srid INTEGER,
             srtext TEXT  )""")
    c.execute("insert into spatial_ref_sys(srid ,auth_name ,auth_srid ,srtext) values(?,?,?,?)",(4326, u'EPSG', 4326, u'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'))
    name = splitext(split(out.name)[1])[0]
    c.execute("""CREATE TABLE geometry_columns (
            f_table_name TEXT, 
            f_geometry_column TEXT, 
            geometry_type INTEGER, 
            coord_dimension INTEGER, 
            srid INTEGER,
            geometry_format TEXT )""")
    c.execute("""insert into geometry_columns( f_table_name, f_geometry_column, geometry_type, coord_dimension, srid,geometry_format) values(?,?,?,?,?,?)""",(name,"GEOMETRY",gType,2,4326))
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
#----
#close file
#----
def closeJSON(out):
    out.write("""]}""")
    out.close()
    return True
    
def closeSqlite(out):
    out[2].commit()
    out[1].close()
    return True
    
def closeCSV(out):
    out[1].close()
    return True

def closeUp(out,fileType):
    if fileType == "geojson":    
        return closeJSON(out)
    elif fileType == "csv":    
        return closeCSV(out)
    if fileType == "json":    
        return closeJSON(out)
    else:
        return False

#this is the meat of the function, we could put it into a seperate file if we wanted
def writeFile(outArray,featureClass,fileType,includeGeometry, first=True):
    parser = parse(outArray,featureClass,fileType,includeGeometry,first)
    #wrap it in a try so we don't lock the database
    try:
        for row in parser.rows:
            #parse row
            parser.parse(row)
    except Exception as e:
        #using chrome has rubbed off on me
        AddMessage("OH SNAP! " + str(e))
    finally:
        #clean up
        return parser.cleanUp(row)

#this is the main entry point into the module
def toOpen(featureClass, outJSON, includeGeometry="geojson"):
    #check the file type based on the extention
    fileType=getExt(outJSON)
    #some sanity checking
    #valid geojson needs features, seriously you'll get an error
    if not int(GetCount_management(featureClass).getOutput(0)):
        AddMessage("No features found, skipping")
        return
    elif not fileType:
        AddMessage("this filetype doesn't make sense")
        return
    #geojson needs geometry
    if fileType=="geojson":
        includeGeometry="geojson"
    elif fileType=="sqlite":
        includeGeometry="well know binary"
    else:
        includeGeometry=includeGeometry.lower()
    #open up the file
    outFile=prepareFile(outJSON,featureClass,fileType,includeGeometry)
    #outFile will be false if the format isn't defined
    if not outFile:
        AddMessage("I don't understand the format")
        return
    #write the rows
    writeFile(outFile,featureClass,fileType,includeGeometry)
    #go home
    closeUp(outFile,fileType)
