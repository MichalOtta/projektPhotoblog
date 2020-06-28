# -*- coding: utf-8 -*-

import requests
import datetime
from bs4 import BeautifulSoup
import os
import re
import csv

# VARS
URL_base = "https://www.photoblog.pl"
URL_userName = ""
URL_postNumber = ""
href_val = "poprzednie »"  # pick "poprzednie »" or "« następne" depending on where You want to start the extraction
href_vals = ["poprzednie »", "« następne"]
baseDir = "D:\\pracadyplomowa\\projektPhotoblog\\src\\"
months = ["STY", "LUT", "MAR", "KWI", "MAJ", "CZE", "LIP", "SIE", "WRZ", "PAź", "LIS", "GRU"]
months2 = ["STYCZNIA", "LUTEGO", "MARCA", "KWIETNIA", "MAJA", "CZERWCA", "LIPCA", "SIERPNIA", "WRZEśNIA",
           "PAźDZIERNIKA", "LISTOPADA", "GRUDNIA"]
path_active = "enterPathHere.csv"
path_history = "enterPathHere.csv"
path_userdump = "enterPathHere.csv"
tmp_postdump = "enterPathHere.csv"
path_postdump = "enterPathHere.csv" + URL_userName + ".csv"
fullURL = URL_base + "/" + URL_userName + "/" + URL_postNumber
isok = 1
isLast = False
downloadDirectory = "enterPathHere"
count = 0
log = []


############## FUNCTIONS ##############

# Checks if the connection is working fine
def statusCheck(fullURL):
    try:
        response = requests.get(fullURL)
        if response.status_code == 200:
            success = True
            print("webpage", fullURL, "opened correctly")
        else:
            success = False
            print("webpage", fullURL, "Connection refused, response code", response)
    except:
        success = False
        print("Connection failure - incorrect address or page cannot be reached")
    return success


# TEST = OK

# get the image link (hits the performance a lot - not used at this stage for downloading photos per se, though it's used for other functions)
def getPhoto(soup):
    try:
        photoLink = soup.find("meta", property="og:image")
        photo = photoLink.get("content", None)
        return photo
    except:
        print('error obtaining image address for property="og:image')


# TEST = OK

# Fetches the date, when needed parses it.
# Date format by default is YYYY_MM_DD
def getDate(soup):
    try:
        dateRAW = [item.get_text(strip=True) for item in soup.select("span.now_date")]
        dateTod = dateRAW[0].replace("/", "_")
        return dateTod
    except:
        try:
            if soup.find("span", {"class": "date"}).contents[0] == "Dodane ":
                dateTod = str(d.today())
                date = dateTod.replace("-", "_")
                return date
            elif soup.find("span", {"class": "date"}).contents[1] == " godz. temu":
                dateTod = str(d.today())
                date = dateTod.replace("-", "_")
                return date
            elif soup.find("span", {"class": "date"}).contents[0] in months:
                dateRAW = soup.find("span", {"class": "date"}).contents
                month = dateRAW[0]
                year = dateRAW[2].contents[0]
                day = dateRAW[1].contents[0]
                month = (monthCheck(month))
                date = year + "_" + month + "_" + day
                return date
            else:
                dateRAW = soup.find("span", {"class": "date"}).contents
                dateSep = dateRAW[0]
                dateSep = dateSep.split(" ")
                month = (monthCheck(dateSep[2]))
                date = dateSep[3] + "_" + month + "_" + dateSep[1]
                return date
        except:
            try:
                dateRAW = soup.find("span", {"class": "date"}).contents
                dateSep = []
                # print('dateraw split:', dateRAW[0].split())
                dateSep = dateRAW[0].split()
                month = (monthCheck(dateSep[2]))
                date = dateSep[3] + "_" + month + "_" + dateSep[1]
            except:
                date = "n/a"
            return date
# TEST = OK

# Support function for parsing the month at newer date formats.
def monthCheck(dateSep):
    if dateSep in months2:
        try:
            if dateSep == "STYCZNIA":
                month = "01"
            elif dateSep == "LUTEGO":
                month = "02"
            elif dateSep == "MARCA":
                month = "03"
            elif dateSep == "KWIETNIA":
                month = "04"
            elif dateSep == "MAJA":
                month = "05"
            elif dateSep == "CZERWCA":
                month = "06"
            elif dateSep == "LIPCA":
                month = "07"
            elif dateSep == "SIERPNIA":
                month = "08"
            elif dateSep == "WRZEśNIA":
                month = "09"
            elif dateSep == "PAźDZIERNIKA":
                month = "10"
            elif dateSep == "LISTOPADA":
                month = "11"
            elif dateSep == "GRUDNIA":
                month = "12"
            return month
        except:
            month = "00"
            return month
    elif dateSep in (months):
        try:
            if dateSep == "STY":
                month = "01"
            elif dateSep == "LUT":
                month = "02"
            elif dateSep == "MAR":
                month = "03"
            elif dateSep == "KWI":
                month = "04"
            elif dateSep == "MAJ":
                month = "05"
            elif dateSep == "CZE":
                month = "06"
            elif dateSep == "LIP":
                month = "07"
            elif dateSep == "SIE":
                month = "08"
            elif dateSep == "WRZ":
                month = "09"
            elif dateSep == "PAź":
                month = "10"
            elif dateSep == "LIS":
                month = "11"
            elif dateSep == "GRU":
                month = "12"
            return month
        except:
            month = "00"
            return month
# TEST = OK

# Gets post title (for earliest post will be empty or fixed as "Photoblog <username> w Photoblog.pl")
def getTitle(soup):
    titleRAW = soup.find("meta", property="og:title")
    title = titleRAW.get("content", None)
    return title
# TEST = OK


# Gets full note content. Parses it and removes all non alphanumeric characters excluding dot (".").
def getNote(soup):
    try:
        noteRAW = soup.find("div", id="photo_note").contents
        # print(noteRAW)
        tmp = []
        for note in noteRAW:
            tmp.append(str(note))
        for row in tmp:
            tmp_row = row
            clean = re.compile('<.*?>')
            tmp_row = tmp_row.replace("</p>", " ")
            tmp_row = re.sub(clean, '', tmp_row)
            note = note + tmp_row
            # note = note.replace("\n", " ")
            # note = note.replace("\t", "")
            note = " ".join(note.split())
            note = " ".join(re.findall(r"[a-zA-Z0-9\.À-ž ]+", note))
        return note
    except:
        note = "Unable to fetch the note, unknown source format"
        print(note)
        return note
# TEST = OK

# Fetches the next page of the user content.
def getNextPage(soup):
    try:
        nextPageRAW = soup.find("span", id="photo_nav")
        nextPage = nextPageRAW.find("a", string="poprzednie »").get("href")
        return nextPage
    except:
        nextPageRAW = soup.find("a", {"class": "prev"}, href=True, )
        nextPage = nextPageRAW.get("href")
        return nextPage
# TEST = OK

# Checks ig the post is the last one
def checkIfLast(soup, isFirst):
    if isFirst:
        try:
            if getNextPage(soup).split("/")[4]:
                isLast = False
                return isLast
        except:
            isLast = True
            return isLast
    else:
        try:
            checkIfLastRAW = soup.find("span", id="photo_nav")
            list = []
            for a in checkIfLastRAW.find_all('a', href=True):
                list.append(a['href'])
            if len(list) == 1:
                isLast = True
            else:
                isLast = False
            return isLast
        except:
            if soup.find("a", {"class": "prev disabled"}, href=True, ):
                isLast = True
            else:
                isLast = False
            return isLast
# TEST = OK

# Fetches the number of post
def getPostnumber(soup):
    postNumber = getPhoto(soup).split("/")[5].split(".")[0]
    return postNumber
# TEST = OK

# Gets the name if the user
def getUserName(soup):
    try:
        name = soup.find("div", id="user_details").contents[1]
        name = name.find("a").contents[0].replace(" ", "")
    except:
        try:
            name = soup.find("span", {"class": "name"}).contents[1]
        except:
            name = "n/a"
    return name
# TEST = OK


# Fetches the age of the user
def getUserAge(soup, profilename):
    try:
        age = soup.find("div", id="user_details").contents[3]
        age = age.find("a").contents[0].replace(" ", "")
        age = age.replace(profilename + ",", "")
        age = age.replace("lat", "")
        age = age.replace(" ", "")
        age = age.replace("\n", "")
        if age.isnumeric() == False:
            age = "n/a"
    except:
        try:
            age = soup.find("span", {"class": "age"}).contents[1]
            age = age.replace(" l.", "")
            age = age.replace(" ", "")
            if age.isnumeric() == False:
                age = "n/a"
        except:
            age = "n/a"
    return age
# TEST = OK - it is however faulty basing on HTML parsing by beautifulsoup

# Fetches the user's city
def getUserCity(soup):
    try:
        city = soup.find("div", id="user_details").contents[5]
        city = city.find("a").contents[0].replace(" ", "")
    except:
        try:
            city = soup.find("div", {"class": "mobile-user-info"})
            city = city.find_all("a")[-1].contents[0]
        except:
            city = "n/a"
    return city
# TEST = OK - it is however faulty basing on HTML parsing by beautifulsoup

# Download the soup. For somplification of the endcode.
def getSoup(URL_base, URL_userName, _URL_postNumber):
    fullURL = URL_base + "/" + URL_userName + "/" + URL_postNumber
    if statusCheck(fullURL):
        page = requests.get(fullURL)
        soup = BeautifulSoup(page.content, 'html.parser', from_encoding="iso-8859-8")
    else:
        print("process terminated")
        quit()
    return soup
# TEST = OK

# Gets all the date to a nice cool and fancy CSV format.
def getLine(soup, row):
    line = row[0] + ", " + getPostnumber(soup) + ", " + getDate(soup) + ", " + getTitle(
        soup) + ", " + getNote(soup) + ", " + str(datetime.datetime.utcnow()) + "\n"
    return line
# TEST = OK

# Gets the list of already scrapped uesrs
def getAlreadyScrapped():
    alreadyScrapped = []
    alreadyScrapped_tmp = os.listdir("D:\\pracadyplomowa\\projektPhotoblog\\dmp")
    for item in alreadyScrapped_tmp:
        alreadyScrapped.append(item.split(".")[0])
    return alreadyScrapped
# TEST = OK


# Check if the user is still active in the service
def checkIfExpired(soup):
    possibility = ["nie istnieje w serwisie Photoblog.pl", "nie dodał jeszcze żadnego wpisu"]
    try:
        expired = soup.find("div", {"class": "msgb_text"}).contents[3]
        expired = expired.decode().replace(".</p>", "").split("<br/>")
        if expired[1] in possibility:
            isexpired = True
        else:
            isexpired = False
    except:
        isexpired = False

    return isexpired
# TEST = OK


# Checks if the blog is password protected
def checkIfPasswordProtected(soup):
    try:
        psswd = soup.find("div", {"class": "show_midoptions_w"}).contents[1]
        psswd = psswd.decode().replace("<h3>", "")
        psswd = psswd.replace("</h3>", "")
        if psswd == "Ten fotoblog zabezpieczony jest hasłem.":
            isProtected = True
        else:
            isProtected = False
    except:
        isProtected = False
    return isProtected
# TEST = OK

############## CORE ##############

print("################# INIT INFO #################")
print('SCRAPPING COMMENCES!')
# I'LL ADD SOME STATS HERE to make it look nice :) Later... much later...

print("################# DIR CHECK #################")
# CREATE LOCATIONS IF NOT EXISTENT

if os.path.isdir(downloadDirectory) == True:
    print("Directory", downloadDirectory, "\t\texists")
else:
    os.makedirs(downloadDirectory)
    print('Directory', downloadDirectory, "\t\tcreated")

with open(path_active, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    log.append(str(datetime.datetime.now()) + ", " + "scrap_start_time : " + str(datetime.datetime.now()) + "\n")
    for row in reader:
        timestart = datetime.datetime.now()
        isFirst = True
        tmp = []
        if row[0] not in getAlreadyScrapped():
            log.append(str(datetime.datetime.now()) + ", " + row[0] + ", " + "user_start_time : " + str(
                datetime.datetime.now()) + "\n")
            URL_userName = row[0]
            soup = getSoup(URL_base, URL_userName, URL_postNumber)
            if not checkIfPasswordProtected(soup):
                if not checkIfExpired(soup):
#                   print("isexpired:", checkIfExpired(soup))
#                   print(checkIfLast(soup, isFirst))
                    if not checkIfLast(soup, isFirst):
                        tmp.append(getLine(soup, row))
                        URL_postNumber = getNextPage(soup).split("/")[4]
                        soup = getSoup(URL_base, URL_userName, URL_postNumber)
                        while not checkIfLast(soup, isFirst):
                            tmp.append(getLine(soup, row))
                            URL_postNumber = getNextPage(soup).split("/")[4]
                            soup = getSoup(URL_base, URL_userName, URL_postNumber)
                        tmp.append(getLine(soup, row))
                    else:
                        tmp.append(getLine(soup, row))
                else:
                    tmp.append(row[0]+", n/a, n/a, n/a, " + str(datetime.datetime.utcnow()) + "\n")
            else:
                tmp.append(row[0] + ", n/a, n/a, n/a, " + str(datetime.datetime.utcnow()) + "\n")
            URL_postNumber = ""
            with open("D:\\pracadyplomowa\\projektPhotoblog\\dmp\\" + URL_userName + ".csv", "w", encoding="utf-8") as postdump:
                      # to be fixed - but as long as it works...
                for a in tmp:
                    postdump.write(a)
                    count += 1
            timeend = datetime.datetime.now()
            duration = timeend - timestart
            tmp = []
            print(count, "lines written in", duration)
            log.append(str(datetime.datetime.now()) + ", " + row[0] + ", " + "user_end_time : " +
                       str(datetime.datetime.now()) + "\n")
            log.append(str(count) + ", " + "lines written in : " + str(duration) + "\n")
            with open("enterpathforlog.csv", "a", encoding="utf-8") as logfile:
               for x in log:
                   logfile.write(x)
            logfile.close()
            postdump.close()
            count = 0
