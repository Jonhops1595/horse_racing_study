from PyPDF2 import PdfReader

top_keywords_allowance_claiming = {
    "track": ["", "-"],
    "date" : ["-", "-"],
    "race_num" : ["-", "ALLOWANCE"],
    "criteria" : ["FOR",'inc', "."],
    "claiming_price" : ["Price", "WEIGHT"],
    "track_length" : ["00", "Current"], #After claiming price
    "purse" : ["Purse", "Plus"],
    "weather" : ["Weather", "Track"],
    "track_type" : ["Track", "Off"],
    "off_time" : ["at", "Start"],
    "start" : ["Start","Timer"]
}




reader = PdfReader("equibaseFile.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
tokenized_text = text.split()



#Do if string contains

print(tokenized_text)

wait = input("Waiting to end program")
