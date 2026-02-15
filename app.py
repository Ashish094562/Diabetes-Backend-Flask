from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from models import PatientRecord
import joblib
import pandas as pd
import os

app = Flask(__name__)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diabetes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Load ML model
model = joblib.load("diabetes_model.pkl")

# Create DB tables
with app.app_context():
    db.create_all()

# -------------------------------
# Health Check
# -------------------------------
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


# -------------------------------
# Predict + Save (Spring Equivalent)
# -------------------------------
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Convert 0/1 → yes/no for model
        hypertension_str = "yes" if str(data.get("hypertension")) == "1" else "no"
        heart_disease_str = "yes" if str(data.get("heart_disease")) == "1" else "no"

        input_data = {
            'gender': str(data.get('gender')),
            'age': int(data.get('age')),
            'hypertension': hypertension_str,
            'heart_disease': heart_disease_str,
            'smoking_history': str(data.get('smoking_history')),
            'bmi': float(data.get('bmi')),
            'HbA1c_level': float(data.get('HbA1c_level')),
            'blood_glucose_level': int(data.get('blood_glucose_level')),
        }

        df = pd.DataFrame([input_data])

        pred = int(model.predict(df)[0])
        result = "Diabetic" if pred == 1 else "NotDiabetic"

        # Save in DB (convert back to 0/1)
        record = PatientRecord(
            gender=input_data['gender'],
            age=input_data['age'],
            hypertension=1 if hypertension_str == "yes" else 0,
            heart_disease=1 if heart_disease_str == "yes" else 0,
            smoking_history=input_data['smoking_history'],
            bmi=input_data['bmi'],
            hba1c_level=input_data['HbA1c_level'],
            blood_glucose_level=input_data['blood_glucose_level'],
            result=result
        )

        db.session.add(record)
        db.session.commit()

        return jsonify({
            "message": "Prediction saved successfully",
            "result": result,
            "recordId": record.id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -------------------------------
# Get All Records
# -------------------------------
@app.route('/api/records', methods=['GET'])
def get_all_records():
    records = PatientRecord.query.all()
    return jsonify([r.to_dict() for r in records])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
