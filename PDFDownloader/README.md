# PDFDownloader
Contains scripts used to download PDFs from Equibase and store them in a GoogleCloud storage bucket. 
**A Virtual Machine is recommended if one were to run this code in order to protect your PC. There is a risk associated with requesting from a large amount of URLs** 

## Runner File
[downloader.py](downloader.py) is the runner file for this section of the project. It utilizes the other modules to generate equibase URLS, request data from Equibase in order to get PDFs, then uploads the PDF to a Google Cloud Storage Bucket.  


## Helper Files & Modules
  - [track_data.json](track_data.json): Contains track name, track accronym used in Equibase, and country accronym the track is located in. Used for generating urls in [generate_urls.py](generate_urls.py). To add or remove any tracks, modify the file. Make sure to visit [Equibase's Historical Result Viewer](https://www.equibase.com/premium/eqbRaceChartCalendar.cfm?tid=AQU&ctry=USA) to get the correct track and country accronym they use in their URLs. 

  - [generate_urls.py](generate_urls.py): Generates all urls for full race pdfs on equibase. PDFs of full race results are located on Equibase through URLs. This module enables users to generate URLs between a start and end date, or over past 50 days. By default, the program only generates for Thursday-Sunday, but you can modify day_list if you want to capture results for different days.

To Use:
```
import generate_urls
import datetime


#To generate a list of urls for past 50 days
urls = generate_urls.generate_urls_last50()

#To generate a list for urls between two days
start_date = datetime.date(2022,1,1) #January 1st 2022
end_date = datetime.date(2022,8,31) #August 31st 2022
urls = generate_urls.generate_urls(start_date, end_date)
```

  - [tor_service.py](tor_service.py): Service used to request PDFs from Equibase URLs. In order to bypass Equibase's robot security, the [requests_tor](https://pypi.org/project/requests-tor/) library is utilized. Requires installation of [Tor](https://community.torproject.org/onion-services/setup/install/) or [Tor Browser](https://www.torproject.org/download/). To utilize different Sock Ports, follow directions on the [requests_tor](https://pypi.org/project/requests-tor/) notes and advanced usage sections. If a request is met with Equibase's robot detection, it saves the URL in a list to attempt later. Can export both the downloaded list(list of all urls where it downloaded a non-empty PDF) and the robot list(urls that were met with Equibases's robot detection) using *write_downloaded_to_file()* and *write_robot_to_file()* respectfully.

To Use:
```
import tor_service

tor = tor_service.TorService(urls) #Tor service to get pdfs from Equibase urls
result = tor.get_next_pdf(os.getcwd()) #Get PDF from tor_service, download it locally 
```

  - [google_cloud_storage.py](google_cloud_storage.py): Service used to put pdfs on the Google Cloud Storage Bucket. View [Google's Documentation](https://cloud.google.com/storage/docs/buckets) to learn more about Google Cloud Storage Buckets. Currently pointing to Jon Hopkins's cloud bucket, but can modify *bucket_name* and *project_id* to change destination.

To Use:
```
import google_cloud_storage

google_cloud_storage.upload_pdf(result, file_name) #Write PDF to google.cloud storage
```
