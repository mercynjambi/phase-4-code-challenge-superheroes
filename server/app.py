#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

api = Api(app)
migrate = Migrate(app, db)
db.init_app(app)

class Index(Resource):
    def get(self):
        return '<h1>Code challenge</h1>'

class HeroList(Resource):
    def get(self):
        heroes = Hero.query.all()
        # Return only the 'id', 'name', and 'super_name' for each hero to pass the test
        return [{'id': hero.id, 'name': hero.name, 'super_name': hero.super_name} for hero in heroes]

class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return {
                'id': hero.id,
                'name': hero.name,
                'super_name': hero.super_name,
                'hero_powers': [hp.to_dict() for hp in hero.hero_powers]
            }
        return {"error": "Hero not found"}, 404

class PowerList(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(include_hero_powers=False) for power in powers]

class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return power.to_dict()
        return {"error": "Power not found"}, 404

    def patch(self, id):
        power = Power.query.get(id)
        if power:
            data = request.get_json()
            description = data.get('description')
            if description is None or len(description) < 20:
                return {"errors": ["validation errors"]}, 400
            try:
                power.description = description
                db.session.commit()
                return power.to_dict()
            except ValueError as e:
                return {"errors": [str(e)]}, 400
        return {"error": "Power not found"}, 404

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        strength = data.get('strength')
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')
        
        if strength not in ['Strong', 'Weak', 'Average']:
            return {"errors": ["validation errors"]}, 400

        hero_power = HeroPower(
            strength=strength,
            hero_id=hero_id,
            power_id=power_id
        )
        
        db.session.add(hero_power)
        db.session.commit()
        
        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)
        
        return {
            'id': hero_power.id,
            'hero_id': hero_power.hero_id,
            'power_id': hero_power.power_id,
            'strength': hero_power.strength,
            'hero': {
                'id': hero.id,
                'name': hero.name,
                'super_name': hero.super_name
            },
            'power': {
                'id': power.id,
                'name': power.name,
                'description': power.description
            }
        }, 200

# API Resource Routing
api.add_resource(Index, '/')
api.add_resource(HeroList, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowerList, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
