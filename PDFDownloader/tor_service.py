#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 10:04:47 2022
Last Updated on Thu Nov 18 2022

@author: Jon Hopkins
"""

from requests_tor import RequestsTor
import pandas as pd
import os
import time
import copy

class TorService:
    def __init__(self, urls):
        self.urls = urls #Urls to be requested
        self.index = 0 #index in the list of urls
        
        '''
        Sets up the RequestsTor object
        Need to edit the torrc file to be able to use all tor ports as well as enable the hash controlled password and set it to a hashed 'TriggerPull'. Follow requests_tor documentation on the README to learn more.
        '''
        self.rt = RequestsTor(tor_ports=(9000,9001,9002,9003,9004,9005),
                              tor_cport=9051,
                              password = 'TriggerPull',
                              autochange_id=1
                              )
        self.robot_list = [] #List of urls that led to robot detection, try again later
        self.downloaded_list = [] #List of urls that had a full race pdf
        self.empty_list = [] #List of urls that were empty

    '''
    Verifies if the page from the request is empty or if the service was detected by Equibase security
    Adds url to either of the three lists:
        -robot_list if the service was detected by equibase security 
        -downloaded_list if the request got a full pdf
        -empty_list if the request got an empty file
    '''
    def verify_page(self,page,url):
        text = page.text
        if(text.__contains__("ROBOTS")):
            print("Found Robots, adding to robot list")
            self.robot_list.append(url)
            self.rt.new_id() #Gets new ID
            return False
        if 'Helvetica' in text:
            self.downloaded_list.append(url)
            return True
        else:
            print("Empty File; Discarding")
            self.empty_list.append(url)
            return False 
        
    '''Runs through the robot_list until it is empty'''
    def run_robot_list(self,result_list,temp_path = os.getcwd()):
        print(type(result_list))
        old_robot_list = copy.deepcopy(self.robot_list)
        self.robot_list = []
        while(len(old_robot_list) > 0):
            print("Running robot list of length {}".format(len(old_robot_list)))
            index = 0
            while(index < len(old_robot_list)):
                url = old_robot_list[index]
                print("Attempting url at index {}".format(index))
                r = self.rt.get(old_robot_list[index])
                if(self.verify_page(r,url)):
                    str_list = url.split('&')
                    track_id = str_list[2].split('=')[1]
                    date = str_list[4].split('=')[1].replace('/','_')
                    name =  track_id +"_"+date
                    result_list.append({"filename" : name, "request" : r})
                index += 1
            old_robot_list = copy.deepcopy(self.robot_list)
            self.robot_list = []
        return result_list
                    
    '''                
    The functions below write the different url lists as a csv                
    Can use temp_path to specify where you want it downloaded to, otherwise it will go in your current working directory 
    '''
    def write_robot_to_file(self,temp_path = os.getcwd()):
        df = pd.DataFrame(self.robot_list, columns = ["url"])
        df.to_csv('robot_list.csv')
        print("Wrote robot_list to {}".format(os.getcwd() + 'robot_list.csv'))
        
    def write_downloaded_to_file(self,temp_path = os.getcwd()):
        df = pd.DataFrame(self.downloaded_list, columns = ["url"])
        df.to_csv('downloaded_list_{}.csv'.format(len(self.downloaded_list)))
        print("Wrote downloaded_list to {}".format(os.getcwd() + 'downloaded_list.csv'))
    
    def write_empty_to_file(self,temp_path = os.getcwd()):
        df = pd.DataFrame(self.empty_list, columns = ["url"])
        df.to_csv('empty_list_{}.csv'.format(len(self.empty_list)))
        print("Wrote empty_list to {}".format(os.getcwd() + 'empty_list.csv'))
        
    
    '''
    Returns a list of dictionaries that contain the filename and request data from the urls containing full race PDFS
    
    params:
    run_robot_list (bool): If True, this method will also run the robot_list until it is depleted. False will not run the robot_list
    
    filename = Name of file. Contains track and date information
    request = Request from URL. Contains raw data gotten from address. Can be used to get pdf
    
    '''
    def get_pdfs(self,run_robot_list = True):
        result_list = []
        while self.index < len(self.urls):
            url = self.urls[self.index]
            print("Attempting url at index {}".format(self.index))
            try:
                r = self.rt.get(url)
            except:
                self.robot_list.append(url)
                self.rt.new_id()
                print("Error has occured; Adding {} to robot list".format(url))
            print(r, "at", url)
            if(r.status_code != 404 and self.verify_page(r,url)): #If pdf is at url
                #Making name for file
                str_list = url.split('&')
                track_id = str_list[2].split('=')[1]
                date = str_list[4].split('=')[1].replace('/','_')
                name =  track_id +"_"+date
                result_list.append({"filename" : name, "request" : r})
            self.index += 1
        if(run_robot_list):
            print("Running robot list until it is cleared")
            final_result_list = self.run_robot_list(result_list)
            return final_result_list
        else:
            return result_list
       