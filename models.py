from datetime import datetime
from database import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


####################################################################
# Implementing 'Show' as association Object to model the
# many-to-many relationship existing between Venues and Artists.
# The use of association Object is to allow me access extra fields
# 'start_time' later
####################################################################

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now())

    venue = db.relationship('Venue', back_populates='artists')
    artist = db.relationship('Artist', back_populates='venues')

    def __repr__(self) -> str:
        formatted_date = date.strftime(self.start_time, "%d-%m-%Y %H:%M")
        return f'<Show id:{self.id} venue_id:{self.venue_id} artist_id:{self.artist_id} start_time:{formatted_date}>'

###########################  NOTE  ###########################
# Proposed implementation for genres, being multi-valued field
# to conform to or satisfy the 3rd NF (3rd Normal Form)
# requirement specified
##############################################################


class VenueGenre(db.Model):
    __tablename__ = 'VenueGenre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<VenueGenre id: {self.id} name:{self.name}>'


class ArtistGenre(db.Model):
    __tablename__ = 'ArtistGenre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)

    def __repr__(self) -> str:
        return f'<ArtistGenre id: {self.id} name:{self.name}>'


###################   END OF GENRES MODELS ##################


# ----------- VENUE Model ---------------

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    # genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    # 'Genres' modeled separately to conform to 3rd-NF requirement
    genres = db.relationship('VenueGenre', backref='genre_venue', lazy=True)
    shows = db.relationship('Show', backref='show_venue')
    artists = db.relationship(
        'Show', backref=db.backref('venues', lazy=True))

    # Method defined to get dictionary equivalence of model object
    def to_dico(self):
        dico = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "genres": self.genres,
            "website": self.website,
            "seeking_talent": self.seeking_talent,
            "seeking_description": self.seeking_description
        }
        return dico

    # minimal info to return as string representation of
    # object when directly called for display in outputs
    def __repr__(self) -> str:
        return f'<Venue id: {self.id} name: {self.name} city: {self.city} state: {self.state}>'


# ----------- ARTIST Model ---------------

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(250))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    # 'Genres' modeled separately to conform to 3rd-NF requirement
    genres = db.relationship('ArtistGenre', backref='genre_artist', lazy=True)
    shows = db.relationship('Show', backref='show_artist', lazy=True)
    venues = db.relationship('Show', backref=db.backref('artists', lazy=True))

    def to_dico(self):
        dico = {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website": self.website,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description
        }
        return dico

    def __repr__(self) -> str:
        return f'<Artist id: {self.id} name: {self.name} city: {self.city} state: {self.state} phone: {self.phone}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# class Show(db.Model):
#     __tablename__ = 'Show'

#     id = db.Column(db.Integer, primary_key=True)
#     venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
#     artist_id = db.Column(db.Integer, db.ForeignKey(
#         'Artist.id'), nullable=False)
#     start_time = db.Column(db.DateTime, default=datetime.today())
