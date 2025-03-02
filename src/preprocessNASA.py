import os
import numpy as np
import scipy.io as sio
import pandas as pd
from tqdm import tqdm

# Define paths
DATASET_PATH = "../data/NASA/"
OUTPUT_PATH = "../data/NASA/preprocessed/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Define capacity thresholds for RUL calculation
CAPACITY_THRESHOLDS = {
    "default": 1.38,  # 70% of nominal capacity
    "B0033-B0036": 1.6,  # 20% fade
    "B0041-B0044": 1.4  # 30% fade
}
NASA_CAPACITY_NOMINAL = 2.0  # Ah (approximate value for NASA batteries)

# Function to determine remaining useful life (RUL)
def compute_rul(capacity_series, threshold):
    rul = []
    for i, cap in enumerate(capacity_series):
        future_cycles = np.where(capacity_series[i:] <= threshold)[0]
        rul.append(future_cycles[0] if len(future_cycles) > 0 else 0)
    return np.array(rul)

# Function to process a single battery dataset
def process_battery(file_path, battery_id):
    print(f"Processing {battery_id}...")
    
    # Load .mat file
    mat_data = sio.loadmat(file_path)
    
    # Extract cycle data
    battery_data = mat_data[battery_id][0, 0]
    cycles = battery_data["cycle"]
    print(cycles)
    
    # Initialize lists for extracted data
    cycle_nums, voltages, currents, temperatures, capacities, soh_values = [], [], [], [], [], []
    
    # Iterate over all cycles
    for cycle in tqdm(cycles):
        cycle_type = cycle["type"][0] if isinstance(cycle["type"], np.ndarray) else cycle["type"]
        
        # Only process discharge cycles
        if cycle_type != "discharge":
            continue
        
        cycle_num = cycle[0][0]
        voltage = cycle["data"]["Voltage_measured"].flatten()
        current = cycle["data"]["Current_measured"].flatten()
        temperature = cycle["data"]["Temperature_measured"].flatten()
        
        # Extract discharge capacity
        try:
            capacity = cycle["data"]["Capacity"][0][0][0][0]
        except (KeyError, IndexError):
            continue  # Skip if capacity extraction fails
        
        cycle_nums.append(cycle_num)
        voltages.append(np.mean(voltage))  # Store mean voltage per cycle
        currents.append(np.mean(current))  # Store mean current per cycle
        temperatures.append(np.mean(temperature))  # Store mean temperature per cycle
        capacities.append(capacity)
        soh_values.append((capacity / capacities[0]) * 100)  # SoH in %
    
    # Convert to DataFrame
    df = pd.DataFrame({
        "Cycle": cycle_nums,
        "Voltage": voltages,
        "Current": currents,
        "Temperature": temperatures,
        "Capacity": capacities,
        "Normalized_Capacity": [cap / NASA_CAPACITY_NOMINAL for cap in capacities],
        "SoH": soh_values
    })
    
    # Determine capacity threshold based on battery ID
    threshold = CAPACITY_THRESHOLDS.get("default")
    if any(battery_id.startswith(x) for x in ["B0033", "B0034", "B0035", "B0036"]):
        threshold = CAPACITY_THRESHOLDS["B0033-B0036"]
    elif any(battery_id.startswith(x) for x in ["B0041", "B0042", "B0043", "B0044"]):
        threshold = CAPACITY_THRESHOLDS["B0041-B0044"]
    
    # Compute RUL
    df["RUL"] = compute_rul(df["Capacity"].values, threshold)
    
    # Add metadata columns
    df["Source"] = "NASA"
    df["Battery_ID"] = battery_id
    
    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, f"{battery_id}_processed.csv")
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Process all batteries
if __name__ == "__main__":
    battery_files = [f for f in os.listdir(DATASET_PATH) if f.endswith(".mat")]
    print(battery_files)
    for battery_file in battery_files:
        battery_id = battery_file.split(".")[0]  # Extract battery ID from filename
        process_battery(os.path.join(DATASET_PATH, battery_file), battery_id)

    print("NASA dataset preprocessing complete!")
