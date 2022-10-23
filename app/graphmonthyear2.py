
import csv
import matplotlib
matplotlib.use('Agg') #this allows the matplotlib to work in python flask
import matplotlib.pyplot as plt
import numpy as np

# from matplotlib import pyplot as plt
import pandas as pd
csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'

reviewCountDict ={'2019':{'January': 0,'February':0,'March':0,'April':0,'May':0,'June':0,'July':0,'August':0,'September':0,'October':0,'November':0,'December':0},'2020':{'January': 0,'February':0,'March':0,'April':0,'May':0,'June':0,'July':0,'August':0,'September':0,'October':0,'November':0,'December':0},'2021':{'January': 0,'February':0,'March':0,'April':0,'May':0,'June':0,'July':0,'August':0,'September':0,'October':0,'November':0,'December':0},'2022':{'January': 0,'February':0,'March':0,'April':0,'May':0,'June':0,'July':0,'August':0,'September':0,'October':0,'November':0,'December':0}}

with open(csv_path+'MonthDate.csv') as file:
    reader = csv.reader(file)

    count = 0

    for row in reader:  #list of 2 already how nice
        if row[1] == 'year':
            continue
        Year = row[1]
        Month = row[0]
        reviewCountDict[Year][Month] += 1


#print(reviewCountDict)
result = reviewCountDict['2022'].get('January')
#print (result)
# print (type(result))
# result = reviewCountDict['2022'].get('February')
result2019 = reviewCountDict['2019']
result2020 = reviewCountDict['2020']
result2021 = reviewCountDict['2021']
result2022 = reviewCountDict['2022']
#print(result2022)






def showgraphmonthyear(x):
    if x==0:
        allgraphyear()
    elif x ==1:
        run2019() #run 2019 data set, which will be in a function
    elif x==2:
        run2020()
    elif x==3:
        run2021()
    elif x==4:
        run2022()


def run2019():    
    data19 = result2019
    names = list(data19.keys())
    values = list(data19.values())
    #plt.bar(range(len(data19)), values, tick_label=names,color='b')
    plt.title('2019')
    plt.xlabel("months")
    plt.ylabel("number of rooms booked")
    plt.bar(names,values, color='b')
    def addlabels(x,y):
        for i in range(len(x)):
            plt.text(i, y[i], y[i], ha = 'center')
    addlabels(names,values)
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/new_year.png')
    plt.close('all')

    # plt.show()



def run2020():
    data20 = result2020
    names = list(data20.keys())
    values = list(data20.values())
    # plt.bar(range(len(data20)), values, tick_label=names,color='r')
    plt.title('2020')
    plt.xlabel("months")
    plt.ylabel("number of rooms booked")
    plt.bar(names,values, color='r')
    def addlabels(x,y):
        for i in range(len(x)):
            plt.text(i, y[i], y[i], ha = 'center')
    addlabels(names,values)
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/new_year.png')
    plt.close('all')
    # plt.show()

  

def run2021():
    data21 = result2021
    names = list(data21.keys())
    values = list(data21.values())
    #plt.bar(range(len(data21)), values, tick_label=names,color='y')
    plt.title('2021')
    plt.xlabel("months")
    plt.ylabel("number of rooms booked")
    plt.bar(names,values,color='y')
    def addlabels(x,y):
        for i in range(len(x)):
            plt.text(i, y[i], y[i], ha = 'center')
    addlabels(names,values)
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/new_year.png')
    plt.close('all')

    # plt.show()
    

def run2022():
    data22 = result2022
    names = list(data22.keys())
    values = list(data22.values())
    # plt.bar(range(len(data22)), values, tick_label=names,color='c')
    plt.title('2022')
    plt.xlabel("months")
    plt.ylabel("number of rooms booked")
    plt.bar(names,values,color='c')
    def addlabels(x,y):
        for i in range(len(x)):
            plt.text(i, y[i], y[i], ha = 'center')
    addlabels(names,values)
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/new_year.png')
    plt.close('all')

    # plt.show()
    
    #graph from year 2022, there's no return?
    
# print(showgraphmonthyear(1))
# print(showgraphmonthyear(2))
# print(showgraphmonthyear(3))
# print(run2022())





#sample data
def allgraphyear():
    result2019 = reviewCountDict['2019']
    result2020 = reviewCountDict['2020']
    result2021 = reviewCountDict['2021']
    result2022 = reviewCountDict['2022']

    X = np.arange(len(result2019))
    ax = plt.subplot(111)
    ax.bar(X-0.3, result2019.values(), width=0.2, color='b', align='center')
    ax.bar(X-0.1, result2020.values(), width=0.2, color='r', align='center')
    ax.bar(X+0.1, result2021.values(), width=0.2, color='y', align='center')
    ax.bar(X+0.3, result2022.values(), width=0.2, color='c', align='center')
    ax.legend(('2019','2020','2021','2022'))
    plt.xticks(X, result2019.keys())
    plt.title("Monthly Booking Reviews", fontsize=17)
    plt.savefig('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/static/css/new_year.png')
    plt.close('all')

    # plt.show()
    

    #this is all the graphs from year 2019 to 2022

#print(showgraphmonthyear(0))

#show average for all years 
#if possible, be able to click, then choose which graphs to look at, e.g. tick 2019 and 2021, then it will automatically show only 2019 and 2021
#another problem is showing months, without it being cramped together(?)
#how to resize the matplotlib?