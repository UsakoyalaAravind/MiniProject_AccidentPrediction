from flask import Flask, request, jsonify, render_template
import requests
import joblib
import datetime
from geopy.distance import geodesic

app = Flask(__name__)

# Load the trained model
model = joblib.load("risk_prediction_model.pkl")

# API Keys
WEATHER_API_KEY = "a9ac81e5ed5c4357a66174957251905"
TOMTOM_API_KEY = "vRq15wX2KxQydk3VoPOIEgCtT8rCRC7R"

# Traffic Density Mapping

traffic_density = {
    'Low': 0,
    'Medium': 1,
    'High': 2
}

# Vehicle Type Mapping
vehicle_map = {
    "car": 2,
    "bike": 1,
    "truck": 5,
    "Auto": 3,
    "Bus": 4
}

# Road Type Mapping (OSM → Model)
road_type_map = {
    # Urban Roads
    "residential": 0,
    "service": 0,
    "living_street": 0,
    "unclassified": 0,
    "tertiary": 0,
    "road": 0,

    # Rural Roads
    "track": 1,
    "path": 1,
    "cycleway": 1,
    "footway": 1,

    # Expressways
    "motorway": 2,
    "motorway_link": 2,

    # Highways
    "primary": 3,
    "secondary": 3,
    "trunk": 3,
    "trunk_link": 3,
    "primary_link": 3,
    "secondary_link": 3
}


def map_weather(desc):
    desc = desc.lower()
    if "rain" in desc or "storm" in desc or "drizzle" in desc:
        return 4
    elif "cloud" in desc or "haze" in desc:
        return 1
    elif "fog" in desc or "mist" in desc:
        return 2
    else:
        return 0


def map_traffic_density(currentSpeed, freeFlowSpeed):
    congestion_ratio = currentSpeed / freeFlowSpeed
    if congestion_ratio < 0.5:
        return traffic_density['Low']
    elif congestion_ratio < 1.5:
        return traffic_density['Medium']
    else:
        return traffic_density['High']


def get_road_type(lat, lon):
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way(around:100,{lat},{lon})["highway"];
    out center tags;
    """
    try:
        res = requests.post(overpass_url, data=query)
        data = res.json()

        closest_type = None
        min_dist = float('inf')

        for el in data.get("elements", []):
            tags = el.get("tags", {})
            rtype = tags.get("highway")
            center = el.get("center")

            if rtype and center:
                dist = geodesic((lat, lon), (center["lat"], center["lon"])).meters
                if dist < min_dist:
                    min_dist = dist
                    closest_type = rtype

        return road_type_map.get(closest_type, 0)  # Default to Urban (0) if unknown
    except:
        return 0  # Fallback to Urban


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    vehicle = data.get("vehicle")
    road_condition = int(data.get("road_condition"))

    # --- Weather ---
    try:
        weather_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={lat},{lon}"
        weather_data = requests.get(weather_url).json()
        weather = weather_data['current']['condition']['text']
        weather_code = map_weather(weather)
        print(weather_code)
    except:
        weather_code = 0  # Default: Clear

    # --- Traffic ---
    try:
        traffic_url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={TOMTOM_API_KEY}"
        traffic_data = requests.get(traffic_url).json()
        current_speed = traffic_data['flowSegmentData']['currentSpeed']
        free_flow_speed = traffic_data['flowSegmentData']['freeFlowSpeed']
        traffic_density_value = map_traffic_density(current_speed, free_flow_speed)
    except:
        traffic_density_value = 0  # Default: Low

    # --- Vehicle ---
    vehicle_code = vehicle_map.get(vehicle, 1)

    # --- Auto-detected Road Type ---
    road_type = get_road_type(lat, lon)

    # --- Time Info ---
    now = datetime.datetime.now()
    hour = now.hour
    day_of_week = now.weekday()
    is_weekend = 1 if day_of_week >= 5 else 0

    # --- Feature Vector ---
    features = [[
        # weather_code,
        0,
        road_type,
        traffic_density_value,
        vehicle_code,
        0,  # Placeholder (keep as-is)
        road_condition,
        hour,
        day_of_week,
        is_weekend
    ]]
    print(features)
    prediction = model.predict(features)[0]
    print(prediction)
    print(features)
    return jsonify({"risk_level": int(prediction)})


if __name__ == "__main__":
    app.run(debug=True)
