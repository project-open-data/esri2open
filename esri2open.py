# ---------------------------------------------------------------------------
# esri2open.py
# Created on: March 11, 2013
# Created by: Michael Byrne
# Federal Communications Commission
# exports the feature classes for any feature class to
# a csv file, JSON file or geoJSON file 
# ---------------------------------------------------------------------------

# Import system modules
import arcpy
from arcpy import env
import sys, string, os, math

#global variables
#need to rewite to connect to a toolbox and accept arguments
theIF = "C:/Users/michael.byrne/opendata/testdata/poly_test.shp"
theOF = "C:/Users/michael.byrne/opendata/poly_test.json"
theOType = "geoJson" # "csv", "Json", "geoJson"
theDelim = "`"

##Function wrtiteCSV - for each row, writes out each field w/ a delimiter
##right now does not deal w/ geometry, blob, or rasters
##has one argument; the name of the output file
def wrtiteCSV(myOF):
    #go open up and read this table
    myFile = open(myOF, 'a')  #open the output file and append to it
    for row in arcpy.SearchCursor(theIF):  #use a search cursor for each row
        myStr = ""
        for myF in arcpy.ListFields(theIF):
             #if it is a string type field, then make sure it is utf-8 and has
             #no spaces before or after it
             if myF.type == "String":
                 myStr = myStr + \
                       str(row.getValue(myF.name).encode('utf-8')).strip()\
                          + theDelim
             #if it is a number type field, no need to quote it; keep it as a number
             if (myF.type == "Float") or (myF.type == "Double") or \
                      (myF.type == "Short") or (myF.type == "Integer") or \
                      (myF.type == "OID"):
                 myStr = myStr + str(row.getValue(myF.name)) + theDelim 
             #if it is a date field, make sure there are no spaces before/after
             #and quote it
             if (myF.type == "Date"):
                 myStr = myStr + str(row.getValue(myF.name)).strip() + theDelim
             #need to deal , blob, and raster
        myLen = len(myStr) - 1
        myStr = myStr[:myLen]
        myFile.write(myStr +  "\n")
    myFile.close()
    del myLen, myStr, myF, myFile, myOF
    del row
    return()


##Function wrtiteJSON - for each row, writes out a JSON Object
##right now does not deal w/ multi-part points
##has one argument;  the name of the output file 
def wrtiteJSON(myOF):
    #go open up and read this table
    myFile = open(myOF, 'a')
    cnt = 1 #used to determine the end of the rows
    #for each row in the feature class input
    for row in arcpy.SearchCursor(theIF):
        myFcnt = 1
        #the next line initializes the variable myGeomStr so that it is available
        #this code sets the geometry object for geoJson at the end of the line 
        #the attributes or properties
        myGeomStr = ""  
        myStr = '{"type": "Feature", "id": ' + str(cnt) + ', "properties": {'
        #for each field in the feature class input
        for myF in arcpy.ListFields(theIF):
             #first get the number of fields in this feature class
             #this helps establish the end of the list so we can close
             #the json object well
             fCnt = int(len(arcpy.ListFields(theIF)))
             #if you are a shape field, so something special w/ it
             if myF.name == "Shape": 
                 if theOType == "geoJson":
                    myField = "geometry"
                    myGeomStr = myGeomStr + writeGeom(row.getValue(myF.name))
             else: #otherwise, just write up the attribues as "properties"
                myField = myF.name.lower()
                myStr = myStr + '"' + myField + '":'                  
             #if it is a string type field, then make sure it is utf-8 and has
             #no spaces before or after it
             if myF.type == "String":
                 if row.getValue(myF.name) <> None:
                     myStr = myStr + '"' + \
                           str(row.getValue(myF.name).encode('utf-8')).strip() \
                           + '"'
                 else: #handle for null fields
                     myStr = myStr + '""'
             #if it is a number type field, no need to quote it; keep it as a number
             if (myF.type == "Float") or (myF.type == "Double")  \
                      or (myF.type == "Short") or (myF.type == "Integer") \
                      or (myF.type == "OID"):
                 if row.getValue(myF.name) <> None:
                     myStr = myStr + str(row.getValue(myF.name))
                 else: #handle for null fields
                     myStr = myStr + ''
             #if it is a date field, make sure there are no spaces before/after
             #and quote it
             if (myF.type == "Date"):
                 if row.getValue(myF.name) <> None:
                     myStr = myStr + '"' + str(row.getValue(myF.name)).strip() + '"'
                 else: #handle for null fields
                     myStr = myStr + '""'
             ##############################################
             #need to deal , blob, and raster at some point
             ##############################################
             #if its not the last field and not Shape, then add comma, 
             #so it can continue appending fields
             if (myFcnt < fCnt) and (myF.name <> "Shape"):
                  myStr = myStr + ", "
             myFcnt = myFcnt + 1
        #if its not the last row, then add then end of row brackets and comma
        if cnt < theCnt :
            #if if the oType is a geoJson file, append the geomStr
            if theOType == "geoJson":  
                myFile.write(myStr + "}, " + myGeomStr + "}," + "\n")
            #if the oType is Json, don't append the geomStr
            else:
                myFile.write(myStr + "} " + "}," + "\n")
        #if it is the last row then just add the ending brackets
        else:   
            #if if the oType is a geoJson file, append the geomStr
            if theOType == "geoJson":  
                myFile.write(myStr + "}, " + myGeomStr + "} \n")
            #if the oType is Json, don't append the geomStr
            else:
                myFile.write(myStr + "} " + "} \n")
        cnt = cnt + 1
    myFile.write("]}" + "\n")
    myFile.close()
    del myStr, myF, myFile, myOF, cnt
    del myFcnt, fCnt, myField, myGeomStr
    del row
    return()

##Function writeGeom - writes out the geometry object to text
##has one argument; first is for the geometry object itelself, 
##myStr gets concatenated and returned
def writeGeom(myGeom):
    #initialize the geometry object 
    myGeomStr = '"geometry": { "type": ' 
    if myGeom.isMultipart == 0:  #then it is simple geometry
        if myGeom.type == "point": #then write out the simple point attributes
            myGeomStr = myGeomStr + '"Point", "coordinates": ['
            myGeomStr = myGeomStr + str(myGeom.getPart().X) + ", " 
            myGeomStr = myGeomStr + str(myGeom.getPart().Y) + "] "
        #then write out the simple polygon features;  
        #currently not supportinginside rings
        if myGeom.type == "polygon": 
            #initialize the coordinates object
            myGeomStr = myGeomStr + '"Polygon", "coordinates": [['
            #set up a geometry part counting variable
            partnum = 0
            for part in myGeom:
                for pnt in myGeom.getPart(partnum):
                    myGeomStr = myGeomStr + "[" + str(pnt.X) + ", "\
                              + str(pnt.Y) + "],"
                partnum = partnum + 1
            myLen = len(myGeomStr) - 1
            myGeomStr = myGeomStr[:myLen] + "]] "
            del myLen, partnum, part, pnt
        if myGeom.type == "polyline": #then write out the simple line features
            myGeomStr = myGeomStr + '"LineString", "coordinates": ['
            partnum = 0
            for part in myGeom:
                for pnt in myGeom.getPart(partnum):
                    myGeomStr = myGeomStr + "[" + str(pnt.X) + ", "\
                              + str(pnt.Y) + "],"
                partnum = partnum + 1
            myLen = len(myGeomStr) - 1
            myGeomStr = myGeomStr[:myLen] + "] "
            del myLen, partnum, part, pnt    

    if myGeom.isMultipart == 1: #then it is multipart geometry
        if myGeom.type == "point": 
            arcpy.AddMessage("haven't written the multi-point yet")

    if myGeom.isMultipart == 1: #then it is multipart geometry
        if myGeom.type == "polygon": 
            #initialize the coordinates object for the geoJson file
            myGeomStr = myGeomStr + '"MultiPolygon", "coordinates": [[['
            #set up a geometry part counting variable
            partnum = 0
            partcount = myGeom.partCount
            while partnum < int(partcount):
                part = myGeom.getPart(partnum)
                pnt = part.next()
                pntcnt = 0
                while pnt:
                    myGeomStr = myGeomStr + "[" + str(pnt.X) + ", "\
                              + str(pnt.Y) + "],"
                    pnt = part.next()
                    pntcnt = pntcnt + 1
                    if not pnt:
                        pnt = part.next()
                        if pnt:
                            arcpy.AddMessage("    interior ring found")
                myLen = len(myGeomStr) - 1
                myGeomStr = myGeomStr[:myLen] + "]],[["
                partnum = partnum + 1
            myLen = len(myGeomStr) - 3 
            myGeomStr = myGeomStr[:myLen] + "]"
        del partnum, parcount, part, pnt, pntcnt    

    if myGeom.isMultipart == 1: #then it is multipart geometry
        if myGeom.type == "polyline": 
            #initialize the coordinates object for the geoJson file
            myGeomStr = myGeomStr + '"MultiLineString", "coordinates": [[['
            #set up a geometry part counting variable
            partnum = 0
            partcount = myGeom.partCount
            while partnum < int(partcount):
                part = myGeom.getPart(partnum)
                pnt = part.next()
                pntcnt = 0
                while pnt:
                    myGeomStr = myGeomStr + "[" + str(pnt.X) + ", "\
                              + str(pnt.Y) + "],"
                    pnt = part.next()
                    pntcnt = pntcnt + 1
                    if not pnt:
                        pnt = part.next()
                        if pnt:
                            arcpy.AddMessage("    interior ring found")
                myLen = len(myGeomStr) - 1
                myGeomStr = myGeomStr[:myLen] + "]],[["
                partnum = partnum + 1
            myLen = len(myGeomStr) - 3 
            myGeomStr = myGeomStr[:myLen] + "]"
        del partnum, parcount, part, pnt, pntcnt
    myGeomStr = myGeomStr + " } "
    del myGeom 
    return(myGeomStr)

##Function prepJSonFile preps the file for writing to a JSON file type
##has one argument, the output file
def prepJSonFile (myOF):
    myFile = open(theOF, 'w')    
    myFile.write("{" + "\n")
    myStr = '"type": "FeatureCollection",'
    myFile.write(myStr + "\n")
    myStr = '"features": ['
    myFile.write(myStr + "\n")    
    myFile.close()            
    del myOF, myStr, myFile
    return()

##Function prepCSVFile preps the file for writing to a CSV file type
##if the field is a geometry, blob, or raster, it does not write them out
def prepCSVFile (myOF):
    myStr = ""
    for myF in arcpy.ListFields(theIF):  #only create data for field types that make sense
        if (myF.type == "String") or (myF.type == "Float") or\
           (myF.type == "Double") or (myF.type == "Short") or\
           (myF.type == "Integer") or (myF.type == "OID") or\
           (myF.type == "Date"):
           myStr = myStr + myF.name + theDelim
    myLen = len(myStr) - 1
    myStr = myStr[:myLen]
    myFile = open(myOF, 'w')    
    myFile.write(myStr + "\n")
    myFile.close()            
    del myOF, myStr, myLen, myFile 
    return()

#****************************************************************************
##################Main Code below
#****************************************************************************
try: 
    #get a count of all rows in the feature class
    theCnt = int(arcpy.GetCount_management(theIF).getOutput(0))
    #message to the end user what you are going to do
    arcpy.AddMessage("Going to write out " + str(theCnt) + " records ")
    arcpy.AddMessage("     from feature class " + theIF)
    arcpy.AddMessage("     to the file " + theOF)
    arcpy.AddMessage("     as a " + theOType + " file")
    #if the output type is csv, write a csv
    if theOType == "csv":
        prepCSVFile(theOF)
        wrtiteCSV(theOF)
    #if the output type is json, or geojson, write a json file
    if (theOType == "Json") or (theOType == "geoJson"):
        prepJSonFile(theOF)
        wrtiteJSON(theOF)
except:
    arcpy.AddMessage("Something bad happened")
