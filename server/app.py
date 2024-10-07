#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
db.init_app(app)

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Welcome to my API</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    heroes_list = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes]
    return jsonify(heroes_list)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        hero_data = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "hero_powers": [
                {
                    "id": hp.id,
                    "hero_id": hp.hero_id,
                    "power_id": hp.power_id,
                    "strength": hp.strength,
                    "power": {
                        "id": hp.power.id,
                        "name": hp.power.name,
                        "description": hp.power.description
                    }
                } for hp in hero.hero_powers
            ]
        }
        return jsonify(hero_data)
    else:
        return make_response(jsonify({"error": "Hero not found"}), 404)
    

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_list = [{"id": power.id, "name": power.name, "description": power.description} for power in powers]
    return jsonify(powers_list)  

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power:
        power_data = {"id": power.id, "name": power.name, "description": power.description}
        return jsonify(power_data)
    else:
        return make_response(jsonify({"error": "Power not found"}), 404)
    

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return make_response(jsonify({"error": "Power not found"}), 404)
    
    data = request.get_json()
    if 'description' in data:
        power.description = data['description']
        db.session.commit()
        return jsonify({
            "id": power.id,
            "name": power.name,
            "description": power.description
        })
    else:
        return make_response(jsonify({"error": "Invalid request"}), 400) 



@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    if strength not in ['Weak', 'Average', 'Strong']:
        return make_response(jsonify({"errors": ["Invalid strength value"]}), 400)

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return make_response(jsonify({"errors": ["Invalid hero or power"]}), 400)

    new_hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(new_hero_power)
    db.session.commit()

    return jsonify({
        "id": new_hero_power.id,
        "strength": new_hero_power.strength,
        "hero": {"id": hero.id, "name": hero.name, "super_name": hero.super_name},
        "power": {"id": power.id, "name": power.name, "description": power.description}
    }), 201   

    




if __name__ == '__main__':
    app.run(port=5555, debug=True)
