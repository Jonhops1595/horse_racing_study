#!/usr/bin/env python
# coding: utf-8

# In[ ]:


def download_pdf(lnk):

    from selenium import webdriver
    from time import sleep

    options = webdriver.ChromeOptions()

    download_folder = "thismac/"

    profile = {"plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_folder,
               "download.extensions_to_open": ""}

    options.add_experimental_option("prefs", profile)

    print("Downloading file from link: {}".format(lnk))

    driver = webdriver.Chrome(chrome_options = options)
    driver.get(lnk)

    filename = lnk.split("/")[4].split(".cfm")[0]
    print("File: {}".format(filename))

    print("Status: Download Complete.")
    print("Folder: {}".format(download_folder))

    driver.close()


download_pdf("https://www.equibase.com/premium/chartEmb.cfm?track=DMR&raceDate=09/11/2022&cy=USA")
