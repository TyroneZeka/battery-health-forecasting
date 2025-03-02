import os
import pandas as pd

# Define paths
NASA_PATH = "../data/NASA/preprocessed/"
OXFORD_PATH = "../data/Oxford/preprocessed/"
MERGED_OUTPUT_PATH = "../data/preprocessed/merged_dataset.csv"

# Load preprocessed NASA dataset
nasa_files = [f for f in os.listdir(NASA_PATH) if f.endswith(".csv")]
nasa_dfs = []
for file in nasa_files:
    df = pd.read_csv(os.path.join(NASA_PATH, file))
    df["Source"] = "NASA"
    df["Battery_ID"] = file.split("_")[0]  # Extract battery ID from filename
    nasa_dfs.append(df)
nasa_df = pd.concat(nasa_dfs, ignore_index=True)

# Load preprocessed Oxford dataset
oxford_files = [f for f in os.listdir(OXFORD_PATH) if f.endswith(".csv")]
oxford_dfs = []
for file in oxford_files:
    df = pd.read_csv(os.path.join(OXFORD_PATH, file))
    df["Source"] = "Oxford"
    df["Battery_ID"] = file.split("_")[0]  # Extract cell ID from filename
    oxford_dfs.append(df)
oxford_df = pd.concat(oxford_dfs, ignore_index=True)

# Align Columns (Ensure both datasets have the same format)
common_columns = ["Cycle", "Voltage", "Current", "Temperature", "Normalized_Capacity", "SoH", "RUL", "Source", "Battery_ID"]
nasa_df = nasa_df[common_columns]
oxford_df = oxford_df[common_columns]

# Merge the datasets
merged_df = pd.concat([nasa_df, oxford_df], ignore_index=True)

# Save merged dataset
merged_df.to_csv(MERGED_OUTPUT_PATH, index=False)
print(f"Merged dataset saved to {MERGED_OUTPUT_PATH}")
