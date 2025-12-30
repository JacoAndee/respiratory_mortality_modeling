# -*- coding: utf-8 -*-
"""
Created on Sun Oct  5 19:50:04 2025

@author: ja090
"""

import arcpy

arcpy.env.overwriteOutput = True

### Specify raster paths

in_temp_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/merged/ERA5_temp_agg.crf"
out_temp_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/merged/ERA5_tempC_agg.crf"

in_sp_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/merged/ERA5_sp_agg.crf"
out_sp_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/merged/ERA5_spmbar_agg.crf"

### Temperature conversion (Kelvin -> Celsius)

temp_c = arcpy.ia.Minus(in_temp_crf,273.15)
temp_c.save(out_temp_crf)

### Surface pressure conversion (Pascals -> Millibars)

sp_mbar = arcpy.ia.Divide(in_sp_crf, 100.00)
sp_mbar.save(out_sp_crf)
