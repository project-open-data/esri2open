from mytypes import Types

class Quantize(Types):
    def __init__(self,x0,y0,kx,ky,distance):
        self.x0=x0
        self.y0=y0
        self.kx=kx
        self.ky=ky
        self.emax=0
        self.distance=distance
    def point(self,point):
        x1 = point[0]
        y1 = point[1]
        x = ((x1 - self.x0) * self.kx)
        y =((y1 - self.y0) * self.ky)
        ee = self.distance(x1, y1, x / self.kx + self.x0, y / self.ky + self.y0)
        if ee > self.emax:
            self.emax = ee
        point[0] = int(x)
        point[1] = int(y)