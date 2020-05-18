# make sure you download chromedriver.exe first and put that in the same directory where this file is.

# importing required modules
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import patoolib
import os

path = r'path to the folder where you want to save the downloaded pages of the comic'
# making an empty list 'files' which will contain the downloaded pages as elemesnts.
files = []
# selenium will wait till the specified time limit before throwing an error if it does not find the element you are trying to get. Increase this if you have a slow internet connection.
timeout = 15
# initializing a variable 'downloading' to true, the while loop will run till this variable is true. The download funtion will make it false if selenium does not find a comic page in given time limit of 'timeout'
downloading = True

# program will ask user these three questions on execution.
comic_name = input("Which comic you want to download: ")                            # name of the comic user want to download
year = input(f"In which year '{comic_name}' was first published: ")                 # year of publication of issue number 1 of the given comic
issue_number = input(f"Which issue of '{comic_name}' you want to download: ")       # comic issue number which user wants to download

# link to the homepage of readcomiconline website
url = "https://readcomiconline.to/"

# changing selenium's default settings
chrome_options = Options()
profile = r"put your chrome browser profile here to keep the browser settings and extensions"
chrome_options.add_argument(f"--user-data-dir={profile}")                           # without this selenium will open a brand new chrome browser without your settings and extensions
chrome_options.add_argument('log-level=3')                                          # this will stop selenium from printing unnecessary information in the terminal
browser = webdriver.Chrome(options=chrome_options)                                  # initializing the browser object
browser.get(url)                                                                    # this will open the homepage of readcomiconline website

# function which will download the comic pages
def download(page_number):
    try:
        img_xpath = f'//*[@id="divImage"]/p[{str(page_number)}]/img'
        img = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, img_xpath)))
        link = img.get_attribute('src')
        urllib.request.urlretrieve(link, f"pages/{page_number}.jpg")
    except:
        global downloading
        downloading = False

# finding the search bar on the homepage
search_bar = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "keyword")))
# entering the comic name in the search bar
search_bar.send_keys(comic_name + " " + year)

# finding the search button on the homepage
search = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "imgSearch")))
# clicking on the search button
search.click()

# finding the first result, which is the comic the user wants to download
comic_xpath = r'//*[@id="leftside"]/div/div[2]/div/table/tbody/tr[3]/td[1]/a'
comic = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, comic_xpath)))
# clicking on the first result
comic.click()

# finding the required issue from the list of all published issues
issue = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, f"{issue_number}")))
# clicking on the required issue
issue.click()

page_number = 1
print("Downloading...")
# calling the download funtion inside loop till all the pages are downloaded
while downloading:                      # download is true by default and will remain true till all the pages are downloaded
    download(page_number)               # calling the download funtion with page number as an argument
    page_number += 1                    # increasing page number by 1 with each iteration


print("Download Complete")
# storing all the downloaded pages in the list 'files'
for r, d, f in os.walk(path):
    for file in f:
        if '.jpg' in file:
            files.append(os.path.join(r, file))


print("Converting images into .cbr format...")
# converting the list 'files' into a tuple 'images' because that is what patool supports
images = tuple(files)
# using patool to convert all the elements inside the tuple 'images' into a .cbr file
patoolib.create_archive(f"#{issue_number}.cbr", images, verbosity=-1)


# this is optional. If you do not want to delete the downloaded images after making the .cbr file, just remove this part
print("Deleting the images...")
for f in files:
    os.remove(f)


print(f"Issue #{issue_number} has been downloaded successfully!")
