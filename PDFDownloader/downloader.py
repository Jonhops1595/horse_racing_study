#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:07:03 2022

@author: grandjourney
"""
import generate_urls
import tor_service
import google_cloud_storage
import os
import pandas as pd
import datetime


start_date = datetime.date(2022,9,15)
end_date = datetime.date(2022,11,4)

#urls = generate_urls.generate_urls(start_date, end_date)
#urls = generate_urls.generate_urls_last50()
#print(urls)



urls = pd.read_csv('robot_list.csv')['url'].to_list()


print(len(urls))
tor = tor_service.TorService(urls) #Tor service to get pdfs from Equibase urls

print(os.getcwd())
while(len(urls) > 0):
    tor.index = 0
    while tor.index < len(urls):
        print(tor.index)
        result = tor.get_next_pdf(os.getcwd()) #Get PDF from tor_service, download it locally 
        if(result != '-1'):
            file_name = result.split("/")[5]
            google_cloud_storage.upload_pdf(result, file_name) #Write PDF to google.cloud storage
            os.remove(file_name)#Delete file from local
    tor.write_robot_to_file()
    tor.write_downloaded_to_file()
    print("reading new robot list")
    urls = pd.read_csv('robot_list.csv')['url'].to_list()
    tor.urls = urls
    tor.robot_list = []
    



    
#result_list = tor.get_pdfs()  
    
    
