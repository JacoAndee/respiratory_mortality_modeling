# -*- coding: utf-8 -*-
"""
Created on Mon Oct  6 21:06:04 2025

@author: ja090
"""

import pandas as pd

hhs_df = pd.read_csv(
    "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/CalHHS/ca_mortality_data_18_23.csv")

### List columns

county_col = "CNTY_NAME"
year_col = "Year"
counts_col = "Count"

### Group by county and sum total deaths for 2018 - 2023

county_totals = (
    hhs_df.groupby([year_col, county_col], as_index = False)[counts_col]
    .sum()
    .rename(columns = {counts_col: "Total deaths"}))

### Save results

county_totals.to_csv(
    "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/CalHHS/ca_mortality_18_23_totals.csv", 
    index = False)
