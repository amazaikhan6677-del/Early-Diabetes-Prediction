from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pickle
import numpy as np
import os

app = Flask(__name__)

# ─── Load ML Model ────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'diabetes_model.pkl')
SCALER_PATH = os.path.join(os.path.dirname(__file__), 'model', 'scaler.pkl')

model = None
scaler = None

try:
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    print("✅ ML model loaded successfully.")
except FileNotFoundError:
    print("⚠️  Model files not found. Using rule-based fallback predictor.")


# ─── Rule-Based Fallback (used if model not trained yet) ──────────────────────
def rule_based_predict(data):
    score = 0

    age = int(data.get('age', 0))
    bmi = float(data.get('bmi', 0))
    glucose = int(data.get('glucose', 100))
    bp = int(data.get('blood_pressure', 80))
    insulin = int(data.get('insulin', 80))
    dpf = float(data.get('dpf', 0.5))
    pregnancies = int(data.get('pregnancies', 0))

    # Scoring rules based on clinical thresholds
    if age >= 45: score += 18
    elif age >= 35: score += 10
    elif age >= 25: score += 4

    if bmi >= 30: score += 22
    elif bmi >= 25: score += 12
    elif bmi >= 23: score += 5

    if glucose >= 200: score += 30
    elif glucose >= 140: score += 22
    elif glucose >= 100: score += 10

    if data.get('family_history') == 'yes': score += 15
    if data.get('high_blood_sugar') == 'yes': score += 18
    if data.get('hypertension') == 'yes': score += 8
    if data.get('heart_disease') == 'yes': score += 6
    if data.get('pcos') == 'yes': score += 8

    activity = data.get('activity', 'moderate')
    if activity == 'sedentary': score += 10
    elif activity == 'light': score += 5

    smoking = data.get('smoking', 'never')
    if smoking == 'current': score += 7
    elif smoking == 'former': score += 3

    if insulin > 100: score += 8
    elif insulin > 25: score += 4
    if bp >= 90: score += 7
    elif bp >= 80: score += 3
    if dpf >= 1.5: score += 10
    elif dpf >= 0.8: score += 5
    if pregnancies >= 4: score += 7
    elif pregnancies >= 2: score += 3

    symptoms = ['polyuria', 'polydipsia', 'weight_loss', 'blurred_vision', 'fatigue', 'slow_healing']
    symptom_count = sum(1 for s in symptoms if data.get(s) == 'yes')
    score += symptom_count * 6

    probability = min(97, max(3, score))

    if probability >= 65:
        level = 'high'
    elif probability >= 35:
        level = 'moderate'
    else:
        level = 'low'

    return probability, level


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    return render_template('home.html', date=date_str)


@app.route('/predict')
def index():
    now = datetime.now()
    date_str = now.strftime("%A, %d %B %Y")
    time_str = now.strftime("%I:%M %p")
    return render_template('index.html', date=date_str, time=time_str)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        age = int(data.get('age', 0))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        bmi = round(weight / ((height / 100) ** 2), 1)
        data['bmi'] = bmi

        probability, level = None, None

        # Try ML model first
        if model and scaler:
            try:
                features = np.array([[
                    int(data.get('pregnancies', 0)),
                    int(data.get('glucose', 100)),
                    int(data.get('blood_pressure', 80)),
                    int(data.get('skin_thickness', 20)),
                    int(data.get('insulin', 80)),
                    bmi,
                    float(data.get('dpf', 0.5)),
                    age
                ]])
                features_scaled = scaler.transform(features)
                prob_array = model.predict_proba(features_scaled)[0]
                probability = round(prob_array[1] * 100)
                if probability >= 65: level = 'high'
                elif probability >= 35: level = 'moderate'
                else: level = 'low'
            except Exception as e:
                print(f"Model predict error: {e}")
                probability, level = rule_based_predict(data)
        else:
            probability, level = rule_based_predict(data)

        recommendations = {
            'high': [
                'Schedule a blood glucose (HbA1c) test with your doctor immediately',
                'Reduce sugar, white bread, and processed food intake',
                'Begin daily physical activity — even 30-minute walks help',
                'Monitor blood sugar at home with a glucometer',
                'Consult a registered dietitian for a diabetes meal plan',
                'Discuss medication options with your doctor if needed'
            ],
            'moderate': [
                'Book a routine diabetes screening with your doctor',
                'Reduce sugary drinks, sweets, and refined carbohydrates',
                'Aim for 150 minutes of moderate exercise per week',
                'Maintain or achieve a healthy BMI through diet',
                'Check blood pressure regularly',
                'Get screened annually if risk factors persist'
            ],
            'low': [
                'Continue your healthy lifestyle habits',
                'Get a diabetes screening every 1–3 years after age 35',
                'Stay physically active and eat a balanced diet',
                'Maintain a healthy weight and manage stress levels',
                'Avoid excessive sugar and processed foods'
            ]
        }

        response = {
            'success': True,
            'probability': probability,
            'level': level,
            'bmi': bmi,
            'recommendations': recommendations[level],
            'timestamp': datetime.now().strftime("%d %B %Y, %I:%M %p")
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
