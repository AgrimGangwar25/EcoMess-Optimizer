import pandas as pd
import random
from datetime import datetime, timedelta

# --- CONTEXTUAL KNOWLEDGE BASE ---
menu_pool = [
    {"name": "Jeera Rice", "category": "Rice", "popularity": "High"},
    {"name": "Palak Paneer", "category": "Curry/Dal", "popularity": "High"},
    {"name": "Aloo Gobhi", "category": "Dry Veg", "popularity": "Medium"},
    {"name": "Dal Makhani", "category": "Curry/Dal", "popularity": "High"},
    {"name": "Plain Roti", "category": "Bread/Roti", "popularity": "High"},
    {"name": "Mix Veg", "category": "Dry Veg", "popularity": "Low"},
    {"name": "Gulab Jamun", "category": "Dessert", "popularity": "High"},
    {"name": "Poha", "category": "Other", "popularity": "Medium"} 
]

weather_conditions = ["Clear", "Cloudy", "Light Rain", "Heavy Rain"]
meal_times = ["Breakfast", "Lunch", "Dinner"]

# --- DATA GENERATION LOGIC ---
data = []
start_date = datetime.now() - timedelta(days=1000)

for i in range(1000):
    current_date = start_date + timedelta(days=i)
    day_of_week = current_date.strftime('%A')
    is_weekend = day_of_week in ['Saturday', 'Sunday']
    weather = random.choice(weather_conditions)
    
    # Simulate 1 to 3 meals logged per day
    for _ in range(random.randint(1, 3)):
        meal = random.choice(menu_pool)
        meal_time = random.choice(meal_times)
        
        # Base amount cooked (Assuming a mess built for ~500 students)
        amount_cooked = random.uniform(40.0, 60.0)
        
        # Base consumption rate (70% to 95% is usually eaten)
        consumption_factor = random.uniform(0.70, 0.95) 
        
        # --- FEATURE ENGINEERING (The Real-World Variables) ---
        if is_weekend:
            consumption_factor -= 0.15 # Students go out on weekends
        if weather == "Heavy Rain":
            consumption_factor -= 0.10 # Students skip the mess
        if meal["popularity"] == "Low":
            consumption_factor -= 0.10 # Unpopular items get left behind
            
        # Ensure the factor stays realistic (between 10% and 98%)
        consumption_factor = max(0.10, min(consumption_factor, 0.98))
        
        amount_consumed = amount_cooked * consumption_factor
        food_waste = amount_cooked - amount_consumed
        
        # Append to our dataset
        data.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "day_of_week": day_of_week,
            "weather": weather,
            "menu_item": meal["name"],
            "food_category": meal["category"],
            "meal_time": meal_time,
            "amount_cooked_kg": round(amount_cooked, 2),
            "amount_consumed_kg": round(amount_consumed, 2),
            "food_waste_kg": round(food_waste, 2)
        })

# --- EXPORT TO CSV ---
df = pd.DataFrame(data)
df.to_csv('mess_historical_data.csv', index=False)
print(f"Successfully generated {len(df)} realistic logs!")
print("Saved to: mess_historical_data.csv")