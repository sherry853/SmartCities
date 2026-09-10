import json
import random
import time
from datetime import datetime

while True:

    pm25 = round(random.uniform(5, 80), 2)
    pm10 = round(random.uniform(10, 120), 2)
    no2 = round(random.uniform(5, 100), 2)

    if pm25 > 50:
        aqi = "Poor"
    elif pm25 > 25:
        aqi = "Moderate"
    else:
        aqi = "Good"

    data = {
        "timestamp": datetime.now().isoformat(),
        "location": random.choice([
            "Sydney_CBD",
            "Mascot",
            "Parramatta",
            "Chatswood"
        ]),
        "pm25": pm25,
        "pm10": pm10,
        "no2": no2,
        "air_quality": aqi
    }

    print(json.dumps(data))

    time.sleep(3)