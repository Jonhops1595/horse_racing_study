# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:05:09 2022

@author: Jon Hopkins
"""
import race_results_scanner
import header_scanner
from PyPDF2 import PdfReader
import pandas as pd
import json



pdf = "equibaseFile.pdf"
#result_df = race_results_scanner.scan_file(pdf)

page_list = race_results_scanner.get_page_list(pdf)
print(page_list)
reader = PdfReader(pdf) #File to be scanned
number_of_pages = len(reader.pages) #Number of pages



header_scanner = header_scanner.HeaderScanner()
pdf_df = pd.DataFrame()
i = 0
for page in page_list:
    header = header_scanner.scan(pdf,page['page_num']) #Header scan for page
    result_tables = race_results_scanner.scan_page(pdf,page['page_num']) #Table scan
    
    #Combine into page DF
    top_table = result_tables[0]
    bottom_table = result_tables[1]
    #Dropping horse name for merge
    bottom_table = bottom_table.drop("Horse Name", axis = 1)
    merged_df = top_table.join(bottom_table.set_index("Pgm"), on = "Pgm", rsuffix = "_RLP")
    for field,value in header.items():
        merged_df[field] = value
    #Changing all cols to object type 
    merged_df = merged_df.astype(object)
    #For every page df
    #Merge into master pdf df
    if(len(pdf_df) < 1):
        pdf_df = merged_df
    else:
        pdf_df = pd.merge(pdf_df, merged_df, how = 'outer')

print(pdf_df)
'''
#Extracting for testing
table_list[1][0].to_csv('top_2.csv')
table_list[1][1].to_csv('bottom_2.csv')
with open ('test_2.json', 'w') as file:
    json.dump(header_list[1], file)
'''
    
    
    

    
