#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:04:47 2022

@author: grandjourney
"""

from requests_tor import RequestsTor
import os

class TorService:
    def __init__(self, urls):
        self.urls = urls
        self.index = 0
        '''
        self.rt = RequestsTor(tor_ports=[9050, 9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 
                            9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018], 
                  tor_cport=9051,
                  autochange_id=1)  
        '''
        self.rt = RequestsTor(tor_ports=(9050,),
                              tor_cport=9051,
                              password = 'TriggerPull',
                              autochange_id=1
                              )

    '''
    Returns path of new pdf downloaded 
    temp_path: path to download pdfs into
    '''
    def get_next_pdf(self,temp_path = os.getcwd()):
        foundPDF = False
        #Loop until valid URL
        while not(foundPDF):
            print(self.index)
            #time.sleep(5)
            r = self.rt.get(self.urls[self.index])
            print(r)
            if(r.status_code != 404 and verify_page(r)): #If pdf is at url
                foundPDF = True
                name =  self.urls[self.index].split('/')[6].split('.')[0]
                filename = '{}/{}.pdf'.format(temp_path,name)
                with open(filename, 'wb') as f:  
                    f.write(r.content) # writes the bytes to a file with the name of the race   
                    f.close()
            self.index += 1
        print("Wrote PDF to : ", filename)
        return filename
        
    def get_pdf_at_url(self,url,temp_path = os.getcwd()):
        r = self.rt.get(url)
        print(r)
        if(r.ok): #If pdf is at url
            name =  self.urls[self.index].split('/')[6].split('.')[0]
            filename = '{}/{}.pdf'.format(temp_path,name)
            #with open(filename, 'wb') as f:  
                #f.write(r.content) # writes the bytes to a file with the name of the race   
                #f.close()
            print("Wrote PDF to : ", filename)
            return filename
        else:
            print("PDF not found at url")
        
def verify_page(page):
    print(page.text)
    if(page.text.__contains__("ROBOTS")):
        print("Found Robots")
        return True
    return True
    
    
    
    