import json
import random
import time
from datetime import datetime

routes = ["B1", "B2", "B3", "T1", "T2"]

while True:
    data = {
        "timestamp": datetime.now().isoformat(),
        "vehicle_id": f"BUS{random.randint(1, 30):03}",
        "route_id": random.choice(routes),
        "passenger_count": random.randint(5, 100),
        "delay_minutes": random.randint(0, 20),
        "location": random.choice([
            "Sydney_CBD",
            "Central_Station",
            "Mascot",
            "Parramatta"
        ])
    }

    print(json.dumps(data))

    time.sleep(2)