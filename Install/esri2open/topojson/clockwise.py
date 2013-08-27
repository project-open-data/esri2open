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
            if geo['type']=='Polygon':
                geo['coordinates'] = self.clockwise_polygon(geo['coordinates'])
            elif geo['type']=='MultiPolygon':
                geo['coordinates'] = map(lambda x:self.clockwise_polygon(x),geo['coordinates'])
        return geo
    def clockwise_polygon(self,rings):
        i=0
        n=0
        r = rings[i]
        if len(rings):
            n=len(rings)
            if self.area(r)<0:
                r=list(reversed(r))
        i+=1
        while i<n:
            r=rings[i]
            if self.area(rings[i]) > 0:
                r=list(reversed(r))
        return rings
