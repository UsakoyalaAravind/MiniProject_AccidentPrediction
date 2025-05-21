import requests
from geopy.distance import geodesic  # To measure distances between coordinates

# Your location
lat = 17.5185
lon = 78.3852

# Step 1: Query nearby roads
query = f"""
[out:json];
way(around:100,{lat},{lon})["highway"];
out center tags;
"""
url = "https://overpass-api.de/api/interpreter"
res = requests.post(url, data=query)
data = res.json()

# Step 2: Find the closest road
closest = None
min_dist = float('inf')

for element in data['elements']:
    center = element.get("center")
    tags = element.get("tags", {})
    if center:
        dist = geodesic((lat, lon), (center['lat'], center['lon'])).meters
        if dist < min_dist:
            min_dist = dist
            closest = {
                "name": tags.get("name", "Unnamed"),
                "type": tags.get("highway", "Unknown"),
                "distance": dist
            }

# Step 3: Print the closest road info
if closest:
    print(f"📍 Closest Road to You ({min_dist:.1f}m away):")
    print(f"➡️ Name: {closest['name']}")
    print(f"🛣️ Type: {closest['type']}")
else:
    print("❌ No nearby road found.")
