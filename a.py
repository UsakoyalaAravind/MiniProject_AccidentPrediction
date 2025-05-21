from flask import Flask, request, jsonify, render_template
import requests
import joblib
import datetime

app = Flask(__name__)

# Load the trained model
model = joblib.load("risk_prediction_model.pkl")

# API Keys
WEATHER_API_KEY = "654bf9399b4c40a3ada173749251904"
TOMTOM_API_KEY = "vRq15wX2KxQydk3VoPOIEgCtT8rCRC7R"

# Traffic Density Mapping
traffic_density = {
    'Low': 0,
    'Medium': 1,
    'High': 2
}

# Function to map traffic speed to density
def map_traffic_density(currentSpeed, freeFlowSpeed):
    congestion_ratio = currentSpeed / freeFlowSpeed
    if congestion_ratio < 0.5:
        return traffic_density['Low']
    elif congestion_ratio < 1.5:
        return traffic_density['Medium']
    else:
        return traffic_density['High']

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    vehicle = data.get("vehicle")
    road_type = data.get("road_type")
    road_condition = data.get("road_condition")

    # --- Fetch weather ---
    weather_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={lat},{lon}"
    weather_data = requests.get(weather_url).json()
    weather = weather_data['current']['condition']['text']

    # --- Fetch traffic ---
    traffic_url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat}%2C{lon}&key={TOMTOM_API_KEY}"
    traffic_data = requests.get(traffic_url).json()
    
    try:
        current_speed = traffic_data['flowSegmentData']['currentSpeed']
        free_flow_speed = traffic_data['flowSegmentData']['freeFlowSpeed']
        traffic_density_value = map_traffic_density(current_speed, free_flow_speed)
    except:
        traffic_density_value = 0  # Default to Low if data is unavailable

    # --- Encode vehicle ---
    vehicle_map = {"car": 2, "bike": 1, "truck": 5, "Auto": 3, "Bus": 4}
    vehicle_code = vehicle_map.get(vehicle, 1)

    now = datetime.datetime.now()
    hour = now.hour
    day_of_week = now.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0

    # --- Construct feature vector ---
    # Format: [weather, road_type, road_condition, vehicle_type, traffic_density, road_condition, hour, day_of_week, is_weekend]
    features = [[map_weather(weather), road_type, traffic_density_value, vehicle_code, 0, road_condition, hour, day_of_week, is_weekend]]

    prediction = model.predict(features)[0]
    return jsonify({"risk_level": int(prediction)})

def map_weather(desc):
    desc = desc.lower()
    if "rain" in desc or "storm" in desc or "Drizzle" in desc:
        return 4
    elif "cloud" in desc or "haze" in desc:
        return 1
    elif "Fog" in desc or "Mist" in desc:
        return 2
    else:
        return 0

if __name__ == "__main__":
    app.run(debug=True)
