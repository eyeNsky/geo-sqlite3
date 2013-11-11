# -*- coding: utf-8 -*-
"""
Copyright (C) 2013 eyeNsky, jasonwoo
Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in 
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF 
OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import os
from osgeo import ogr
from sqlite3 import dbapi2 as db

theDb = '/path/to/theDb.sqlite'
dbExist = 1

# test if db exists 
if not os.path.isfile(theDb):
    dbExist = 0

# if the db does not exist create and populate
# with tables and geoms
if dbExist == 0:
    conn = db.connect(theDb)
    cur = conn.cursor()        
    # create a table for the project
    # based on http://www.gaia-gis.it/spatialite-2.4.0-4/splite-python.html
    sql = 'CREATE TABLE breweries ('
    sql += 'OGC_FID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
    sql += 'GEOMETRY BLOB NOT NULL,'
    sql += 'brewery TEXT NOT NULL)'
    cur.execute(sql)

    # create the geometry table
    # based on a working SQlite db created by ogr2ogr
    cur.execute('CREATE TABLE geometry_columns (f_table_name TEXT,f_geometry_column TEXT, geometry_type INTEGER, coord_dimension INTEGER, srid INTEGER, geometry_format TEXT )')
    # populate the geometry_columns, each table (if > 1) needs an entry
    cur.execute("""INSERT INTO geometry_columns (f_table_name,f_geometry_column , geometry_type,coord_dimension,srid,geometry_format ) VALUES ('breweries','GEOMETRY',3,2,4326,'WKB')""")
    # create the spatial ref sys
    cur.execute('CREATE TABLE spatial_ref_sys( srid INTEGER UNIQUE, auth_name TEXT, auth_srid TEXT, srtext TEXT)')
    # populate the srs, using the proper ? substitution method
    cur.execute("""INSERT INTO spatial_ref_sys( srid , auth_name , auth_srid , srtext) VALUES (?,?,?,?)""",(4326,'EPSG',4326,'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'))
    conn.commit()
    conn.close()

curWkt = 'POLYGON ((-77.44799 38.27992,-77.44752 38.28002,-77.44714 38.27900,-77.44762 38.27889,-77.44799 38.27992))'
curPoly = ogr.CreateGeometryFromWkt(curWkt)
# the default "byte_order=wkbXDR" does not play well with php
# the buffer command blobs the data
curPoly = buffer(curPoly.ExportToWkb(byte_order=ogr.wkbNDR))

# insert data 
conn = db.connect(theDb)
cur = conn.cursor()
cur.execute("""INSERT INTO breweries (OGC_FID, GEOMETRY, brewery) VALUES (NULL,?,?)""",(curPoly,'Blue & Gray'))
conn.commit()
conn.close()
