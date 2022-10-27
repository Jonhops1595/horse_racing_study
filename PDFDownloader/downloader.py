#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:07:03 2022

@author: grandjourney
"""
import generate_urls
import tor_service

urls = generate_urls.generate_urls_last50()
#print(urls)
first_10 = urls[:10]
print(first_10)
test_urls_hr = [
    "https://www.equibase.com/static/chart/pdf/BAQ102222USA.pdf",
    "https://www.equibase.com/static/chart/pdf/BAQ102122USA.pdf"
    ]
first_10.append(test_urls_hr[0])
first_10.append(test_urls_hr[1])
print(len(urls))
tor = tor_service.TorService(urls)
for i in range(len(urls)):
    result = tor.get_next_pdf()
    
    
