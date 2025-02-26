#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response, abort
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):
    def get(self):
        """Get all plants."""
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        """Create a new plant."""
        data = request.get_json()

        # Validate required fields
        if not data or not all(key in data for key in ['name', 'image', 'price']):
            abort(400, description="Missing required fields: name, image, price")

        # Create new plant
        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
            is_in_stock=data.get('is_in_stock', True)  # Default to True if not provided
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(jsonify(new_plant.to_dict()), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):
    def get(self, id):
        """Get a specific plant by ID."""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            abort(404, description="Plant not found")
        return make_response(jsonify(plant.to_dict()), 200)

    def patch(self, id):
        """Update a specific plant by ID."""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            abort(404, description="Plant not found")

        data = request.get_json()

        # Update fields if provided
        if 'name' in data:
            plant.name = data['name']
        if 'image' in data:
            plant.image = data['image']
        if 'price' in data:
            plant.price = data['price']
        if 'is_in_stock' in data:
            plant.is_in_stock = data['is_in_stock']

        db.session.commit()

        return make_response(jsonify(plant.to_dict()), 200)

    def delete(self, id):
        """Delete a specific plant by ID."""
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            abort(404, description="Plant not found")

        db.session.delete(plant)
        db.session.commit()

        return make_response('', 204)  # No content response for successful deletion


api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)