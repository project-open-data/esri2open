from arcs import Arcs
from utils import point_compare,is_point,Strut,mysterious_line_test


class Line:
    def __init__(self,Q):
        self.arcs = Arcs(Q)
    def arc(self,current_arc, last=False):
        n = len(current_arc)
        if last and not len(self.line_arcs) and n == 1:
            point = current_arc[0]
            index = self.arcs.get_index(point)
            if len(index):
                self.line_arcs.append(index[0])
            else:
                index.append(self.arcs.length)
                self.line_arcs.append(index[0])
                self.arcs.push(current_arc)
        elif n > 1:
            self.line_arcs.append(self.arcs.check(current_arc))

    def line(self,points,opened):
        self.line_arcs = [];
        n = len(points)
        current_arc = Strut()
        k = 1
        p=False
        t=False
        if not opened:
            points.pop()
            n-=1
        while k < n:
            t = self.arcs.peak(points[k])
            if opened:
                break
            if p and not mysterious_line_test(p, t):
                tInP = all(map(lambda line:line in p,t))
                pInT = all(map(lambda line:line in t,p))
                if tInP and not pInT:
                    k-=1
                break
            p = t
            k+=1
        # If no shared starting point is found for closed lines, rotate to minimum.
        if k == n and isinstance(p,list) and len(p) > 1:
            point0 = points[0]
            i = 2
            k=0
            while i<n:
                point = points[i];
                if point_compare(point0, point) > 0:
                    point0 = point
                    k = i
                i+=1
        i = 0
        if opened:
            m = n
        else:
            m = n+1
        while i < m:
            i+=1
            point = points[(i + k) % n]
            p = self.arcs.peak(point)
            if not mysterious_line_test(p, t):
                tInP = all(map(lambda line: line in p,t))
                pInT = all(map(lambda line: line in t,p))
                if tInP:
                    current_arc.append(point);
                self.arc(current_arc)
                if not tInP and not pInT and len(current_arc):
                    self.arc(Strut([current_arc[-1], point]))
                if pInT and len(current_arc):
                    current_arc = Strut([current_arc[-1]])
                else:
                    current_arc = Strut();
            if not len(current_arc) or point_compare(current_arc[-1], point):
                current_arc.append(point) # skip duplicate points
            t = p
        self.arc(current_arc, True)
        return self.line_arcs
    def line_closed(self,points):
        return self.line(points,False)
    def line_open(self,points):
        return self.line(points,True)
    def map_func (self,arc):
        if len(arc)==2 and type(arc[0])==type(1):
            arc= [arc]
        i = 1
        n = len(arc)
        point = arc[0]
        x1 = point[0]
        x2= dx =y2 = dy=False
        y1 = point[1]
        points = [[int(x1), int(y1)]]
        while i < n:
            point = arc[i]
            if not is_point(point):
                i+=1
                continue
            x2 = point[0]
            y2 = point[1]
            dx = int(x2 - x1)
            dy = int(y2 - y1)
            if dx or dy:
                points.append([dx, dy])
                x1 = x2
                y1 = y2
            i+=1
        return points
    def get_arcs (self):
        for num in range(0,self.arcs.length):
            yield self.map_func(self.arcs.arcs[str(num)])
        self.arcs.close()
