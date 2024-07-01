#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])


class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
            pizzas = [Pizza.query.get(rp.pizza_id).to_dict() for rp in restaurant_pizzas]
            restaurant_data = restaurant.to_dict()
            restaurant_data["restaurant_pizzas"] = pizzas
            return jsonify(restaurant_data)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)


class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])


class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        pizza_id = data.get('pizza_id')
        restaurant_id = data.get('restaurant_id')
        price = data.get('price')

        if not pizza_id or not restaurant_id or not isinstance(price, (int, float)) or not (1 <= price <= 30):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            new_restaurant_pizza = RestaurantPizza(
                pizza_id=pizza_id,
                restaurant_id=restaurant_id,
                price=price,
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)


api.add_resource(RestaurantListResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzaListResource, "/pizzas")
api.add_resource(RestaurantPizzaResource, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
