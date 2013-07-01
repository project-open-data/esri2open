esri2open
=========

This repo is an ESRI toolbox and tool(s) that exports ESRI Feature Classes to open data formats, CSV, JSON, SQLite, and GeoJSON.

What Problem This Solves
------------------------
Much of the data in government coffers is contained in spatial databases.  A large percentage of government spatial data is ESRI software.  While the common interchange format, the ESRI Shapefile, is easily exported and imported by many other softwares, this data file format (the Shapefile) is not intrinsically part of the www ecology.  Moreover, ESRI software does not provide an export of its generic 'feature class' (shapefile, file geodatabase, and personal geodatabase) to the most common open data file formats, CSV, JSON, and/or GeoJSON.  Finally while open source tools easily transform ESRI shapefiles to open data, most government geospatial infrastructures only have ESRI tools.  Lacking this basic export feature presented here, means the lion share of government spatial data users cannot export their data to the most common open data formats.

How This Solves It
------------------
This repo is two components that work inside ESRI ArcGIS.  First it is a python script that works at the lowest ESRI software license level to export ESRI "Feature Classes" to the the most common interchange formats; CSV, JSON and GeoJSON.  Second, this repo has an ESRI toolbox (or .tbx file) that allows any ESRI user to easily connect this python script to native ESRI software.  The toolbox points at the script.  Users of this software need both files (the .tbx and the .py) to operate these functions.  Once these files are download, just add the .tbx file to the normal ESRI toolbox and run the .py script by double clicking on the script icon in the toolbox.

Requirements
------------
Runs inside the ESRI ArcGIS desktop suite.

Usage
------
1. Copy the .tbx file and the .py file to any local directory
2. With ArcGIS desktop software running (e.g. ArcCatalog), add the .tbx file to your tool box by right clicking and choosing 'Add Toolbox'.
3. Double click on the which script you want to run which are

ESRI To Open
---------
Output one feature to an open format, arguments are:

* `Feature Class`: the name of the Feature Class you want to export
* `Output Dataset`: the output feature class, choose the format you want to output to here, choices are GeoJSON (default), CSV, JSON, and SQLite.
* `Geometry Type`: choices are Default, GeoJSON, WKT, and None, defaults to GeoJSON, ignored if the file is output to GeoJSON or SQLite.


ESRI To Open (multiple)
---------
Output multiple features to an open format, arguments are:

* `Features`: the names of the Feature Classes you want to export
* `Output Folder`: the output folder.
* `Type`: output data type, choices are want choices are GeoJSON (default), CSV, JSON, SQLite
* `Geometry Type`: choices are Default, GeoJSON, WKT, and None, defaults to GeoJSON, ignored if the file is output to GeoJSON or SQLite.

ESRI To Open (merge)
---------
Merge several feature classes into one GeoJSON file, useful for mixed geometry types:

* `Feature Classes`: the names of the Feature Classes you want to export
* `Out File`: the name of the output file.

License
-------
GPLv3 or later.

Issues
------
* Need to work on error trapping a bit more
* This does not handle blob fields, or raster fields
* Need to document python version; not sure how compatible it is with all current versions
* Developed in ArcGIS 10.0
