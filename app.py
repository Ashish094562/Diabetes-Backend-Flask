from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import certifi
import joblib
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise Exception("MONGO_URI not found")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

client.admin.command("ping")

db = client["diabetes_db"]
collection = db["patients"]

model = joblib.load("diabetes_model.pkl")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        hypertension_str = "yes" if str(data.get("hypertension")) == "1" else "no"
        heart_disease_str = "yes" if str(data.get("heart_disease")) == "1" else "no"

        input_data = {
            "gender": str(data.get("gender")),
            "age": int(data.get("age")),
            "hypertension": hypertension_str,
            "heart_disease": heart_disease_str,
            "smoking_history": str(data.get("smoking_history")),
            "bmi": float(data.get("bmi")),
            "HbA1c_level": float(data.get("HbA1c_level")),
            "blood_glucose_level": int(data.get("blood_glucose_level")),
        }

        df = pd.DataFrame([input_data])

        prediction = int(model.predict(df)[0])
        result = "Diabetic" if prediction == 1 else "NotDiabetic"

        record = {
            "gender": input_data["gender"],
            "age": input_data["age"],
            "hypertension": 1 if hypertension_str == "yes" else 0,
            "heart_disease": 1 if heart_disease_str == "yes" else 0,
            "smoking_history": input_data["smoking_history"],
            "bmi": input_data["bmi"],
            "hba1c_level": input_data["HbA1c_level"],
            "blood_glucose_level": input_data["blood_glucose_level"],
            "result": result
        }

        inserted = collection.insert_one(record)

        return jsonify({
            "success": True,
            "result": result,
            "recordId": str(inserted.inserted_id)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/records", methods=["GET"])
def get_all_records():
    records = []
    for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        records.append(doc)
    return jsonify(records)

@app.route("/api/records/<id>", methods=["GET"])
def get_record(id):
    try:
        record = collection.find_one({"_id": ObjectId(id)})
        if not record:
            return jsonify({"error": "Record not found"}), 404
        record["_id"] = str(record["_id"])
        return jsonify(record)
    except:
        return jsonify({"error": "Invalid ID"}), 400

@app.route("/api/records/<id>", methods=["DELETE"])
def delete_record(id):
    try:
        result = collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Record not found"}), 404
        return jsonify({"message": "Record deleted successfully"})
    except:
        return jsonify({"error": "Invalid ID"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
