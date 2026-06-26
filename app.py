from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # <-- NEW: Import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # <-- NEW: Enable CORS for all routes

# TODO: Replace with your actual PostgreSQL credentials
# Format: postgresql://username:password@localhost:5432/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:agrim2510@localhost:5432/mess_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    menu_item = db.Column(db.String(100), nullable=False)
    portions_cooked = db.Column(db.Integer, nullable=False)
    food_waste_kg = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'menu_item': self.menu_item,
            'portions_cooked': self.portions_cooked,
            'food_waste_kg': self.food_waste_kg
        }

# --- API ROUTES ---

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Mess Tracker API is running!"})

@app.route('/logs', methods=['POST'])
def add_log():
    """Endpoint to submit a new daily waste log"""
    data = request.get_json()
    
    try:
        new_log = DailyLog(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            menu_item=data['menu_item'],
            portions_cooked=data['portions_cooked'],
            food_waste_kg=data['food_waste_kg']
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Log added successfully!", "log": new_log.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/logs', methods=['GET'])
def get_logs():
    """Endpoint to retrieve all historical logs"""
    logs = DailyLog.query.order_by(DailyLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

# --- INITIALIZATION ---
if __name__ == '__main__':
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, port=5000)