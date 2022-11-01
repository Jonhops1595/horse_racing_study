#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:07:03 2022

@author: grandjourney
"""
import generate_urls
import tor_service
import os


urls = generate_urls.generate_urls_last50()
#print(urls)

print(len(urls))
tor = tor_service.TorService(urls)
print(os.getcwd())
while tor.index < len(urls):
    result = tor.get_next_pdf(os.getcwd() + '/PDFS')
    #IF pdf is wrote
        #Get PDF Data
        #Write PDF df to master df list
        
    
    
