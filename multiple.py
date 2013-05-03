from arcpy import GetParameterAsText, AddMessage
from esri2open import toOpen
from os import path, sep
def getName(feature):
    name = path.splitext(path.split(feature)[1])
    if name[1]:
        if name[1]==".shp":
            return name[0]
        else:
            return name[1][1:]
    else:
        return name[0]
    
features = GetParameterAsText(0).split(";")
outFolder = GetParameterAsText(1)
outType = GetParameterAsText(2)
includeGeometries = ("geojson" if (GetParameterAsText(3)=="Default") else GetParameterAsText(3)).lower()
for feature in features:
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    outName = getName(feature)
    outPath = "{0}{1}{2}.{3}".format(outFolder,sep,outName,outType)
    if path.exists(outPath):
        AddMessage("{0} exists, skipping".format(outName))
        continue
    AddMessage("starting {0}".format(outName))
    toOpen(feature,outPath,includeGeometries)