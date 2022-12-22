# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 13:04:49 2022

@author: jonho
"""

from PyPDF2 import PdfReader
import re
import json
from difflib import SequenceMatcher



class HeaderScanner():
        
    def __init__(self):
        #race_types.json holds scanning information for different race types
        #For edits and additions to race_types, edit race_types.json and read scanner's README
        with open('race_types.json') as json_file:
            race_types = json.load(json_file)
        self.race_types_dict = race_types["race_types"]
        self.race_types = []
        for field,value in race_types["race_types"].items():
            print(field)
            self.race_types.append(field)

    
        #List of tracks using track_data
        self.track_list = []
        with open('../PDFDownloader/track_data.json') as json_file:
            data = json.load(json_file)
            track_data = data['tracks']
        for track in track_data:
            self.track_list.append(track["name"])
            
            
        #Returns header_scanner dictionary of header scanning tools
        #header_scaner["split_word"]: Word to split pdf on after criteria. Purse or Price
        #header_scanner["word_list"]: Tuple that contains keywords, startword, endword, and if either is inclusive via numeric code
        

    #Returns a score 0-1 on how simlar two strings, a and b are
    def similar(self,a, b):
        return SequenceMatcher(None, a, b).ratio()

    #Returns race type dictionary with scanning data, split_word, and race type
    def get_race_type(self,text):
        #Get race type in lowercase from text
        race_type =  text.split("\n")[1].split("-")[0].lower()
        
        #In the case of stakes, get rid of qualifier 
        if(race_type.split()[0] == 'stakes'):
            race_type = "stakes"
        
        #Find most simlar race type
        best_score = 0
        best_index = -1
        for i in range(len(self.race_types)):
            score = self.similar(race_type, self.race_types[i]) * 100
            if(score > best_score):
                best_score = score
                best_index = i
        race_type = self.race_types[best_index]
        return self.race_types_dict[race_type]  


    def scan(self,file,page_num):
        top_fields = {}
        pdf = file
        
        
        reader = PdfReader(pdf) #File to be scanned
        page = reader.pages[page_num] #Page to be scanned
        
        
        text = page.extract_text()
        #Get race type here
        race_type_dict = self.get_race_type(text)
        word_list = race_type_dict["word_list"]
        split_word = race_type_dict["split_word"]
        
        
        
        initial_split = text.split("VideoRaceReplay")
        text = initial_split[0]
        split_cap = text.split(split_word) #Spliting 
        
        #Top, capitalized section
        top_text = split_cap[0]
        
        #Bottom, post price section
        bottom_text = ""
        for i in range(1,len(split_cap)):
            bottom_text += split_cap[i]
            
        #tokenized_bottom_text = re.findall('[A-Z][^A-Z]*', bottom_text) #Split on capital letters
        tokenized_bottom_text = [s for s in re.split("([A-Z][^A-Z]*)", bottom_text) if s]
        
        #Adding text back together
        top_text += " {}".format(split_word)
        for i in range(len(tokenized_bottom_text)):
            top_text += " {}".format(tokenized_bottom_text[i])
        
            
        tokenized_text = top_text.replace(':',' ').split()
        
        #Finding text on PDF
        keyword_count = 0 #Num of keywords found
        i = -1 #Counter for tokenized string
        
        print(tokenized_text)
        print()
        
        
        while i < (len(tokenized_text) - 1):
            found_start = False #If found start of phrase to record
            found_end = False
            recorded_phrase = ""
            i+=1 #Increment at start of loop
            keyword_tuple = word_list[keyword_count]
            keyword = keyword_tuple[0]
            #Keyword option is if start/end word is inclusive/exclusive of phrase
            #Default is exclusve
            if(len(keyword_tuple) > 3):
                keyword_option = keyword_tuple[3]
            else:
                keyword_option = -1
            #Look for start word(s)
            text_word = tokenized_text[i]
            if(type(keyword_tuple[1]) == list): #If start words are a list
                for word in keyword_tuple[1]:
                    if(text_word.__contains__(word)):
                        found_start = True
            elif(text_word.__contains__(keyword_tuple[1])): #If only 1 start_word
                found_start = True
                        
            #Once found start word; Loop until end word
            if(found_start):
                if(keyword_option == 1 or keyword_option == 3): #Checks if start is inclusive
                        recorded_phrase = recorded_phrase + " " +  text_word #Add word to phrase
                while not(found_end or i >= (len(tokenized_text) - 1)):
                    i+= 1 #Increment tokenized string counter
                    text_word = tokenized_text[i]
                    if(type(keyword_tuple[2]) == list): #If end words are a list
                        for end_word in keyword_tuple[2]:
                            if(text_word.__contains__(end_word)):
                                found_end = True
                    elif(text_word.__contains__(keyword_tuple[2])): #If only 1 end_word
                        found_end = True
                    else:
                        recorded_phrase =recorded_phrase + " " +  text_word #Add word to phrase
                
                if(found_end and (keyword_option == 2 or keyword_option == 3)): #If end is inclusive
                        recorded_phrase =recorded_phrase + " " +  text_word #Add word to phrase
                elif(found_end):
                    i -= 1 #Decrement since exclusive
                top_fields.update({keyword: recorded_phrase}) #Add to dictionary
                keyword_count+=1 #Increment to next keyword
            if keyword_count >= len(word_list): #Check if keywords are filled
                break
            
        #Cleaing results
        #Prints out top fields for debugging
        for field,value in top_fields.items():
            print(field ,':', value)
            
            
        for key in top_fields.keys():
            value = top_fields[key]
            value = value.lstrip() #Gets rid of starting spaces
            value = value.replace(".","")
            top_fields[key] = value
        
        top_fields['off_time'] = top_fields['off_time'].replace(" ", ":")  #Changes to readable time
        
        #Cleans often too long length of track string
        nums = ["One", "Two", "Three", "Four", "Five","Six", "Seven","Eigth","Nine"] #Assist on cleaning track
        length_str = top_fields['track_length'].split(" ")
        found_flag = False
        for i in range(len(length_str)):
            for num_word in nums:
                if(length_str[i] == num_word):
                    found_flag = True
                    break
            if(found_flag):
                break
        final_str = ""
        for i in range(i,len(length_str)):
            final_str += " {}".format(length_str[i])
        top_fields['track_length'] = final_str
        
        
        #Cleaning track name
        current_name = top_fields['track'].title()
        best_score = 0
        best_name = current_name
        for track_name in self.track_list:
            score = self.similar(current_name,track_name) * 100
            if(score > best_score):
                best_score = score
                best_name = track_name
        top_fields['track'] = best_name
        
        #Adding race type
        top_fields['race_type'] = race_type_dict['type']
    
        '''
        #Prints out top fields for debugging
        for field,value in top_fields.items():
            print(field ,':', value)
        '''
        return top_fields