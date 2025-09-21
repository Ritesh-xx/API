from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory fake database with sample data
db = {
    1: {"name": "Apple", "price": 1.99},
    2: {"name": "Banana", "price": 0.99}
}

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the Flask API!",
        "sample_data": db
    })

@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = db.get(item_id)
    if item:
        return jsonify({"item": item})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["POST"])
def create_item(item_id):
    data = request.json
    db[item_id] = data
    return jsonify({"message": "Item created", "item": db[item_id]}), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    if item_id in db:
        data = request.json
        db[item_id] = data
        return jsonify({"message": "Item updated", "item": db[item_id]})
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if item_id in db:
        del db[item_id]
        return jsonify({"message": "Item deleted"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
