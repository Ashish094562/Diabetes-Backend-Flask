from database import db

class PatientRecord(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    hypertension = db.Column(db.Integer)
    heart_disease = db.Column(db.Integer)
    smoking_history = db.Column(db.String(50))
    bmi = db.Column(db.Float)
    hba1c_level = db.Column(db.Float)
    blood_glucose_level = db.Column(db.Integer)
    result = db.Column(db.String(50))

    def to_dict(self):
        return {
            "id": self.id,
            "gender": self.gender,
            "age": self.age,
            "hypertension": self.hypertension,
            "heart_disease": self.heart_disease,
            "smoking_history": self.smoking_history,
            "bmi": self.bmi,
            "hba1c_level": self.hba1c_level,
            "blood_glucose_level": self.blood_glucose_level,
            "result": self.result
        }
