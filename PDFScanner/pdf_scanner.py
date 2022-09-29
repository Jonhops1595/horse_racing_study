from PyPDF2 import PdfReader

top_keywords_allowance_claiming = ( #Keywords for allowance claiming races
    ("track", "", "-", 1),
    ("date" ,  "-", "-"),
    ("race_num" ,  "-", "ALLOWANCE"),
    ("criteria" ,  "FOR", ".", 1),
    ("claiming_price" ,  "Price", "("),
    ("track_length" ,  "00", "Current"), #After claiming price
    ("purse" ,  "Purse", "Plus"),
    ("weather" ,  "Weather", "Track"),
    ("track_type" ,  "Track", "Off"),
    ("off_time" ,  "at", "Start"),
    ("start" ,  "Start","Timer")
)

#0 = keyword
#1 = startword
#2 = endword
#3 (optional) = 1 if start is inclusive, 2 if end is inclusive, 3 if both
#default is exclusive

top_fields = {}


reader = PdfReader("equibaseFile.pdf")
number_of_pages = len(reader.pages)
page = reader.pages[0]
text = page.extract_text()
tokenized_text = text.split()

keyword_count = 0
i = -1
while i < len(tokenized_text) - 1:
    i+=1 #Increment at start of loop
    keyword_tuple = top_keywords_allowance_claiming[keyword_count]
    if tokenized_text[i].__contains__(keyword_tuple[1]): #If startword is found
        value_string = "" #Start of string
        keyword = keyword_tuple[0] #Save keyword
        if len(keyword_tuple) > 3 and keyword_tuple[3] != 2:#Checking if start is inclusive
            next_word = tokenized_text[i] #Increment to next word (inclusive)
        else:
            i += 1
            next_word = tokenized_text[i] #Increment to next word (exclusive)
        while not(next_word.__contains__(keyword_tuple[2])) and i < len(tokenized_text) - 1:
            value_string = value_string + " " + next_word
            i += 1
            next_word = tokenized_text[i]
        if len(keyword_tuple) > 3 and keyword_tuple[3] != 1: #Checking if end is inclusive
            value_string = value_string + " " + next_word
        else: #End is exclusive, decrement by 1 to start at this word next loop
            i -= 1
        top_fields.update({keyword: value_string}) #Add to dictionary
        keyword_count+=1 #Increment to next keyword
    if keyword_count >= len(top_keywords_allowance_claiming): #Check if keywords are filled
        break

print(tokenized_text)
#print(top_fields)
