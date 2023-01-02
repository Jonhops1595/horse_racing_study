# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:05:09 2022

@author: Jon Hopkins
"""
import race_results_scanner
import header_scanner as hs
import google_cloud_downloader as gcd
from PyPDF2 import PdfReader
import pandas as pd
import json
import os
import time


start_time = time.perf_counter()
cwd = os.getcwd() #Gets current workding directory

#Made PDF List from Google Cloud Storage
pdf_list = gcd.list_pdfs()
#PDF List from errors
with open('error_pdfs.txt','r') as f:
    data = f.read()
pdf_list = data.split("\n")
pdf_list = pdf_list[:len(pdf_list)-1]
#pdf_list = ["equibaseFile.pdf","equibaseFile2.pdf","equibaseFile3.pdf"]
#result_df = race_results_scanner.scan_file(pdf)
master_df = pd.DataFrame()

CA_Abbrevs = ["AJX","HST","WO"]
#Try-again pdfs
error_pdfs = []
scanned_pdfs = []
CA_flag = False
for pdf in pdf_list:
    #File work
    filepath =  '{}/{}'.format(cwd,pdf)
    error_filepath = '{}/Error_PDFS/{}'.format(cwd,pdf)
    gcd.download_pdf(pdf,filepath)
    
    error_flag = False 

    #Skipping canadian
    for abrev in CA_Abbrevs:
        if(pdf.__contains__(abrev)):
            error_pdfs.append(pdf)
            CA_flag = True
            gcd.download_pdf(pdf,error_filepath)
            os.remove(filepath)
            print("Skipping {} for CA".format(pdf))
    if(CA_flag):
        CA_flag = False
        continue        

    page_list = race_results_scanner.get_page_list(pdf)
    print(page_list)
    
    reader = PdfReader(pdf) #File to be scanned
    number_of_pages = len(reader.pages) #Number of pages
    header_scanner = hs.HeaderScanner()
    pdf_df = pd.DataFrame()
    i = 0
    for page in page_list:
        try:
            header = header_scanner.scan(pdf,page['page_num']) #Header scan for page
            result_tables = race_results_scanner.scan_page(pdf,page['page_num'], page['horse_count'], page['last_pgm']) #Table scan
        except:
            print("Error with {}".format(pdf))
            error_flag = True
            if(pdf not in error_pdfs):
                error_pdfs.append(pdf)
                gcd.download_pdf(pdf,error_filepath)
            break
        #Combine into page DF
        top_table = result_tables[0].astype(object)
        bottom_table = result_tables[1].astype(object)
        #Dropping horse name for merge
        bottom_table = bottom_table.drop("Horse Name", axis = 1)
        top_table = top_table.astype({'Pgm' : float})
        bottom_table = bottom_table.astype({'Pgm' : float})
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
        #Merging into master 
        if(len(master_df) < 1):
            master_df = pdf_df
        else:
            master_df = pd.merge(master_df,pdf_df, how = 'outer') 
    if(not(error_flag)):
        scanned_pdfs.append(pdf)
    os.remove(filepath)#Delete file from local
    
end_time = time.perf_counter()
print("Time : {}".format(end_time - start_time))

#Saving lists as txt files
with open('scanned_pdfs.txt', 'w+') as f:
    for pdf in scanned_pdfs:
        f.write('%s\n' %pdf)
with open('error_pdfs.txt', 'w+') as f:
    for pdf in error_pdfs:
        f.write('%s\n' %pdf)   
master_df.to_csv('master_df.csv')
'''
#Extracting for testing
table_list[1][0].to_csv('top_2.csv')
table_list[1][1].to_csv('bottom_2.csv')
with open ('test_2.json', 'w') as file:
    json.dump(header_list[1], file)
'''
    
    
    

    
