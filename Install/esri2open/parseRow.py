from utilities import listFields, getShp, getOID, statusMessage, parseProp, makeInter
from arcpy import SpatialReference, SearchCursor  
from parseGeometry import getParseFunc
from json import dump

#really the only global
wgs84="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision"

class parse:
    def __init__(self,outFile,featureClass,fileType,includeGeometry, first=True):
        self.outFile = outFile
        self.fileType = fileType
        #first we set put the local variables we'll need
        [self.shp,self.shpType]=getShp(featureClass)
        self.fields=listFields(featureClass)
        self.oid=getOID(self.fields)
        sr=SpatialReference()
        sr.loadFromString(wgs84)
        #the search cursor
        self.rows=SearchCursor(featureClass,"",sr)
        #don't want the shape field showing up as a property
        del self.fields[self.shp]
        self.first=first
        self.status = statusMessage(featureClass)
        #define the correct geometry function if we're exporting geometry
        self.parseGeo = getParseFunc(self.shpType,includeGeometry)
        self.i=0
        if fileType=="geojson":    
            self.parse = self.parseGeoJSON
        elif fileType=="csv":    
            self.parse = self.parseCSV
        elif fileType=="json":    
            self.parse = self.parseJSON
        elif fileType=="sqlite":    
            self.parse = self.parseSqlite

    def cleanUp(self,row):
        del row
        del self.rows
        return True

    def parseCSV(self,row):
        #more messages
        self.status.update()
        fc=parseProp(row,self.fields, self.shp)
        if self.parseGeo:
            try:
                fc["geometry"]=self.parseGeo(row.getValue(self.shp))
            except:
                return
        self.outFile[0].writerow(fc)

    def parseGeoJSON(self,row):
        #more messages
        self.status.update()
        fc={"type": "Feature"}
        if self.parseGeo:
            try:
                fc["geometry"]=self.parseGeo(row.getValue(self.shp))
            except:
                return
        else:
            raise NameError("we need geometry for geojson")
        fc["id"]=row.getValue(self.oid)
        fc["properties"]=parseProp(row,self.fields, self.shp)
        if fc["geometry"]=={}:
            return
        if self.first:
            self.first=False
            dump(fc,self.outFile)
        else:
            #if it isn't the first feature, add a comma
            self.outFile.write(",")
            dump(fc,self.outFile)

    def parseJSON(self,row):
        #more messages
        self.status.update()
        fc=parseProp(row,self.fields, self.shp)
        if self.parseGeo:
            try:
                fc["geometry"]=self.parseGeo(row.getValue(self.shp))
            except:
                return
        if self.first:
            self.first=False
            dump(fc,self.outFile)
        else:
            self.outFile.write(",")
            dump(fc,self.outFile)

    def parseSqlite(self,row):
        #more messages
        self.status.update()
        fc=parseProp(row,self.fields, self.shp)
        self.i=self.i+1
        fc["OGC_FID"]=self.i
        if self.parseGeo:
            try:
                fc["GEOMETRY"]=self.parseGeo(row.getValue(self.shp))
            except:
                return
        keys = fc.keys()
        values = fc.values()
        [name,c,conn]=self.outFile
        c.execute("""insert into {0}({1})
                values({2})
                """.format(name,", ".join(keys),makeInter(len(values))),values)
        conn.commit()