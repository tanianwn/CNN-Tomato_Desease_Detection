from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from collections import Counter
from predict import predict_image
from datetime import datetime
from sqlalchemy import func
import pytz

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    image_path = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['image']
    result = predict_image(file.read())

    mexico_tz = pytz.timezone("America/Mexico_City")
    now_mexico = datetime.now(mexico_tz).replace(tzinfo=None)

    prediction = Prediction(
        label=result['label'],
        confidence=result['confidence'],
        timestamp=now_mexico
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify(result)

@app.route('/history', methods=['GET'])
def get_history():
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(10).all()
    result = [{
        'label': p.label,
        'confidence': p.confidence,
        'timestamp': p.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for p in predictions]
    return jsonify(result)

@app.route('/class_distribution', methods=['GET'])
def class_distribution():
    predictions = Prediction.query.with_entities(
        func.date(Prediction.timestamp).label('date'),
        Prediction.label
    ).all()

    distribution = {}
    for prediction in predictions:
        date = prediction.date
        label = prediction.label

        if date not in distribution:
            distribution[date] = {'Healthy': 0, 'Sick': 0}

        if label == 'Healthy':
            distribution[date]['Healthy'] += 1
        else:
            distribution[date]['Sick'] += 1

    daily_percentages = []
    for date, counts in distribution.items():
        total = counts['Healthy'] + counts['Sick']
        healthy_percent = (counts['Healthy'] / total) * 100 if total else 0
        sick_percent = (counts['Sick'] / total) * 100 if total else 0

        daily_percentages.append({
            'date': date,
            'healthy_percent': healthy_percent,
            'sick_percent': sick_percent
        })

    return jsonify(daily_percentages)

@app.route('/class_distribution_counts', methods=['GET'])
def class_distribution_counts():
    predictions = Prediction.query.all()
    labels = [p.label for p in predictions]
    class_counts = dict(Counter(labels))
    return jsonify(class_counts)

if __name__ == '__main__':
    app.run(debug=True)
