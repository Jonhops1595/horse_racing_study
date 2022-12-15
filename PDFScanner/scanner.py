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

reader = PdfReader(pdf) #File to be scanned
number_of_pages = len(reader.pages) #Number of pages
header_list = []


header_scanner = header_scanner.HeaderScanner()

for i in range(number_of_pages):
    header_list.append(header_scanner.scan(pdf,i))

for i in range(len(header_list)):
    for field,value in header_list[i].items():
        print(field ,':', value)
    print()

    
