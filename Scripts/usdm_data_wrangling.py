# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 21:27:19 2025

@author: ja090
"""

import pandas as pd

### Read the data frame

df = pd.read_csv(
    "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/USDM/dm_export_20240101_20241231.csv", 
    dtype = str)

### Keep relevant columns

df = df[["Name", "USDMLevel", "AreaCurrentPercent", "MapDate"]].copy()
df.rename(columns={"Name": "County"}, inplace = True)

### Clean numerics and dates

df["AreaCurrentPercent"] = df["AreaCurrentPercent"].str.replace(",", "", regex = False).astype(float)
df["MapDate"] = pd.to_datetime(df["MapDate"])
df["Year"] = df["MapDate"].dt.year

### Filter to 2024

df = df[df["Year"] == 2024].copy()

### Compute mean % area by drought level per county

g = (df.groupby(["County", "USDMLevel"])["AreaCurrentPercent"]
       .mean()
       .reset_index())

### Generate wide format

wide = (g.pivot(index="County", columns="USDMLevel", values="AreaCurrentPercent")
          .reset_index())

### Ensure all D-levels exist and fill missing with 0

for lvl in ["D0", "D1", "D2", "D3", "D4"]:
    if lvl not in wide.columns:
        wide[lvl] = 0.0
        
wide = wide[["County", "D0", "D1", "D2", "D3", "D4"]]

### Write output

out_path = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/USDM/USDM_Data_2024_Dlevels.csv"
wide.to_csv(out_path, index = False)

print(wide.head(5))
