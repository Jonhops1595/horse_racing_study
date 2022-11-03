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


urls = generate_urls.generate_urls_last50()
#print(urls)

print(len(urls))
urls = urls[:100]
print(len(urls))
tor = tor_service.TorService(urls) #Tor service to get pdfs from Equibase urls
print(os.getcwd())

while tor.index < len(urls):
    result = tor.get_next_pdf(os.getcwd()) #Get PDF from tor_service, download it locally 
    file_name = result.split("/")[5]
    google_cloud_storage.upload_pdf(result, file_name) #Write PDF to google.cloud storage
tor.write_robot_to_file()


    

#result_list = tor.get_pdfs()  
    
    
