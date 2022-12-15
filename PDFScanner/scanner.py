# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:05:09 2022

@author: Jon Hopkins
"""
import race_results_scanner
import header_scanner
from PyPDF2 import PdfReader



pdf = "equibaseFile.pdf"
#result_df = race_results_scanner.scan_file(pdf)

page_list = race_results_scanner.get_page_list(pdf)
print(page_list)
reader = PdfReader(pdf) #File to be scanned
number_of_pages = len(reader.pages) #Number of pages

header_list = []
table_list = []

header_scanner = header_scanner.HeaderScanner()
i = 0
for page in page_list:
    header_list.append(header_scanner.scan(pdf,page['page_num'])) #Header scan for page
    table_list.append(race_results_scanner.scan_page(pdf,page['page_num'])) #Table scan
    print(table_list[i])
    i += 1
    if(i > 2):
        break
    
    #Combine into page DF
    
#For every page df
    #Merge into master pdf df
    
#Extracting for testing

    
    
    

    
