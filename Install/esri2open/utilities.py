from arcpy import ListFields,Describe,SetProgressorLabel,SetProgressorPosition,GetCount_management, SetProgressor, AddMessage
from os.path import splitext

#utility functions we will call more then once

#takes the input feature class and returns a dict with 
#	the field name as key and field types as values
def listFields(featureClass):
    fields=ListFields(featureClass)
    out=dict()
    for fld in fields:
        if (fld.name.lower() not in ('shape_length','shape_area','shape.len','shape.length','shape_len','shape.area') and fld.name.find(".")==-1):
            out[fld.name]=fld.type
    return out

#takes the input geometry object and returns
#	a list of [name of shape field, name of shape type]
def getShp(shp):
    desc = Describe(shp)
    return [desc.ShapeFieldName,desc.shapeType.lower()]
    
#takes the fields object from above, tells you which is the OID 
def getOID(fields):
    for key, value in fields.items():
        if value== u'OID':
            return key
            
#for putting a % based status total up
class statusMessage:
    def __init__(self,featureClass):
        self.featureCount = int(GetCount_management(featureClass).getOutput(0))
        SetProgressor("step", "Found {0} features".format(str(self.featureCount)), 0, 100,1)
        AddMessage("Found "+str(self.featureCount)+" features")
        self.percent = 0
        self.current=0
    def update(self):
        self.current+=1
        newPercent = int((self.current*100)/self.featureCount)
        if newPercent != self.percent:
            self.percent=newPercent
            SetProgressorLabel("{0}% done".format(str(self.percent)))
            SetProgressorPosition(self.percent)

#parse the properties, get rid of ones we don't want, i.e. null, or the shape
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

def getExt(fileName):
    split=splitext(fileName)
    if split[1]:
        return split[1][1:].lower()
    else:
        return False

def parseFieldType(name, esriType):
    if esriType.lower() in ("text","string","date"):
        return name+" text"
    elif esriType.lower() in ("short","long","integer"):
        return name+" integer"
    elif esriType.lower() in ("float","single","double"):
        return name+" real"
    else:
        return name+" blob"

def zm(shp):
    desc = Describe(shp)
    return [desc.hasZ,desc.hasM]

def makeInter(n):
    out = []
    i = 0
    while i<n:
        i+=1
        out.append("?")
    return ",".join(out)