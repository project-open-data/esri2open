from arcpy import GetParameterAsText
from esri2open import toOpen
toOpen(GetParameterAsText(0),GetParameterAsText(1),("geojson" if (GetParameterAsText(2)=="Default") else GetParameterAsText(2)))