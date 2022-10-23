
import pandas as pd
import numpy as np

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')
import matplotlib.pyplot as plt
import seaborn as sns
color = sns.color_palette()
import string
from gensim.parsing.preprocessing import STOPWORDS
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'

input_url = 'https://www.booking.com/reviews/sg/hotel/citadines-rochor.en-gb.html?aid=356980&sid=4581fecdf88e3c532e910a9a05e6eb81&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE'

# initializing empty list where we are going to have words counted
stopwords_nltk = set(stopwords.words('english'))
stopwords_nltk.update(["br","href","hotel","room","rooms","stay","stayed","would","could","really","get","also","us","one","time","great",
                      "good","bad","nice","like","best","review","reviews","negative","positive","little","well","check","super",
                      "quite","india","singapore","malaysia","china","japan","korea","philippines","door","day","night","everything",
                      "nothing","entrance","need","first","last","close","even","in","pillow","pillows","still","wet","value","late",
                      "guest","guests","always","morning","sleep","places","feel","feels","people","floor","front","worth","gone",
                      "walking","lovely","love","made","make","plus","overall","air","free","pressure","it","access","go","wonderful",
                      "probably","2","near","staying","within","better","request","around","size","long","way","activity","too","got"
                      "activities","two","loved","especially","much","property","back","desk","in","1","bit","ice","tap","told","side",
                      "water","take","cream","new","excellent","different","though","lobby","took","well","walk","available","next","3",
                      "wait","lack","perfect","book","booked","booking","early","fun","ask","asked","enough","amazing","rail","rails",
                      "easy","hard","difficult","extremely","extreme","4","smell","5","6","7","8","9","10","money","every","food","space",
                      "distance","many","hear","said","pay","days","ok","okay","price","luggage","pretty","fast","all","due","noise","dirty",
                      "filthy","greasy","sooty","moldy","grimy","grubby","soiled","unwashed","stain","stained","spotted","cloudy","muddy",
                      "dusty","paper","street","another","open","corridor","outside","nice","poor","use","rude","lavender","want","theres",
                      "see","friendly","helpful","disgusting","terrible","areas","liked","needed","turn","keep","short","tall","come","came",
                      "went","change","changes","found","home","working","call","arrived","arrive","station","stations","find","hot","freeze"
                      "centrally","located","things","work","instead","again","allow","allowed","requested","right","left","freezing","cold"
                      "standard","enjoy","machine","proper","definitely","find","needs","extra","building","small","noisy","nil","standard"
                      "awesome","spent","recommend","recommended","recommendation","hours","awkward","hose","fix","fixed","work","worked","give",
                      "broke","broken","wall","point","pointed","evening","tea","cake","fantastic","everyone","thank","sure","care","impeccable",
                      "experience","absolute","absolutely","special","crowds","limited","amount","guests","step","complaints","laid","charm",
                      "added","canapã©s","didnâ\x80\x99t","beautiful","surprise","team","got","direct","experience","attentive","exceptional",
                      "couple","couples","birthday","prepare","prepared","quiet","beyond","outstanding","1904","felt","making","met","spritz",
                      "gavin","afternoon","hi","relaxing","peaceful","peace","personal","personalised","wish","wishes","thing","drinks",
                      "might","pay","paid","payable","feeling","part","offer","choice","choices","course","yet","kept","checking","check",
                      "checks","wonderful","canâ\x80\x99t","polite","you","me","aaron","anniversary","receive","received","receives","bottle",
                      "member","personalize","personalized","names","name","named","flow","emily","welcomed","welcome","mr","mrs","ms","mister",
                      "misses","missus","miss"])

stopwords_gensim = STOPWORDS
sw_list = {"not"}
stopwords_gensim = STOPWORDS.difference(sw_list)


def top15words(input_url):
    # df = pd.read_csv(csv_path+scrapeone(input_url), encoding = "ISO-8859-1")
    df = pd.read_csv(csv_path+input_url+'.csv', encoding = "ISO-8859-1")

    #synonym check
    _review_ = []
    # getting review strings and appending it to the _review_ list
    for review in df.review_text:
        _review_.append(review)

    # setting a function that will split those reviews strings into separate words
    def split_name(review):
        spl = str(review).split()
        return spl


    _review_count_ = []

    # getting name string from our list and using split function, later appending to list above
    # Punctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    punctuation = [",",";",":","?",".","\'","\\","-","(",")","+","#","@","<",">","_","{","}","[","]","/","*","%"]
    ambiguous= ["","us","in","too","again","well","india","singapore","stay","good","great","awesome","stations","station","time","no","yes",
                "amazing","it","nothing","experience","everything","food","pay","paid","surprise","beyond","choice","choices","exceptional",
                "wonderful","team","personal","you","me","relaxing","night","day","nice","lovely"]
    for x in _review_:
        for word in split_name(x):
            if word in punctuation:
                continue
            else:
                word = word.strip() #removes whitespace
                word = word.lower()
                if word not in stopwords_nltk:
                    if word not in stopwords_gensim:
                        if word not in ENGLISH_STOP_WORDS:
                            word = word.translate(str.maketrans('', '', string.punctuation))
                            if word not in ambiguous:
                                _review_count_.append(word)

    # we are going to use counter
    from collections import Counter

    comfortable_synonyms = ["comfy","cosy","warm","pleasant","enjoyable","agreeable","congenial","plush","secure","safe","homely","snuggly","enjoyed","cozy","coziness"]
    service_synonyms = ["staff","staffs","servicing","assistance","help","provided","checkin","checkout","friendly","provided","provide","serve","served","helpful"]
    dorm_synonyms = ["dorms"]
    apartment_synonyms = ["apartments"]
    toilet_synonyms = ["toilets","bathroom","bathrooms","lavatory","lavatories","urinal","sink"]
    pool_synonyms = ["pools","swim","swimming"]
    kid_synonyms = ["kid","kids","children","child","youngster","baby","toddler","infant","minor","adolescent","teenager","youth","son","daughter"]
    restaurant_synonyms = ["restaurants","eatery"]
    aircon_synonyms = ["ac","aircon","air-con","aircondition","air-condition","airconditioner","air-conditioner"]
    location_synonyms = ["spot","place","area","central","centrally","nearby","india"]
    cleanliness_synonyms = ["clean","neat","sanitize","sanitise","spotless","sanittion","disinfect"]
    spacious_synonyms = ["wide","big","roomy","vast","large","palatial","huge"]
    facilities_synonyms = ["amenity","facility","amenities","convenience","convenient"]
    housekeeping_synonyms = ["cleaning","equipped","cleaned","towel","towels","toiletries"]
    family_synonyms = ["family","families","household"]
    bar_synonyms = ["alcohol","liquor","cocktail","booze","cocktails","champagne","wine","winery"]
    #_synonyms = []
    for i in range(len(_review_count_)):
        if _review_count_[i] in comfortable_synonyms:
            _review_count_[i] = "comfortable"
        elif _review_count_[i] in service_synonyms:
            _review_count_[i] = "service"
        elif _review_count_[i] in dorm_synonyms:
            _review_count_[i] = "dorm"
        elif _review_count_[i] in apartment_synonyms:
            _review_count_[i] = "apartment"
        elif _review_count_[i] in toilet_synonyms:
            _review_count_[i] = "toilet"
        elif _review_count_[i] in pool_synonyms:
            _review_count_[i] = "pool"
        elif _review_count_[i] in kid_synonyms:
            _review_count_[i] = "kid-friendly"
        elif _review_count_[i] in restaurant_synonyms:
            _review_count_[i] = "restaurant"
        elif _review_count_[i] in aircon_synonyms:
            _review_count_[i] = "air-conditioned"
        elif _review_count_[i] in location_synonyms:
            _review_count_[i] = "location"
        elif _review_count_[i] in cleanliness_synonyms:
            _review_count_[i] = "cleanliness"
        elif _review_count_[i] in spacious_synonyms:
            _review_count_[i] = "spacious"
        elif _review_count_[i] in facilities_synonyms:
            _review_count_[i] = "facilities"
        elif _review_count_[i] in housekeeping_synonyms:
            _review_count_[i] = "housekeeping"
        elif _review_count_[i] in family_synonyms:
            _review_count_[i] = "family-friendly"
        elif _review_count_[i] in bar_synonyms:
            _review_count_[i] = "bar"
        else:
            continue

    _top_15_w = Counter(_review_count_).most_common()
    # Sort number of words viewed
    _top_15_w = _top_15_w[0:15]

    sub_w=pd.DataFrame(_top_15_w)
    sub_w.rename(columns={0:'Words', 1:'Count'}, inplace=True)

    # Defining the plot size
    plt.figure(figsize=(10,6))
    # Defining the values for x-axis & y-axis and from which dataframe the values are to be picked
    viz_5=sns.barplot(x='Count', y='Words', data=sub_w)
    viz_5.set_title('Counts of the top 15 used words for reviews')
    viz_5.set_ylabel('Words')
    viz_5.set_xlabel('Count of words')
    for i in viz_5.patches:
        viz_5.text(i.get_width()+0.2, i.get_y()+0.5,
                 str(round((i.get_width()))),
                 fontsize = 10, color ='black')
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/'+input_url+'top15words.png')
    plt.show()

