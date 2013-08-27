from hashtable import Hashtable
from os import remove
import shelve
from tempfile import mkdtemp
from hashlib import sha1
from utils import point_compare
class Arcs:
    def __init__(self,Q):
        self.coincidences = Hashtable(Q * 10)
        self.arcsByPoint = Hashtable(Q * 10)
        self.pointsByPoint = Hashtable(Q * 10)
        self.arc_db_path=mkdtemp()+'/arc_db'
        self.arcs= shelve.open(self.arc_db_path)
        #self.arcs={}
        self.length=0
        self.storage_path = mkdtemp()+'/db'
        self.db = shelve.open(self.storage_path)
        #self.db={}
    def get_index(self,point):
        return self.pointsByPoint.get(point)
    def get_point_arcs(self,point):
        return self.arcsByPoint.get(point)
    def coincidence_lines(self,point):
        return self.coincidences.get(point)
    def peak(self,point):
        return self.coincidences.peak(point)
    def push(self,arc):
        self.arcs[str(self.length)]=arc
        self.length+=1
        return self.length
    def close(self):
        self.db.close()
        remove(self.storage_path)
        self.arcs.close()
        remove(self.arc_db_path)
    def get_hash(self,arc):
        ourhash = sha1()
        ourhash.update(str(arc))
        return ourhash.hexdigest()
    def check(self,arcs):
        a0 = arcs[0]
        a1 = arcs[-1]
        point = a0 if point_compare(a0, a1) < 0 else a1
        point_arcs = self.get_point_arcs(point)
        h = self.get_hash(arcs)
        if h in self.db:
            return int(self.db[h])
        else:
            index = self.length
            point_arcs.append(arcs)
            self.db[h]=index
            self.db[self.get_hash(list(reversed(arcs)))]=~index
            self.push(arcs)
            return index
        
