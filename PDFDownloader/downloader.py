#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:07:03 2022
Last Updated on Thu Nov 18 2022

@author: Jon Hopkins
"""
import generate_urls
import tor_service
import google_cloud_storage
import os
import pandas as pd
import datetime

'''
If want to pick two dates, can create them here using datetime

start_date = datetime.date(2022,9,15)
end_date = datetime.date(2022,11,4)

'''
#urls = generate_urls.generate_urls(start_date, end_date)

urls = generate_urls.generate_urls_last50()
print(len(urls))

tor = tor_service.TorService(urls) #Tor service to get pdfs from Equibase urls
cwd = os.getcwd()

result_list = tor.get_pdfs()

for result in result_list:
    filepath =  '{}/{}.pdf'.format(cwd,result['filename'])
    with open(filepath, 'wb') as f:  
        f.write(result['request'].content) # writes the bytes to a file with the name of the race
        print("Wrote PDF to : ", filepath)
    google_cloud_storage.upload_pdf(result, filepath) #Write PDF to google.cloud storage
    os.remove(filepath)#Delete file from local
    
   