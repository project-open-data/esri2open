class Clock:
    def __init__(self,area):
        self.area=area
    def clock(self,feature):
        if 'geometries' in feature:
            feature['geometries'] = map(self.clock_geometry,feature['geometries'])
        elif 'geometry' in feature:
            feature['geometry']=self.clock_geometry(feature['geometry'])
        return feature
    def clock_geometry(self,geo):
        if 'type' in geo:
            if geo['type']=='Polygon' or geo['type']=='MultiLineString':
                geo['coordinates'] = self.clockwise_polygon(geo['coordinates'])
            elif geo['type']=='MultiPolygon':
                geo['coordinates'] = map(lambda x:self.clockwise_polygon(x),geo['coordinates'])
            elif geo['type']=='LineString':
                geo['coordinates'] = self.clockwise_ring(geo['coordinates'])
        return geo
    def clockwise_polygon(self,rings):
        return map(lambda x:self.clockwise_ring(x),rings)
    def clockwise_ring(self,ring):
        if self.area(ring) > 0:
            return list(reversed(ring))
        else:
            return ring
