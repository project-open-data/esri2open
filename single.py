from arcpy import GetParameterAsText
from esri2open import toOpen
toOpen(GetParameterAsText(0),GetParameterAsText(1),GetParameterAsText(2))