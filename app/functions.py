import time
import os
from flask import render_template, flash, redirect, url_for
import csv
import requests
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import seaborn as sns
color = sns.color_palette()
import folium
from folium.plugins import HeatMap
import branca.colormap
from collections import defaultdict
import altair as alt
from app import db
from app.models import Hotel


csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'
delfile = True
################################################## Scrape One Hotel ###################################################################################################
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


def scrapeone(x):
    df = pd.read_csv(csv_path+'master_sg.csv', encoding="ISO-8859-1", engine='python', error_bad_lines=False)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    start_url = x

    s = Service(r'S:\SIT Tri 1\Programming\Python Project Hotel\Hotel\app\chromedriver.exe')  # Local file location for chromedriver.exe to use selenium to use the webbrowser

    driver = webdriver.Chrome(service=s)  # To get the chrome service started
    driver.get(start_url)  # To go to the url
    time.sleep(1)
    # driver.find_element(By.CLASS_NAME,"hp-review-score-cta-container-remote").click()
    # time.sleep(2)
    page_source = driver.page_source
    # with open('pagetestzz.html', 'w+', encoding="utf-8") as f:
    #     f.write(driver.page_source)  # Saves and writes the page source or html code locally

    writeheader = True
    deletefile =True
    deletemaster = True
    while True:
        try:
            newurl = driver.current_url
            # print(newurl)
            driver.get(newurl)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

            hotelname = [t.get_text(strip=True) for t in
                         soup.find_all('a', attrs={'class': 'standalone_header_hotel_link'})]
            hoteladdress = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'hotel_address'})]
            review_score = [t.get_text(strip=True) for t in
                            soup.find_all('span', attrs={'class': 'review-score-badge'})]
            overall_review = [review_score[0]]
            scoresz = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'review_score_value'})]
            review_score = review_score[1::]
            test_texxt = soup.find_all("span",
                                       itemprop="reviewBody")  # Retrieves all text within the reviewBody so mixes both positive and negative
            if deletefile == True:
                if os.path.exists(csv_path + hotelname[0] + ".csv"):
                    os.remove(csv_path + hotelname[0] + ".csv")
                if os.path.exists(csv_path+'master_sg.csv'):
                    os.remove(csv_path+'master_sg.csv')
                df.drop(df.index[(df['hotelname'] == hotelname[0])], axis=0, inplace=True)
                df = df.fillna('')
                df = df.values.tolist()
            deletefile = False


            review_fix = [t.get_text for t in soup.find_all("div", attrs={
                "class": "review_item_review_content"})]  # Retrieves all text within the reviewBody so mixes both positive and negative
            review_pos = []
            review_neg = []
            for reviews in review_fix:

                review_fix_test = BeautifulSoup(str(reviews), 'lxml')
                pos_review = [t.get_text(strip=True) for t in review_fix_test.find_all('p', attrs={
                    'class': 'review_pos'})]
                neg_review = [t.get_text(strip=True) for t in review_fix_test.find_all('p', attrs={
                    'class': 'review_neg'})]
                if review_check_pos(review_fix_test) == True:
                    review_pos.append(pos_review)
                if review_check_pos(review_fix_test) == False:
                    review_pos.append([""])
                if review_check_neg(review_fix_test) == True:
                    review_neg.append(neg_review)
                if review_check_neg(review_fix_test) == False:
                    review_neg.append([""])
            review_negz = [item for sublist in review_neg for item in sublist]
            review_negz = [item.replace('\n', '') for item in review_negz]

            review_posz = [item for sublist in review_pos for item in sublist]
            review_posz = [item.replace('\n', '') for item in review_posz]

            'Grab just postal code'
            postalcodecountry = hoteladdress[0].split(' ')
            postalcode = ''
            for x in postalcodecountry:  # Check array of split text for 6 digit postal code
                count = sum(map(str.isdigit, x))
                if count >= 5:
                    postalcode = x
            postalcodefinal = ''.join(c for c in str(postalcode) if c.isdigit())

            from geopy.geocoders import Nominatim

            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode(postalcodefinal + ' Singapore, SG', exactly_one=True, timeout=60)
            getLoc = location.raw

            updatedscore = []

            # Append Review Score together with Review
            review_score = [float(x) for x in review_score]
            review_score = [int(x) for x in review_score]

            for x in review_score:
                if int(x) < 5:
                    updatedscore.append(1)
                if int(x) == 6:
                    updatedscore.append(2)
                if int(x) == 7:
                    updatedscore.append(3)
                if int(x) == 8:
                    updatedscore.append(4)
                if int(x) == 9:
                    updatedscore.append(5)
                if int(x) == 10:
                    updatedscore.append(5)
            scoreandreview = []
            scorecount = 1


            combined = zip(review_posz, review_negz, updatedscore)

            combined2 = []
            for i in combined:
                addin = hotelname[0], postalcodefinal, getLoc['lat'], getLoc['lon'], i[0], i[1], i[2], overall_review, scoresz[0], scoresz[1], scoresz[2],scoresz[3], scoresz[4], scoresz[5], scoresz[6]
                combined2.append(addin)

            if deletemaster == True:
                for item in combined2:
                    addin = item[0], item[1], item[2], item[3], item[4], item[5], item[4] + ' ' + item[5], item[6]
                    df.append(addin)
                with open(csv_path+ 'master_sg.csv', "a", newline='', encoding="utf-8") as csvFile:
                    fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg',
                                  'review_text', 'review-score']
                    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                    writer.writeheader()
                    for item in df:
                        writer.writerow(
                            {'hotelname': item[0], 'postalcode': item[1], 'latitude': item[2],
                             'longitude': item[3],
                             'review_pos': item[4], 'review_neg': item[5],
                             'review_text': str(item[4]) + ' ' + str(item[5]),
                             'review-score': item[7]})
                csvFile.close()
            deletemaster = False

            'print output to csv'

            with open(csv_path + hotelname[0] + ".csv", "a", encoding="utf-8", newline='') as csvFile:
                fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg',
                              'review_text', 'review-score', 'overall_score', 'cleanliness', 'comfort', 'location',
                                  'facilities', 'staff', 'value_for_money', 'Free_Wifi']
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                if writeheader == True:
                    writer.writeheader()
                    writeheader = False
                for item in combined2:
                    writer.writerow(
                        {'hotelname': item[0], 'postalcode': item[1], 'latitude': item[2],
                         'longitude': item[3],
                         'review_pos': item[4], 'review_neg': item[5],
                         'review_text': str(item[4]) + ' ' + str(item[5]),
                         'review-score': item[6],'overall_score': item[7],'cleanliness': item[8],'comfort': item[9],'location': item[10],'facilities': item[11],'staff': item[12],'value_for_money': item[13],'Free_Wifi': item[14]})
            csvFile.close()
            with open(csv_path+'master_sg.csv', "a", newline='', encoding="utf-8") as csvFile:
                fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg',
                              'review_text',
                              'review-score']
                writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                for item in combined2:
                    writer.writerow(
                        {'hotelname': item[0], 'postalcode': item[1], 'latitude': item[2],
                         'longitude': item[3],
                         'review_pos': item[4], 'review_neg': item[5],
                         'review_text': str(item[4]) + ' ' + str(item[5]),
                         'review-score': item[6]})
            csvFile.close()
            driver.find_element("xpath", "//*[contains(@id, 'review_next_page_link')]").click()
        except:
            print("fail or end of pages")
            break

    hoteloutputcsv = hotelname[0]
    return hoteloutputcsv
    driver.quit()


############################################## End Scrape One Hotel ###########################################################################################################


def s_multilinks(x):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    start_url = x

    s = Service(r'S:\SIT Tri 1\Programming\Python Project Hotel\Hotel\app\chromedriver.exe')  # Local file location for chromedriver.exe to use selenium to use the webbrowser

    driver = webdriver.Chrome(service=s)  # To get the chrome service started
    driver.get(start_url)  # To go to the url
    time.sleep(1)

    writeheader = True
    links = []
    hotels = []
    while True:
        try:

            newurl = driver.current_url
            # print(newurl)
            driver.get(newurl)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

            for link in soup.find_all(
                    class_="rlp-main-hotel-review__review_link"):  # to append the link that is retrieved from html
                review_link = link.a.get('href')
                links.append(
                    'https://www.booking.com' + review_link)  # because the html containing the link does not have the https link
            hotelname = [t.get_text(strip=True) for t in
                         soup.find_all('a', attrs={'class': 'rlp-main-hotel__hotel-name-link'})]
            hotels.extend(hotelname)

            driver.find_element(By.CSS_SELECTOR, "a.rlp-main-pagination__btn-txt--next").click()

        except Exception as e:
            # print(e)
            break

    name_link = dict(zip(hotels, links))
    print(name_link)
    for name, link in name_link.items():
        exist_name = Hotel.query.filter_by(hotel_name=name).first()
        if exist_name is not None:
            continue
        else:
            h = Hotel(hotel_name=name, hotel_link=link)
            db.session.add(h)
    db.session.commit()


###################################################################################################################

def scrapemulti(x,y):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

    # start_url='https://www.booking.com/reviews/sg/hotel/rasa-sentosa-resort-by-the-shangri-la.en-gb.html?aid=356980&label=gog235jc-1BEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgXgAgE&sid=db2ad224c338fc25044fbb34d57e5a03'
    #review_start_url = 'https://www.booking.com/reviews/sg/city/singapore.en-gb.html?aid=356980&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE'
    review_start_url = x
    s = Service(
        r'D:\School\INF1002\Week2\chromedriver.exe')  # Local file location for chromedriver.exe to use selenium to use the webbrowser

    driver = webdriver.Chrome(service=s)  # To get the chrome service started
    driver.get(review_start_url)  # To go to the url
    time.sleep(1)
    # driver.find_element(By.CLASS_NAME,"hp-review-score-cta-container-remote").click()
    # time.sleep(2)
    page_source = driver.page_source
    with open('pagetestzz.html', 'w+', encoding="utf-8") as f:
        f.write(driver.page_source)  # Saves and writes the page source or html code locally

    links = []
    name_of_hotel_csv={}
    while True:
        try:
            review_url = driver.current_url
            #print(review_url)
            driver.get(review_url)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

            for link in soup.find_all(
                    class_="rlp-main-hotel-review__review_link"):  # to append the link that is retrieved from html
                review_link = link.a.get('href')
                links.append(
                    'https://www.booking.com' + review_link)  # because the html containing the link does not have the https link
            #print(links)
            driver.find_element(By.CSS_SELECTOR, "a.rlp-main-pagination__btn-txt--next").click()
            writeheader = True
        except:
            print("error")
            break

    for x in range(y):
        driver.get(links[x])
        while True:
            try:
                newurl = driver.current_url
                # print(newurl)
                checkString = links[x]

                driver.get(newurl)

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

                # html_text = soup.get_text() #Retrieves all the text (Don't use this)
                testing = soup.find_all('p', attrs={'class': 'review_pos'})
                # categories_pos = [t.get_text(strip=True) for t in soup.find_all('p', attrs={
                #    'class': 'review_pos'})]  # Retrieves all text within the reviewBody so mixes both positive and negative and saves them in a list
                # categories_neg = [t.get_text(strip=True) for t in soup.find_all('p', attrs={
                #    'class': 'review_neg'})]  # ('p' is for class type, followed by name of class in ,attrs={'class' : 'here'}
                hotelname = [t.get_text(strip=True) for t in
                             soup.find_all('a', attrs={'class': 'standalone_header_hotel_link'})]
                hoteladdress = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'hotel_address'})]
                review_score = [t.get_text(strip=True) for t in
                                soup.find_all('span', attrs={'class': 'review-score-badge'})]
                overall_review=[review_score[0]]
                scoresz=[t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'review_score_value'})]
                review_score = review_score[1::]

                review_fix = [t.get_text for t in soup.find_all("div", attrs={
                    "class": "review_item_review_content"})]  # Retrieves all text within the reviewBody so mixes both positive and negative
                review_pos = []
                review_neg = []
                for reviews in review_fix:

                    review_fix_test = BeautifulSoup(str(reviews), 'lxml')
                    pos_review = [t.get_text(strip=True) for t in review_fix_test.find_all('p', attrs={
                        'class': 'review_pos'})]
                    neg_review = [t.get_text(strip=True) for t in review_fix_test.find_all('p', attrs={
                        'class': 'review_neg'})]
                    if review_check_pos(review_fix_test) == True:
                        review_pos.append(pos_review)
                    if review_check_pos(review_fix_test) == False:
                        review_pos.append(["No positive review"])
                    if review_check_neg(review_fix_test) == True:
                        review_neg.append(neg_review)
                    if review_check_neg(review_fix_test) == False:
                        review_neg.append(["No negative review"])
                review_negz = [item for sublist in review_neg for item in sublist]
                review_negz = [item.replace('\n', '') for item in review_negz]

                review_posz = [item for sublist in review_pos for item in sublist]
                review_posz = [item.replace('\n', '') for item in review_posz]

                'Grab just postal code'
                postalcodecountry = hoteladdress[0].split(' ')
                count = ''
                postalcode = ''
                postalcodefinal = ''
                for x in postalcodecountry:  # Check array of split text for 6 digit postal code
                    count = sum(map(str.isdigit, x))
                    if count >= 5:
                        postalcode = x
                postalcodefinal = ''.join(c for c in str(postalcode) if c.isdigit())

                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="geoapiExercises")
                location = geolocator.geocode(postalcodefinal+ ' Singapore, SG')
                getLoc = location.raw

                updatedscore = []

                # Append Review Score together with Review
                review_score = [float(x) for x in review_score]
                review_score = [int(x) for x in review_score]

                for x in review_score:
                    if int(x) < 5:
                        updatedscore.append(1)
                    if int(x) == 6:
                        updatedscore.append(2)
                    if int(x) == 7:
                        updatedscore.append(3)
                    if int(x) == 8:
                        updatedscore.append(4)
                    if int(x) == 9:
                        updatedscore.append(5)
                    if int(x) == 10:
                        updatedscore.append(5)

                combined = zip(review_posz, review_negz, updatedscore,overall_review,scoresz[0],scoresz[1],scoresz[2],scoresz[3],scoresz[4],scoresz[5],scoresz[6])

                combined2 = []
                for i in combined:
                    addin = postalcodefinal, getLoc['lat'], getLoc['lon'], i[0], i[1], i[2]
                    combined2.append(addin)

                'print output to csv'
                with open(hotelname[0] + ".csv", "a", encoding="utf-8", newline='') as csvFile:
                    fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg',
                                  'review_text', 'review-score','overall_score','cleanliness','comfort','location',
                                  'facilities','staff','value_for_money','Free_Wifi']
                    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                    if writeheader == True:
                        writer.writeheader()
                        writeheader = False
                    for item in combined2:
                        writer.writerow(
                            {'hotelname': hotelname[0], 'postalcode': item[0], 'latitude': item[1],
                             'longitude': item[2],
                             'review_pos': item[3], 'review_neg': item[4],
                             'review_text': str(item[3]) + ' ' + str(item[4]), 'review-score': item[5],'overall_score':item[6],
                             'cleanliness':item[7],'comfort':item[8],'location':item[9],'facilities':item[10],
                             'staff':item[11],'value_for_money':item[12],'Free_Wifi':item[13]})

                with open('SingaporeHotel.csv', "a", newline='', encoding="utf-8") as csvFile:
                    fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg',
                                  'review_text', 'review-score','overall_score','cleanliness','comfort','location',
                                  'facilities','staff','value_for_money','Free_Wifi']
                    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                    for item in combined2:
                        writer.writerow(
                            {'hotelname': hotelname[0], 'postalcode': item[0], 'latitude': item[1],
                             'longitude': item[2],
                             'review_pos': item[3], 'review_neg': item[4],
                             'review_text': str(item[3]) + ' ' + str(item[4]),
                             'review-score': item[5],'overall_score':item[6],
                             'cleanliness':item[7],'comfort':item[8],'location':item[9],'facilities':item[10],
                             'staff':item[11],'value_for_money':item[12],'Free_Wifi':item[13]})
                csvFile.close()
                combined = 0
                review_score = 0
                categories_pos = 0
                name_of_hotel_csv.update({hotelname[0]+'.csv':x})


                driver.find_element("xpath", "//*[contains(@id, 'review_next_page_link')]").click()
            except:
                print("fail or end of pages")
                break

    driver.quit()
    hotel_csv_name_values = list(name_of_hotel_csv.keys())
    hotel_csv_name=hotel_csv_name_values
    return hotel_csv_name

# A=s_multilinks('https://www.booking.com/reviews/sg/city/singapore.en-gb.html?aid=356980&sid=248efadb06977d69b94338011302293d&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE')
# A=str(','.join(A))
# print(A)

####################################################################################################################################
# User input
# df01 = pd.read_csv('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/master_sg.csv', encoding="ISO-8859-1")
# df02 = pd.read_csv('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/Carlton Hotel Singapore.csv', encoding="ISO-8859-1")

##########################
'Histogram'
# fig = px.histogram(df, x='reviews_rating')
# fig.update_layout(title_text='Review rating')
# fig.show()
##########################

# Heatmap of either US or SG


def heatmap(x):
    df = x
    # Heatmap SG
    m = folium.Map([1.44255, 103.79580], zoom_start=11)
    steps = 20
    colormap = branca.colormap.linear.YlOrRd_09.scale(0, 1).to_step(steps)
    gradient_map = defaultdict(dict)
    for i in range(steps):
        gradient_map[1 / steps * i] = colormap.rgb_hex_str(1 / steps * i)

    HeatMap(df[['latitude', 'longitude']].dropna(), radius=13,
            gradient={0.4: 'blue', 0.6: 'purple', 0.8: 'orange', 1.0: 'red'}).add_to(m)
    colormap.add_to(m)
    m.save('app/templates/generated/sg_HeatMap.html')
    # webbrowser.open('USHeatMap.html')
    heatmapname = 'sg_HeatMap.html'
    return heatmapname


# Hotel Vicinity function
def sghotelvicinitymap(x, y):
    df = x
    df2 = y
    # Get and set scrapped excel values
    pointerlatitude = df2['latitude'][1]  # Preset specified hotel's Lat/Lon/Name
    pointerlongitude = df2['longitude'][
        1]  # Crucial for comparing with master dataset to see what is nearby specified hotel
    pointername = df2['hotelname'][1]

    m = folium.Map(location=[pointerlatitude, pointerlongitude], zoom_start=17)  # plot where map will look

    # Specified Hotel Details, stored inside a popup that appears when mouse hovers over marker
    popup = "<html></html>" \
            "<body>" + "<p>" + pointername + "</p>" + \
            "<p>Latitude:" + str(pointerlatitude)[0:7] + "</p>" + \
            "<p>Longitude:" + str(pointerlongitude)[0:7] + "</p>" + \
            "</body>"

    pointerlatitude = df2['latitude'][1]
    pointerlongitude = df2['longitude'][1]
    pointername = df2['hotelname'][1]

    # Plot marker for scraped hotel, in red
    folium.Marker([pointerlatitude, pointerlongitude], popup=popup, max_width=len(pointername) * 20,
                  icon=folium.Icon(color='red', icon_color='#FFFF00')).add_to(m)

    # Get +-  lat/long of scraped hotel
    differencelatitudep2 = float(pointerlatitude) + 0.005
    differencelatitudem2 = float(pointerlatitude) - 0.005
    differencelongitudep2 = float(pointerlongitude) + 0.005
    differencelongitudem2 = float(pointerlongitude) - 0.005

    # get unique name of each hotel in area
    count = 1
    storage = []
    storagecount = []
    for i in range(0, len(df)):
        if (float(df['latitude'][i]) > differencelatitudem2 and float(df['latitude'][i]) < differencelatitudep2) and (
                float(df['longitude'][i]) > differencelongitudem2 and float(
            df['longitude'][i]) < differencelongitudep2):
            if not storage:
                count -= 1
                addin = df['hotelname'][i], df['latitude'][i], df['longitude'][i], df['review-score'][i], \
                        df['review_text'][i]
                storage.append(addin)
                storagecount.append(count)

            if storage[int(count)][0] != df['hotelname'][i]:
                addin = df['hotelname'][i], df['latitude'][i], df['longitude'][i], df['review-score'][i], \
                        df['review_text'][i]
                storage.append(addin)
                storagecount.append(count)
                count += 1

    hotel = []
    df = df.fillna('')
    for i in storage:
        for x in range(0, len(df)):
            if i[0] == df['hotelname'][x]:
                reviewpos = df['review_pos'][x]
                reviewneg = df['review_neg'][x]
                if reviewpos == 'nan':
                    reviewpos = ''
                if reviewneg == 'nan':
                    reviewneg = ''
                addin = df['hotelname'][x], df['review-score'][x], reviewpos, reviewneg, df['review_text'][x]
                hotel.append(addin)

    score1 = 0
    score2 = 0
    score3 = 0
    score4 = 0
    score5 = 0
    piepos = 0
    pieneg = 0
    hoteltotalscore = []
    for i in storage:
        for x in hotel:  # Get total scores 1 to 5 stars for each hotel, as well as whether its positive or negative
            if i[0] == x[0]:
                if x[1] == 1:
                    score1 += 1
                    pieneg += 1
                elif x[1] == 2:
                    score2 += 1
                    pieneg += 1
                elif x[1] == 3:
                    score3 += 1
                    piepos += 1
                elif x[1] == 4:
                    score4 += 1
                    piepos += 1
                elif x[1] == 5:
                    score5 += 1
                    piepos += 1
        addin = i[0], score1, score2, score3, score4, score5, piepos, pieneg
        hoteltotalscore.append(addin)
        score1 = 0
        score2 = 0
        score3 = 0
        score4 = 0
        score5 = 0
        piepos = 0
        pieneg = 0

    pointerlowreviewtext = ''
    pointerhighreviewtext = ''
    pointerreviewscore = ''
    highreviewtext = ''
    lowreviewtext = ''
    reviewscore = ''
    addedintomap = ''

    # Loop through master excel file, check if nearby hotels with required lat/long
    for i in range(0, len(df)):
        if df['hotelname'][i] in addedintomap:
            continue
        if (float(df['latitude'][i]) > differencelatitudem2 and float(df['latitude'][i]) < differencelatitudep2) and \
                (float(df['longitude'][i]) > differencelongitudem2 and float(
                    df['longitude'][i]) < differencelongitudep2) and (df['hotelname'][i] != pointername):
            for x in hotel:
                if x[0] == df['hotelname'][i] and x[4] != ' ':
                    if x[2] == '':
                        highreviewtext = 'No Positive Review'
                    else:
                        highreviewtext = x[2]
                    if x[3] == '':
                        lowreviewtext = 'No Negative Review'
                    else:
                        lowreviewtext = x[3]
                    if int(x[1]) > 4:
                        highreviewtext = highreviewtext
                        lowreviewtext = lowreviewtext
                        reviewscore = x[1]
                    elif int(x[1]) > 3:
                        highreviewtext = highreviewtext
                        lowreviewtext = lowreviewtext
                        reviewscore = x[1]
                    elif int(x[1]) > 2:
                        highreviewtext = highreviewtext
                        lowreviewtext = lowreviewtext
                        reviewscore = x[1]
                    elif int(x[1]) > 1:
                        highreviewtext = highreviewtext
                        lowreviewtext = lowreviewtext
                        reviewscore = x[1]
                    elif int(x[1]) == 0:
                        highreviewtext = highreviewtext
                        lowreviewtext = lowreviewtext
                        reviewscore = x[1]
                if x[0] == pointername and x[4] != ' ':
                    if not x[2]:
                        pointerhighreviewtext = 'No Positive Review'
                    else:
                        pointerhighreviewtext = x[2]
                    if not x[3]:
                        pointerlowreviewtext = 'No Negative Review'
                    else:
                        pointerlowreviewtext = x[3]
                    if int(x[1]) > 4:
                        pointerhighreviewtext = pointerhighreviewtext
                        pointerlowreviewtext = pointerlowreviewtext
                        pointerreviewscore = x[1]
                    elif int(x[1]) > 3:
                        pointerhighreviewtext = pointerhighreviewtext
                        pointerlowreviewtext = pointerlowreviewtext
                        pointerreviewscore = x[1]
                    elif int(x[1]) > 2:
                        pointerhighreviewtext = pointerhighreviewtext
                        pointerlowreviewtext = pointerlowreviewtext
                        pointerreviewscore = x[1]
                    elif int(x[1]) > 1:
                        pointerhighreviewtext = pointerhighreviewtext
                        pointerlowreviewtext = pointerlowreviewtext
                        pointerreviewscore = x[1]
                    elif int(x[1]) == 0:
                        pointerhighreviewtext = pointerhighreviewtext
                        pointerlowreviewtext = pointerlowreviewtext
                        pointerreviewscore = x[1]

            html_template = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                          <script src="https://cdn.jsdelivr.net/npm/vega@{vega_version}"></script>
                          <script src="https://cdn.jsdelivr.net/npm/vega-lite@{vegalite_version}"></script>
                          <script src="https://cdn.jsdelivr.net/npm/vega-embed@{vegaembed_version}"></script>
                          <style>
                            table, td, th ,h3{{  
                            font-family: Verdana, sans-serif;
                            text-align: center;
                            }}

                            table {{
                            border-collapse: collapse;
                            width: 100%;
                                }}
                            th, td {{
                            padding: 15px;
                            }}
                            </style>
                        </head>
                        <body>
                        <table>
                        <tr>
                        <th><h3>""" + str(pointername) + """</h3></th>
                        <th><h3>""" + df['hotelname'][i] + """</h3></th>
                        </tr>
                        <tr>
                        <td><table><tr><th>Latitude</th><th>Longitude</th></tr><tr><td>""" + str(pointerlatitude)[
                                                                                             0:7] + """</td><td>""" + str(
                pointerlongitude)[0:7] + """</td></tr></table></td>
                        <td><table><tr><th>Latitude</th><th>Longitude</th></tr><tr><td>""" + str(df['latitude'][i])[
                                                                                             0:7] + """</td><td>""" + str(
                df['longitude'][i])[0:7] + """</td></tr></table></td>
                        <td></td>
                        </tr>
                        <tr>
                        <h3>Hotel Reviews and Sentiment Analysis</h3>
                        <td><div id="vis0"></div></td>
                        <td><div id="vis1"></div></td>
                        </tr>
                        <tr>
                        <td><div id="vis2"></div></td>
                        <td><div id="vis3"></div></td>
                        </tr>
                        <tr>
                        <td><table><tr><th>A Review of the hotel</th><th>Rating</th></tr><tr><td><table><tr><th>Positive Review</th><th>Negative Review</th></tr><tr><td>""" + \
                            str(pointerhighreviewtext) + """</td><td>""" + str(
                pointerlowreviewtext) + """</td></tr></table></td><td>""" + str(pointerreviewscore) + """</td></tr></table></td>
                        <td><table><tr><th>A Review of the hotel</th><th>Rating</th></tr><tr><td><table><tr><th>Positive Review</th><th>Negative Review</th></tr><tr><td>""" + \
                            str(highreviewtext) + """</td><td>""" + str(
                lowreviewtext) + """</td></tr></table></td><td>""" + str(reviewscore) + """</td></tr></table></td>
                        </tr>  
                        </table>
                        <table>
                        <tr>
                        <th>
                        Comparing hotels
                        </th>
                        </tr>
                        <tr><td>
                        <div id="vis4"></div>   
                        </td><tr>
                        <tr><td>
                        <div id="vis5"></div>   
                        </td><tr>
                        </table>
                        <script type="text/javascript">
                          vegaEmbed('#vis0', {spec0}).catch(console.error);
                          vegaEmbed('#vis1', {spec1}).catch(console.error);
                          vegaEmbed('#vis2', {spec2}).catch(console.error);
                          vegaEmbed('#vis3', {spec3}).catch(console.error);
                          vegaEmbed('#vis4', {spec4}).catch(console.error);
                          vegaEmbed('#vis5', {spec5}).catch(console.error);
                        </script>
                        </body>
                        </html>
                        """

            tooltip = "<html></html>" \
                      "<body>" + "<p>" + df['hotelname'][i] + "</p>" + \
                      "<p>Latitude:" + str(df['latitude'][i])[0:7] + "</p>" + \
                      "<p>Longitude:" + str(df['longitude'][i])[0:7] + "</p>" + \
                      "<p>Latest Review:" + str(df['review-score'][i]) + "</p>" + \
                      "</body>"

            # Extract from hotel list, which has values of hotels and their total 1 to 5 star reviews and positive/negative review
            for x in hoteltotalscore:
                if pointername == x[0]:
                    currentscore1 = [x[1], x[2], x[3], x[4], x[5]]
                    pointerpie = [x[6], x[7]]

            for x in hoteltotalscore:
                if df['hotelname'][i] == x[0]:
                    currentscore2 = [x[1], x[2], x[3], x[4], x[5]]
                    hotelpie = [x[6], x[7]]

            # Plot dataframes that store data to be plotted into maps
            # BarGraph of total reviews, 1 to 5 stars for specified hotel
            source0 = pd.DataFrame(
                {
                    'Review Rating': ['1', '2', '3', '4', '5'],
                    'Amount of review': currentscore1,
                }
            )
            # BarGraph of total reviews, 1 to 5 stars for surrounding hotel
            source1 = pd.DataFrame(
                {
                    'Review Rating': ['1', '2', '3', '4', '5'],
                    'Amount of review': currentscore2,
                }
            )
            # PieGraph of total reviews, split into either positive/negative for specified hotel
            source2 = pd.DataFrame(
                {
                    'Review sentiment': ['Positive', 'Negative'],
                    'Amount of review': pointerpie,
                }
            )
            # PieGraph of total reviews, split into either positive/negative for surrounding hotel
            source3 = pd.DataFrame(
                {
                    'Review sentiment': ['Positive', 'Negative'],
                    'Amount of review': hotelpie,
                }
            )
            # Combined values of bargraph containing total reviews
            source4 = pd.DataFrame(
                {
                    'Review Rating': ['1', '2', '3', '4', '5'],
                    pointername: [currentscore1[0], currentscore1[1], currentscore1[2], currentscore1[3],
                                  currentscore1[4]],
                    df['hotelname'][i]: [currentscore2[0], currentscore2[1], currentscore2[2], currentscore2[3],
                                         currentscore2[4]],
                }
            )
            # Combined values of piegraph containing postive/negative
            source5 = pd.DataFrame(
                {
                    'Review Rating': ['Positive', 'Negative'],
                    pointername: [pointerpie[0], pointerpie[1]],
                    df['hotelname'][i]: [hotelpie[0], hotelpie[1]],
                }
            )
            # Plot the grahps based on pandas database made above
            chart0 = alt.Chart(source0).mark_bar().encode(alt.X('Review Rating'), alt.Y('Amount of review'),
                                                          tooltip=alt.Tooltip('Amount of review')).properties(width=300,
                                                                                                              height=200,
                                                                                                              title=pointername + ' overallreview',
                                                                                                              autosize=alt.AutoSizeParams(
                                                                                                                  type='pad',
                                                                                                                  contains='padding'))
            chart1 = alt.Chart(source1).mark_bar().encode(alt.X('Review Rating'), alt.Y('Amount of review'),
                                                          tooltip=alt.Tooltip('Amount of review')).properties(width=300,
                                                                                                              height=200,
                                                                                                              title=df[
                                                                                                                        'hotelname'][
                                                                                                                        i] + ' overall review',
                                                                                                              autosize=alt.AutoSizeParams(
                                                                                                                  type='pad',
                                                                                                                  contains='padding'))
            chart2 = alt.Chart(source2).mark_arc().encode(
                theta=alt.Theta(field="Amount of review", type="quantitative"), tooltip=alt.Tooltip('Amount of review'),
                color=alt.Color(field="Review sentiment", type="nominal")).properties(width=300, height=200,
                                                                                      title=pointername + ' review sentiment',
                                                                                      autosize=alt.AutoSizeParams(
                                                                                          type='pad',
                                                                                          contains='padding'))
            chart3 = alt.Chart(source3).mark_arc().encode(
                theta=alt.Theta(field="Amount of review", type="quantitative"), tooltip=alt.Tooltip('Amount of review'),
                color=alt.Color(field="Review sentiment", type="nominal")).properties(width=300, height=200,
                                                                                      title=df['hotelname'][
                                                                                                i] + ' review sentiment',
                                                                                      autosize=alt.AutoSizeParams(
                                                                                          type='pad',
                                                                                          contains='padding'))
            chart4 = alt.Chart(source4).mark_bar().encode(alt.X('Amt of Reviews:Q'), alt.Y('score:N'),
                                                          tooltip=alt.Tooltip('Amt of Reviews:Q'), color='score:N',
                                                          row=alt.Row('Review Rating',
                                                                      sort=['1', '2', '3', '4', '5'])).transform_fold(
                as_=['score', 'Amt of Reviews'], fold=[pointername, df['hotelname'][i]]).properties(width=700,
                                                                                                    title=pointername + ' against ' +
                                                                                                          df[
                                                                                                              'hotelname'][
                                                                                                              i],
                                                                                                    autosize=alt.AutoSizeParams(
                                                                                                        type='pad',
                                                                                                        contains='padding'))
            chart5 = alt.Chart(source5).mark_bar().encode(alt.X('Positive/Negative amount:Q'), alt.Y('Sentiment:N'),
                                                          tooltip=alt.Tooltip('Positive/Negative amount:Q'),
                                                          color='Sentiment:N', row=alt.Row('Review Rating',
                                                                                           sort=['Positive',
                                                                                                 'Negative'])).transform_fold(
                as_=['Sentiment', 'Positive/Negative amount'], fold=[pointername, df['hotelname'][i]]).properties(
                width=700, title=pointername + ' against ' + df['hotelname'][i],
                autosize=alt.AutoSizeParams(type='pad', contains='padding'))

            charts_code = html_template.format(
                vega_version=alt.VEGA_VERSION,
                vegalite_version=alt.VEGALITE_VERSION,
                vegaembed_version=alt.VEGAEMBED_VERSION,
                spec0=chart0.to_json(indent=None),
                spec1=chart1.to_json(indent=None),
                spec2=chart2.to_json(indent=None),
                spec3=chart3.to_json(indent=None),
                spec4=chart4.to_json(indent=None),
                spec5=chart5.to_json(indent=None),
            )

            iframe = branca.element.IFrame(html=charts_code, width=1100, height=800)
            popup = folium.Popup(iframe, max_width=1100, max_height=800)
            folium.Marker(location=[df['latitude'][i], df['longitude'][i]], tooltip=tooltip, popup=popup).add_to(m)
            addedintomap = addedintomap + df['hotelname'][i]

    m.save('app/templates/generated/'+pointername + ' HotelVicinity.html')

    # webbrowser.open(pointername + ' HotelVicinity.html')
    hotelvicinityname = pointername + ' HotelVicinity.html'

    return hotelvicinityname

# Output file names, heatmap ontop hotelvicnity below

# # heatmapname = heatmap(df01)
# hotelvicinityname = sghotelvicinitymap(df01, df02)

##########################################################################################

#Scrape by Category
def overall_reviews(csvfile):
    reader=pd.read_csv(csvfile)
    list_overall=[reader['overall_score'][0],reader['cleanliness'][0],reader['comfort'][0],reader['location'][0],reader['facilities'][0],
                  reader['staff'][0],reader['value_for_money'][0],reader['Free_Wifi'][0]]
    return list_overall


#########################################################################################
#Scrape by Month
def scrapemonth(x):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    start_url = x

    s = Service(
        r'C:\Users\USER\Documents\Pycharm_download\Hotel\chromedriver.exe')  # Local file location for chromedriver.exe to use selenium to use the webbrowser

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


            # test_texxt=soup.find_all("span", itemprop="reviewBody") #Retrieves all text within the reviewBody so mixes both positive and negative
            monthdate = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'review_staydate'})]

            monthdateseperate =[]
            for i in monthdate:
                split = i.split(' ')
                splitadd = split[2],split[3]
                monthdateseperate.append(splitadd)

            'print output to csv'
            with open(csv_path+"MonthDate.csv", "a", encoding="utf-8", newline='') as csvFile:
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

    hoteloutputcsv = "MonthDate.csv"
    return hoteloutputcsv
    driver.quit()
