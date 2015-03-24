
GEOMETRY_TYPES = (
  'LineString',
  'MultiLineString',
  'MultiPoint',
  'MultiPolygon',
  'Point',
  'Polygon',
  'GeometryCollection'
)

class Types:
    def Feature(self,feature):
        if 'geometry' in feature:
            self.geometry(feature['geometry'])
    def FeatureCollection(self,collection):
        for feature in collection['features']:
            self.Feature(feature)
    def GeometryCollection(self,collection):
        if 'geometry' in collection:
            for geometry in collection['geometries']:
                self.geometry(geometry)
    def LineString(self,lineString):
        self.line(lineString['coordinates'])
    def MultiLineString(self,multiLineString):
        for coordinate in multiLineString['coordinates']:
            self.line(coordinate)
    def MultiPoint(self,multiPoint):
        for coordinate in multiPoint['coordinates']:
            self.point(coordinate);
    def MultiPolygon(self,multiPolygon):
        for coordinate in multiPolygon['coordinates']:
            self.polygon(coordinate);
    def Point(self,point):
        self.point(point['coordinates'])
    def Polygon(self,polygon):
        self.polygon(polygon['coordinates'])
    def obj(self,obj):
        if obj == None :
            self.outObj = None
        elif not ('type' in obj):
            self.outObj = {}
            for fName in obj:
                self.outObj[fName]=self.FeatureCollection(obj[fName])
        elif obj['type']=='Feature':
            self.outObj = self.Feature(obj)
        elif obj['type']=='FeatureCollection':
            self.outObj = self.FeatureCollection(obj)
        elif obj['type'] in GEOMETRY_TYPES:
            self.outObj = self.geometry(obj)
        return self.outObj
    def geometry(self,geometry):
        if not (geometry != None and geometry['type'] in GEOMETRY_TYPES):
            return None
        elif geometry['type']== 'LineString':
            return self.LineString(geometry)
        elif geometry['type']== 'MultiLineString':
            return self.MultiLineString(geometry)
        elif geometry['type']== 'MultiPoint':
            return self.MultiPoint(geometry)
        elif geometry['type']== 'MultiPolygon':
            return self.MultiPolygon(geometry)
        elif geometry['type']== 'Point':
            return self.Point(geometry)
        elif geometry['type']== 'Polygon':
            return self.Polygon(geometry)
        elif geometry['type']== 'GeometryCollection':
            return self.GeometryCollection(geometry)
    def point(*arguments):
        pass
    def line(self,coordinates):
        for coordinate in coordinates:
            self.point(coordinate)
    def polygon(self,coordinates):
        for coordinate in coordinates:
            self.line(coordinate)
