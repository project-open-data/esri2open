def point_compare(a, b):
    if is_point(a) and is_point(b):
        return a[0] - b[0] or a[1] - b[1]
#def is_point(p):
#    try:
#        float(p[0]), float(p[1])
#    except (TypeError, IndexError):
#        return False
is_point = lambda x : isinstance(x,list) and len(x)==2
class Strut(list):
    def __init__(self,ite=[]):
        self.index=0
        list.__init__(self,ite)
def is_infinit(n):
    return abs(n)==float('inf')
E = 1e-6
def mysterious_line_test(a, b):
    for arg in (a, b):
        if not isinstance(arg, list):
            return True
    return a == b
