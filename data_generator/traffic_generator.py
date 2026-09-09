import json
import random
import time
from datetime import datetime

locations = [
    "Sydney_CBD",
    "Central_Station",
    "Mascot",
    "Parramatta",
    "Chatswood"
]

while True:
    vehicle_count = random.randint(10, 150)
    average_speed = round(random.uniform(10, 70), 2)

    if average_speed < 25:
        congestion = "High"
    elif average_speed < 45:
        congestion = "Medium"
    else:
        congestion = "Low"

    data = {
        "timestamp": datetime.now().isoformat(),
        "sensor_id": f"T{random.randint(1, 10):03}",
        "location": random.choice(locations),
        "vehicle_count": vehicle_count,
        "average_speed": average_speed,
        "congestion_level": congestion
    }

    print(json.dumps(data))

    time.sleep(1)