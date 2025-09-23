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

@app.route("/items", methods=["POST"])
def create_item():
    data = request.json
    try:
        item = Item(name=data["name"], price=data["price"])
        db.session.add(item)
        db.session.commit()
        return jsonify({
            "message": "Item created",
            "item": {"id": item.id, "name": item.name, "price": item.price}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create item", "details": str(e)}), 500

@app.route("/items", methods=["PUT"])
def update_item_by_index():
    data = request.json
    try:
        index = data.get("index")
        if index is None:
            return jsonify({"error": "Index is required when no ID is provided"}), 400

        items = Item.query.order_by(Item.id).all()
        if index < 0 or index >= len(items):
            return jsonify({"error": "Index out of range"}), 404

        item = items[index]
        item.name = data.get("name", item.name)
        item.price = data.get("price", item.price)
        db.session.commit()

        return jsonify({
            "message": "Item updated by index",
            "item": {"id": item.id, "name": item.name, "price": item.price}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update item", "details": str(e)}), 500

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
