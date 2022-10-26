#!/usr/bin/env python
# coding: utf-8

# In[24]:


import json
from datetime import datetime
import pandas as pd
 
# Getting track_data from json file
with open('track_data.json') as json_file:
    data = json.load(json_file)
track_data = data['tracks']


# In[44]:


#Gets past 50 days from today in datelist
today = datetime.today()
today = "{} {} {}".format(today.month,today.day,today.year)

datelist = pd.date_range(end = today, periods=50).tolist()


# In[61]:


queryString = "https://www.equibase.com/static/chart/pdf/{raceid}{month}{day}{year}{country}.pdf"

urls = []

for track in track_data:
    for date in datelist:
        urls.append(queryString.format(raceid = track["abrev"],
                                  month = date.month,
                                  day = date.day,
                                  year = date.year % 1000,
                                  country = 'USA'
                                  ))


# In[ ]:




