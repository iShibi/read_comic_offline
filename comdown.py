# This program supports both Chrome and Firefox in headless as well as in head mode. readcomiconline contains a lot of ads,
# that's why this program installs an adblock extension for Firefox (in headless as well as in head mode) everytime you run it.
# Chrome does not support extensions in headless mode so if you want to use chrome with extensions you will have to run it in head mode after
# setting the path to your chrome profile down below. The profile path will help selenium to open your chrome browser with all your settings and
# extensions in place. I could do the same with Firefox instead of installing adblock everytime but Firefox has an issue where it opens your
# profile but your installed extensions don't work even though they are enabled. So, both Chrome and Firefox have some issues but still I'll advice
# you to use Firefox mode because it's easy and less work. For Chrome, extensions are not available in headless mode and even in head mode you
# will have to do some work to make it open the browser with already installed extensions.


# These two lines make the terminal clean, they are optional.
from os import system
system('cls')

browser_option = input("Choose a browser (chrome/firefox): ")
browser_mode = input("Choose a mode (head/headless): ")

from selenium import webdriver

if browser_option == 'chrome':
    from selenium.webdriver.chrome.options import Options
elif browser_option == 'firefox':
    from selenium.webdriver.firefox.options import Options

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import urllib.request
import patoolib
import os


def download(page):
    try:
        img_xpath = f'//*[@id="divImage"]/p[{str(page)}]/img'
        img = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, img_xpath)))
        link = img.get_attribute('src')
        urllib.request.urlretrieve(link, f"pages/{page}.jpg")
    except:
        global downloading
        downloading = False


path = r'PATH\TO\The\FOLDER\WHERE\YOU\WANT\TO\SAVE\YOUR\COMIC\PAGES'
files = []
timeout = 20
i = 1
downloading = True

quality_set = input("\nChoose quality of the comic (high/low): ")
comic_url = input("Enter url of the comic (Enter 's' to open search mode): ")

options = Options()

if browser_mode == 'headless':
    options.headless = True

if browser_option == 'chrome':
    profile = r"C:\Users\Username\AppData\Local\Google\Chrome\User Data"        # search 'chrome://version' to find your chrome profile path. Remove the stuff after 'User Data'
    options.add_argument(f"--user-data-dir={profile}")
    browser = webdriver.Chrome(options = options, executable_path=r"PATH\TO\chromedriver.exe")
    #options.add_argument('log-level=3')
    #options.add_experimental_option('excludeSwitches', ['enable-logging'])
elif browser_option == 'firefox':
    browser = webdriver.Firefox(options = options, executable_path=r"PATH\TO\geckodriver.exe")
    browser.install_addon(r"PATH\TO\uBlock0@raymondhill.net.xpi")          # this will install an adblock extension in firefox

if comic_url == 's':
    comic_name = input("\nWhich comic you want to download: ")
    year = int(input(f"In which year '{comic_name}' was first published (Enter '1' if it's a oneshot): "))
    if year != 1:
        issue_number = input(f"Which issue of '{comic_name}' you want to download: ")
    url = "https://readcomiconline.to/"

    browser.get(url)

    search_bar = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "keyword")))
    search_bar.send_keys(comic_name)

    search = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, r'//*[@id="imgSearch"]')))
    search.click()

    if year == 1:
        comic = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, r"(//*[@class='listing']//a)[1] | (//*[@class='list']//a)[1]")))
        comic.click()
    else:
        comic = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, f"{year}")))
        comic.click()        

    if year != 1:        
        top_issue = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, r"(//*[@class='listing']//a)[1] | (//*[@class='list']//a)[1]")))
        top_issue_name = top_issue.text
        top_issue_number = int(top_issue_name.partition("#")[-1])
        required_issue = top_issue_number - (int(issue_number) - 1)
        issue = WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, f"(//*[@class='listing']//a)[{required_issue}] | (//*[@class='list']//a)[{required_issue}]")))
        issue.click()
else:
    browser.get(comic_url)

if quality_set == 'high':
    quality = Select(WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.ID, "selectQuality"))))
    quality.select_by_value("hq")

reading_type = Select(WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, r'//*[@id="selectReadType"]'))))
reading_type.select_by_value("1")

print("Downloading...")
while downloading:
    download(i)
    i += 1


print("Download Complete")
for r, d, f in os.walk(path):
    for file in f:
        if '.jpg' in file:
            files.append(os.path.join(r, file))


print("Converting images into .cbr format...")
images = tuple(files)
if comic_url == 's':
    patoolib.create_archive(f"#{issue_number}.cbr", images, verbosity=-1)
else:
    patoolib.create_archive("comic.cbr", images, verbosity=-1)


print("Deleting the images...")
for f in files:
    os.remove(f)


print(f"Comic has been downloaded successfully!")
browser.close()