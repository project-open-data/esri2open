from arcpy import GetParameterAsText
from esri2open import writeFile, prepareGeoJSON, prepareTOPO,closeJSON,closeTOPOJSON, getExt, getName

#compute the peramaters
features = GetParameterAsText(0).split(";")
outJSON=GetParameterAsText(1)
includeGeometry = "geojson"
fileType = getExt(outJSON)
if fileType == 'geojson':
    prepare = prepareGeoJSON
    closing = closeJSON
elif fileType == 'topojson':
    prepare = prepareTOPO
    closing = closeTOPOJSON
out=prepare(outJSON)
first=True#this makes sure sure we arn't missing commas
i=0
for feature in features:
    i+=1
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    writeFile(out,feature,fileType,includeGeometry, first,getName(feature))
    first=False
closing(out)