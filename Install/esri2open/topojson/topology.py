# coding=utf8
from mytypes import Types
from coordinatesystems import systems
from line import Line
from clockwise import Clock
from decimal import Decimal
from simplify import Simplify
from utils import is_infinit,E
from quantize import Quantize
from os import remove
import shelve
from tempfile import mkdtemp
from json import dump,dumps
from functools import partial
from stitchpoles import Stitch
from bounds import Bounds
def property_transform (outprop, key, inprop):
        outprop[key]=inprop
        return True
class Topology:
    def __init__(self,quantization=1e4,id_key='id',property_transform=property_transform,system = False,simplify=False,stitch_poles=False):
        self.ln = Line(quantization)
        self.id_func = lambda x:x[id_key]
        self.quantization=quantization
        self.system=system
        self.property_transform=property_transform
        self.bounds=Bounds()
        if simplify:
            self.simplify = Simplify(simplify)
        else:
            self.simplify=False
        if stitch_poles:
            self.stitch_poles=Stitch()
        else:
            self.stitch_poles=False
        self.feature_dir = mkdtemp()
        self.feature_path=[]
        self.feature_db= {}
        self.feature_length = 0
        class Coincidences(Types):
            def __init__(self,ln):
                self.ln = ln
            def line(self,line):
                for point in line:
                    lines = self.ln.arcs.coincidence_lines(point)
                    if not line in lines:
                        lines.append(line)
        self.coincidences = Coincidences(self.ln)
    def start(self):
        oversize = self.bounds.x0 < -180 - E or self.bounds.x1 > 180 + E or self.bounds.y0 < -90 - E or self.bounds.y1 > 90 + E
        if not self.system:
            if oversize:
                self.system = systems["cartesian"]
            else:
                self.system = systems["spherical"]
        if self.system == systems['spherical']:
            if self.bounds.x0 < -180 + E:
                self.bounds.x0 = -180
            if self.bounds.x1 > 180 - E:
                self.bounds.x1 = 180
            if self.bounds.y0 < -90 + E:
                self.bounds.y0 = -90
            if self.bounds.y1 > 90 - E:
                self.bounds.y1 = 90;
        if is_infinit(self.bounds.x0):
            self.bounds.x0 = 0
        if is_infinit(self.bounds.x1):
            self.bounds.x1 = 0;
        if is_infinit(self.bounds.y0):
            self.bounds.y0 = 0;
        if is_infinit(self.bounds.y1):
            self.bounds.y1 = 0;
        if not self.quantization:
            self.quantization = self.bounds.x1 + 1
            self.bounds.x0 = self.bounds.y0 = 0
        [self.kx,self.ky]=make_ks(self.quantization,self.bounds.x0,self.bounds.x1,self.bounds.y0,self.bounds.y1)
        self.quant = Quantize(self.bounds.x0,self.bounds.y0,self.kx,self.ky,self.system.distance)
        self.clock = Clock(self.system.ring_area)
        polygon = lambda poly:map(self.ln.line_closed,poly)
        #Convert features to geometries, and stitch together arcs.
        class Topo(Types):
            def __init__(self,ln,id_func,property_transform):
                self.ln = ln
                self.id_func = id_func
                self.property_transform=property_transform
            def Feature (self,feature):
                geometry = feature["geometry"]
                if feature['geometry'] == None:
                    geometry = {};
                if 'id' in feature:
                    geometry['id'] = feature['id']
                if 'properties' in feature:
                    geometry['properties'] = feature['properties']
                return self.geometry(geometry);
            def FeatureCollection(self,collection):
                collection['type'] = "GeometryCollection";
                collection['geometries'] = map(self.Feature,collection['features'])
                del collection['features']
                return collection
            def GeometryCollection(self,collection):
                collection['geometries'] = map(self.geometry,collection['geometries'])
            def MultiPolygon(self,multiPolygon):
                multiPolygon['arcs'] = map(polygon,multiPolygon['coordinates'])
            def Polygon(self,polygon):
                 polygon['arcs'] = map(self.ln.line_closed,polygon['coordinates'])
            def MultiLineString(self,multiLineString):
                multiLineString['arcs'] = map(self.ln.line_open,multiLineString['coordinates'])
            def LineString(self,lineString):
                lineString['arcs'] = self.ln.line_open(lineString['coordinates'])
            def geometry(self,geometry):
                if geometry == None:
                    geometry = {};
                else:
                    Types.geometry(self,geometry)
                geometry['id'] = self.id_func(geometry)
                if geometry['id'] == None:
                    del geometry['id']
                properties0 = geometry['properties']
                if properties0:
                    properties1 = {}
                    del geometry['properties']
                    for key0 in properties0:
                        if self.property_transform(properties1, key0, properties0[key0]):
                            geometry['properties'] = properties1
                if 'arcs' in geometry:
                    del geometry['coordinates']
                return geometry;
        self.topo = Topo(self.ln,self.id_func,self.property_transform)
        for db in self.feature_db:
            for i in self.feature_db[db]:
                self.tweak(self.feature_db[db],i)
    def dump(self,f):
        self.start()
        #print('writing')
        f.write('{"type":"Topology","bbox":')
        dump([self.bounds.x0, self.bounds.y0, self.bounds.x1, self.bounds.y1],f)
        f.write(',"transform":')
        dump({
            'scale': [1.0 / self.kx, 1.0 / self.ky],
            'translate': [self.bounds.x0, self.bounds.y0]
        },f)
        #print('dumping objects')
        f.write(',"objects":')
        for thing in self.get_objects():
            f.write(thing)
        #print('dumping arcs')
        f.write(',"arcs":[')
        first = True
        for arc in self.ln.get_arcs():
            if first:
                first=False
            else:
                f.write(',')
            dump(arc,f)
        f.write(']}')
    def add(self,object,feature):
        if not (object in self.feature_db):
            path = self.feature_dir+'/'+object
            self.feature_path.append(path)
            self.feature_db[object]=shelve.open(path)
        storage = self.feature_db[object]
        if self.simplify:
            feature = self.simplify.Feature(feature)
        if self.stitch_poles:
            self.stitch_poles.Feature(feature)
        self.bounds.Feature(feature)
        self.feature_db[object][str(self.feature_length)]=feature
        self.feature_length+=1
    def tweak(self,db,i):
        feature = db[i]
        self.quant.Feature(feature)
        feature=self.clock.clock(feature)
        self.coincidences.Feature(feature)
        db[i] = feature
    def get_objects(self):
        firstDB = True
        yield '{'
        for db in self.feature_db:
            if firstDB:
                firstDB=False
            else:
                yield ','
            first = True
            yield '"'+db+'":{"type":"GeometryCollection","geometries":['
            for object in self.feature_db[db]:
                if first:
                    first = False
                else:
                    yield ','
                yield dumps(self.topo.Feature(self.feature_db[db][object]))
            self.feature_db[db].close()
            yield ']}'
        for path in self.feature_path:
            remove(path)
        yield '}'
    def object_factory(self,object):
        return partial(self.add,object)

def make_ks(quantization,x0,x1,y0,y1):
    [x,y]=[1,1]
    if quantization:
        if x1 - x0:
            x= (quantization - 1.0) / (x1 - x0)
        if y1 - y0:
            y=(quantization - 1.0) / (y1 - y0)
    return [x,y]
