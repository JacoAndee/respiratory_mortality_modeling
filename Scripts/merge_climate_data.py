# -*- coding: utf-8 -*-
"""
Created on Fri Sep 26 12:45:26 2025

@author: ja090
"""

import os
import glob
import arcpy

arcpy.env.overwriteOutput = True

### Establish key parameters for geoprocessing tasks

gdb = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/Project_Data.gdb"
md_name = "ERA5_precip"
md = os.path.join(gdb, md_name)
src_folder = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5"
var_name = "tp"
out_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/merged/ERA5_precip_agg.crf"

### Create mosaic dataset

if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(gdb), os.path.basename(gdb))
if not arcpy.Exists(md):
    arcpy.management.CreateMosaicDataset(
        in_workspace=gdb,
        in_mosaicdataset_name=md_name,
        coordinate_system=4326
    )

data_dirs = []
for name in os.listdir(src_folder):
    full_path = os.path.join(src_folder, name)
    if os.path.isdir(full_path):
        data_dirs.append(full_path)

### Add NetCDF rasters

arcpy.management.AddRastersToMosaicDataset(
    in_mosaic_dataset = md,
    raster_type = "NetCDF",
    input_path = src_folder,
    update_cellsize_ranges = "UPDATE_CELL_SIZES",
    update_boundary = "UPDATE_BOUNDARY",
    update_overviews = "NO_OVERVIEWS",
    maximum_pyramid_levels = None,
    maximum_cell_size = 0,
    minimum_dimension = 1500,
    spatial_reference = None,
    filter = "*.nc;*.nc4",
    sub_folder = "SUBFOLDERS",
    duplicate_items_action = "ALLOW_DUPLICATES",
    build_pyramids = "BUILD_PYRAMIDS",
    calculate_statistics = "CALCULATE_STATISTICS",
    build_thumbnails = "NO_THUMBNAILS",
    operation_description = "",
    force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
    estimate_statistics = "ESTIMATE_STATISTICS",
    aux_inputs = None,
    enable_pixel_cache = "NO_PIXEL_CACHE"
)

### Aggregate to monthly mean

agg = arcpy.ia.AggregateMultidimensionalRaster(
    in_multidimensional_raster=md,
    dimension = "StdTime",
    aggregation_method = "SUM",
    variables = var_name,
    aggregation_def = "INTERVAL_KEYWORD",
    interval_keyword = "MONTHLY",
    ignore_nodata = "DATA",
    dimensionless = "DIMENSIONS"
)
agg.save(out_crf)
