# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 18:01:48 2025

@author: ja090
"""

import requests
import pandas as pd

### API endpoint for CalHHS

ckan_sql = "https://data.chhs.ca.gov/api/3/action/datastore_search_sql"

### Collection:
### 2014 - 2023 Provisional Deaths by Month by County

resource_id = "579cc04a-52d6-4c4c-b2df-ad901c9049b7"

### Query for "All Cause Mortality"

sql = f"""
SELECT
    "Year",
    "Month",
    "County",
    "Geography_Type",
    "Strata",
    "Strata_Name",
    "Cause",
    "Cause_Desc",
    "ICD_Revision",
    "Count"
FROM "{resource_id}"
WHERE
    ("Cause_Desc" ILIKE 'ALL%%' OR "Cause" = 'ALL')
AND "Year" >= '2018'
ORDER BY
    "Month",
    "County"
"""

resp = requests.get(
    ckan_sql,
    params = {"sql": sql},
    timeout = 60)

resp.raise_for_status()

rows = resp.json()["result"]["records"]

df = pd.DataFrame.from_records(rows)

### Save the data frame

df.to_csv(
    "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/CalHHS/ca_mortality_data.csv")
