esri2open
=========

This repo is an ESRI toolbox and tool(s) that export ESRI Feature Classes to open data formats, CSV, JSON, and GeoJSON.

What Problem This Solves
------------------------
Much of the data in government coffers is contained in spatial databases.  A large percentage of government spatial data is ESRI software.  While the common interchange format, the ESRI Shapefile, is easily exported and imported by many other softwares, this data file format is not intrinsically part of the www ecology.  Moreover, ESRI software does not provide an export of its generic 'feature class' (shapefile, file geodatabase, and personal geodatabase) to the most common open data file formats, CSV, JSON, and/or GeoJSON.  Lacking this basic export, the lion share of government spatial data users cannot export their data to the most common open data format.


How This Solves It
------------------
This repo is two components that work inside ESRI ArcGIS.  First it is a python script that works at the lowest ESRI software license level to export ESRI "Feature Classes" to the the most common interchange formats; CSV, JSON and GeoJSON.  Second, this repo has an ESRI toolbox (or .tbx file) that allows any ESRI user to easily connect this python script to native ESRI software.  The toolbox points at the script.  Users of this software need both files (the .tbx and the .py) to operate these functions.  Once these files are download, just add the .tbx file to the normal ESRI toolbox and run the .py script by double clicking on the script icon in the toolbox.

Requirements
------------
Runs inside the ESRI ArcGIS desktop suite.

Usaage
------
1. Copy the .tbx file and the .py file to any local directory
2. With ArcGIS desktop software running (e.g. ArcCatalog), add the .tbx file to your tool box by right clicking and choosing 'Add Toolbox'.
3. Double click on the script with the esri2open toolbox called esri2open.py to run the tool.
4. Follow the dialog box to export 'feature classes' to CSV, JSON, or GeoJSON files

Arguments
---------
* `Feature Class`: the name of the Feature Class you wish to export
* `Output Location`: the folder location where the output file will be generated
* `CSV|JSON|GeoJSON`: file type you wish to create
* `Delimiter`: Optional - if you select CSV, you will need to select a delimiter; the default is "|"

License
-------
GPLv3 or later.

Issues
------
* Still need to finish up the file management aspect of the code base
* Need to work on error trapping a bit more
* This does not handle blob fields, or raster fields
* Still need to work out multipart features

