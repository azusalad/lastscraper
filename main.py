from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm
import time
import os
import csv

from config import *

def monthToNum(abbr):
    """Turns month abbreviation to a numbeer"""
    return {
            'jan': '01',
            'feb': '02',
            'mar': '03',
            'apr': '04',
            'may': '05',
            'jun': '06',
            'jul': '07',
            'aug': '08',
            'sep': '09',
            'oct': '10',
            'nov': '11',
            'dec': '12'
    }[abbr]

def to_24hr(tod):
    """Converts the time to 24 hour format"""
    # first split tod at the colon because some hours have 1 digit some hours have 2
    if tod.split(':')[1][2:] == 'pm':
        a = int(tod.split(':')[0])
        a += 12
        return str(a) + tod[-5:-2]
    else:
        return tod.split('am')[0]

def check(existing, title, artist, year, month, day ,dow, tod, delimiter):
    """I hate dst.  Too lazy so this just checks if the song exists within a +- 1 hour range.  Same minutes tho"""
    r = [int(tod.split(':')[0])]
    r.append(int(tod.split(':')[0]) + 1)
    r.append(int(tod.split(':')[0]) - 1)
    s = tod.split(':')[1]
    if not f"{title}{delimiter}{artist}{delimiter}{year}{delimiter}{month}{delimiter}{day}{delimiter}{dow}{delimiter}{r[0]}:{s}\n" in existing:
        if not f"{title}{delimiter}{artist}{delimiter}{year}{delimiter}{month}{delimiter}{day}{delimiter}{dow}{delimiter}{r[1]}:{s}\n" in existing:
            if not f"{title}{delimiter}{artist}{delimiter}{year}{delimiter}{month}{delimiter}{day}{delimiter}{dow}{delimiter}{r[2]}:{s}\n" in existing:
                return True
    return False

def create_driver(headless,ublock):
    """Create driver"""
    print('creating driver')
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    driver = webdriver.Firefox(executable_path=path,options=options)
    try:
        driver.install_addon(os.path.join(os.getcwd(), ublock),
                            temporary=True)
    except:
        print('Invalid ublock path specified')
    return driver

def load(profile):
    """read existing file if exists else just write it"""
    if os.path.exists(profile + ".csv"):
        new_profile = False
        f = open(profile + ".csv", 'r')
        existing = f.readlines()
        f.close()
        # make a backup
        f = open(profile + ".csv~", 'w')
        f.write(''.join(x for x in existing))
        f.close()
    else:
        new_profile = True
        f = open(profile + ".csv", 'w')
        f.close()
        existing = []
    line_count = len(existing)
    return (line_count,existing,new_profile)

def login(driver, profile, password):
    """log in, needed because you won't be able to go past page 1 in the library"""
    driver.get('https://www.last.fm/login')
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id_username_or_email')))
    driver.find_element(By.CSS_SELECTOR,'#id_username_or_email').send_keys(profile)
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR,'#id_password').send_keys(password)
    driver.find_element(By.CSS_SELECTOR,'button.btn-primary').click()
    input('Press enter once you have finished logging in\n>')

def reorder(profile,line_count):
    """Reorders the csv file so it is still reverse chronological.  Need to copy everything from line # line_count and put insert it starting at line #2"""
    f = open(profile + ".csv", 'r')
    a = f.readlines()
    header = a[0]
    old = a[1:line_count]
    new = a[line_count:]
    f.close()
    # now rewrite the csv with the new stuff at the top
    f = open(profile + ".csv", 'w')
    f.write(header)
    f.write(''.join(str(x) for x in new))
    f.write(''.join(str(x) for x in old))
    f.close()

def find_data(song):
    """Finds song data when given the list of songs on the website"""
    title = song.find_element(By.CLASS_NAME,'chartlist-name').text
    artist = song.find_element(By.CLASS_NAME,'chartlist-artist').text
    timestamp = song.find_element(By.CLASS_NAME,'chartlist-timestamp').find_element(By.TAG_NAME,('span')).get_attribute('title')
    timestamp = timestamp.split(" ")
    dow = timestamp[0]
    if len(timestamp[1]) == 1:
        day = "0" + str(timestamp[1])
    else:
        day = timestamp[1]
    month = monthToNum(timestamp[2].lower())
    year = timestamp[3].split(',')[0]
    tod = to_24hr(timestamp[4])
    return title, artist, timestamp, dow, day, month, year, tod

def loop(driver, profile, delimiter):
    """Main loop of the program.  Keeps going to next page scraping data"""
    driver.get('https://www.last.fm/user/' + str(profile) + '/library')
    exist_count = 0
    while True:
        # write to file after every page to ensure that if one page goes wrong, still saves progress
        finish = False
        a = open(profile + ".csv",'a')
        csv_writer = csv.writer(a, delimiter=delimiter)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'nav.navlist:nth-child(1) > ul:nth-child(1) > li:nth-child(1) > a:nth-child(1)')))
        time.sleep(cooldown)
        songs = driver.find_elements(By.CLASS_NAME,'chartlist-row')
        for song in tqdm(songs):
            title, artist, timestamp, dow, day, month, year, tod = find_data(song)
            if check(existing, title, artist, year, month, day, dow, tod, delimiter):
                csv_writer.writerow([title,artist,year,month,day,dow,tod])
                exist_count = 0
            else:
                print('exists, skipping')
                exist_count += 1
        if exist_count > 2:
            finish = True
        # write to file and move to next page.  writing file after every page in case program crashes
        a.close()
        try:
            driver.find_element(By.CSS_SELECTOR,'.pagination-next > a:nth-child(1)').click()
        except:
            break
        else:
            # if there are more than three existing entries in a row then you probably reached the point where you stopped scraping last time
            if finish:
                break
            print('moving to next page')


driver = create_driver(headless,ublock)
line_count, existing, new_profile = load(profile)
login(driver,profile,password)
loop(driver, profile, delimiter)
if not new_profile:
    reorder(profile,line_count)

driver.close()
print('Process completed')


