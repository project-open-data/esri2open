def point(c):
    return "{0} {1}".format(c[0],c[1])
def multiPoint(coordinates):
    values =[]
    for coord in coordinates:
        values.append("({0})".format(point(coord)))
    return ", ".join(values)
def linearRing(coordinates):
    values =[]
    for coord in coordinates:
        values.append(point(coord))
    return ", ".join(values)
def multiRing(coordinates):
    values =[]
    for lineString in coordinates:
        values.append("({0})".format(linearRing(lineString)))
    return ", ".join(values)
def metaMultiRing(coordinates):
    values =[]
    for lineString in coordinates:
        values.append("({0})".format(multiRing(lineString)))
    return ", ".join(values)
def makePoint(c):
    return ["Point",point(c)]
def makeMultiPoint(c):
    return ["MultiPoint",multiPoint(c)]
def makeLineString(c):
    return ["LineString",linearRing(c)]
def makeMultiLineString(c):
    return ["MultiLineString",multiRing(c)]
def makePolygon(c):
    return ["Polygon",multiRing(c)]
def makeMultiPolygon(c):
    return ["MultiPolygon",metaMultiRing(c)]
def makeCollection(geometries):
    values = []
    for geom in geometries:
        [ptrn,coords]=parseGeo(geom)
        values.append("{0} ({1})".format(ptrn,coords))
    return ["GeomCollection",", ".join(values)]
def parseGeo(geometry):
    if geometry["type"]=="Point":
        return makePoint(geometry["coordinates"])
    elif geometry["type"]=="MultiPoint":
        return makeMultiPoint(geometry["coordinates"])
    elif geometry["type"]=="LineString":
        return makeLineString(geometry["coordinates"])
    elif geometry["type"]=="MultiLineString":
        return makeMultiLineString(geometry["coordinates"])
    elif geometry["type"]=="Polygon":
        return makePolygon(geometry["coordinates"])
    elif geometry["type"]=="MultiPolygon":
        return makeMultiPolygon(geometry["coordinates"])
    elif geometry["type"]=="GeometryCollection":
        return makeCollection(geometry["geometries"])

def makeWKT(geometry):
    [ptrn,coords]=parseGeo(geometry)
    return "{0} ({1})".format(ptrn,coords)

def getWKTFunc(fun):
    return lambda x: makeWKT(fun(x))
    