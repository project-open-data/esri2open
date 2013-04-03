from arcpy import GetParameterAsText
from esri2open import prepareGeoJson,writeFile,closeUp
features = GetParameterAsText(0).split(";")
outJSON=GetParameterAsText(1)
includeGeometry = True
fileType = "geojson"
out=open(outJSON,"wb")
prepareGeoJson(out)
first=True
for feature in features:
    if feature[0] in ("'",'"'):
        feature = feature[1:-1]
    writeFile(out,feature,fileType,includeGeometry, first)
    first=False
closeUp(out,fileType)