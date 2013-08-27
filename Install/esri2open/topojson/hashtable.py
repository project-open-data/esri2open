from math import ceil, log

def hasher(size):
    mask = int(size) - 1;
    def retFunc(point):
        if type(point)==type([]) and len(point)==2:
            key = (int(point[0]) + 31 * int(point[1])) | 0
            return (~key if key < 0 else key) & mask
    return retFunc

class Hashtable:
    def __init__(self,size):
        self.size = 1 << int(ceil(log(size)/log(2)))
        self.table = map(lambda x:False,range(0,int(size)))
        self.h = hasher(size)
        
    def peak(self,key):
        matches = self.table[self.h(key)]
        if matches:
            for match in matches:
                if equal(match['key'], key):
                    return match['values']
        return None
    def get(self,key):
        index = self.h(key)
        if not index:
            return []
        matches = self.table[index]
        if (matches):
            for match in matches:
                if equal(match['key'], key):
                    return match['values']
        else:
            matches = self.table[index] = []
        values = []
        matches.append({'key': key, 'values': values})
        return values
def equal(keyA, keyB):
    return keyA[0] == keyB[0] and keyA[1] == keyB[1]
