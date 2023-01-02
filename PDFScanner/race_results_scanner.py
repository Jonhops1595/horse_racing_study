# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:06:17 2022

@author: Jon Hopkins
"""

import tabula
import pandas as pd
import numpy as np
import re

#Extracting key words
from typing import Any
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


#Gets the non-empty pages and number of horses per page
from PyPDF2 import PdfReader
def get_page_list(file):  #Pdf file
    reader = PdfReader(file)
    num_pages = len(reader.pages)
    
    
    page_list = []
    for page_num in range(1,num_pages + 1):
        page = reader.pages[page_num - 1]
        text = page.extract_text()
        tokenized_text = text.split()

        start_count_bool = False
        count = 0
        pgm = -1
        for i in range(0,len(tokenized_text) - 1):
            if(tokenized_text[i] == "Trainers:"):
                start_count_bool = True
            elif(tokenized_text[i] == "Owners:"):
                start_count_bool = False
            elif(start_count_bool and tokenized_text[i] == '-'):
                count += 1
            elif(start_count_bool and tokenized_text[i].isdigit()):
                pgm = tokenized_text[i]

        if count > 0:
            page_list.append({'page_num' : page_num - 1, 'horse_count' : count, 'last_pgm' : pgm})
    return page_list


#Extracts key words on the pdf
#Returns a data frame of keywords and it's location on the pdf, with page numbers
#Step 1 in table parsing
def extract_to_df(pages: Any):
    cols = ["Page","Text", "x_1", "y_1", "x_2", "y_2"]
    words = ["Last Raced", "Fractional Times","Winner", "Past Performance Running Line Preview", "Fin", "Trainers"]
    text_loc_df = pd.DataFrame(columns = cols)
    
    page_counter = -1
    for page_layout in pages:
        page_counter += 1
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                element_text = element.get_text()
                for word in words:
                    if(element_text.__contains__(word)):
                        loc_nums = []
                        for num in element.bbox:
                            loc_nums.append(num) #Adding binding box numbers
                        text_loc_df.loc[len(text_loc_df.index)] = [page_counter,
                                                                     word,
                                                                     loc_nums[0], 
                                                                     loc_nums[1], 
                                                                     loc_nums[2], 
                                                                     loc_nums[3]]
    return text_loc_df


#Getting pixel location of words per page
#Step 2 in table parsing

def create_text_loc_df(page_num,df):
    text_loc_df = df.loc[df['Page'] == page_num] 
    
    #Saving only last instance of fin; Lowest y_1
    fin_df = text_loc_df.loc[text_loc_df['Text'] == "Fin"] #df with only Fin
    fin_df = fin_df.sort_values(by=['y_1']) #Sort by y_1 descending
    fin_row = fin_df.iloc[0] #Save 1st row
    text_loc_df = text_loc_df.loc[text_loc_df['Text'] != "Fin"].reset_index(drop = True) #Delete Fin rows
    #text_loc_df = pd.concat(text_loc_df,fin_row.to_frame(),ignore_index=True) #Append right Fin row
    text_loc_df.loc[len(text_loc_df) + 1] = fin_row
    
    #Saving only last instance of winner; Lowest y_1
    winner_df = text_loc_df.loc[text_loc_df['Text'] == "Winner"] #df with only winner
    winner_df = winner_df.sort_values(by=['y_1']) #Sort by y_1 descending
    winner_row = winner_df.iloc[0] #Save 1st row
    text_loc_df = text_loc_df.loc[text_loc_df['Text'] != "Winner"].reset_index(drop = True) #Delete winner rows
    #text_loc_df = pd.concat(text_loc_df,winner_row.to_frame(),ignore_index=True) #Append right winner row
    text_loc_df.loc[len(text_loc_df) + 1] = winner_row

    #Resort table by index
    text_loc_df = text_loc_df.sort_index()
    return text_loc_df


#Creating table location dataframe
#Converts to inches and then pdf_location for tabula
#Step 3 of table parsing
def table_location_to_df(page_num,text_loc_df):
    print(text_loc_df)
    df = text_loc_df
    
    cols = ["Page","Table",'Top','Left','Bottom','Right']
    table_loc_df = pd.DataFrame(columns = cols)
    page = page_num
    #Top Table

    left = 7.92
    right = 559.44

    y_1 = df.loc[df['Text'] == "Last Raced",'y_1'].tolist()[0] #Getting y_1 value
    top = (((729 - y_1) * 11)/792) *72

    try:
        y_1 = df.loc[df['Text'] == "Fractional Times",'y_1'].tolist()[0]
    except:
        y_1 = df.loc[df['Text'] == "Winner",'y_1'].tolist()[0]
    bottom = (((729 - y_1) * 11)/792 + .50) *72

    #Adding Table 1 to df
    table_loc_df.loc[len(table_loc_df.index)] =[page,1,top,left,bottom,right]

    #Bottom Table

    left = 126
    right = 424.08

    y_1 = df.loc[df['Text'].str.contains("Past Performance"),'y_1'].tolist()[0]
    top = (((729 - y_1) * 11)/792) * 72


    y_1 = df.loc[df['Text'] == "Trainers",'y_1'].tolist()[0]
    bottom = ((((729 - y_1) * 11)/792 + .75)) * 72

    #Adding Table 2 to df
    table_loc_df.loc[len(table_loc_df.index)] =[page,2,top,left,bottom,right]
    return table_loc_df

#Gets a table from a pdf, using a dataframe of rough locations of the tables on the pdf
#Returns a dataframe of the table
#Step 4 of table parsing
def get_table(file,
              table_loc_df, #Dataframe of locations of tables on pdf
              table_num, #Table we are parsing for (1 = top, 2 = bottom)
              page, #Page number
              num_horses, #Number of horses on page
              last_pgm): #Last Pgm of race

    print(table_loc_df)
    print("Looking for tables...")
    #Setting variables 
    num_target_rows = num_horses * 2
    test_area =[
            table_loc_df.iloc[table_num - 1,2],
            table_loc_df.iloc[table_num - 1,3],
            table_loc_df.iloc[table_num - 1,4],
            table_loc_df.iloc[table_num - 1,5]
        ]
    
    pgm_col_name = "Pgm"
    
    #Initial table scan
    try:
        scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
        table_df = scan_df[0]
        col_names = list(table_df.columns.values)
        num_rows = len(table_df.index)
        print(table_df)
    except:
        print("Couldn't read a table from default area")
        col_names = ["top_not_found"]
        num_rows = 0
        
    #Finding top bound
    
    
    #Setting header value to look for
    if(table_num == 1):
        target_headers = ['Last Raced', 'Last Raced Pgm']
    else:
        target_headers = ['Pgm', 'Pgm Horse Name']
        

    
    #Loop until top bound is right
    bound_num = 0 #Increased bounds by 10, both positive and negative to find the right headers. Ex: 10, -10, 20, -20, 30...
    top_bound = table_loc_df.iloc[table_num - 1,2]
    found_top = False
    while(not(found_top) or bound_num > 200):    
        top_bound = table_loc_df.iloc[table_num - 1,2]
        top_bound += bound_num
        test_area[0] = top_bound
        try:
            scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
            table_df = scan_df[0]
            col_names = list(table_df.columns.values)
            #print(table_df)

            
            #If found one of the target headers for the first column
            for target_header in target_headers:
                if(col_names[0] == target_header):
                    found_top = True
                    if(target_header.__contains__("Pgm")): #Saves col where pgm is under for bottom bound
                        pgm_col_name = target_header
        except:
            print("Couldn't read a table, moving on from {} top_bound".format(top_bound))
        
        #Change bound_num
        if(bound_num <= 0): #If number is in negative cycle
            bound_num *= -1
            bound_num += 10
        else:
            bound_num *= -1
        if(bound_num > 200 or bound_num < -200):
            print("Error: Couldn't find top bound")
            raise Exception("Couldn't find top table")

    #Found table top bound
    print("Found table top bound at {}".format(top_bound))
    table_loc_df.iloc[table_num - 1, 2] = top_bound #Adding new top bound to df
    
    #Finding bottom bound

    bound_num = 0 #Increased bounds by 10, both positive and negative to find the right headers. Ex: 10, -10, 20, -20, 30...
    bottom_bound = table_loc_df.iloc[table_num - 1,4]
    found_bottom = False
    while(not(found_bottom) or bound_num > 200):
        bottom_bound = table_loc_df.iloc[table_num - 1,4]
        bottom_bound += bound_num
        test_area[2] = bottom_bound
        if(bottom_bound > 0):
            try:
                scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
                table_df = scan_df[0]
                if(str(table_df.loc[len(table_df)-1][pgm_col_name]).__contains__(str(last_pgm))): #Checks if last Pgm of scan is last Pgm of race
                    found_bottom = True
                #print(table_df)

            except:
                print("Couldn't read a table, moving on from {} bottom_bound".format(bottom_bound))

         #Change bound_num
        if(bound_num <= 0): #If number is in negative cycle
            bound_num *= -1
            bound_num += 10
        else:
            bound_num *= -1
    
        if(bound_num > 200 or bound_num < -200):
            print("Error: Couldn't find bottom bound")
            raise Exception("Couldn't find top table")

    #Found table bottom_bound
    table_loc_df.iloc[table_num - 1, 4] = bottom_bound #Adding new bottom bound to df
    print("Found table bottom bound at {}".format(bottom_bound))
    return table_df

#Top Table
def clean_top_table(df): #df of top table to be cleaned
    
    col_list = list(df.columns.values)
    #Cleaning if Last Raced and PGM are mixed
    if(col_list[0] == "Last Raced Pgm"):
        last_raced_vals = []
        pgm_vals = []

        for i in range(len(df)):
            if(i % 2 == 0):
                last_raced_vals.append(df.loc[i,"Last Raced Pgm"])
                pgm_vals.append(-1)
            else:
                split_val = df.loc[i,"Last Raced Pgm"].split(" ")
                pgm_vals.append(split_val[len(split_val) - 1])
                new_val = split_val[0]
                for j in range(1,len(split_val)):
                    new_val = new_val + " " + split_val[j]
                last_raced_vals.append(new_val)
        df = df.drop("Last Raced Pgm", axis = 1)
        df.insert(loc=0, column = "Last Raced", value = last_raced_vals)
        df.insert(loc=1, column = "Pgm", value = pgm_vals)
        df["Pgm"] = df["Pgm"].replace(-1,np.NaN)
 
    #Getting rid of unnamed cols
    for col_name in col_list:
        if(col_name.__contains__("Unnamed")):
            df = df.drop(col_name,axis=1)
    
    #Seperating Horse Name and Jockey's names
    df['horse_name'] = df['Horse Name (Jockey)'].str.split("(", expand = True)[0]
    df['Jockey'] =  df['Horse Name (Jockey)'].str.split("(", expand = True)[1]
    df = df.drop('Horse Name (Jockey)', axis = 1)
    jockey = df['Jockey'].astype(str)
    j_split = jockey.str.split(",", expand = True)
    last_name = []
    first_name = []
    for i in range(len(j_split)):
        row = j_split.loc[i]
        for j in reversed(range(len(row))):
            if(not(type(row[j]) == None.__class__)):
                first_name.append(j_split.loc[i,j].split(")")[0].lstrip())
                last_name.append("")
                for k in range(j):
                    last_name[i] = last_name[i] + " " + j_split.loc[i,k]
                break
        last_name[i] = last_name[i].lstrip()
    df.insert(loc=2, column = "jockey_first_name", value = first_name)
    df.insert(loc=3, column = "jockey_last_name", value = last_name)
    df = df.drop('Jockey', axis = 1)
    
    #Merging super scripts
    script_df = df.loc[df['Pgm'].isnull()]
    
    #Get col names of race partitions
    start_index = script_df.columns.get_loc('Start')
    end_index = script_df.columns.get_loc('Odds')
    
    col_name_list = script_df.columns[start_index + 1:end_index]
    col_name_list = [*['Last Raced'],*col_name_list]
     
    script_df = script_df.loc[:,col_name_list]
    
    col_name_list[0] = col_name_list[0] + '_super_script'
    for i in range (1,len(col_name_list)):
        col_name_list[i] = col_name_list[i] + '_length_behind'
    script_df.columns = col_name_list
    
    df_horses = df.loc[df['Pgm'].isnull()==False].reset_index(drop=False)
    script_df.reset_index(drop = True, inplace = True)
    final_df = df_horses.merge(script_df,left_index=True,right_index=True,how='left')

    #Splitting Wgt and M/E
    col_list = list(final_df.columns.values)

    if(not("Wgt" in col_list and "M/E" in col_list)):
        try:
            final_df[['Wgt', 'M/E']] = final_df['Wgt M/E'].str.split(' ', 1,expand = True)
            final_df.drop('Wgt M/E', axis = 1, inplace = True)
        except:
            for col_name in col_list:
                if(col_name.__contains__('Wgt')):
                   final_df[['Wgt', 'M/E']] = final_df[col_name].str.split(' ', 1,expand = True)
                   final_df.drop(col_name, axis = 1, inplace = True)
                   break

    #Removing old index
    final_df.drop('index', axis = 1, inplace = True)
        
    return final_df

def clean_bottom_table(df): #df of top table to be cleaned

    #If Pgm and Horse Name are combined from scan
    col_list = list(df.columns.values)
    #Cleaning if Last Raced and PGM are mixed
    if(col_list[0] == "Pgm Horse Name"):
        pgm_vals = []
        horse_name_vals = []

        for i in range(len(df)):
            if(pd.isnull(df.loc[i,"Pgm Horse Name"])):
                pgm_vals.append(-1)
                horse_name_vals.append(-1)
            else:    
                split_val = df.loc[i,"Pgm Horse Name"].split(" ",1)
                pgm_vals.append(split_val[0])
                horse_name_vals.append(split_val[1])
        df = df.drop("Pgm Horse Name", axis = 1)
        df.insert(loc=0, column = "Pgm", value = pgm_vals)
        df.insert(loc=1, column = "Horse Name", value = horse_name_vals)
        df["Pgm"] = df["Pgm"].replace(-1,np.NaN)
        df["Horse Name"] = df["Horse Name"].replace(-1,np.NaN)

        
    #Cleaning if Pgm and Start are mixed
    if(col_list[1] == "Horse Name Start"):
        horse_name_vals = []
        start_vals = []

        for i in range(len(df)):
            if(pd.isnull(df.loc[i,"Horse Name Start"])):
                horse_name_vals.append(-1)
                start_vals.append(-1)
            else:    
                split_val = df.loc[i,"Horse Name Start"].split(" ")
                horse_name = ""
                for i in range(len(split_val)-1):
                    horse_name = horse_name + " {}".format(split_val[i])
                start = split_val[len(split_val)-1]
                if(len(start) > 3): #If start string is greater than 3 chars
                    split = re.findall('\d+|\D+', start)
                    horse_name  = horse_name + " {}".format(split[0])
                    start = split[1]
                horse_name_vals.append(horse_name)
                start_vals.append(start)
        df = df.drop("Horse Name Start", axis = 1)
        df.insert(loc=1, column = "Horse Name", value = horse_name_vals)
        df.insert(loc=2, column = "Start", value = start_vals)
        df["Horse Name"] = df["Horse Name"].replace(-1,np.NaN)
        df["Start"] = df["Start"].replace(-1,np.NaN)
        
    #Getting rid of unnamed cols
    for col_name in col_list:
        if(col_name.__contains__("Unnamed")):
            df = df.drop(col_name,axis=1)
    #Merging super scripts
    script_df = df.loc[df['Pgm'].isnull()]
  
    #Get col names of race partitions
    start_index = script_df.columns.get_loc('Start')
    end_index = script_df.columns.get_loc('Fin') + 1
    
    col_name_list = script_df.columns[start_index + 1:end_index]
    
    col_name_list = [*col_name_list]
    script_df = script_df.loc[:,col_name_list]
    

    for i in range (0,len(col_name_list)):
        col_name_list[i] = col_name_list[i] + '_length_behind'
    script_df.columns = col_name_list
    
    df_horses = df.loc[df['Pgm'].isnull()==False].reset_index(drop=False)
    script_df.reset_index(drop = True, inplace = True)
    final_df = df_horses.merge(script_df,left_index=True,right_index=True,how='left')

    df_horses = df.loc[df['Pgm'].isnull()==False].reset_index(drop=False)
    final_df = df_horses.merge(script_df,left_index=True,right_index=True,how='left')


    #Removing old index
    final_df.drop('index', axis = 1, inplace = True)
    
    #Removing any extra rows
    final_df = final_df.astype({'Pgm': str})
    for i in range(len(final_df)):
        if((re.search('[a-zA-Z]',final_df.loc[i,"Pgm"]))): #If a Pgm is not number in a row
            final_df = final_df.drop([i])

    return final_df


def scan_page(pdf, page_num, horse_count,last_pgm):
    #Extract words on position
    pages = extract_pages(pdf)
    full_text_loc_df = extract_to_df(pages)
    #try:
    text_loc_df = create_text_loc_df(page_num,full_text_loc_df) #Locations of key text on page
    table_loc_df = table_location_to_df(page_num,text_loc_df) #Locations of tables on page
    top_table = get_table(pdf,table_loc_df,1,page_num,horse_count,last_pgm) #Getting top table
    bottom_table = get_table(pdf,table_loc_df,2,page_num,horse_count,last_pgm) #Getting bottom table
    #except:
        #print("Error with page", page["page_num"])#Clean all dataframes in first pdf
    
    #Cleaning df superscripts
    cleaned_df_list = []
    try:
        cleaned_df_list.append(clean_top_table(top_table))
    except:
         #cleaned_df_list.append(top_table) #For Debugging
         raise Exception("Error in cleaning top table")
    try:
        cleaned_df_list.append(clean_bottom_table(bottom_table))
    except:
         #cleaned_df_list.append(bottom_table) #For Debugging
         raise Exception("Error in cleaning bottom table")
    return cleaned_df_list

            

