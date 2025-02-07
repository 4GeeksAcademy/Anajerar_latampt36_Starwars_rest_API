"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['POST'])
def addPeople():
    data = request.json
    print('Json Data name:', type(data),data)
    name = data.get('name')
    birth_year = data.get('birth_year')
    gender = data.get('gender')
    height = data.get('height')
    hair_color = data.get('hair_color')
    homeworld = data.get('homeworld')

    people_exist = db.session.execute(db.select(People).filter_by(name=name)).one_or_none()
    if people_exist==None:
        new_people = People(
            name = name,
            birth_year = birth_year,
            gender = gender,
            height = height,
            hair_color = hair_color,
            homeworld = homeworld
            )
        try:
            db.session.add(new_people)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print('Error:',error)
            return jsonify({"message": "Error saving People to database"}), 500

        return jsonify({
            "user": new_people.serialize(),
            "message": "ok"
        }), 200
    else:
        return jsonify({"msg":"People already exist"}),400

@app.route('/user', methods=['POST'])
def addUser():
    data = request.json
    email = data.get('email')
    user_name = data.get('user_name')
    full_name = data.get('full_name')
    password = data.get('password')
    
    user_exist = db.session.execute(db.select(User).filter_by(email=email)).one_or_none()
    if user_exist==None:
        new_user = User(
            email = email,
            user_name = user_name,
            full_name = full_name,
            password = password
            )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print('Error:',error)
            return jsonify({"message": "Error saving user to database"}), 500

        return jsonify({
            "user": new_user.serialize(),
            "message": "ok"
        }), 200
    else:
        return jsonify({"msg":"Planet already exist"}),400

@app.route('/users',methods=['GET'])
def listUsers():
    users_list=[]
    users = db.session.execute(db.select(User)).all()
    for user in users:
        users_list.append(user[0].serialize())
    return jsonify({'msg':'ok','users':users_list})

@app.route('/users/<int:id>',methods=['GET'])
def singleUser(id):
    user = db.session.execute(db.select(User).filter_by(id=id)).one_or_none();
    if user == None:
        return jsonify({"msg":"user not found"}),404
    else:
        print("This is the user",user[0].serialize())
        return jsonify({"msg":"ok","user":user[0].serialize()})

@app.route('/planet', methods=['POST'])
def addPlanet():
    data = request.json
    print('Json Data name:', type(data),data)
    planet_name = data.get('planet_name')
    population = data.get('population')
    climate = data.get('climate')
    diameter = data.get('diameter')
    gravity = data.get('gravity')
    picture_url = data.get('picture_url')

    planet_exist = db.session.execute(db.select(Planets).filter_by(planet_name=planet_name)).one_or_none()
    if planet_exist==None:
        new_planet = Planets(
            planet_name = planet_name,
            population = population,
            climate = climate,
            diameter = diameter,
            gravity = gravity,
            picture_url = picture_url
            )
        try:
            db.session.add(new_planet)
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            print('Error:',error)
            return jsonify({"message": "Error saving Planet to database"}), 500

        return jsonify({
            "user": new_planet.serialize(),
            "message": "ok"
        }), 200
    else:
        return jsonify({"msg":"Planet already exist"}),400

@app.route('/planets', methods=['GET'])
def listPlanets():
    planets_list=[]
    planets = db.session.execute(db.select(Planets)).all()
    for planet in planets:
        planets_list.append(planet[0].serialize())
    return jsonify({'msg':'ok','users':planets_list})

@app.route('/planets/<int:id>', methods=['GET'])
def singlePlanet(id):
    planet = db.session.execute(db.select(Planets).filter_by(id=id)).one_or_none();
    if planet == None:
        return jsonify({"msg":"planet not found"}),404
    else:
        return jsonify({"msg":"ok","planet":planet[0].serialize()})


@app.route('/people', methods=['GET'])
def people():
    people_list=[]
    people = db.session.execute(db.select(People)).all()
    for single_person in people:
        people_list.append(single_person[0].serialize())
    return jsonify({'msg':'ok','users':people_list})
    

@app.route('/people/<int:people_id>',methods=['GET'])
def single_person(people_id):
    person = db.session.execute(db.select(People).filter_by(id=people_id)).one_or_none();
    if person == None:
        return jsonify({"msg":"person not found"}),404
    else:
        return jsonify({"msg":"ok","planet":person[0].serialize()})

@app.route('/users/favorites',methods=['GET'])
def user_favorites():
    return {"msg":"under construction"},200

@app.route('/user/favorite/<int:planet_id>',methods=['POST'])
def user_fav_planet(planet_id):
    
    return{"msg":"under construction"},200

@app.route('/user/favorite/<int:people_id>',methods=['POST'])
def user_fav_people(people_id):
    return {"msg":"under construction"},200

@app.route('/user/favorite/<int:planet_id>',methods=['DELETE'])
def user_del_planet(planet_id):
    return{"msg":"under construction"},200

@app.route('/user/favorite/<int:people_id>',methods=['DELETE'])
def user_del_people(people_id):
    return {"msg":"under construction"},200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
