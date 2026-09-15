import csv
import random
from datetime import datetime, timedelta

# Output file
filename = "historical_traffic.csv"

# Locations
locations = [
    "Sydney_CBD",
    "Central_Station",
    "Mascot",
    "Parramatta",
    "Chatswood"
]

# Number of historical records
number_of_records = 1000

# Starting date
start_date = datetime(2026, 8, 1, 0, 0, 0)

# Create CSV file
with open(filename, "w", newline="") as file:

    writer = csv.writer(file)

    # CSV column headings
    writer.writerow([
        "timestamp",
        "sensor_id",
        "location",
        "vehicle_count",
        "average_speed",
        "congestion_level"
    ])

    # Generate historical records
    for i in range(number_of_records):

        timestamp = start_date + timedelta(minutes=i * 5)

        vehicle_count = random.randint(10, 150)

        average_speed = round(random.uniform(10, 70), 2)

        if average_speed < 25:
            congestion = "High"
        elif average_speed < 45:
            congestion = "Medium"
        else:
            congestion = "Low"

        writer.writerow([
            timestamp.isoformat(),
            f"T{random.randint(1, 10):03}",
            random.choice(locations),
            vehicle_count,
            average_speed,
            congestion
        ])

print(f"Historical data created successfully: {filename}")
print(f"Total records: {number_of_records}")