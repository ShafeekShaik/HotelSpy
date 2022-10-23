import time
import csv
import requests
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

input_url = 'https://www.booking.com/reviews/sg/hotel/four-season-singapore.en-gb.html?aid=356980&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE&sid=0592c1baed62f1328376ae7ea3a086ed&customer_type=total&hp_nav=0&old_page=0&order=featuredreviews&page=3&r_lang=en&rows=75&'
input_url2= 'https://www.booking.com/reviews/sg/hotel/marina-bay-sands.en-gb.html?aid=356980&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE&sid=1648af7e7596bfe6a1287d095be08961'
csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'

def review_check_pos(positive_review):
    pos_review = [t.get_text(strip=True) for t in positive_review.find_all('p', attrs={
        'class': 'review_pos'})]
    if pos_review == []:
        return False
    elif pos_review != []:
        return True


def review_check_neg(negative_review):
    neg_review = [t.get_text(strip=True) for t in negative_review.find_all('p', attrs={
        'class': 'review_neg'})]
    if neg_review == []:
        return False
    elif neg_review != []:
        return True


def scrapemonth(x):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    start_url = x

    s = Service(
        r'S:\SIT Tri 1\Programming\Python Project Hotel\Hotel\app\chromedriver.exe')  # Local file location for chromedriver.exe to use selenium to use the webbrowser

    driver = webdriver.Chrome(service=s)  # To get the chrome service started
    driver.get(start_url)  # To go to the url
    time.sleep(1)
    # driver.find_element(By.CLASS_NAME,"hp-review-score-cta-container-remote").click()
    # time.sleep(2)
    # page_source = driver.page_source
    # with open('pagetestzz.html', 'w+', encoding="utf-8") as f:
    #     f.write(driver.page_source)  # Saves and writes the page source or html code locally

    writeheader = True
    while True:
        try:
            newurl = driver.current_url
            print(newurl)
            driver.get(newurl)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

            hotelname = [t.get_text(strip=True) for t in
                         soup.find_all('a', attrs={'class': 'standalone_header_hotel_link'})]

            # test_texxt=soup.find_all("span", itemprop="reviewBody") #Retrieves all text within the reviewBody so mixes both positive and negative
            monthdate = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'review_staydate'})]

            monthdateseperate =[]
            for i in monthdate:
                split = i.split(' ')
                splitadd = split[2],split[3]
                monthdateseperate.append(splitadd)

            'print output to csv'
            with open("MonthDate.csv", "a", encoding="utf-8", newline='') as csvFile:
                fieldnames = ['month','year']
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                if writeheader == True:
                    writer.writeheader()
                    writeheader = False
                for item in monthdateseperate:
                    writer.writerow(
                        {'month': item[0],'year': item[1]})

            csvFile.close()
            driver.find_element("xpath", "//*[contains(@id, 'review_next_page_link')]").click()
        except:
            print("fail or end of pages")
            break

    hoteloutputcsv = hotelname[0]+"MonthDate.csv"
    return hoteloutputcsv
    driver.quit()


# test = scrapemonth(input_url2)
# print(test)
