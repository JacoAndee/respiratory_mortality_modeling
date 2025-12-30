# -*- coding: utf-8 -*-
"""
Created on Tue Sep  2 18:53:02 2025

@author: ja090
"""

from harmony import Client, Collection, Request, BBox
from pathlib import Path
from datetime import datetime, timezone

collection_id = "S5P_L2__O3_TOT_HiR"
bbox = BBox(-124.4, 32.5, -114.1, 42.0)
temporal = {
    "start": datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
    "stop":  datetime(2024, 2, 28, 0, 0, 0, tzinfo=timezone.utc)
}
out_dir = "C:/Users/ja090/Desktop/Files/JHU/FA25_CAPSTONE/Project/Data/TROPOMI/02"

client = Client()
req = Request(collection = Collection(id = collection_id),
              spatial = bbox,
              temporal = temporal)

print("Submitting request ... ")
job_id = client.submit(req)
client.wait_for_processing(job_id)
print("Job complete.")

urls = list(client.result_urls(job_id))
print("URLs fetched: ", str(len(urls)))

Path(out_dir).mkdir(parents = True, 
                    exist_ok = True)
paths = [f.result() for f in client.download_all(job_id, 
                                                 directory = out_dir, 
                                                 overwrite = True)]

print("Downloaded ", str(len(paths)) + " files: " + out_dir)
for p in paths:
    print(" - ", str(p))