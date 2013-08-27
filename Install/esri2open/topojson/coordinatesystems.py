# coding=utf8
from math import sqrt, pi, cos, sin, atan2, tan, atan, asin

PI4 = pi / 4
RADIANS = pi / 180


class BaseCoordinateSystem(object):
    name = "BaseCoordinateSystem"

    def format_distance(self, distance):
        return str(distance)

    def ring_area(self, ring):
        raise Exception('Not implemented')

    def triangle_area(self, triangle):
        raise Exception('Not implemented')

    def distance(self, x0, y0, x1, y1):
        raise Exception('Not implemented')

    def absolute_area(self, area):
        return abs(area)


class Cartesian(BaseCoordinateSystem):
    name = "cartesian"

    def ring_area(self, ring):
        calc_area = lambda p1, p2: p1[1] * p2[0] - p1[0] * p2[1]
        # last and first
        area = calc_area(ring[-1], ring[0])
        for i, p in enumerate(ring[1:]):   # skip first so p is current and
            area += calc_area(p, ring[i])  # ring[i] is the previous
        return area * 0.5

    def triangle_area(self, triangle):
        return abs(
            (triangle[0][0] - triangle[2][0]) * (triangle[1][1] - triangle[0][1]) -
            (triangle[0][0] - triangle[1][0]) * (triangle[2][1] - triangle[0][1])
        )

    def distance(self, x0, y0, x1, y1):
        dx = x0 - x1
        dy = y0 - y1
        return sqrt(dx * dx + dy * dy)


class Spherical(BaseCoordinateSystem):
    name = 'spherical'

    def haversin(self, x):
        return sin(x / 2) ** 2

    def format_distance(self, distance):
        km = distance * 6371.0
        if km > 1:
            return u"{:0.03f}km".format(km)
        else:
            return u"{:0.03f} ({0.03f}°)".format(km * 1000, distance * 180 / pi)

    def ring_area(self, ring):
        if len(ring) == 0:
            return 0
        area = 0
        p = ring[0]
        PI4 = 1
        lambda_ = p[0] * RADIANS
        phi = p[1] * RADIANS / 2.0 + PI4
        lambda0 = lambda_
        cosphi0 = cos(phi)
        sinphi0 = sin(phi)
        for pp in ring[1:]:
            lambda_ = pp[0] * RADIANS
            phi = pp[1] * RADIANS / 2.0 + PI4
            # Spherical excess E for a spherical triangle with vertices: south pole,
            # previous point, current point.  Uses a formula derived from Cagnoli’s
            # theorem.  See Todhunter, Spherical Trig. (1871), Sec. 103, Eq. (2).
            dlambda = lambda_ - lambda0
            cosphi = cos(phi)
            sinphi = sin(phi)
            k = sinphi0 * sinphi
            u = cosphi0 * cosphi + k * cos(dlambda)
            v = k * sin(dlambda)
            area += atan2(v, u)
            #Advance the previous point.
            lambda0 = lambda_
            cosphi0 = cosphi
            sinphi0 = sinphi
        return 2 * area

    def absolute_area(self, area):
        return area + 4 * pi if area < 0 else area

    def triangle_area(self, triangle):
        def distance(a, b):    # why 2 implementations? I don't know, original has the same question in comments
            x0, y0, x1, y1 = [(n * RADIANS) for n in (a + b)]
            delta_lambda = x1 - x0
            return atan2(
                sqrt(
                    (cos(x1) * sin(delta_lambda)) ** 2 +
                    (cos(x0) * sin(x1) - sin(x0) * cos(x1) * cos(delta_lambda)) ** 2
                ),
                sin(x0) * sin(x1) + cos(x0) * cos(x1) * cos(delta_lambda)
            )
        a = distance(triangle[0], triangle[1])
        b = distance(triangle[1], triangle[2])
        c = distance(triangle[2], triangle[0])
        s = (a + b + c) / 2.0
        return 4 * atan(sqrt(max(0, tan(s / 2.0) * tan((s - a) / 2.0) * tan((s - b) / 2.0) * tan((s - c) / 2.0))))

    def distance(self, x0, y0, x1, y1):
        x0, y0, x1, y1 = [(n * RADIANS) for n in [x0, y0, x1, y1]]
        return 2.0 * asin(sqrt(self.haversin(y1 - y0) + cos(y0) * cos(y1) * self.haversin(x1 - x0)))


systems = {'cartesian': Cartesian(), 'spherical': Spherical()}