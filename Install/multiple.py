from arcpy import GetParameterAsText, AddMessage
from esri2open import toOpen, getName
from os import path, sep
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