#!/usr/bin/env python
# coding: utf-8
import json
from datetime import datetime
import pandas as pd

'''
Generates all urls for full race pdfs on equibase for the past 50 days
Returns a list of urls
'''
def generate_urls_last50():
    # Getting track_data from json file
    with open('track_data.json') as json_file:
        data = json.load(json_file)
    track_data = data['tracks']

    #Gets past 50 days from today in datelist
    today = datetime.today()
    today = "{} {} {}".format(today.month,today.day,today.year)

    datelist = pd.date_range(end = today,periods=50).tolist()
    df = pd.DataFrame(datelist, columns = ['date']) #Creates df of dates
    df['day_of_week'] = df['date'].dt.day_name() #Adds day_of_week  asa column
    df = df.loc[df['day_of_week'].isin(['Thursday', 'Friday', 'Saturday', 'Sunday'])] #Selects rows with dates of specified days
    filtered_date_list = df['date'] #Put new dates into list
    
    
    
    

    queryString = "https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID={raceid}&CTRY={country}&DT={month}/{day}/{year}&DAY=D&STYLE=EQB"

    urls = []

    for track in track_data:
        for date in filtered_date_list:
            if(date.day < 10): #Makes sure leading 0 is in day
                date_day = "0{}".format(date.day)
            else:
                date_day = date.day
            if(date.month < 10):
                date_month = "0{}".format(date.month)
            else:
                date_month = date.month
            urls.append(queryString.format(raceid = track["abrev"],
                                      month = date_month,
                                      day = date_day,
                                      year = date.year,
                                      country = track['country']
                                      ))
    return urls

'''
Generates all urls for full race pdfs on equibase
start_date = Beginning of days in range to generate urls for
end_date = Last day in range of urls
Returns a list of urls
'''
def generate_urls(start_date, end_date):
    # Getting track_data from json file
    with open('track_data.json') as json_file:
        data = json.load(json_file)
    track_data = data['tracks']

    start = "{} {} {}".format(start_date.month,start_date.day,start_date.year)
    end = "{} {} {}".format(end_date.month,end_date.day,end_date.year)

    datelist = pd.date_range(start,end).tolist()
    df = pd.DataFrame(datelist, columns = ['date']) #Creates df of dates
    df['day_of_week'] = df['date'].dt.day_name() #Adds day_of_week  asa column
    df = df.loc[df['day_of_week'].isin(['Thursday', 'Friday', 'Saturday', 'Sunday'])] #Selects rows with dates of specified days
    filtered_date_list = df['date'] #Put new dates into list
    

    queryString = "https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID={raceid}&CTRY={country}&DT={month}/{day}/{year}&DAY=D&STYLE=EQB"

    urls = []

    for track in track_data:
        for date in filtered_date_list:
            if(date.day < 10): #Makes sure leading 0 is in day
                date_day = "0{}".format(date.day)
            else:
                date_day = date.day
            if(date.month < 10):
                date_month = "0{}".format(date.month)
            else:
                date_month = date.month
            urls.append(queryString.format(raceid = track["abrev"],
                                      month = date_month,
                                      day = date_day,
                                      year = date.year,
                                      country = track['country']
                                      ))
    return urls
