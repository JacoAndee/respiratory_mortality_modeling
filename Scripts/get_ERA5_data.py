# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 12:08:38 2025

@author: ja090
"""

import cdsapi

out_file = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/ERA5/12/era5land_CA_2024_12.nc"
dataset = "reanalysis-era5-land"

### Make request for temperature, surface pressure, and precipitation raster datasets

request = {
    "variable": [
        "2m_temperature",
        "surface_pressure",
        "total_precipitation"
    ],
    "year": "2024",
    "month": "12",
    "day": [
        "01", "02", "03",
        "04", "05", "06",
        "07", "08", "09",
        "10", "11", "12",
        "13", "14", "15",
        "16", "17", "18",
        "19", "20", "21",
        "22", "23", "24",
        "25", "26", "27",
        "28", "29", "30",
        "31"
    ],
    "time": [
        "00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ],
    "format": "netcdf",
    "download_format": "unarchived",
    "area": [42, -124.4, 32.5, -114.1]
}
client = cdsapi.Client()
client.retrieve(dataset, request, out_file)

print("Saved file: ", out_file)