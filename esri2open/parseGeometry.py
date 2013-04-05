def parseLineGeom(line):
    out=[]
    lineCount=line.count
    if lineCount ==1:
        return ["Point",[line[0].X,line[0].Y]]
    i=0
    while i<lineCount:
        pt=line[i]
        out.append([pt.X,pt.Y])
        i+=1
    if len(out)==2 and out[0]==out[1]:
        return ["Point",out[0]]
    return ["LineString",out]
def parsePolyGeom(poly):
    out=[]
    polyCount=poly.count
    i=0
    polys=[]
    while i<polyCount:
        pt=poly[i]
        if pt:
            out.append([pt.X,pt.Y])
        else:
            polys.append(out)
            out=[]
        i+=1
    polys.append(out)
    if len(polys[0])==3:
        return ["LineString", polys[0][:2]]
    if len(polys[0])<3:
        return ["Point",polys[0][0]]
    return ["Polygon",polys]
def parsePoint(geometry):
    geo=dict()
    geo["type"]="Point"
    geo["coordinates"]=[geometry.firstPoint.X,geometry.firstPoint.Y]
    return geo
def parseMultiPoint(geometry):
    if not geometry.partCount:
        return {}
    elif geometry.pointCount == 1:
        return parsePoint(geometry)
    else:
        geo=dict()
        geo["type"]="MultiPoint"
        points=[]
        pointCount=geometry.pointCount
        i=0
        while i<pointCount:
            point=geometry.getPart(i)
            points.append([point.X,point.Y])
            i+=1
        geo["coordinates"]=points
        return geo
def parseLineString(geometry):
    if not geometry.partCount:
        return {}
    geo=dict()
    outLine=parseLineGeom(geometry.getPart(0))
    geo["type"]=outLine[0]
    geo["coordinates"]=outLine[1]
    return geo
def parseMultiLineString(geometry):
    if not geometry.partCount:
        return {}
    elif geometry.partCount==1:
        return parseLineString(geometry)
    else:
        lineGeo=dict()
        points=[]
        lines=[]
        lineCount=geometry.partCount
        i=0
        while i<lineCount:
            outLine = parseLineGeom(geometry.getPart(i))
            if outLine[0]=="LineString":
                lines.append(outLine[1])
            elif outLine[1]=="Point":
                points.append(outLine[1])
            i+=1
        if lines:
            if len(lines)==1:
                lineGeo["type"]="LineString"
                lineGeo["coordinates"]=lines[0]
            else:
                lineGeo["type"]="MultiLineString"
                lineGeo["coordinates"]=lines
        if points:
            pointGeo={}
            pointGeo["coordinates"]=points
            if len(pointGeo["coordinates"])==1:
                pointGeo["coordinates"]=pointGeo["coordinates"][0]
                pointGeo["type"]="Point"
            else:
                pointGeo["type"]="MultiPoint"
        if lines and not points:
            return lineGeo
        elif points and not lines:
            return pointGeo
        elif points and lines:
            out = {}
            out["type"]="GeometryCollection"
            out["geometries"] = [pointGeo,lineGeo]
            return out
        else:
            return {}
def parsePolygon(geometry):
    if not geometry.partCount:
        return {}
    geo={}
    outPoly = parsePolyGeom(geometry.getPart(0))
    geo["type"]=outPoly[0]
    geo["coordinates"]=outPoly[1]
    return geo
def parseMultiPolygon(geometry):
    if not geometry.partCount:
        return {}
    elif geometry.partCount==1:
        return parsePolygon(geometry)
    else:
        polys=[]
        lines=[]
        points=[]
        polyCount=geometry.partCount
        i=0
        while i<polyCount:
            polyPart = parsePolyGeom(geometry.getPart(i))
            if polyPart[0]=="Polygon":
                polys.append(polyPart[1])
            elif polyPart[0]=="Point":
                points.append(polyPart[1])
            elif polyPart[0]=="LineString":
                lines.append(polyPart[1])
            i+=1
        num = 0
        if polys:
            polyGeo={}
            num+=1
            polyGeo["coordinates"]=polys
            if len(polyGeo["coordinates"])==1:
                polyGeo["coordinates"]=polyGeo["coordinates"][0]
                polyGeo["type"]="Polygon"
            else:
                polyGeo["type"]="MultiPolygon"
        if points:
            num+=1
            pointGeo={}
            pointGeo["coordinates"]=points
            if len(pointGeo["coordinates"])==1:
                pointGeo["coordinates"]=pointGeo["coordinates"][0]
                pointGeo["type"]="Point"
            else:
                pointGeo["type"]="MultiPoint"
        if lines:
            num+=1
            lineGeo={}
            lineGeo["coordinates"]=lineGeo
            if len(lineGeo["coordinates"])==1:
                lineGeo["coordinates"]=lineGeo["coordinates"][0]
                pointGeo["type"]="LineString"
            else:
                pointGeo["type"]="MultiLineString"
        if polys and not points and not lines:
            return polyGeo
        elif points and not polys and not lines:
            return pointGeo
        elif lines and not polys and not points:
            return lineGeo
        elif num>1:
            out = {}
            out["type"]="GeometryCollection"
            outGeo = []
            if polys:
                outGeo.append(polyGeo)
            if points:
                outGeo.append(pointGeo)
            if lines:
                outGeo.append(lineGeo)
            out["geometries"]=outGeo
            return out
        else:
            return {}
def parseMultiPatch():
    #noop at the moment
    return {}

#this should probobly be a class
def getParseFunc(shpType):
    if shpType == "point":
        return parsePoint
    elif shpType == "multipoint":
        return parseMultiPoint
    elif shpType == "polyline":
        return parseMultiLineString
    elif shpType == "polygon":
        return parseMultiPolygon
    else:
        return parseMultiPatch
