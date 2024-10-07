#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import database, Character, Ability, CharacterAbility
import os
from flask_cors import CORS

# Set up of the  base directory and database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_URI = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, database)
database.init_app(app)
CORS(app)

@app.route("/")
def home():
    return "<h1>Character and Ability API</h1>"

@app.route("/characters", methods=["GET"])
def list_characters():
    all_characters = Character.query.all()
    response_data = [character.to_dict(only=("id", "real_name", "alias")) for character in all_characters]
    return make_response(response_data, 200)

@app.route("/characters/<int:id>", methods=["GET"])
def get_character(id):
    character = Character.query.get(id)
    if character:
        response_data = character.to_dict()
        return make_response(response_data, 200)
    return make_response({"error": "Character not found"}, 404)

@app.route("/abilities", methods=["GET"])
def list_abilities():
    all_abilities = Ability.query.all()
    response_data = [ability.to_dict(only=("id", "title", "details")) for ability in all_abilities]
    return make_response(response_data, 200)

@app.route("/abilities/<int:id>", methods=["GET", "PATCH"])
def manage_ability(id):
    ability = Ability.query.get(id)
    if request.method == "GET":
        if ability:
            response_data = ability.to_dict(only=("id", "title", "details"))
            return make_response(response_data, 200)
        return make_response({"error": "Ability not found"}, 404)
    
    if request.method == "PATCH":
        if not ability:
            return make_response({"error": "Ability not found"}, 404)
        data = request.get_json() if request.is_json else request.form
        try:
            for key, value in data.items():
                setattr(ability, key, value)
            database.session.commit()
            return make_response(ability.to_dict(), 200)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

@app.route("/character_abilities", methods=["POST"])
def add_character_ability():
    try:
        data = request.get_json() if request.is_json else request.form
        character_ability = CharacterAbility(**data)
        database.session.add(character_ability)
        database.session.commit()
        return make_response(character_ability.to_dict(), 201)
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
