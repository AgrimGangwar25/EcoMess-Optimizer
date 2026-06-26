from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) 

# Replace 'your_password' with your actual Postgres password
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:agrim2510@localhost:5432/mess_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    menu_item = db.Column(db.String(100), nullable=False)
    amount_cooked_kg = db.Column(db.Float, nullable=False)
    amount_consumed_kg = db.Column(db.Float, nullable=False)
    food_waste_kg = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'menu_item': self.menu_item,
            'amount_cooked_kg': self.amount_cooked_kg,
            'amount_consumed_kg': self.amount_consumed_kg,
            'food_waste_kg': self.food_waste_kg
        }

# API Routes
@app.route('/logs', methods=['POST'])
def add_log():
    data = request.get_json()
    try:
        cooked = float(data['amount_cooked_kg'])
        consumed = float(data['amount_consumed_kg'])
        waste = round(cooked - consumed, 2)

        new_log = DailyLog(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            menu_item=data['menu_item'],
            amount_cooked_kg=cooked,
            amount_consumed_kg=consumed,
            food_waste_kg=waste
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"message": "Log added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = DailyLog.query.order_by(DailyLog.date.desc()).all()
    return jsonify([log.to_dict() for log in logs]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)