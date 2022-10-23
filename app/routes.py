from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, RegistrationForm, SpyForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Hotel
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.functions import scrapeone, s_multilinks, heatmap, sghotelvicinitymap, overall_reviews
from urllib.parse import urlparse
import pandas as pd
from app.sentiment import generate_graph
from app.top15words import top15words
from app.MonthDate import scrapemonth
import os
import io
import random
from flask import Response
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import csv
from app.graphmonthyear2 import showgraphmonthyear

csv_path = 'S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'


@app.route('/')
@app.route('/index')
@login_required
def index():
    form = SpyForm()
    yo = Hotel.query.all()
    hotel_choices = []
    for x in yo:
        hotel_choices.append(x.hotel_name)
    # flash(hotel_choices)

    return render_template('index.html', title='Home', form=form, hotel_choices=hotel_choices)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    all_hotels = Hotel.query.all()
    hotel_choices = []
    for x in all_hotels:
        hotel_choices.append(x.hotel_name)
    form = RegistrationForm()

    if form.validate_on_submit():
        searched_hotel = Hotel.query.filter_by(hotel_name=form.hotel_name.data).first()

        if searched_hotel is None:
            flash("Please select from the given hotels")
            return redirect(url_for('register'))

        elif searched_hotel:  # Valid
            user = User(username=form.username.data, email=form.email.data, hotel_name=form.hotel_name.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            scrapeone(searched_hotel.hotel_link)

            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form, hotel_choices=hotel_choices)


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    company_csv = user.hotel_name + '.csv'

    return render_template('profile.html', user=user, vic_comp_name=company_csv)


@app.route("/spy", methods=['GET', 'POST'])
@login_required
def spy():
    form = SpyForm()
    if form.validate_on_submit():

        if form.hotel_name.data == "" and form.hotel_url.data == "":
            flash('Please enter a hotel name or a review link from booking.com')
            return redirect(url_for('index'))

        elif form.hotel_name.data and form.hotel_url.data:
            flash('Please enter either hotel name or hotel link, not both')
            return redirect(url_for('index'))

        elif form.hotel_name.data and form.hotel_url.data == "":
            searched_hotel = Hotel.query.filter_by(hotel_name=form.hotel_name.data).first()

            if searched_hotel is None:
                flash("Please select from the given hotels or provide the hotel link")
                return redirect(url_for('index'))

            elif searched_hotel:                                                    #Valid
                ######Cat Compare#########
                spied_hotelcsvname = scrapeone(searched_hotel.hotel_link)
                my_hotel = overall_reviews(csv_path + current_user.hotel_name+'.csv')
                spied_hotel = overall_reviews(csv_path + spied_hotelcsvname+'.csv')
                print("step 1")

                ######Bar Graphs of Sentiment Analysis Technical Machine Learning########
                spied_df = read_csv(csv_path+spied_hotelcsvname+'.csv')
                print("step 1s")
                generate_graph(spied_df)
                print("step 1sa")
                my_hotel_df = read_csv(csv_path + current_user.hotel_name + '.csv')
                print("step 1q")
                generate_graph(my_hotel_df)
                print("step 1q3")

                ######Pie Charts of Sentiment Analysis Technical Machine Learning########
                spied_gen_df = generate_dataframe_column(spied_df)
                spied_break_df = breakdown_dataframe(spied_gen_df)
                rating(spied_break_df)
                rating_further(spied_break_df)
                mine_gen_df = generate_dataframe_column(my_hotel_df)
                mine_break_df = breakdown_dataframe(mine_gen_df)
                rating(mine_break_df)
                rating_further(mine_break_df)
                #####################################
                top15words(spied_hotelcsvname)
                top15words(current_user.hotel_name)



                return render_template('compare.html', vic_comp_name=spied_hotelcsvname, user=current_user,
                               spied_hotel=spied_hotel, my_hotel=my_hotel)

        elif form.hotel_url.data and form.hotel_name.data == "":
            input_url = form.hotel_url.data
            p_url = urlparse(input_url)
            path = '/reviews/sg/hotel/'

            if (p_url.netloc == "www.booking.com") and (path in p_url.path):        #Valid
                spied_hotelcsvname = scrapeone(form.hotel_url.data)
                my_hotel = overall_reviews(csv_path + current_user.hotel_name+'.csv')
                spied_hotel = overall_reviews(csv_path + spied_hotelcsvname)




                return render_template('compare.html', vic_comp_name=spied_hotelcsvname, user=current_user,
                           spied_hotel=spied_hotel, my_hotel=my_hotel)

            else:
                flash('Please use a Booking.com review URL')
                return redirect(url_for('index'))
        else:
            flash("Please enter correct values")
    else:
        return redirect(url_for('index'))


@app.route('/vicinity/<vic_comp_name>', methods=['GET', 'POST'])
@login_required
def vicinity(vic_comp_name):
    df01 = pd.read_csv('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/master_sg.csv', encoding="ISO-8859-1")
    df02 = pd.read_csv('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/'+vic_comp_name, encoding="ISO-8859-1")
    hotelvicinityname = sghotelvicinitymap(df01, df02)

    return render_template('/generated/' + hotelvicinityname)

@app.route('/heatmap')
@login_required
def heatmaplink():
    df01 = pd.read_csv('S:/SIT Tri 1/Programming/Python Project Hotel/Hotel/app/csvfiles/master_sg.csv', encoding="ISO-8859-1")
    sgheatmap = heatmap(df01)

    return render_template('/generated/' + sgheatmap)


@app.route('/getallhotels', methods=['GET', 'POST'])
@login_required
def getallhotels():
    A = s_multilinks('https://www.booking.com/reviews/sg/city/singapore.en-gb.html?aid=356980&sid=248efadb06977d69b94338011302293d&label=gog235jc-1FEgdyZXZpZXdzKIICOOgHSDNYA2jJAYgBAZgBCbgBF8gBDNgBAegBAfgBDYgCAagCA7gCgrj9mAbAAgHSAiQ1NjY2NDdjNy03NjEzLTRiNjEtYjQ1OC04MDk1Y2M2MzhlYjLYAgbgAgE')

    return redirect(url_for('index'))
##############################################################################
from app.sentiment import read_csv, generate_dataframe_column,breakdown_dataframe,rating,rating_further,top_ten_pos,top_ten_neg
@app.route("/tablereviews")
@login_required
def tablereviews():
    test = pd.read_csv(r"S:\SIT Tri 1\Programming\Python Project Hotel\Hotel\app\csvfiles\master_sg.csv",encoding='latin1')  # Use your own local file location
    #graph = generate_graph(test)
    print("pass")
    #graphz = generate_stopword(test)
    dataframez = generate_dataframe_column(test)
    new_dataframez = breakdown_dataframe(dataframez)
    rating(new_dataframez)
    rating_further(new_dataframez)
    top_tenpos = top_ten_pos(new_dataframez)
    top_tenneg = top_ten_neg(new_dataframez)
    return render_template('tablereviews.html', toptenpos=top_tenpos,toptenneg=top_tenneg[::-1])
    # should make the input_url be into this file, so that don't need to use that long hardcode input

import os
from app.sentiment import scrapereviewoneh,read_csv, generate_dataframe_column,breakdown_dataframe,rating,rating_further,top_ten_pos,top_ten_neg
@app.route("/tablereviewsRecent/<csv_name>")
@login_required
def tablereviewsRecent(csv_name):
    searched_hotel = Hotel.query.filter_by(hotel_name=csv_name).first()
    input_url = searched_hotel.hotel_link
    testscrape = scrapereviewoneh(input_url)
    test = pd.read_csv(r"S:\SIT Tri 1\Programming\Python Project Hotel\Hotel\app\csvfiles\\"+csv_name+"_mini.csv",encoding='latin1')  # Use your own local file location
    #graph = generate_graph(test)
    print("pass")
    #graphz = generate_stopword(test)
    dataframez = generate_dataframe_column(test)
    new_dataframez = breakdown_dataframe(dataframez)
    rating(new_dataframez)
    rating_further(new_dataframez)
    top_tenpos = top_ten_pos(new_dataframez)
    top_tenneg = top_ten_neg(new_dataframez)
    os.remove(csv_path+testscrape+"_mini.csv")
    return render_template('tablereviewsRecent.html', toptenpos=top_tenpos,toptenneg=top_tenneg[::-1])
    # should make the input_url be into this file, so that don't need to use that long hardcode input


@app.route("/reviews")
@login_required
def reviews():
    #scrape_cat_filename = scrape_cat('https://www.booking.com/reviews/sg/hotel/the-barracks-by-far-east-hospitality.en-gb.html?')
    file = open(csv_path+"overview.csv", "r")
    data = list(csv.reader(file, delimiter=","))
    file.close()
    return render_template('reviews.html', keywords = data[0], numberrating = data[1])

@app.route("/graph",methods=["POST","GET"])
@login_required
def graph():
    searched_hotel = Hotel.query.filter_by(hotel_name=current_user.hotel_name).first()
    input_url = searched_hotel.hotel_link
    scrapemonth(input_url)
    return render_template('graph.html')

@app.route("/graphresult/<value>",methods=["POST","GET"])
@login_required
def graphresult(value):
    # flash(value)
    graphyear = showgraphmonthyear(value)
    # return render_template('graphresult.html')
    newyeargraph=''
    value = int(value)
    def graphyear(value):
        print(value)
        if value == 0:
            showgraphmonthyear(value)
            newyeargraph='../static/css/new_year.png'
            return newyeargraph
        elif value==1:
            showgraphmonthyear(value)
            newyeargraph="../static/css/new_year.png"
            return newyeargraph
        elif value==2:
            showgraphmonthyear(value)
            newyeargraph='../static/css/new_year.png'
            return newyeargraph
        elif value==3:
            showgraphmonthyear(value)
            newyeargraph='../static/css/new_year.png'
            return newyeargraph
        elif value==4:
            showgraphmonthyear(value)
            newyeargraph='../static/css/new_year.png'
            return newyeargraph
    graphyear(value)
    # flash(newyeargraph)
    return render_template('graph.html')


if __name__ == "__main__":
    app.run(debug=True)
