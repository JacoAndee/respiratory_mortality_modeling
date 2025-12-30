# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 18:27:24 2025

@author: ja090
"""

import arcpy
from arcpy.sa import Raster

arcpy.env.overwriteOutput = True

### Input rasters
### TEMPO ozone below cloud (DU)
### TEMPO cloud pressure (hPa)
### ERA5 surface pressure (hPa)

o3_du = Raster("C:/Users/ja090/Documents/ArcGIS/Projects/RPollution/TEMPO_O3_01.crf")

cp_hpa = Raster("C:/Users/ja090/Documents/ArcGIS/Projects/RPollution/TEMPO_O3_CP_01.crf")

sp_hpa = Raster("C:/Users/ja090/Documents/ArcGIS/Projects/RPollution/ERA5_SP_01.crf")

### Compute ozone in ppm

ppm = o3_du / (0.78914 * (sp_hpa - cp_hpa))

### Save the resulting raster

ppm.save("C:/Users/ja090/Documents/ArcGIS/Projects/RPollution/RPollution.gdb/o3_ppm_01")

