from struct import pack
from sqlite3 import Binary
def pts(c):
    return ["dd",[c.X,c.Y]]
def linearRing(coordinates):
    partCount=coordinates.partCount
    i=0
    values =[0]
    outnum = "I"
    out = ["I",[0]]
    while i<partCount:
        pt = coordinates.getPart(i)
        if pt:
            [ptrn,c]=pts(pt)
            outnum+=ptrn
            values[0]+=1
            values.extend(c)
        else:
            out[0]+=outnum
            out[1][0]+=1
            out[1].extend(values)
            values =[0]
            outnum = "I"
        i+=1
    out[0]+=outnum
    out[1][0]+=1
    out[1].extend(values)
    return out
def makePoint(c):
    values = ["<BI",1,1]
    [ptrn,coords] = pts(c)
    values[0]+=ptrn
    values.extend(coords)
    return Binary(pack(*values))
def makeMultiPoint(c):
    values = ["<BI",1,4]
    [ptrn,coords]=linearRing(c)
    values[0]+=ptrn
    values.extend(coords)
    return Binary(pack(*values))
def makeMultiLineString(c):
    values = ["<BI",1,5]
    [ptrn,coords]=linearRing(c)
    values[0]+=ptrn
    values.extend(coords)
    return Binary(pack(*values))
def makeMultiPolygon(c):
    values = ["<BI",1,6]
    [ptrn,coords]=linearRing(c)
    values[0]+=ptrn
    values.extend(coords)
    return Binary(pack(*values))



def getWKBFunc(type):
    if type == "point":
        return makePoint
    elif type == "multipoint":
        return makeMultiPoint
    elif type == "polyline":
        return makeMultiLineString
    elif type == "polygon":
        return makeMultiPolygon