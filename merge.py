from arcpy import GetParameterAsText
from esri2open import writeFile, prepareGeoJSON, closeJSON
#compute the peramaters
features = GetParameterAsText(0).split(";")
outJSON=GetParameterAsText(1)
includeGeometry = "geojson"
fileType = "geojson"
out=prepareGeoJSON(outJSON)
first=True#this makes sure sure we arn't missing commas
for feature in features:
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    writeFile(out,feature,fileType,includeGeometry, first)
    first=False
closeJSON(out)