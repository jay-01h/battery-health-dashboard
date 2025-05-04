import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define number of rows and battery packs
n_rows = 10000
num_packs = 3
rows_per_pack = n_rows // num_packs
start_time = datetime(2024, 1, 1, 0, 0, 0)

# List of battery IDs
battery_ids = [f"Pack-{i:02d}" for i in range(1, num_packs + 1)]

# Generate dataset for each battery pack
dfs = []
for pack_id in battery_ids:
    data = {
        "Time Stamp": [start_time + timedelta(minutes=30 * i) for i in range(rows_per_pack)],
        "Step": np.random.choice([1, 2, 3], size=rows_per_pack),
        "Status": np.random.choice(["Charging", "Rest", "Discharging"], size=rows_per_pack),
        "Prog Time": ["00:{:02d}:00".format(np.random.randint(10, 60)) for _ in range(rows_per_pack)],
        "Step Time": ["00:{:02d}:00".format(np.random.randint(10, 60)) for _ in range(rows_per_pack)],
        "Cycle": np.random.randint(1, 1000, size=rows_per_pack),
        "Cycle Level": np.random.choice(["Low", "Medium", "High"], size=rows_per_pack),
        "Procedure": np.random.choice(["CC-CV", "Rest", "CC"], size=rows_per_pack),
        "Voltage": np.round(np.random.uniform(3.5, 4.2, size=rows_per_pack), 2),
        "Current": np.round(np.random.uniform(-2.0, 2.0, size=rows_per_pack), 2),
        "Temperature": np.round(np.random.uniform(20.0, 45.0, size=rows_per_pack), 1),
        "Capacity": np.round(np.random.uniform(0.5, 2.5, size=rows_per_pack), 3),
        "WhAccu": np.round(np.random.uniform(1.0, 10.0, size=rows_per_pack), 2),
        "Cnt": np.arange(1, rows_per_pack + 1),
        "battery_id": [pack_id] * rows_per_pack
    }
    dfs.append(pd.DataFrame(data))

# Concatenate all battery dataframes and save to CSV
df_all = pd.concat(dfs, ignore_index=True)
df_all.to_csv("battery_data.csv", index=False)
print("✅ 'battery_data.csv' regenerated with multiple battery packs:", battery_ids)
