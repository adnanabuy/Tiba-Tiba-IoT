from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(_name_)
client = MongoClient("localhost", 27017)
db = client["iotdb"]
collection = db["iot-data-collection"]

@app.route("/save", methods=['POST'])
def save_data():
    try:
        data = request.json 
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = collection.insert_one(data)
        return jsonify({"message": "Data saved successfully", "id": str(result.inserted_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch', methods=['GET'])
def fetch_data():
    try:
        data = list(collection.find({}, {"_id": 0}))
        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=8080, debug=True)