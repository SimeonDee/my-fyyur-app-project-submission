###########################################################################
# Contributor: Adedoyin Simeon Adeyemi
# LinkedIn:    https://www.linkedin.com/in/adedoyin-adeyemi-a7827b160/
# GitHub:      https://github.com/SimeonDee
# Project:     https://github.com/SimeonDee/fyyur-music-artist-connect-app
# Date:        20th August, 2022
###########################################################################

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.policy import default
import json
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response
from flask import flash, redirect, url_for
from flask_moment import Moment
from sqlalchemy import func, exc
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


import sys
from datetime import date, datetime
from database import db
from models import Venue, Artist, VenueGenre, ArtistGenre, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

######################### NOTE #########################
# Following Separation of Concern Pattern Requirement,
# See 'database.py' and 'models.py' for all the
# defined models
########################################################


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    if type(value) != str:
        value = datetime.strftime(value, format="%m/%d/%Y, %H:%M:%S")

    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


####################################################################
# My Utility Function(s)
####################################################################

def get_formatted_shows(shows, shows_for='venue'):
    fmtd_shows = []
    for show in shows:
        data = dict()
        if shows_for == 'venue':  # if 'venue', get artist details
            show_artist = show.artist
            data["artist_id"] = show_artist.id
            data["artist_name"] = show_artist.name
            data["artist_image_link"] = show_artist.image_link
            data["start_time"] = show.start_time

        else:   # if shows_for == 'artist', then get venue details
            show_venue = show.venue
            data["venue_id"] = show_venue.id
            data["venue_name"] = show_venue.name
            data["venue_image_link"] = show_venue.image_link
            data["start_time"] = show.start_time

        fmtd_shows.append(data)

    return fmtd_shows


#######################################
# --------- Controllers ------
#######################################


@app.route('/')
def index():
    recent_listed_artists = Artist.query.limit(10).all()
    recent_listed_venues = Venue.query.limit(10).all()
    return render_template('pages/home.html', venues=recent_listed_venues, artists=recent_listed_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    error = False
    data = []
    try:
        # Distinct cities fetch
        distinct_cities = db.session.query(Venue).distinct(Venue.city).all()

        # All upcoming shows
        upc_shows = Show.query.filter(Show.start_time >= datetime.now()).all()

        for venue in distinct_cities:
            city = venue.city
            state = venue.state

            upc_city_venues = [
                {
                    "id": show.venue.id,
                    "name": show.venue.name,
                    "num_upcoming_shows": len(
                        [s for s in upc_shows if s.show_venue.city == city and s.show_venue.name == show.venue.name])
                } for show in upc_shows if show.show_venue.city == city]

            # copy created to avoid in-place modification
            # when removing duplicates
            copy_upc_city_venues = upc_city_venues.copy()

            # Remove duplicates
            names = []
            for t in copy_upc_city_venues:
                if t['name'] in names:
                    upc_city_venues.remove(t)
                else:
                    names.append(t['name'])
            names = None  # clear memory

            data.append({
                'city': city,
                'state': state,
                'venues': upc_city_venues
            })

        # Mock data provided by default
        # data = [{
        #     "city": "San Francisco",
        #     "state": "CA",
        #     "venues": [{
        #         "id": 1,
        #         "name": "The Musical Hop",
        #         "num_upcoming_shows": 0,
        #     }, {
        #         "id": 3,
        #         "name": "Park Square Live Music & Coffee",
        #         "num_upcoming_shows": 1,
        #     }]
        # }, {
        #     "city": "New York",
        #     "state": "NY",
        #     "venues": [{
        #         "id": 2,
        #         "name": "The Dueling Pianos Bar",
        #         "num_upcoming_shows": 0,
        #     }]
        # }]

        flash('Fetch successful')

    except exc.SQLAlchemyError as err:
        error = True
        print(err)

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                db.session.rollback()
                print(sys.exc_info())
                flash('Fetch failed', 'error')
                # return redirect(url_for('index'))

            db.session.close()

        return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term', '')
    q_found_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    found_venues = q_found_venues.all()

    response = {
        "count": q_found_venues.count(),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter(Show.start_time >= datetime.now(), Show.venue_id == venue.id).count()
        } for venue in found_venues]
    }

    # # Mock data provided by default
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    # return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    curr_venue = Venue.query.get(venue_id)
    curr_venue = curr_venue.to_dico()

    # Moderating 'genres' for display
    curr_venue['genres'] = [genre.name for genre in curr_venue['genres']]

    q_upcoming_shows = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time >= datetime.now())

    q_past_shows = Show.query.filter(
        Show.venue_id == venue_id, Show.start_time < datetime.now())

    past_shows = get_formatted_shows(q_past_shows.all(), shows_for='venue')
    upcoming_shows = get_formatted_shows(
        q_upcoming_shows.all(), shows_for='venue')

    curr_venue["past_shows"] = past_shows
    curr_venue["upcoming_shows"] = upcoming_shows
    curr_venue["past_shows_count"] = q_past_shows.count()
    curr_venue["upcoming_shows_count"] = q_upcoming_shows.count()

    # # Mock data provided by default
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }

    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]
    # return render_template('pages/show_venue.html', venue=data)

    return render_template('pages/show_venue.html', venue=curr_venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    venue_name = ''
    try:
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        address = request.form.get('address', '')
        phone = request.form.get('phone', '')
        image_link = request.form.get('image_link', '')
        facebook_link = request.form.get('facebook_link', '')
        website = request.form.get('website_link', '')
        seeking_talent = request.form.get('seeking_talent', '')
        seeking_description = request.form.get('seeking_description', '')

        genres = request.form.getlist('genres')

        # Because seeking_talent returns 'y' instead of True/False
        if type(seeking_talent) is not bool:
            seeking_talent = True if seeking_talent.startswith('y') else False
        venue_name = name

        # print('#' * 30)
        # for key in request.form.keys():
        #     print(key, request.form[key])

        # Creating a new instance of Venue
        new_venue = Venue(
            name=name, city=city, state=state, address=address,
            phone=phone, image_link=image_link, facebook_link=facebook_link,
            website=website, seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )

        # Adding each selected genre to Venue
        for genre in genres:
            new_genre = VenueGenre(name=genre)
            new_venue.genres.append(new_genre)

        # on successful db insert, flash success
        # flash('Venue ' + request.form['name'] + ' was successfully listed!')
        db.session.add(new_venue)
        db.session.commit()
        flash(
            f'Venue "{new_venue.name}:{new_venue.id}" was successfully listed!')

    except exc.SQLAlchemyError as err:
        print(err)
        error = True

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                # TODO: on unsuccessful db insert, flash an error instead.
                # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
                # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
                db.session.rollback()
                print(sys.exc_info())
                flash(
                    f'An error occurred. Venue "{venue_name}" could not be listed.')

            db.session.close()

        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        # db.session.query(Venue).filter_by(id == venue_id).delete()
        venue = Venue.query.get_or_404(venue_id)

        for genre in venue.genres:
            db.session.delete(genre)

        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue "{venue.name}" deleted succefully')

    except exc.SQLAlchemyError as err:
        error = True
        print(err)

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                db.session.rollback()
            db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    # =====================================================================
    # BONUS CHALLENGE IMPLEMENTED in the 'pages/show_venue.html' template
    # =====================================================================
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = db.session.query(Artist.id, Artist.name).all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]

    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    q_found_artists = db.session.query(Artist).filter(
        Artist.name.ilike(f'%{search_term}%'))

    found_artists = q_found_artists.all()

    response = {
        "count": q_found_artists.count(),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": Show.query.filter(
                Show.start_time >= datetime.now(), Show.artist_id == artist.id).count()
        } for artist in found_artists]
    }

    # mock data Provided by default
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    # return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    curr_artist = Artist.query.get(artist_id)
    curr_artist = curr_artist.to_dico()

    #################
    curr_artist['genres'] = [genre.name for genre in curr_artist['genres']]

    q_upcoming_shows = Show.query.filter(
        Show.artist_id == artist_id, Show.start_time >= datetime.now())

    q_past_shows = Show.query.filter(
        Show.artist_id == artist_id, Show.start_time < datetime.now())

    past_shows = get_formatted_shows(q_past_shows.all(), shows_for='artist')
    upcoming_shows = get_formatted_shows(
        q_upcoming_shows.all(), shows_for='artist')

    curr_artist["past_shows"] = past_shows
    curr_artist["upcoming_shows"] = upcoming_shows
    curr_artist["past_shows_count"] = q_past_shows.count()
    curr_artist["upcoming_shows_count"] = q_upcoming_shows.count()

    # # Testing
    # print('*' * 10, f'Artist <{artist_id}> --- ', '*' * 10)
    # for key in curr_artist.keys():
    #     if key == 'past_shows':
    #         print(f'{key}:')
    #         for p_show in curr_artist[key]:
    #             print('\t', p_show)

    #     elif key == 'upcoming_shows':
    #         print(f'{key}:')
    #         for u_show in curr_artist[key]:
    #             print('\t', u_show)

    #     elif key == 'genres':
    #         print(f'{key}:')
    #         for genre in curr_artist[key]:
    #             print('\t', genre)
    #     else:
    #         print(f'{key}: {curr_artist[key]}')

    # print('*' * 32)

    # # data1 = {
    # #     "id": 4,
    # #     "name": "Guns N Petals",
    # #     "genres": ["Rock n Roll"],
    # #     "city": "San Francisco",
    # #     "state": "CA",
    # #     "phone": "326-123-5000",
    # #     "website": "https://www.gunsnpetalsband.com",
    # #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    # #     "seeking_venue": True,
    # #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    # #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # #     "past_shows": [{
    # #         "venue_id": 1,
    # #         "venue_name": "The Musical Hop",
    # #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    # #         "start_time": "2019-05-21T21:30:00.000Z"
    # #     }],
    # #     "upcoming_shows": [],
    # #     "past_shows_count": 1,
    # #     "upcoming_shows_count": 0,
    # # }
    # # data2 = {
    # #     "id": 5,
    # #     "name": "Matt Quevedo",
    # #     "genres": ["Jazz"],
    # #     "city": "New York",
    # #     "state": "NY",
    # #     "phone": "300-400-5000",
    # #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    # #     "seeking_venue": False,
    # #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    # #     "past_shows": [{
    # #         "venue_id": 3,
    # #         "venue_name": "Park Square Live Music & Coffee",
    # #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    # #         "start_time": "2019-06-15T23:00:00.000Z"
    # #     }],
    # #     "upcoming_shows": [],
    # #     "past_shows_count": 1,
    # #     "upcoming_shows_count": 0,
    # # }
    # # data3 = {
    # #     "id": 6,
    # #     "name": "The Wild Sax Band",
    # #     "genres": ["Jazz", "Classical"],
    # #     "city": "San Francisco",
    # #     "state": "CA",
    # #     "phone": "432-325-5432",
    # #     "seeking_venue": False,
    # #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    # #     "past_shows": [],
    # #     "upcoming_shows": [{
    # #         "venue_id": 3,
    # #         "venue_name": "Park Square Live Music & Coffee",
    # #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    # #         "start_time": "2035-04-01T20:00:00.000Z"
    # #     }, {
    # #         "venue_id": 3,
    # #         "venue_name": "Park Square Live Music & Coffee",
    # #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    # #         "start_time": "2035-04-08T20:00:00.000Z"
    # #     }, {
    # #         "venue_id": 3,
    # #         "venue_name": "Park Square Live Music & Coffee",
    # #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    # #         "start_time": "2035-04-15T20:00:00.000Z"
    # #     }],
    # #     "past_shows_count": 0,
    # #     "upcoming_shows_count": 3,
    # # }
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]
    # return render_template('pages/show_artist.html', artist=data)
    return render_template('pages/show_artist.html', artist=curr_artist)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # # Mock Data provided by default
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }

    # TODO: populate form with fields from artist with ID <artist_id>

    artist = Artist.query.get_or_404(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    # Load genres
    genres = []
    for genre in artist.genres:
        genres.append(genre.name)

    form.genres.data = genres

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    error = False
    artist_name = request.form.get('name', '')
    try:
        found_artist = Artist.query.get_or_404(artist_id)

        found_artist.name = request.form.get('name', '')
        found_artist.city = request.form.get('city', '')
        found_artist.state = request.form.get('state', '')
        found_artist.phone = request.form.get('phone', '')
        found_artist.website = request.form.get('website_link', '')
        found_artist.facebook_link = request.form.get('facebook_link', '')
        found_artist.seeking_description = request.form.get(
            'seeking_description', '')
        found_artist.image_link = request.form.get('image_link', '')
        seeking_venue = request.form.get('seeking_venue', '')

        # Because seeking_talent returns 'y' instead of True/False
        if type(seeking_venue) is not bool:
            seeking_venue = True if seeking_venue.startswith('y') else False

        found_artist.seeking_venue = seeking_venue

        new_genres = request.form.getlist('genres')

        # Delete all existing genres for current artist
        for old_genre in found_artist.genres:
            db.session.delete(old_genre)

        # add new genres for current artist
        for genre in new_genres:
            new_genre = ArtistGenre(name=genre)
            found_artist.genres.append(new_genre)

        db.session.commit()

    except exc.SQLAlchemyError as err:
        error = True
        print(err)

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                db.session.rollback()
                print(sys.exc_info())
                flash(f'Error updating artist "{artist_name}"', 'error')
            else:
                flash(f'Successfully updated artist "{artist_name}"', 'info')

            db.session.close()

        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # # Mock Data Provided by default
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }

    # TODO: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get_or_404(venue_id)

    form.name.data = venue.name
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    # Load genres
    genres = []
    for genre in venue.genres:
        genres.append(genre.name)

    form.genres.data = genres

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    venue_name = request.form.get('name', '')
    try:
        found_venue = Venue.query.get_or_404(venue_id)

        found_venue.name = request.form.get('name', '')
        found_venue.address = request.form.get('address', '')
        found_venue.city = request.form.get('city', '')
        found_venue.state = request.form.get('state', '')
        found_venue.phone = request.form.get('phone', '')
        found_venue.website = request.form.get('website_link', '')
        found_venue.facebook_link = request.form.get('facebook_link', '')
        found_venue.seeking_description = request.form.get(
            'seeking_description', '')
        found_venue.image_link = request.form.get('image_link', '')

        seeking_talent = request.form.get('seeking_talent', '')

        # Moderating 'seeking_talent' field into boolean
        # Because seeking_talent returns 'y' instead of True/False
        if type(seeking_talent) is not bool:
            seeking_talent = True if seeking_talent.startswith('y') else False
        found_venue.seeking_talent = seeking_talent

        new_genres = request.form.getlist('genres')

        # Delete all existing genres for current artist
        for old_genre in found_venue.genres:
            db.session.delete(old_genre)

        # add new genres for current artist
        for genre in new_genres:
            new_genre = VenueGenre(name=genre)
            found_venue.genres.append(new_genre)

        db.session.commit()
        flash(
            f'Successfully updated venue "{venue_name}:{found_venue.id}"', 'info')

    except exc.SQLAlchemyError as err:
        error = True
        print(err)

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                db.session.rollback()
                print(sys.exc_info())
                flash(f'Error updating venue "{venue_name}"', 'error')

            db.session.close()

        return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

    error = False
    artist_name = request.form.get('name', '')
    try:
        name = request.form.get('name', '')
        city = request.form.get('city', '')
        state = request.form.get('state', '')
        phone = request.form.get('phone', '')
        website = request.form.get('website_link', '')
        facebook_link = request.form.get('facebook_link', '')
        seeking_venue = request.form.get('seeking_venue')
        seeking_description = request.form.get('seeking_description', '')
        image_link = request.form.get('image_link', '')

        genres = request.form.getlist('genres')

        # Because seeking_talent returns 'y' instead of True/False
        if type(seeking_venue) is not bool:
            seeking_venue = True if seeking_venue.startswith('y') else False

        # print('Keys Gotten', '#' * 30)
        # for key in request.form.keys():
        #     print(key, request.form[key])

        # Creating a new instance of Artist
        new_artist = Artist(
            name=name, city=city, state=state, phone=phone,
            website=website, facebook_link=facebook_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
            image_link=image_link
        )

        # Adding each selected genre to Venue
        for genre in genres:
            new_genre = ArtistGenre(name=genre)
            new_artist.genres.append(new_genre)

        db.session.add(new_artist)
        db.session.commit()
        flash(
            f'Artist "{artist_name}:{new_artist.id}" was successfully listed!')

    except exc.SQLAlchemyError as err:
        print(err)
        error = True

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:
            if error:
                db.session.rollback()
                print(sys.exc_info())
                flash(
                    f'An error occurred. Artist "{artist_name}" could not be listed.')

            db.session.close()

        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    shows = db.session.query(Show).all()

    data = [{
        "venue_id": show.show_venue.id,
        "venue_name": show.show_venue.name,
        "artist_id": show.show_artist.id,
        "artist_name": show.show_artist.name,
        "artist_image_link": show.show_artist.image_link,
        "start_time": show.start_time
    } for show in shows]

    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    error = False
    try:
        venue_id = int(request.form.get('venue_id', '1'))
        artist_id = int(request.form.get('artist_id', '1'))
        start_time = request.form.get('start_time')

        new_show = Show(venue_id=venue_id, artist_id=artist_id,
                        start_time=start_time)

        db.session.add(new_show)
        db.session.commit()

        # on successful db insert, flash success
        flash(
            f'Show "{new_show.show_artist.name}:{artist_id} => {new_show.show_venue.name}:{venue_id}" was successfully listed!')

    except exc.SQLAlchemyError as err:
        error = True
        print(err)

    except Exception as err:
        error = True
        print(err)

    finally:
        if db.session:

            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

            if error:
                db.session.rollback()
                print(sys.exc_info())
                flash('An error occurred. Show could not be listed.')

            db.session.close()

        return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
