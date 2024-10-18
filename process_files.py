import pandas as pd
import numpy as np
import argparse
import os

# Set up argument parser
parser = argparse.ArgumentParser(description='Process Lateral and RAW CSV files.')
parser.add_argument('--lateral_file', type=str, help='Path to the Lateral CSV file')
parser.add_argument('--raw_file', type=str, help='Path to the RAW CSV file')
parser.add_argument('--output_file', type=str, help='Path to save the output CSV file')
args = parser.parse_args()

# Function to list CSV files in a directory
def list_csv_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Interactive input if paths are not provided as arguments
if not args.lateral_file:
    lateral_dir = input("Please enter the path to the Lateral CSV directory: ")
    lateral_files = list_csv_files(lateral_dir)
    if not lateral_files:
        raise FileNotFoundError(f"No CSV files found in the directory: {lateral_dir}")
    print("Available Lateral CSV files:")
    for i, file in enumerate(lateral_files):
        print(f"{i+1}. {file}")
    file_choice = int(input("Select the Lateral CSV file by number: ")) - 1
    args.lateral_file = os.path.join(lateral_dir, lateral_files[file_choice])

if not args.raw_file:
    raw_dir = input("Please enter the path to the RAW CSV directory: ")
    raw_files = list_csv_files(raw_dir)
    if not raw_files:
        raise FileNotFoundError(f"No CSV files found in the directory: {raw_dir}")
    print("Available RAW CSV files:")
    for i, file in enumerate(raw_files):
        print(f"{i+1}. {file}")
    file_choice = int(input("Select the RAW CSV file by number: ")) - 1
    args.raw_file = os.path.join(raw_dir, raw_files[file_choice])
if not args.output_file:
    args.output_file = input("Please enter the path to save the output CSV file: ")

# Print the file paths to ensure they are correct
print(f"Lateral file: {args.lateral_file}")
print(f"Raw file: {args.raw_file}")
print(f"Output file: {args.output_file}")

# Verify the file paths point to actual files
if not os.path.isfile(args.lateral_file):
    raise FileNotFoundError(f"Lateral file does not exist: {args.lateral_file}")

if not os.path.isfile(args.raw_file):
    raise FileNotFoundError(f"Raw file does not exist: {args.raw_file}")

# Load the provided CSV files
try:
    lateral_df = pd.read_csv(args.lateral_file)
    raw_df = pd.read_csv(args.raw_file)
    print("Files loaded successfully.")
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure the file paths are correct and the files exist.")
    exit(1)

# Function to find the closest match based on GPS coordinates
def find_and_remove_closest_event(lat, lon, event_df):
    lat_diff = np.abs(event_df['GPS latitude'] - lat)
    lon_diff = np.abs(event_df['GPS longitude'] - lon)
    event_df['total_diff'] = lat_diff + lon_diff
    closest_idx = event_df['total_diff'].idxmin()
    closest_event = event_df.loc[closest_idx]
    event_df.drop(closest_idx, inplace=True)
    return closest_event['!"Filename"']

# Apply the function to match events for each row in the lateral dataframe
matched_filenames = []
for _, row in lateral_df.iterrows():
    matched_filename = find_and_remove_closest_event(row['GPS latitude'], row['GPS longitude'], raw_df)
    matched_filenames.append(matched_filename)

lateral_df['Matched Filename'] = matched_filenames

# Save the results to a new CSV file
output_path = os.path.join(args.output_file, 'matched_output.csv')
lateral_df.to_csv(output_path, index=False)

# Print the path of the saved file
print(f"The new CSV file is saved at: {output_path}")

# Display the results
print(lateral_df)
