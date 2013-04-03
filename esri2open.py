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
# edits made 4/3/2013
# ---------------------------------------------------------------------------
from arcpy import ListFields,Describe, SetProgressorLabel,SetProgressorPosition,GetCount_management,SetProgressor,AddMessage,SpatialReference,SearchCursor
from csv import DictWriter
from json import dump
#uncomment the following line and comment the final line to use in the console
#arcpy.env.workspace = os.getcwd()
wgs84="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"

def listFields(featureClass):
    fields=ListFields(featureClass)
    out=dict()
    for fld in fields:
        out[fld.name]=fld.type
    return out
def getShp(shp):
    desc = Describe(shp)
    return [desc.ShapeFieldName,desc.shapeType.lower()]
def getOID(fields):
    for key, value in fields.items():
        if value== u'OID':
            return key
def statusMessage(total,current,last):
    newPercent = int((current*100)/total)
    if newPercent == last:
        return last
    else:
        SetProgressorLabel("{0}% done".format(str(newPercent)))
        SetProgressorPosition(newPercent)
        return newPercent
def parseProp(row,fields, shp):
    out=dict()
    for field in fields:
        if (fields[field] != u'OID') and field.lower() not in ('shape_length','shape_area','shape.len','shape.length','shape_len','shape.area',shp.lower()) and row.getValue(field) is not None:
            if fields[field] == "Date":
                value = str(row.getValue(field).date())
            elif fields[field] == "String":
                value = row.getValue(field).strip()
            else:
                value = row.getValue(field)
            if value != "":
                out[field]=value
    return out
def parseLineGeom(line):
    out=[]
    lineCount=line.count
    if lineCount ==1:
        return ["Point",[line[0].X,line[0].Y]]
    i=0
    while i<lineCount:
        pt=line[i]
        out.append([pt.X,pt.Y])
        i+=1
    if len(out)==2 and out[0]==out[1]:
        return ["Point",out[0]]
    return ["LineString",out]
def parsePolyGeom(poly):
    out=[]
    polyCount=poly.count
    i=0
    polys=[]
    while i<polyCount:
        pt=poly[i]
        if pt:
            out.append([pt.X,pt.Y])
        else:
            polys.append(out)
            out=[]
        i+=1
    polys.append(out)
    if len(polys[0])==3:
        return ["LineString", polys[0][:2]]
    if len(polys[0])<3:
        return ["Point",polys[0][0]]
    return ["Polygon",polys]
def parsePoint(geometry):
    geo=dict()
    geo["type"]="Point"
    geo["coordinates"]=[geometry.firstPoint.X,geometry.firstPoint.Y]
    return geo
def parseMultiPoint(geometry):
    if geometry.pointCount == 1:
        return parsePoint(geometry)
    else:
        geo=dict()
        geo["type"]="MultiPoint"
        points=[]
        pointCount=geometry.pointCount
        i=0
        while i<pointCount:
            point=geometry.getPart(i)
            points.append([point.X,point.Y])
            i+=1
        geo["coordinates"]=points
        return geo
def parseLineString(geometry):
    geo=dict()
    outLine=parseLineGeom(geometry.getPart(0))
    geo["type"]=outLine[0]
    geo["coordinates"]=outLine[1]
    return geo
def parseMultiLineString(geometry):
    if geometry.partCount==1:
        return parseLineString(geometry)
    else:
        lineGeo=dict()
        points=[]
        lines=[]
        lineCount=geometry.partCount
        i=0
        while i<lineCount:
            outLine = parseLineGeom(geometry.getPart(i))
            if outLine[0]=="LineString":
                lines.append(outLine[1])
            elif outLine[1]=="Point":
                points.append(outLine[1])
            i+=1
        if lines:
            if len(lines)==1:
                lineGeo["type"]="LineString"
                lineGeo["coordinates"]=lines[0]
            else:
                lineGeo["type"]="MultiLineString"
                lineGeo["coordinates"]=lines
        if points:
            pointGeo={}
            pointGeo["coordinates"]=points
            if len(pointGeo["coordinates"])==1:
                pointGeo["coordinates"]=pointGeo["coordinates"][0]
                pointGeo["type"]="Point"
            else:
                pointGeo["type"]="MultiPoint"
        if lines and not points:
            return lineGeo
        elif points and not lines:
            return pointGeo
        elif points and lines:
            out = {}
            out["type"]="GeometryCollection"
            out["geometries"] = [pointGeo,lineGeo]
            return out
        else:
            return {}
def parsePolygon(geometry):
    geo={}
    outPoly = parsePolyGeom(geometry.getPart(0))
    geo["type"]=outPoly[0]
    geo["coordinates"]=outPoly[1]
    return geo
def parseMultiPolygon(geometry):
    if geometry.partCount==1:
        return parsePolygon(geometry)
    else:
        polys=[]
        lines=[]
        points=[]
        polyCount=geometry.partCount
        i=0
        while i<polyCount:
            polyPart = parsePolyGeom(geometry.getPart(i))
            if polyPart[0]=="Polygon":
                polys.append(polyPart[1])
            elif polyPart[0]=="Point":
                points.append(polyPart[1])
            elif polyPart[0]=="LineString":
                lines.append(polyPart[1])
            i+=1
        num = 0
        if polys:
            polyGeo={}
            num+=1
            polyGeo["coordinates"]=polys
            if len(polyGeo["coordinates"])==1:
                polyGeo["coordinates"]=polyGeo["coordinates"][0]
                polyGeo["type"]="Polygon"
            else:
                polyGeo["type"]="MultiPolygon"
        if points:
            num+=1
            pointGeo={}
            pointGeo["coordinates"]=points
            if len(pointGeo["coordinates"])==1:
                pointGeo["coordinates"]=pointGeo["coordinates"][0]
                pointGeo["type"]="Point"
            else:
                pointGeo["type"]="MultiPoint"
        if lines:
            num+=1
            lineGeo={}
            lineGeo["coordinates"]=lineGeo
            if len(lineGeo["coordinates"])==1:
                lineGeo["coordinates"]=lineGeo["coordinates"][0]
                pointGeo["type"]="LineString"
            else:
                pointGeo["type"]="MultiLineString"
        if polys and not points and not lines:
            return polyGeo
        elif points and not polys and not lines:
            return pointGeo
        elif lines and not polys and not points:
            return lineGeo
        elif num>1:
            out = {}
            out["type"]="GeometryCollection"
            outGeo = []
            if polys:
                outGeo.append(polyGeo)
            if points:
                outGeo.append(pointGeo)
            if lines:
                outGeo.append(lineGeo)
            out["geometries"]=outGeo
            return out
        else:
            return {}
def parseMultiPatch():
    return {}
def prepareGeoJson(out):
    out.write("""{"type":"FeatureCollection","features":[""")
    return out
def prepareJson(out):
    out.write("""{"rows":[""")
    return out
def prepareCsv(out,featureClass,fileType,includeGeometry):
    shp=getShp(featureClass)[0]
    fields=listFields(featureClass)
    fieldNames = []
    for field in fields:
        if (fields[field] != u'OID') and field.lower() not in ('shape_length','shape_area','shape.len','shape.length','shape_len','shape.area',shp.lower()):
            fieldNames.append(field)
    if includeGeometry:
        fieldNames.append("geometry")
    outCSV=DictWriter(out,fieldNames,extrasaction='ignore')
    fieldObject = {}
    for fieldName in fieldNames:
        fieldObject[fieldName]=fieldName
    outCSV.writerow(fieldObject)
    return outCSV
def prepareFile(out,featureClass,fileType,includeGeometry):
    if fileType=="geojson":
        return prepareGeoJson(out)
    elif fileType=="csv":
        return prepareCsv(out,featureClass,fileType,includeGeometry)
    elif fileType=="json":
        return prepareJson(out)
def closeUp(out,fileType):
    if fileType=="geojson" or fileType=="json":
            out.write("""]}""")
    out.close()
def writeFile(outFile,featureClass,fileType,includeGeometry, first=True):
    [shp,shpType]=getShp(featureClass)
    fields=listFields(featureClass)
    oid=getOID(fields)
    sr=SpatialReference()
    sr.loadFromString(wgs84)
    rows=SearchCursor(featureClass,"",sr)
    del fields[shp]
    i=0
    iPercent=0
    featureCount = int(GetCount_management(featureClass).getOutput(0))
    SetProgressor("step", "Found {0} features".format(str(featureCount)), 0, 100,1)
    AddMessage("Found "+str(featureCount)+" features")
    if fileType=="geojson" or includeGeometry:
        if shpType == "point":
            parseGeo = parsePoint
        elif shpType == "multipoint":
            parseGeo = parseMultiPoint
        elif shpType == "polyline":
            parseGeo = parseMultiLineString
        elif shpType == "polygon":
            parseGeo = parseMultiPolygon
        else:
            parseGeo = parseMultiPatch
    try:
        for row in rows:
            i+=1
            iPercent=statusMessage(featureCount,i,iPercent)
            fc={"type": "Feature"}
            if fileType=="geojson" or includeGeometry:
                fc["geometry"]=parseGeo(row.getValue(shp))
            fc["id"]=row.getValue(oid)
            fc["properties"]=parseProp(row,fields, shp)
            if fileType=="geojson":
                if fc["geometry"]=={}:
                    continue
                if first:
                    first=False
                    dump(fc,outFile)
                else:
                    outFile.write(",")
                    dump(fc,outFile)
            elif fileType=="csv":
                if includeGeometry:
                    fc["properties"]["geometry"]=str(fc["geometry"])
                outFile.writerow(fc["properties"])
            elif fileType=="json":
                if includeGeometry:
                    fc["properties"]["geometry"]=str(fc["geometry"])
                if first:
                    first=False
                    dump(fc["properties"],outFile)
                else:
                    outFile.write(",")
                    dump(fc["properties"],outFile)
    except Exception as e:
        print("OH SNAP! " + str(e))
    finally:
        del row
        del rows
        return True
def toOpen(featureClass, outJSON, includeGeometry="true"):
    if not int(GetCount_management(featureClass).getOutput(0)):
        AddMessage("No features found, skipping")
        return
    includeGeometry = (includeGeometry=="true")
    if outJSON[-8:].lower()==".geojson":
        fileType = "geojson"
    elif outJSON[-5:].lower()==".json":
        fileType = "json"
    elif outJSON[-4:].lower()==".csv":
        fileType = "csv"
    if outJSON[-len(fileType)-1:]!="."+fileType:
        outJSON = outJSON+"."+fileType
    out=open(outJSON,"wb")
    outFile=prepareFile(out,featureClass,fileType,includeGeometry)
    writeFile(outFile,featureClass,fileType,includeGeometry)
    closeUp(out,fileType)
