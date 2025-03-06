import os
import numpy as np
import pandas as pd
import scipy.io as sio
from tqdm import tqdm

# Define paths
INPUT_FOLDER = './data/NASA/'
OUTPUT_FOLDER = os.path.join(INPUT_FOLDER, 'preprocessed')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Define RUL capacity thresholds
RUL_THRESHOLDS = {
    "default": 1.38,  # B0005-B0032
    "high_capacity": 1.6,  # B0033-B0040
    "mid_capacity": 1.4   # B0041-B0044
}

def compute_rul(capacities, threshold):
    """Compute RUL by tracking future capacity drops."""
    rul = np.full(len(capacities), np.nan)  # Initialize with NaNs
    capacities = np.array(capacities)
    
    # Iterate in reverse to track future capacity thresholds
    for i in range(len(capacities) - 1, -1, -1):
        future_cycles = np.where(capacities[i:] <= threshold)[0]
        rul[i] = future_cycles[0] + 1 if future_cycles.size > 0 else len(capacities) - i  # Ensure non-zero RUL
    
    return list(rul)

def process_battery(file_path, battery_id):
    print(f"\nProcessing {battery_id}...")

    try:
        mat_data = sio.loadmat(file_path)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

    # Extract cycle data
    if battery_id not in mat_data:
        print(f"Warning: No {battery_id} key in {file_path}")
        return None

    battery_data = mat_data[battery_id]
    if battery_data.size == 0 or len(battery_data.shape) < 2:
        print(f"Warning: Invalid structure for {battery_id}")
        return None

    cycle_field = battery_data[0, 0]["cycle"]
    cycle_data = cycle_field[0] if cycle_field.size > 0 else np.array([])

    if cycle_data.size == 0:
        print(f"Warning: No cycle data for {battery_id}")
        return None

    # Process discharge cycles
    all_data = []
    capacities = []

    print(f"Total cycles found: {len(cycle_data)}")
    for cycle_idx, cycle in enumerate(tqdm(cycle_data, desc=f"Processing {battery_id}")):
        if "type" not in cycle.dtype.names or cycle["type"][0] != "discharge":
            continue

        data = cycle["data"]
        try:
            # Extract scalar values for Voltage, Current, Temperature
            voltage = np.mean(np.array(data["Voltage_measured"]).astype(np.float64).flatten()) if data["Voltage_measured"].size > 0 else np.nan
            current = -np.mean(np.array(data["Current_measured"]).astype(np.float64).flatten()) if data["Current_measured"].size > 0 else np.nan
            temp = np.mean(np.array(data["Temperature_measured"]).astype(np.float64).flatten()) if data["Temperature_measured"].size > 0 else np.nan

            # Extract capacity
            capacity = float(data["Capacity"][0, 0]) if "Capacity" in data.dtype.names and data["Capacity"].size > 0 else np.nan
            if np.isnan(capacity) or capacity < 0 or capacity > 5:  
                capacity = np.nan

            capacities.append(capacity)

            all_data.append([cycle_idx + 1, voltage, current, temp, capacity, "NASA"])
        except Exception as e:
            all_data.append([cycle_idx + 1, np.nan, np.nan, np.nan, np.nan, "NASA"])

    # Compute RUL AFTER collecting all capacities
    valid_capacities = [c if not np.isnan(c) else 0 for c in capacities]
    threshold = RUL_THRESHOLDS.get("default")
    if battery_id in {"B0033", "B0034", "B0035", "B0036", "B0038", "B0039", "B0040"}:
        threshold = RUL_THRESHOLDS["high_capacity"]
    elif battery_id in {"B0041", "B0042", "B0043", "B0044"}:
        threshold = RUL_THRESHOLDS["mid_capacity"]

    rul_values = compute_rul(valid_capacities, threshold)

    # Add RUL to the dataset
    for i in range(len(all_data)):
        all_data[i].append(rul_values[i])

    # Save DataFrame
    df = pd.DataFrame(all_data, columns=["Cycle", "Voltage (V)", "Current (A)", "Temperature (°C)", "Capacity (Ah)", "Source", "RUL (Cycles)"])
    
    output_path = os.path.join(OUTPUT_FOLDER, f"{battery_id}_processed.csv")
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to {output_path}")
    return df
