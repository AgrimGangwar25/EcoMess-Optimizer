from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app) 

# IMPORTANT: Update your password here!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:agrim2510@localhost:5432/mess_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class DailyLog(db.Model):
    __tablename__ = 'daily_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    menu_item = db.Column(db.String(100), nullable=False)
    
    # New ML Features
    food_category = db.Column(db.String(50), nullable=False) 
    meal_time = db.Column(db.String(20), nullable=False)     
    
    amount_cooked_kg = db.Column(db.Float, nullable=False)
    amount_consumed_kg = db.Column(db.Float, nullable=False)
    food_waste_kg = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'menu_item': self.menu_item,
            'food_category': self.food_category,
            'meal_time': self.meal_time,
            'amount_cooked_kg': self.amount_cooked_kg,
            'amount_consumed_kg': self.amount_consumed_kg,
            'food_waste_kg': self.food_waste_kg
        }

# --- HELPER FUNCTION ---
def auto_categorize_food(food_name):
    """Automatically assigns a category based on food name keywords."""
    name = food_name.lower()
    
    if any(word in name for word in ['rice', 'pulao', 'biryani']):
        return "Rice"
    elif any(word in name for word in ['dal', 'paneer', 'chhole', 'rajma', 'curry', 'gravy', 'kofta']):
        return "Curry/Dal"
    elif any(word in name for word in ['roti', 'naan', 'paratha', 'puri', 'bread']):
        return "Bread/Roti"
    elif any(word in name for word in ['aloo', 'gobhi', 'bhindi', 'mix veg', 'fry', 'dry']):
        return "Dry Veg"
    elif any(word in name for word in ['kheer', 'halwa', 'jamun', 'ice cream', 'sweet']):
        return "Dessert"
    
    return "Other"

# --- API ROUTES ---
@app.route('/logs', methods=['POST'])
def add_log():
    data = request.get_json()
    try:
        cooked = float(data['amount_cooked_kg'])
        consumed = float(data['amount_consumed_kg'])
        waste = round(cooked - consumed, 2)

        # Automatically calculate the category based on the menu item name
        calculated_category = auto_categorize_food(data['menu_item'])

        new_log = DailyLog(
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            menu_item=data['menu_item'],
            food_category=calculated_category,
            meal_time=data['meal_time'],
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