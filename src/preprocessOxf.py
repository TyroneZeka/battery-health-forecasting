import os
import numpy as np
import scipy.io as sio
import pandas as pd
from tqdm import tqdm

# Define paths
DATASET_PATH = "../data/Oxford/"
OUTPUT_PATH = "../data/preprocessed/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Oxford capacity threshold for failure (80% of initial capacity)
INITIAL_CAPACITY = 0.740  # Ah
FAILURE_THRESHOLD = 0.592  # Ah (80% SoH)

# Function to determine remaining useful life (RUL)
def compute_rul(capacity_series, threshold):
    rul = []
    for i, cap in enumerate(capacity_series):
        future_cycles = np.where(capacity_series[i:] <= threshold)[0]
        rul.append(future_cycles[0] if len(future_cycles) > 0 else 0)
    return np.array(rul)

# Function to process a single cell dataset
def process_cell(file_path, cell_id):
    print(f"Processing {cell_id}...")
    
    # Load .mat file
    mat_data = sio.loadmat(file_path)
    
    # Extract cycle data
    cell_data = mat_data[cell_id]
    print(cell_data)
    
    # Initialize lists for extracted data
    cycle_nums, voltages, currents, temperatures, capacities, soh_values = [], [], [], [], [], []
        
    # Iterate over all cycles
    for cycle_key in tqdm(cell_data.keys()):
        if not cycle_key.startswith("cyc"):
            continue  # Skip non-cycle keys
        
        cycle_num = int(cycle_key.replace("cyc", ""))
        cycle_data = cell_data[cycle_key][0, 0]
        
        # Extract data fields
        voltage = cycle_data["v"].flatten()
        current = cycle_data["C1dc"].flatten()  # Discharge current
        temperature = cycle_data["T"].flatten()
        capacity = cycle_data["q"].flatten()[-1]  # Last capacity value
        
        cycle_nums.append(cycle_num)
        voltages.append(np.mean(voltage))  # Store mean voltage per cycle
        currents.append(-np.mean(current))  # Current should be negative for discharge
        temperatures.append(np.mean(temperature))
        capacities.append(capacity)
        soh_values.append((capacity / INITIAL_CAPACITY) * 100)  # SoH in %
    
    # Convert to DataFrame
    df = pd.DataFrame({
        "Cycle": cycle_nums,
        "Voltage": voltages,
        "Current": currents,
        "Temperature": temperatures,
        "Capacity": capacities,
        "Normalized_Capacity": [cap / INITIAL_CAPACITY for cap in capacities],
        "SoH": soh_values
    })
    
    # Compute RUL
    df["RUL"] = compute_rul(df["Capacity"].values, FAILURE_THRESHOLD)
    
    # Add metadata columns
    df["Source"] = "Oxford"
    df["Battery_ID"] = cell_id
    
    # Save to CSV
    output_file = os.path.join(OUTPUT_PATH, f"{cell_id}_processed.csv")
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Process all cells
cell_files = [f for f in os.listdir(DATASET_PATH) if f.endswith(".mat")]
for cell_file in cell_files:
    cell_id = cell_file.split(".")[0]  # Extract cell ID from filename
    process_cell(os.path.join(DATASET_PATH, cell_file), cell_id)

print("Oxford dataset preprocessing complete!")
