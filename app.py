import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)


# Define a model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    items = Item.query.all()
    return jsonify([
        {"id": i.id, "name": i.name, "price": i.price} for i in items
    ])

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if item:
        return jsonify({"item": {"name": item.name, "price": item.price}})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items", methods=["GET"])
def get_all_items():
    items = Item.query.all()
    return jsonify([
        {"id": item.id, "name": item.name, "price": item.price} for item in items
    ])

@app.route("/items/<int:item_id>", methods=["POST"])
def create_item(item_id):
    data = request.json
    item = Item(id=item_id, name=data["name"], price=data["price"])
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "Item created", "item": data}), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if item:
        data = request.json
        item.name = data["name"]
        item.price = data["price"]
        db.session.commit()
        return jsonify({"message": "Item updated", "item": data})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
