"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
"""
PSQL commands to populate database from CSV files in /docs
\COPY 'user' FROM '/workspaces/Anajerar_latampt36_Starwars_rest_API/docs/user.csv' DELIMITER ',' CSV HEADER;
\COPY 'panets' FROM '/workspaces/Anajerar_latampt36_Starwars_rest_API/docs/planets.csv' DELIMITER ',' CSV HEADER;
\COPY 'people' FROM '/workspaces/Anajerar_latampt36_Starwars_rest_API/docs/people.csv' DELIMITER ',' CSV HEADER;
\COPY 'favorite_planets' FROM '/workspaces/Anajerar_latampt36_Starwars_rest_API/docs/favorite_planets.csv' DELIMITER ',' CSV HEADER;
\COPY 'favorite_people' FROM '/workspaces/Anajerar_latampt36_Starwars_rest_API/docs/favorite_people.csv' DELIMITER ',' CSV HEADER;
"""


import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, FavoritePeople, FavoritePlanets
from sqlalchemy import and_


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

@app.route('/people', methods=['POST','PUT'])
def add_people():
    data = request.json
    method = request.method
    name = data.get('name')
    birth_year = data.get('birth_year')
    gender = data.get('gender')
    height = data.get('height')
    hair_color = data.get('hair_color')
    homeworld = data.get('homeworld')
    picture_url = data.get('picture_url')

    people_exist = db.session.execute(db.select(People).filter_by(name=name)).scalars().one_or_none()

    if method == 'POST':
        if people_exist==None:
            new_people = People(
                name = name,
                birth_year = birth_year,
                gender = gender,
                height = height,
                hair_color = hair_color,
                homeworld = homeworld,
                picture_url = picture_url
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
    elif method == 'PUT':
        if people_exist !=None:
            people_exist.name = name
            people_exist.birth_year = birth_year
            people_exist.gender = gender
            people_exist.height = height
            people_exist.hair_color = hair_color
            people_exist.homeworld = homeworld
            people_exist.picture_url = picture_url
            try:
                db.session.commit()
                return jsonify({'msg':'update completed','people_id':people_exist.id})
            except Exception as error:
                db.session.rollback()
                print('Error:',error)
                return jsonify({"message": "Error updating People to database"}), 500
        else:
            return jsonify({'msg':'people does not exist'})


@app.route('/user', methods=['POST'])
def add_user():
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
        return jsonify({"msg":"User already exist"}),400

@app.route('/users',methods=['GET'])
def list_users():
    users_list=[]
    users = db.session.execute(db.select(User)).all()
    for user in users:
        users_list.append(user[0].serialize())
    return jsonify({'msg':'ok','users':users_list})

@app.route('/users/<int:id>',methods=['GET'])
def single_user(id):
    user = db.session.execute(db.select(User).filter_by(id=id)).one_or_none();
    if user == None:
        return jsonify({"msg":"user not found"}),404
    else:
        print("This is the user",user[0].serialize())
        return jsonify({"msg":"ok","user":user[0].serialize()})

@app.route('/planet', methods=['POST','PUT'])
def add_planet():
    data = request.json
    method = request.method
    planet_name = data.get('planet_name')
    population = data.get('population')
    climate = data.get('climate')
    diameter = data.get('diameter')
    gravity = data.get('gravity')
    picture_url = data.get('picture_url')

    planet_exist = db.session.execute(db.select(Planets).filter_by(planet_name=planet_name)).scalars().one_or_none()
    if method == 'POST':
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
                return jsonify({"message": "Error saving Planet to database"}), 500

            return jsonify({
                "user": new_planet.serialize(),
                "message": "ok"
            }), 200
        else:
            return jsonify({"msg":"Planet already exist"}),400
    elif method == 'PUT':
        if planet_exist != None:
            planet_exist.planet_name = planet_name
            planet_exist.population = population
            planet_exist.climate = climate
            planet_exist.diameter = diameter
            planet_exist.gravity = gravity
            planet_exist.picture_url = picture_url
            
            try:
                db.session.commit()
                return jsonify({'msg':'update completed','planet_id':planet_exist.id})
            except Exception as error:
                db.session.rollback()
                print('Error:',error)
                return jsonify({"message": "Error updating Planet to database"}), 500
        else:
                return jsonify({'msg':'planet does not exist'})
        
@app.route('/planets', methods=['GET'])
def list_planets():
    planets_list=[]
    planets = db.session.execute(db.select(Planets)).all()
    for planet in planets:
        planets_list.append(planet[0].serialize())
    return jsonify({'msg':'ok','users':planets_list})

@app.route('/planets/<int:id>', methods=['GET','DELETE'])
def single_planet(id):
    method = request.method
    planet = db.session.execute(db.select(Planets).filter_by(id=id)).scalars().one_or_none();
    if planet == None:
        return jsonify({"msg":"planet not found"}),404
    else:
        if method == 'DELETE':
            try:
                db.session.delete(planet)
                db.session.commit()
                return jsonify({"msg":"planet deleted", "id":id})
            except Exception as error:
                db.session.rollback()
                print('error', error)
                return jsonify({"message": "Error deleting Planet"}), 500
        else:
            return jsonify({"msg":"ok","planet":planet.serialize()})

@app.route('/people', methods=['GET'])
def people():
    people_list=[]
    people = db.session.execute(db.select(People)).all()
    for single_person in people:
        people_list.append(single_person[0].serialize())
    return jsonify({'msg':'ok','people':people_list})
    
@app.route('/people/<int:people_id>',methods=['GET','DELETE'])
def single_person(people_id):
    method = request.method
    person = db.session.execute(db.select(People).filter_by(id=people_id)).scalars().one_or_none();
    if person == None:
        return jsonify({"msg":"person not found"}),404
    else:
        if method == 'DELETE':
            try:
                db.session.delete(person)
                db.session.commit()
                return jsonify({"msg":"person deleted", "id":people_id})
            except Exception as error:
                db.session.rollback()
                print('error', error)
                return jsonify({"message": "Error deleting People"}), 500
        else:
            return jsonify({"msg":"ok","planet":person.serialize()})

@app.route('/user/favorites',methods=['GET'])
def user_favorites():
    data = request.json
    user_id = data.get('user_id')
    try:
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalars().one_or_none();
    except:
        return jsonify({"msg":"Database processing error, try again"}),500
    if user == None:
        return jsonify({"msg":"user not found"}),404
    else:
        return jsonify({"msg":"ok",
                        "user_id":user_id,
                        "user_name":user.user_name,
                        "user_favorites":user.favorites()}),200

@app.route('/favorite/planet/<int:planet_id>',methods=['POST','DELETE'])
def user_fav_planet(planet_id):
    data = request.json
    method = request.method
    current_user_id = data.get('current_user_id')
    is_valid_planet = db.session.execute(db.select(Planets).filter_by(id=planet_id)).one_or_none()
    is_valid_user = db.session.execute(db.select(User).filter_by(id=current_user_id)).one_or_none()
    already_favorite = db.session.execute(db.select(FavoritePlanets).filter(and_(FavoritePlanets.user_fav_id == current_user_id,
             FavoritePlanets.planet_fav_id == planet_id))).scalars().one_or_none()
    if method=='DELETE':
        if already_favorite == None:
            return jsonify({'msg':'planet is not favorite for this user'})
        else:
            try:
                db.session.delete(already_favorite)
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                return jsonify({"message": "Error deleting Favorite Planet record"}), 500
            return jsonify ({'msg':'favorite planet record deleted',
                             'user_id':current_user_id,
                             'people':planet_id})
    if is_valid_planet == None or is_valid_user == None :
        return jsonify ({'msg':'non valid user or people id'})
    elif already_favorite != None :
        return jsonify ({'msg':'planet already favorite for this user'})
    else:
        new_planet_favorite=FavoritePlanets(
            planet_fav_id = planet_id,
            user_fav_id = current_user_id)

    try:
            db.session.add(new_planet_favorite)
            db.session.commit()
    except Exception as error:
            db.session.rollback()
            return jsonify({"message": "Error saving Favorite People to database"}), 500         

    print("response:",new_planet_favorite.serialize())
    return {"msg":"ok",
            "favorite_people":new_planet_favorite.serialize()},200

@app.route('/favorite/people/<int:people_id>',methods=['POST','DELETE'])
def user_fav_people(people_id):
    data = request.json
    method = request.method
    current_user_id = data.get('current_user_id')
    is_valid_people = db.session.execute(db.select(People).filter_by(id=people_id)).one_or_none()
    is_valid_user = db.session.execute(db.select(User).filter_by(id=current_user_id)).one_or_none()
    already_favorite = db.session.execute(db.select(FavoritePeople).filter(and_(FavoritePeople.user_fav_id == current_user_id,
             FavoritePeople.people_fav_id == people_id))).scalars().one_or_none()
    if method=='DELETE':
        if already_favorite == None:
            return jsonify({'msg':'people is not favorite for this user'})
        else:
            try:
                db.session.delete(already_favorite)
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                return jsonify({"message": "Error deleting Favorite People record"}), 500
            return jsonify ({'msg':'favorite people record deleted',
                             'user_id':current_user_id,
                             'people':people_id})
    if is_valid_people == None or is_valid_user == None :
        return jsonify ({'msg':'non valid user or people id'})
    elif already_favorite != None :
        return jsonify ({'msg':'people already favorite for this user'})
    else:
        new_people_favorite=FavoritePeople(
            people_fav_id = people_id,
            user_fav_id = current_user_id)

    try:
            db.session.add(new_people_favorite)
            db.session.commit()
    except Exception as error:
            db.session.rollback()
            return jsonify({"message": "Error saving Favorite People to database"}), 500         

    print("response:",new_people_favorite.serialize())
    return {"msg":"ok",
            "favorite_people":new_people_favorite.serialize()},200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
