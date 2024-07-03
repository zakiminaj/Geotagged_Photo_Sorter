import pandas as pd
import numpy as np
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Process Lateral and RAW CSV files.')
parser.add_argument('--lateral_file', type=str, default=r'C:\path\to\your\LATERAL.csv', help='Path to the Lateral CSV file')
parser.add_argument('--raw_file', type=str, default=r'C:\path\to\your\RAW.csv', help='Path to the RAW CSV file')
parser.add_argument('--output_file', type=str, default=r'C:\path\to\your\output.csv', help='Path to save the output CSV file')
args = parser.parse_args()

# Interactive input if paths are not provided as arguments
if not args.lateral_file:
    args.lateral_file = input("Please enter the path to the Lateral CSV file: ")

if not args.raw_file:
    args.raw_file = input("Please enter the path to the RAW CSV file: ")

if not args.output_file:
    args.output_file = input("Please enter the path to save the output CSV file: ")

# Print the file paths to ensure they are correct
print(f"Lateral file: {args.lateral_file}")
print(f"Raw file: {args.raw_file}")
print(f"Output file: {args.output_file}")

# Debug: Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Additional Debug: List files in the specified directory
lateral_dir = os.path.dirname(args.lateral_file)
raw_dir = os.path.dirname(args.raw_file)
print(f"Contents of the lateral directory ({lateral_dir}):")
print(os.listdir(lateral_dir))
print(f"Contents of the raw directory ({raw_dir}):")
print(os.listdir(raw_dir))

# Check if files exist before loading
if not os.path.isfile(args.lateral_file):
    print(f"Lateral file does not exist: {args.lateral_file}")
    exit(1)

if not os.path.isfile(args.raw_file):
    print(f"Raw file does not exist: {args.raw_file}")
    exit(1)

# Load the provided CSV files
try:
    lateral_df = pd.read_csv(args.lateral_file)
    raw_df = pd.read_csv(args.raw_file)
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure the file paths are correct and the files exist.")
    exit(1)

# Define a threshold for matching GPS coordinates
latitude_threshold = 0.0001
longitude_threshold = 0.0001

# Function to find the closest match based on GPS coordinates
def find_closest_event(lat, lon, event_df):
    lat_diff = np.abs(event_df['GPS latitude'] - lat)
    lon_diff = np.abs(event_df['GPS longitude'] - lon)
    event_df['total_diff'] = lat_diff + lon_diff
    closest_event = event_df.loc[event_df['total_diff'].idxmin()]
    return closest_event['!"Filename"']

# Apply the function to match events for each row in the lateral dataframe
lateral_df['Matched Filename'] = lateral_df.apply(
    lambda row: find_closest_event(row['GPS latitude'], row['GPS longitude'], raw_df), axis=1)

# Save the results to a new CSV file
lateral_df.to_csv(args.output_file, index=False)

# Print the path of the saved file
print(f"The new CSV file is saved at: {args.output_file}")

# Display the results
print(lateral_df)
