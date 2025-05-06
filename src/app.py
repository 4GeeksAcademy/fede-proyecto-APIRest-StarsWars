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
from models import db, User, People, Planets, Favorites
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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
def get_user():
    users = User.query.all()

    return jsonify([user.serialize()for user in users]), 200


@app.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()

    user = User(
        email=body['email'],
        password=body['password'],
        is_active=body['is_active']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 200


@app.route('/people', methods=['GET'])
def get_people():
    peoples = People.query.all()
    return jsonify([people.serialize()for people in peoples]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    return jsonify(person.serialize()), 200


@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": f"Person with id {people_id} has been deleted."}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planets.query.all()

    return jsonify([planet.serialize()for planet in planets]), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planets.query.get(planet_id)
    return jsonify(planet.serialize()), 200


@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planets.query.get(planet_id)
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": f"Planet with id {planet_id} has been deleted."}), 200


@app.route('/people', methods=['POST'])
def create_people():
    body = request.get_json()

    people = People(
        id=body['id'],
        name=body['name'],
        birth_year=body['birth_year'],
        eye_color=body['eye_color'],
    )

    db.session.add(people)
    db.session.commit()
    return jsonify(people.serialize()), 201


@app.route('/favorites/planet/<int:planet_id>', methods=['POST'])
def get_favorite_planet_by_id(planet_id):
    body = request.get_json()
    existing_favorite = Favorites.query.filter_by(
        user_id=body['user_id'], planets_id=planet_id).first()
    if existing_favorite:
        return jsonify({'msg': 'el planeta ya existe en favoritos'}), 400
    new_favorites = Favorites(user_id=body['user_id'], planets_id=planet_id)
    db.session.add(new_favorites)
    db.session.commit()
    return jsonify(new_favorites.serialize()), 201


@app.route('/favorites/people/<int:people_id>', methods=['POST'])
def get_favorite_people_by_id(people_id):
    body = request.get_json()
    existing_favorite = Favorites.query.filter_by(
        user_id=body['user_id'], people_id=people_id).first()
    if existing_favorite:
        return jsonify({'msg': 'el personaje ya existe en favoritos'}), 400
    new_favorites = Favorites(user_id=body['user_id'], people_id=people_id)
    db.session.add(new_favorites)
    db.session.commit()
    return jsonify(new_favorites.serialize()), 201


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    body = request.get_json()
    favorites = Favorites.query.filter_by(user_id=body['user_id']).all()
    return jsonify([fav.serialize() for fav in favorites]), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
