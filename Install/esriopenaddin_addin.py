from os.path import dirname,join
from sys.path import insert
from pythonaddins import GPToolDialog

# enable local imports
local_path = dirname(__file__)
insert(0, local_path)

# get the path for our TBX
toolbox = join(local_path, "esri2open.tbx")

class OpenStandard(object):
    """Implementation for esriopen_standard.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        GPToolDialog(toolbox, 'esri2open')

class OpenMerge(object):
    """Implementation for esriopen_merge.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        GPToolDialog(toolbox, 'esri2openMerge')

class OpenMultiple(object):
    """Implementation for esriopen_multiple.button (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        GPToolDialog(toolbox, 'esri2openMulti')
