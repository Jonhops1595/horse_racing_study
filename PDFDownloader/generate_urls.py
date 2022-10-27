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

    datelist = pd.date_range(end = today, periods=50).tolist()

    queryString = "https://www.equibase.com/static/chart/pdf/{raceid}{month}{day}{year}{country}.pdf"

    urls = []

    for track in track_data:
        for date in datelist:
            urls.append(queryString.format(raceid = track["abrev"],
                                      month = date.month,
                                      day = date.day,
                                      year = date.year % 1000,
                                      country = track["country"]
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

    queryString = "https://www.equibase.com/static/chart/pdf/{raceid}{month}{day}{year}{country}.pdf"

    urls = []

    for track in track_data:
        for date in datelist:
            urls.append(queryString.format(raceid = track["abrev"],
                                      month = date.month,
                                      day = date.day,
                                      year = date.year % 1000,
                                      country = track["country"]
                                      ))
    return urls
