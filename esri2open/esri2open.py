# ---------------------------------------------------------------------------
# esri2open.py
# Created on: March 11, 2013
# Created by: Michael Byrne
# Federal Communications Commission
# exports the feature classes for any feature class to
# a csv file, JSON file or geoJSON file 
# also adding edits from sgillies, Shaun Walbridge, and Calvin Metcalf
# updates include using the python json.dumps method and indentation issues
# merge of Calvin's esri2geo and export to sqlite
# last edits made 5/4/2013
# ---------------------------------------------------------------------------
#imports
from arcpy import AddMessage, GetCount_management
from utilities import getExt
from parseRow import parse
from prepare import prepareFile

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
        includeGeometry="well known binary"
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
