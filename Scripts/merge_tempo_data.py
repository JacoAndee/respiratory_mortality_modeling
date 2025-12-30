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
md_name = "TEMPO_O3"
md = os.path.join(gdb, md_name)
src_folder = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/TEMPO/12"
var_name = "/product/column_amount_o3"
out_crf = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/TEMPO/merged/TEMPO_O3_12_tot.crf"

### Create mosaic dataset

if not arcpy.Exists(gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(gdb), os.path.basename(gdb))
if not arcpy.Exists(md):
    arcpy.management.CreateMosaicDataset(
        in_workspace=gdb,
        in_mosaicdataset_name=md_name,
        coordinate_system=4326
    )

nc_paths = glob.glob(os.path.join(src_folder, "**", "*.nc4"), recursive=True) + \
           glob.glob(os.path.join(src_folder, "**", "*.nc"), recursive=True)

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
    operation_description  ="",
    force_spatial_reference = "NO_FORCE_SPATIAL_REFERENCE",
    estimate_statistics = "ESTIMATE_STATISTICS",
    aux_inputs = None,
    enable_pixel_cache = "NO_PIXEL_CACHE"
)

### Aggregate to monthly mean

agg = arcpy.ia.AggregateMultidimensionalRaster(
    in_multidimensional_raster = md,
    dimension = "StdTime",
    aggregation_method = "MEAN",
    variables = var_name,
    aggregation_def = "INTERVAL_KEYWORD",
    interval_keyword = "MONTHLY",
    ignore_nodata = "DATA",
    dimensionless = "DIMENSIONS"
)
agg.save(out_crf)
