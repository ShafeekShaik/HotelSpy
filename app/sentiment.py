import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from selenium import webdriver
color = sns.color_palette()
from wordcloud import WordCloud
import numpy as np
import plotly.offline as py
from bs4 import BeautifulSoup
import plotly.graph_objs as go
import plotly.tools as tls
import plotly.express as px

import nltk
from selenium.webdriver.chrome.service import Service
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os
csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'

nltk.download('vader_lexicon')
vader = SentimentIntensityAnalyzer()
input_url = 'https://www.booking.com/reviews/sg/hotel/the-barracks-by-far-east-hospitality.en-gb.html?aid=356980&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE&sid=248efadb06977d69b94338011302293d'


# Use this function to read the file, input file path as input
def read_csv(filename):
    csv_file_df = pd.read_csv(filename)
    return csv_file_df


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
# Call this function and map it to a variable

# Use this function to generate a graph for data visualization with reference to the function read_csv
def generate_graph(csv_df):
    fig = px.histogram(csv_df, x="review-score")  # Change according to the current data set using

    # This Below is for the airbnb locally sourced data
    # fig = px.histogram(df, x="review_scores_rating")
    fig.update_traces(marker_color="blue", marker_line_color='rgb(8,48,107)',
                      marker_line_width=1.5)
    fig.update_layout(title_text='Product Score')
    fig.write_image('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/bargraph'+csv_df['hotelname'][0]+'.png')


stopwords = set(stopwords.words('english'))


# use this function to generate a stop word with the input being the output of the function read_csv
def generate_stopword(csv_df):
    stopwords.update(["br", "href", "room", "hotel", "rooms", "good", "great"])
    textt = " ".join(map(str, csv_df.review_text))
    wordcloud = WordCloud(stopwords=stopwords).generate(textt)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/wordcloud12.png')
    plt.close('all')
    # plt.show()


def remove_punctuation(text):
    final = "".join(u for u in text if u not in ("?", ".", ";", ":", "!", '"'))
    return final


# Pre trained model to classify the test data
# Function to generate the data frame analysis column along with the vader lexicon compound numbers
# Used to get a solid breakdown later
def generate_dataframe_column(dataframe_input):
    # print(dataframe_input)
    # dataframe_input.head(10)
    dataframez = dataframe_input.dropna(subset=['review_text'])

    dataframenew = dataframez[['hotelname', 'postalcode', 'review_pos', 'review_neg', 'review_text', 'review-score']]
    function = lambda title: vader.polarity_scores(title)['compound']
    dataframenew['compound'] = dataframenew['review_text'].apply(function)
    dataframenew['sentiment_score'] = dataframenew['review-score'].apply(
        lambda rating: 'Positive' if rating > 3 else ('Neutral' if rating == 3 else 'Negative'))
    return dataframenew


def getAnalysis(
        score):  # Function to break down the compound scores given to us to determine if review is negative or positive
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def breakdown_dataframe(new_dataframe):  # Use with reference in regard to the generate_dataframe_column function important for later parts so please use this
    new_dataframe['sentiment'] = new_dataframe['compound'].apply(getAnalysis)
    # print(new_dataframe.head())
    newest_dataframe = new_dataframe[['hotelname', 'postalcode', 'review_pos', 'review_neg', 'review_text', 'review-score','sentiment','sentiment_score','compound']]

    newest_dataframe['sentimentt'] = newest_dataframe['sentiment'].replace({'Negative': -1})

    newest_dataframe['sentimentt'] = newest_dataframe['sentimentt'].replace({'Positive': 1})
    newest_dataframe['sentimentt'] = newest_dataframe['sentimentt'].replace({'Neutral': 0})
    # newest_dataframe.to_csv('Final_product.csv')
    # newest_dataframe = newest_dataframe[['reviews_text', 'sentimentt']]
    newest_dataframe['Combined Sentiment'] = newest_dataframe['sentiment_score']+newest_dataframe['sentiment'] #Merges sentiment together with rating first then reviews
    return newest_dataframe


def export_csv(dataframe): #outputs final csv file with the analysis portion done
    dataframe.to_csv('Final_product.csv')

def filterhotel(csvfile,hotelpostal): #Filter hotel base on postal code
    reader=csvfile
    reader=reader[reader['postalcode']==hotelpostal]
    hotelname=reader['hotelname'][0]
    reader.to_csv(hotelname+'.csv')

def lowest_review(csvfile): #most negative review
    reader=csvfile
    mostnegative=reader['compound'].min()
    listtest=reader.loc[reader['compound'] == mostnegative]
    finaltest=listtest.values.tolist()
    output=finaltest[0][0::]
    return output

def top_ten_pos(csvfile): #for all the reviews in the database
    reader = csvfile
    mostpositive = reader.nlargest(10,['review-score','compound'])
    finaltest = mostpositive.values.tolist()
    output = finaltest
    return output

def top_ten_neg(csvfile):
    reader = csvfile
    mostpositive = reader.nsmallest(10,['review-score','compound'])
    finaltest = mostpositive.values.tolist()
    output = finaltest
    return output


def highest_review(csvfile): #Most positive review
    reader=csvfile
    mostpositive=reader['compound'].max()
    listtest=reader.loc[reader['compound'] == mostpositive]
    finaltest=listtest.values.tolist()
    output=finaltest[0][0::]
    return output

def wordcloud_gen(dataframe):  # Get dataframe from previous function breakdown_dataframe to generate word cloud
    positive = dataframe[dataframe['sentimentt'] == 1]
    negative = dataframe[dataframe['sentimentt'] == -1]
    # generate positive wordcloud
    pos = " ".join(review for review in positive.review_text)
    wordcloud2 = WordCloud(stopwords=stopwords).generate(pos)
    plt.imshow(wordcloud2, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/wordcloudPos.png')
    plt.close('all')
    #plt.show()

    # In[6]:

    # generate negative wordcloud
    neg = " ".join(review for review in negative.review_text)
    wordcloud3 = WordCloud(stopwords=stopwords).generate(neg)
    plt.imshow(wordcloud3, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/wordcloudNeg.png')
    plt.close('all')
    #plt.show()


def func(pct, allvalues): #Pie chart formatting
    absolute = int(pct / 100.*np.sum(allvalues))
    return "{:.1f}%\n({:d})".format(pct, absolute)

def rating(csvfile):#Data display
    rowcount=len(csvfile.index)
    pos_count=len(csvfile[csvfile['sentiment_score']=='Positive'])
    neg_count=len(csvfile[csvfile['sentiment_score']=='Negative'])
    neutral_count=len(csvfile[csvfile['sentiment_score']=='Neutral'])
    pietest=np.array([pos_count,neg_count,neutral_count])
    mylabels = ["Positive", "Negative", "Neutral"]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(pietest,labels = mylabels, startangle = 90,autopct=lambda pct: func(pct, pietest),)
    ax.set_title("Overall review ratings")
    ax.legend(mylabels,title ="Sentiment",
          loc ="center left",
          bbox_to_anchor =(1, 1))
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/'+csvfile['hotelname'][0]+'rating.png')
    plt.close('all')
    #plt.show()

def rating_further(csvfile):#DAta display with the neutral positive and neutral negative scores and neutral neutral
    pos_count = len(csvfile[csvfile['sentiment_score'] == 'Positive'])
    neg_count = len(csvfile[csvfile['sentiment_score'] == 'Negative'])
    neutral_count = len(csvfile[csvfile['sentiment_score'] == 'Neutral'])
    neutral_pos=len(csvfile[csvfile['Combined Sentiment']=='NeutralPositive'])
    neutral_neg=len(csvfile[csvfile['Combined Sentiment']=='NeutralNegative'])
    neutral_neutral = len(csvfile[csvfile['Combined Sentiment'] == 'NeutralNeutral'])
    total_pos=pos_count+neutral_pos
    total_neg=neg_count+neutral_neg
    total_neutral=neutral_neutral
    pietest = np.array([total_pos, total_neg, total_neutral])
    mylabels = ["Positive", "Negative", "Neutral"]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(pietest, labels=mylabels, startangle=90, autopct=lambda pct: func(pct, pietest), )
    ax.set_title("Overall review ratings with neutral breakdown")
    ax.legend(mylabels, title="Sentiment",
              loc="center left",
              bbox_to_anchor=(1, 1))
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/'+csvfile['hotelname'][0]+'rating_further.png')
    plt.close('all')
    #plt.show()

def scrapereviewoneh(x):

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
    page_source = driver.page_source
    with open('pagetestzz.html', 'w+', encoding="utf-8") as f:
        f.write(driver.page_source)  # Saves and writes the page source or html code locally

    writeheader = True
    for x in range(2):

        newurl = driver.current_url
        print(newurl)
        driver.get(newurl)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')  # Parses the data/html code

        hotelname = [t.get_text(strip=True) for t in
                     soup.find_all('a', attrs={'class': 'standalone_header_hotel_link'})]
        hoteladdress = [t.get_text(strip=True) for t in soup.find_all('p', attrs={'class': 'hotel_address'})]
        review_score = [t.get_text(strip=True) for t in soup.find_all('span', attrs={'class': 'review-score-badge'})]
        review_score = review_score[1::]
        # test_texxt=soup.find_all("span", itemprop="reviewBody") #Retrieves all text within the reviewBody so mixes both positive and negative

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
        location = geolocator.geocode('Singapore ' + postalcodefinal)
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
            addin = postalcodefinal, getLoc['lat'], getLoc['lon'], i[0], i[1], i[2]
            combined2.append(addin)

        'print output to csv'

        with open(csv_path+hotelname[0] + "_mini.csv", "a", encoding="utf-8", newline='') as csvFile:
            fieldnames = ['hotelname', 'postalcode', 'latitude', 'longitude', 'review_pos', 'review_neg','review_text', 'review-score']
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            if writeheader == True:
                writer.writeheader()
                writeheader = False
            for item in combined2:
                writer.writerow({'hotelname': hotelname[0], 'postalcode': item[0], 'latitude': item[1], 'longitude': item[2],
                                 'review_pos': item[3], 'review_neg': item[4], 'review_text':item[3]+item[4], 'review-score': item[5]})
        csvFile.close()
        driver.find_element("xpath", "//*[contains(@id, 'review_next_page_link')]").click()
    driver.quit()
    return hotelname[0]



# if __name__ == '__main__':
#     # Sample on how to use the whole program
#     print("Test")
#     test = pd.read_csv(r"C:\Users\USER\Documents\Pycharm_download\Hotel\SingaporeHotel (3).csv",
#                        encoding='latin1')  # Use your own local file location


#     #graph = generate_graph(test)
#     testscrape = scrapereviewoneh(input_url)

#     test2 = pd.read_csv(r"C:\Users\USER\Documents\Pycharm_download\Hotel\\"+testscrape+"_mini.csv",encoding='latin1')  # Use your own local file location
# # 

#     print("pass")
#     # #graphz = generate_stopword(test)
#     # dataframez = generate_dataframe_column(test)
#     # # # new_dataframez = breakdown_dataframe(dataframez)
#     # # # rating(new_dataframez)
#     # # # rating_further(new_dataframez)
#     # # # top_ten = top_ten_pos(new_dataframez)
#     # # # word_cloud_gen = wordcloud_gen(new_dataframez)
    
#     # print("running test2")
#     dataframez2 = generate_dataframe_column(test2)
    
#     new_dataframez2 = breakdown_dataframe(dataframez2)
#     rating(new_dataframez2)
#     rating_further(new_dataframez2)
#     top_ten2 = top_ten_pos(new_dataframez2)
#     word_cloud_gen2 = wordcloud_gen(new_dataframez2)
    
#     # print(top_ten[0][0])
#     # print(top_ten[0][1])
#     # print(top_ten[0][2])
    

    
#     #print(new_dataframez.head())
    
    
    
#     #export_csv(new_dataframez)
#     #print(new_dataframez.head(10))
#     #filterhotel(dataframez,189673)
    
#     #able to get png for rating, rating_further, wordcloudpos, wordcloudneg
    
#   os.remove(testscrape+"_mini.csv")

