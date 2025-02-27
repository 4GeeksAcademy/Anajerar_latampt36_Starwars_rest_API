from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100))
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    fav_planet = db.relationship('FavoritePlanets',back_populates='user')
    fav_people = db.relationship('FavoritePeople', back_populates='user_fav')

    def __init__(self,email,user_name,full_name,password):
        self.email = email
        self.user_name = user_name
        self.full_name = full_name
        self.password = password
        self.is_active = True

    def favorites(self):
        fav_planet_list = [favorite_planet.planet.planet_name for favorite_planet in self.fav_planet]
        fav_people_list = [favorite_people.fav_people.name for favorite_people in self.fav_people]
        return {"favorite_planets":fav_planet_list,
                "favorite_people":fav_people_list}
    
    def __repr__(self):
        return '<User %r>' % self.user_name

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user_name": self.user_name,
            "full_name": self.full_name
            # do not serialize the password, its a security breach
        }
    
class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(50), unique=True)
    population = db.Column(db.String(40),nullable=True)
    climate = db.Column(db.String(25),nullable=True)
    diameter = db.Column(db.Integer,nullable=True)
    gravity = db.Column(db.String(15),nullable=True)
    picture_url = db.Column(db.String(300),nullable=True)

    planet_fav = db.relationship('FavoritePlanets', back_populates='planet')

    def __init__(self,planet_name,population,climate,diameter,gravity,picture_url):
        self.planet_name = planet_name
        self.population = population
        self.climate = climate
        self.diameter = diameter
        self.gravity = gravity
        self.picture_url = picture_url

    def __repr__(self):
        return '<Planet %r>' % self.planet_name
    
    def serialize(self):
        return {
            "planet": self.planet_name,
            "population": self.population,
            "picture_url":self.picture_url,
            "climate":self.climate,
            "diameter":self.diameter,
            "gravity":self.diameter,
            "id":self.id
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    birth_year = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10),nullable=True)
    height = db.Column(db.String(10),nullable=True)
    hair_color = db.Column(db.String(10),nullable=True)
    homeworld = db.Column(db.String(25), nullable=True)
    picture_url = db.Column(db.String(300), nullable=True)

    people_fav = db.relationship('FavoritePeople', back_populates='fav_people')

    def __init__(self,name,birth_year,gender,height,hair_color,homeworld,picture_url):
        self.name = name
        self.birth_year = birth_year
        self.gender = gender
        self.height = height
        self.hair_color = hair_color
        self.homeworld = homeworld
        self.picture_url = picture_url

    def __repr__(self):
        return '<People %r>' % self.name
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "hair_color": self.hair_color,
            "homeworld":self.homeworld,
            "picture_url": self.picture_url
        }

class FavoritePlanets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_fav_id = db.Column(db.Integer, ForeignKey(Planets.id))
    user_fav_id = db.Column(db.Integer,ForeignKey(User.id))
    user = db.relationship(User, back_populates='fav_planet')
    planet = db.relationship(Planets, back_populates='planet_fav')

    def __init__(self,planet_fav_id, user_fav_id):
        self.planet_fav_id = planet_fav_id
        self.user_fav_id = user_fav_id

    def __repr__(self):
        return '<FavPlanet %r>' % self.id

    def serialize(self):
        return {'id':self.id,
                'user_fav_id':self.user.user_name,
                'people_fav_id':self.planet.planet_name
                }

class FavoritePeople(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    people_fav_id = db.Column(db.Integer, ForeignKey(People.id))
    user_fav_id = db.Column(db.Integer,ForeignKey(User.id))
    user_fav = db.relationship(User,back_populates='fav_people')
    fav_people = db.relationship(People, back_populates='people_fav')

    def __init__(self,people_fav_id,user_fav_id):
        self.people_fav_id = people_fav_id
        self.user_fav_id = user_fav_id

    def __repr__(self):
        return '<FavPeople %r>' % self.id

    def serialize(self):
        return {'id':self.id,
                'user_fav_id':self.user_fav.user_name,
                'people_fav_id':self.fav_people.name
                }
