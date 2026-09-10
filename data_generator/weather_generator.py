import json
import random
import time
from datetime import datetime

while True:

    data = {
        "timestamp": datetime.now().isoformat(),
        "location": random.choice([
            "Sydney_CBD",
            "Mascot",
            "Parramatta",
            "Chatswood"
        ]),
        "temperature": round(random.uniform(10, 35), 2),
        "humidity": round(random.uniform(40, 90), 2),
        "rainfall": round(random.uniform(0, 20), 2),
        "wind_speed": round(random.uniform(0, 40), 2)
    }

    print(json.dumps(data))

    time.sleep(5)