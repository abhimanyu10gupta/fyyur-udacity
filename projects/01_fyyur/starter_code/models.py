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

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(240))
    shows = db.relationship('Show', backref='venues', lazy=True)

    @property
    def get_city_state(self):
        return {
            "city": self.city,
            "state": self.state,
        }

    @property
    def self_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
        }

    @property
    def venue_details(self):
        past_shows = past_venue_shows(self.id)
        upcoming_shows = upcoming_venue_shows(self.id)
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "genres": self.genres,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
            "upcoming_shows": [{
                "venue_id": show.venues.id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            }for show in upcoming_shows],
            "past_shows": [{
                "venue_id": show.venues.id,
                "venue_name": show.venues.name,
                "venue_image_link": show.venues.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            }for show in past_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

    @property
    def venue_form_details(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "genres": self.genres,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description,
        }


def past_venue_shows(venue_id):
    return db.session.query(Show).filter(
        Show.start_time < datetime.now(),
        Show.venue_id == venue_id).all()


def upcoming_venue_shows(venue_id):
    return db.session.query(Show).filter(
        Show.start_time > datetime.now(),
        Show.venue_id == venue_id).all()


def past_artist_shows(artist_id):
    return db.session.query(Show).filter(
        Show.start_time < datetime.now(),
        Show.artist_id == artist_id).all()


def upcoming_artist_shows(artist_id):
    return db.session.query(Show).filter(
        Show.start_time > datetime.now(),
        Show.artist_id == artist_id).all()


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String(120)))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(240))
    shows = db.relationship('Show', backref='artists',
                            lazy=True)
    availability = db.relationship(
        'ArtistAvailability', backref='artists', lazy=True)

    @property
    def artist_details(self):
        past_shows = past_artist_shows(self.id)
        upcoming_shows = upcoming_artist_shows(self.id)
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "genres": self.genres,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
            "upcoming_shows": [{
                "artist_id": show.artists.id,
                "artist_name": show.artists.name,
                "artist_image_link": show.artists.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            }for show in upcoming_shows],
            "past_shows": [{
                "artist_id": show.artists.id,
                "artist_name": show.artists.name,
                "artist_image_link": show.artists.image_link,
                "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            }for show in past_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }


# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class ArtistAvailability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    # start_day = db.Column(db.DateTime())
    # end_day = db.Column(db.DateTime())
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
