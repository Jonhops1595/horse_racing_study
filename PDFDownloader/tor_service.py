#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:04:47 2022

@author: grandjourney
"""

from requests_tor import RequestsTor
import pandas as pd
import os
import time

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
        self.rt = RequestsTor(tor_ports=(9000,9001,9002,9003,9004,9005),
                              tor_cport=9051,
                              password = 'TriggerPull',
                              autochange_id=1
                              )
        self.robot_list = []
        self.downloaded_list = []


    def verify_page(self,page):
        text = page.text
        if(text.__contains__("ROBOTS")):
            print("Found Robots, adding to try later list")
            self.robot_list.append(self.urls[self.index])
            self.rt.new_id()
            return False
        if 'Helvetica' in text:
            return True
        else:
            print("Empty File; Discarding")
            return False 
        
    '''Runs through the robot_list until it is empty'''
    def run_robot_list(self,temp_path = os.getcwd()):
        while(len(self.robot_list) > 0):
            index = 0
            while(index < len(self.robot_list)):
                r = self.rt.get(self.robot_list[index])
                if(self.verify_page(r)):
                    str_list = self.urls[self.index].split('&')
                    track_id = str_list[2].split('=')[1]
                    date = str_list[4].split('=')[1].replace('/','_')
                    name =  track_id +"_"+date
                    filename = '{}/{}.pdf'.format(temp_path,name)
                    with open(filename, 'wb') as f:  
                        f.write(r.content) # writes the bytes to a file with the name of the race   
                        f.close()
                    self.robot_list.pop(index)
        
    def write_robot_to_file(self,temp_path = os.getcwd()):
        df = pd.DataFrame(self.robot_list, columns = ["url"])
        df.to_csv('robot_list.csv')
        print("Wrote robot_list to {}".format(os.getcwd() + 'robot_list.csv'))
        
    def write_downloaded_to_file(self,temp_path = os.getcwd()):
        df = pd.DataFrame(self.downloaded_list, columns = ["url"])
        df.to_csv('downloaded_list.csv')
        print("Wrote downloaded_list to {}".format(os.getcwd() + 'downloaded_list.csv'))
        
    
    '''
    Returns path of new pdf downloaded 
    temp_path: path to download pdfs into
    '''
    def get_next_pdf(self,temp_path = os.getcwd()):
        filename = '-1'
        foundPDF = False
        #Loop until valid URL
        while not(foundPDF) and self.index < len(self.urls):
            #time.sleep(5)
            r = self.rt.get(self.urls[self.index])
            print(r, "at", self.urls[self.index])
            if(r.status_code != 404 and self.verify_page(r)): #If pdf is at url
                foundPDF = True
                #Making name for file
                str_list = self.urls[self.index].split('&')
                track_id = str_list[2].split('=')[1]
                date = str_list[4].split('=')[1].replace('/','_')
                name =  track_id +"_"+date
                filename = '{}/{}.pdf'.format(temp_path,name)
                with open(filename, 'wb') as f:  
                    f.write(r.content) # writes the bytes to a file with the name of the race   
                    f.close()
                self.downloaded_list.append(self.urls[self.index])
                print("Wrote PDF to : ", filename)
            self.index += 1
            
        return filename
        
    def get_pdf_at_url(self,url,temp_path = os.getcwd()):
        r = self.rt.get(url)
        print(r, "at", self.urls[self.index])
        if(r.status_code != 404 and self.verify_page(r)): #If pdf is at url
            #Making name for file
            str_list = self.urls[self.index].split('&')
            track_id = str_list[2].split('=')[1]
            date = str_list[4].split('=')[1].replace('/','_')
            name =  track_id +"_"+date
            filename = '{}/{}.pdf'.format(temp_path,name)
            with open(filename, 'wb') as f:  
                f.write(r.content) # writes the bytes to a file with the name of the race   
                f.close()
            print("Wrote PDF to : ", filename)
            return filename
        else:
            print("PDF not found at url")

        

    
    
    
    