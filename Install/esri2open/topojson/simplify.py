#from https://github.com/omarestrella/simplify.py
from mytypes import Types

def getSquareDistance(p1, p2):
    """
    Square distance between two points
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]

    return dx * dx + dy * dy


def getSquareSegmentDistance(p, p1, p2):
    """
    Square distance between point and a segment
    """
    x = p1[0]
    y = p1[1]

    dx = p2[0] - x
    dy = p2[1] - y

    if dx != 0 or dy != 0:
        t = ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = p2[0]
            y = p2[1]
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = p[0] - x
    dy = p[1] - y

    return dx * dx + dy * dy


def simplifyRadialDistance(points, tolerance):
    length = len(points)
    prev_point = points[0]
    new_points = [prev_point]

    for i in range(length):
        point = points[i]

        if getSquareDistance(point, prev_point) > tolerance:
            new_points.append(point)
            prev_point = point

    if prev_point != point:
        new_points.append(point)

    return new_points


def simplifyDouglasPeucker(points, tolerance):
    length = len(points)
    markers = [0] * length  # Maybe not the most efficent way?

    first = 0
    last = length - 1

    first_stack = []
    last_stack = []

    new_points = []

    markers[first] = 1
    markers[last] = 1

    while last:
        max_sqdist = 0

        for i in range(first, last):
            sqdist = getSquareSegmentDistance(points[i], points[first], points[last])

            if sqdist > max_sqdist:
                index = i
                max_sqdist = sqdist

        if max_sqdist > tolerance:
            markers[index] = 1

            first_stack.append(first)
            last_stack.append(index)

            first_stack.append(index)
            last_stack.append(last)

        # Can pop an empty array in Javascript, but not Python, so check
        # the length of the list first
        if len(first_stack) == 0:
            first = None
        else:
            first = first_stack.pop()

        if len(last_stack) == 0:
            last = None
        else:
            last = last_stack.pop()

    for i in range(length):
        if markers[i]:
            new_points.append(points[i])

    return new_points


def simplify(points, tolerance=0.1, highestQuality=True):
    sqtolerance = tolerance * tolerance

    if not highestQuality:
        points = simplifyRadialDistance(points, sqtolerance)

    points = simplifyDouglasPeucker(points, sqtolerance)

    return points


class Simplify(Types):
    def __init__(self, tolerance):
        self.tolerance = tolerance
    def Feature(self,feature):
        if 'geometry' in feature:
            feature['geometry'] = self.geometry(feature['geometry'])
        return feature
    def line(self,points):
        return simplify(points,self.tolerance)
    def polygon(self,coordinates):
        return map(self.line,coordinates)
    def GeometryCollection(self,collection):
        if collection.has_key('geometries'):
            collection['geometries'] = map(self.geometry,collection['geometries'])
    def LineString(self,lineString):
        lineString['coordinates'] = self.line(lineString['coordinates'])
    def MultiLineString(self,multiLineString):
        multiLineString['coordinates']=map(self.line,multiLineString['coordinates'])
    def MultiPolygon(self,multiPolygon):
        multiPolygon['coordinates'] = map(self.polygon,multiPolygon['coordinates'])
    def Polygon(self,polygon):
        polygon['coordinates']=self.polygon(polygon['coordinates'])
