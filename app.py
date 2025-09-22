import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)

# Create tables
with app.app_context():
    db.create_all()

# Routes

@app.route("/")
def home():
    items = Item.query.all()
    return jsonify([
        {"id": i.id, "name": i.name, "price": i.price} for i in items
    ])

@app.route("/items", methods=["GET"])
def get_all_items():
    items = Item.query.all()
    return jsonify([
        {"id": item.id, "name": item.name, "price": item.price} for item in items
    ])

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if item:
        return jsonify({"item": {"id": item.id, "name": item.name, "price": item.price}})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["POST"])
def create_item(item_id):
    data = request.json
    if Item.query.get(item_id):
        return jsonify({"error": "Item already exists"}), 400
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

@app.route("/items/<int:item_id>", methods=["PATCH"])
def patch_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    data = request.json
    if "name" in data:
        item.name = data["name"]
    if "price" in data:
        item.price = data["price"]
    db.session.commit()
    return jsonify({
        "message": "Item patched",
        "item": {"id": item.id, "name": item.name, "price": item.price}
    })

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["HEAD"])
def head_item(item_id):
    item = Item.query.get(item_id)
    return ('', 200) if item else ('', 404)

@app.route("/items/<int:item_id>", methods=["OPTIONS"])
def options_item(item_id):
    return jsonify({
        "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    }), 200, {
        "Allow": "GET,POST,PUT,PATCH,DELETE,HEAD,OPTIONS",
        "Content-Type": "application/json"
    }

@app.route("/items", methods=["OPTIONS"])
def options_items():
    return jsonify({
        "allowed_methods": ["GET", "POST", "OPTIONS"]
    }), 200, {
        "Allow": "GET,POST,OPTIONS",
        "Content-Type": "application/json"
    }

# Run the server
if __name__ == "__main__":
    app.run(debug=True)
