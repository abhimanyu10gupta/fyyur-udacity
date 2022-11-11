#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import date
import json
from xml.dom.minidom import NamedNodeMap
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
import sys

from sqlalchemy import ForeignKey, true
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
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


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = [
        venue.get_city_state for venue in Venue.query.distinct(Venue.city, Venue.state).all()
    ]

    for d in data:
        d["venues"] = [
            venue.self_dict for venue in Venue.query.filter_by(city=d["city"], state=d["state"]).all()
        ]
    # data = Venue.query.all()
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search = request.form.get('search_term', '')

    data = Venue.query.filter(Venue.name.ilike(f'%{search}%')).all()
    count = len(data)

    response = {
        "count": count,
        "data": data,
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id).venue_details
    print(venue)

    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=venue)

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
    try:
        form = VenueForm(request.form)
        print(form.genres.data)
        if form.validate():
            venue = Venue(name=form.name.data, city=form.city.data,
                          state=form.state.data,
                          address=form.address.data,
                          genres=form.genres.data,
                          phone=form.phone.data,
                          facebook_link=form.facebook_link.data,
                          image_link=form.image_link.data,
                          website=form.website_link.data,
                          seeking_talent=form.seeking_talent.data,
                          seeking_description=form.seeking_description.data,
                          )
            db.session.add(venue)
            db.session.commit()
        else:
            print(form.errors.items())
            print('nah')
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = Artist.query.all()

    data = Artist.query.with_entities(Artist.id, Artist.name)

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search = request.form.get('search_term', '')

    data = Artist.query.filter(Artist.name.ilike(f'%{search}%')).all()
    count = len(data)
    response = {
        "count": count,
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # for show in range(len(past_artist_shows(artist_id))):
    #     print(past_artist_shows(artist_id)[show])
    data = Artist.query.get(artist_id).artist_details
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.image_link.data = artist.image_link
    form.city.data = artist.city
    form.facebook_link.data = artist.facebook_link
    form.genres.data = artist.genres
    form.name.data = artist.name
    form.seeking_description.data = artist.seeking_description
    form.seeking_venue.data = artist.seeking_venue
    form.website_link.data = artist.website
    form.phone.data = artist.phone
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    artist = Artist.query.get(artist_id)
    try:
        if form.validate():
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.genres = form.genres.data
            artist.seeking_venue = form.seeking_venue
            artist.seeking_description = form.seeking_description
            artist.website = form.website_link
            artist.facebook_link = form.facebook_link
            artist.image_link = form.image_link
            artist.phone = form.phone
            db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.address.data = venue.address
    form.image_link.data = venue.image_link
    form.city.data = venue.city
    form.facebook_link.data = venue.facebook_link
    form.genres.data = venue.genres
    form.name.data = venue.name
    form.seeking_description.data = venue.seeking_description
    form.seeking_talent.data = venue.seeking_talent
    form.website_link.data = venue.website
    form.phone.data = venue.phone
    # TODO: populate form with values from venue with ID <venue_id>
    # form = VenueForm(venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    venue = Venue.query.get(venue_id)
    try:
        if form.validate():
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.genres = form.genres.data
            venue.seeking_venue = form.seeking_venue
            venue.seeking_description = form.seeking_description
            venue.website = form.website_link
            venue.facebook_link = form.facebook_link
            venue.image_link = form.image_link
            venue.phone = form.phone
            db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/availabilities', methods=['GET'])
def add_availability(artist_id):
    form = AvailabilityForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/add_availabilities.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/availabilities', methods=['POST'])
def add_availabilities(artist_id):
    form = AvailabilityForm(request.form)
    availability = ArtistAvailability(
        start_time=form.start_time.data, end_time=form.end_time.data, artist_id=artist_id)
    try:
        db.session.add(availability)
        db.session.commit()
        flash(' Availability added.')
    except:
        flash('Incorrect details. Availability could not be added.')
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    error = False
    try:
        print(form.genres.data)

        if form.validate():
            artist = Artist(name=form.name.data, city=form.city.data,
                            state=form.state.data,
                            phone=form.phone.data,
                            genres=form.genres.data,
                            facebook_link=form.facebook_link.data,
                            image_link=form.image_link.data,
                            website=form.website_link.data,
                            seeking_venue=form.seeking_venue.data,
                            seeking_description=form.seeking_description.data,)
            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + request.form['name'] +
                  ' was successfully listed!')

        else:
            flash('The details entered are incorrect')
            error = True
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()
        if error is True:
            return render_template('forms/new_artist.html', form=form)
        else:
            return render_template('pages/home.html')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # data = Show.query.all()
    data = [{
        "venue_id": show.venue_id,
        "venue_name": Venue.query.get(show.venue_id).name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.get(show.artist_id).name,
        "artist_image_link": Artist.query.get(show.artist_id).image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    }for show in Show.query.all()]
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
        form = ShowForm(request.form)
        if form.validate():
            show = Show(artist_id=form.artist_id.data,
                        venue_id=form.venue_id.data, start_time=form.start_time.data)
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        else:
            flash('Incorrect details. Show could not be listed.')
            error = True
    except:
        db.session.rollback()
        error = True
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    if error is True:
        return render_template('forms/new_show.html', form=form)
    else:
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
