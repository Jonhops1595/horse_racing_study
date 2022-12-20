# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 13:06:17 2022

@author: Jon Hopkins
"""

import tabula
import pandas as pd

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
        for i in range(0,len(tokenized_text) - 1):
            if(tokenized_text[i] == "Trainers:"):
                start_count_bool = True
            elif(tokenized_text[i] == "Owners:"):
                start_count_bool = False
            elif(start_count_bool and tokenized_text[i] == '-'):
                count += 1

        if count > 0:
            page_list.append({'page_num' : page_num - 1, 'horse_count' : count})
    return page_list


#Extracts key words on the pdf
#Returns a data frame of keywords and it's location on the pdf, with page numbers
#Step 1 in table parsing
def extract_to_df(pages: Any):
    cols = ["Page","Text", "x_1", "y_1", "x_2", "y_2"]
    words = ["Last Raced", "Fractional Times", "Past Performance Running Line Preview", "Fin", "Trainers"]
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
    text_loc_df = text_loc_df.loc[text_loc_df['Text'] != "Fin"] #Delete Fin rows
    #text_loc_df = pd.concat(text_loc_df,fin_row.to_frame(),ignore_index=True) #Append right Fin row
    text_loc_df.loc[len(text_loc_df) + 1] = fin_row

    #Resort table by index
    text_loc_df = text_loc_df.sort_index()
    return text_loc_df


#Creating table location dataframe
#Converts to inches and then pdf_location for tabula
#Step 3 of table parsing
def table_location_to_df(page_num,text_loc_df):
    df = text_loc_df
    cols = ["Page","Table",'Top','Left','Bottom','Right']
    table_loc_df = pd.DataFrame(columns = cols)
    page = page_num
    #Top Table

    left = 7.92
    right = 559.44

    y_1 = df.loc[df['Text'] == "Last Raced",'y_1'].tolist()[0] #Getting y_1 value
    top = (((729 - y_1) * 11)/792) *72

    y_1 = df.loc[df['Text'] == "Fractional Times",'y_1'].tolist()[0]
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
              num_horses): #Number of horses on page
    print("Looking for tables...")
    #Setting variables 
    num_target_rows = num_horses * 2
    test_area =[
            table_loc_df.iloc[table_num - 1,2],
            table_loc_df.iloc[table_num - 1,3],
            table_loc_df.iloc[table_num - 1,4],
            table_loc_df.iloc[table_num - 1,5]
        ]
    
    #Initial table scan
    try:
        scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
        table_df = scan_df[0]
        col_names = list(table_df.columns.values)
        num_rows = len(table_df.index)
    except:
        print("Couldn't read a table from default area")
        col_names = ["top_not_found"]
        num_rows = 0
        
    #Finding top bound
    
    
    #Setting header value to look for
    if(table_num == 1):
        target_header = 'Last Raced'
    else:
        target_header = 'Pgm'
        

    
    #Loop until top bound is right
    bound_num = 0 #Increased bounds by 10, both positive and negative to find the right headers. Ex: 10, -10, 20, -20, 30...
    top_bound = table_loc_df.iloc[table_num - 1,2]
    while(col_names[0] != target_header or bound_num > 200):    
        top_bound = table_loc_df.iloc[table_num - 1,2]
        top_bound += bound_num
        test_area[0] = top_bound
        try:
            scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
            table_df = scan_df[0]
        except:
            print("Couldn't read a table, moving on from {} top_bound".format(top_bound))
            
        col_names = list(table_df.columns.values)

        #Change bound_num
        if(bound_num <= 0): #If number is in negative cycle
            bound_num *= -1
            bound_num += 10
        else:
            bound_num *= -1
    
    if(bound_num > 200):
        print("Error: Couldn't find top bound")
        return
    else:
        print("Found table top bound at {}".format(top_bound))
        table_loc_df.iloc[table_num - 1, 2] = top_bound #Adding new top bound to df
    
    #Finding bottom bound

    bound_num = 0 #Increased bounds by 10, both positive and negative to find the right headers. Ex: 10, -10, 20, -20, 30...
    bottom_bound = table_loc_df.iloc[table_num - 1,4]
    while(num_rows != num_target_rows or bound_num > 200):
        bottom_bound = table_loc_df.iloc[table_num - 1,4]
        bottom_bound += bound_num
        test_area[2] = bottom_bound
        if(bottom_bound > 0):
            try:
                scan_df = tabula.read_pdf(file, pages = page + 1, area = [test_area])
                table_df = scan_df[0]
            except:
                print("Couldn't read a table, moving on from {} bottom_bound".format(bottom_bound))

            num_rows = len(table_df.index)

         #Change bound_num
        if(bound_num <= 0): #If number is in negative cycle
            bound_num *= -1
            bound_num += 10
        else:
            bound_num *= -1
    
    if(bound_num > 200):
        print("Error: Couldn't find bottom bound")
    else:
        table_loc_df.iloc[table_num - 1, 4] = bottom_bound #Adding new bottom bound to df
        print("Found table bottom bound at {}".format(bottom_bound))
        return table_df

#Top Table
def clean_top_table(df): #df of top table to be cleaned
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
    final_df[['Wgt', 'M/E']] = final_df['Wgt M/E'].str.split(' ', 1,expand = True)

    #Removing unnamed & old index
    final_df.drop(['index', 'Wgt M/E'], axis = 1, inplace = True)

    #Removing unnamed
    end_index = final_df.columns.get_loc('Pgm')
    for i in range(1,end_index):
        final_df.drop(final_df.columns[1],axis = 1, inplace = True)
        
    return final_df

def clean_bottom_table(df): #df of top table to be cleaned
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

    return final_df


def scan_page(pdf, page_num, horse_count):
    #Extract words on position
    pages = extract_pages(pdf)
    full_text_loc_df = extract_to_df(pages)
    #try:
    text_loc_df = create_text_loc_df(page_num,full_text_loc_df) #Locations of key text on page
    print(text_loc_df)
    table_loc_df = table_location_to_df(page_num,text_loc_df) #Locations of tables on page
    print(table_loc_df)
    top_table = get_table(pdf,table_loc_df,1,page_num,horse_count) #Getting top table
    bottom_table = get_table(pdf,table_loc_df,2,page_num,horse_count) #Getting bottom table
    #except:
        #print("Error with page", page["page_num"])#Clean all dataframes in first pdf
    
    #Cleaning df superscripts
    cleaned_df_list = []
    try:
        cleaned_df_list.append(clean_top_table(top_table))
    except:
        print("Error with top df on page", page_num)
        cleaned_df_list.append(top_table)
    try:
        cleaned_df_list.append(clean_bottom_table(bottom_table))
    except:
        print("Error with bottom df on page", page_num)
        cleaned_df_list.append(bottom_table)
    return cleaned_df_list

            

