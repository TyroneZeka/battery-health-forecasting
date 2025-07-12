import os
import scipy.io
import pandas as pd
import matplotlib.pyplot as plt

from typing import List, Dict

def load_all_nasa_batteries(data_dir: str) -> Dict[str, List[Dict]]:
    """Load all NASA battery .mat files in the directory."""
    battery_data = {}
    for file in os.listdir(data_dir):
        if file.endswith('.mat') and file.startswith('B'):
            file_path = os.path.join(data_dir, file)
            battery_name = file.split('.')[0]
            mat_data = scipy.io.loadmat(file_path)
            try:
                battery_data[battery_name] = mat_data[battery_name][0][0][0]
            except KeyError:
                print(f"Warning: Could not find expected key for {battery_name}")
    return battery_data

def extract_cycle_data(battery_name: str, cycle_data: List[Dict]) -> pd.DataFrame:
    """Extract relevant data from cycles."""
    records = []

    for i, cycle in enumerate(cycle_data):
        cycle_type = cycle['type'][0]
        ambient_temp = cycle['ambient_temperature'][0][0]
        data = cycle['data'][0, 0]

        if cycle_type == 'discharge':
            time = data['Time'][0]
            voltage = data['Voltage_measured'][0]
            current = data['Current_measured'][0]
            temperature = data['Temperature_measured'][0]
            capacity = data['Capacity'][0][0]

            for j in range(len(time)):
                records.append({
                    'battery': battery_name,
                    'cycle': i,
                    'time': time[j],
                    'voltage': voltage[j],
                    'current': current[j],
                    'temperature': temperature[j],
                    'capacity': capacity,
                    'ambient_temperature': ambient_temp
                })

    return pd.DataFrame(records)

def plot_capacity_trend(df: pd.DataFrame, batteries_to_plot: List[str]):
    """Plot capacity vs. cycle number for selected batteries."""
    plt.figure(figsize=(10, 6))
    for battery in batteries_to_plot:
        battery_df = df[df['battery'] == battery]
        capacity_by_cycle = battery_df.groupby('cycle').first().reset_index()
        plt.plot(capacity_by_cycle['cycle'], capacity_by_cycle['capacity'], marker='o', label=battery)

    plt.title('Battery Capacity Degradation over Cycles')
    plt.xlabel('Cycle')
    plt.ylabel('Capacity (Ah)')
    plt.legend()
    plt.grid(True)
    plt.show()

def save_preprocessed_data(df: pd.DataFrame, output_path: str):
    """Save preprocessed data to a CSV file."""
    df.to_csv(output_path, index=False)

def main():
    raw_data_dir = 'data/raw/NASA'
    output_path = 'data/processed/nasa_all_batteries_processed.csv'

    print("Loading all NASA battery data...")
    all_battery_data = load_all_nasa_batteries(raw_data_dir)

    all_records = []
    for battery_name, cycles in all_battery_data.items():
        print(f"Processing {battery_name}...")
        battery_df = extract_cycle_data(battery_name, cycles)
        all_records.append(battery_df)

    full_df = pd.concat(all_records, ignore_index=True)

    print("Saving cleaned data...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_preprocessed_data(full_df, output_path)

    print("Visualizing feature trends for selected batteries...")
    selected_batteries = ['B0005', 'B0006', 'B0018']
    plot_capacity_trend(full_df, selected_batteries)

if __name__ == '__main__':
    main()
