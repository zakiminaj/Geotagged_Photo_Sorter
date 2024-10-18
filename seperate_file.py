import os
import shutil
import pandas as pd
import argparse
import chardet

# Set up argument parser
parser = argparse.ArgumentParser(description='Copy files based on matched filenames from a CSV.')
parser.add_argument('--source_folder', type=str, help='Path to the source folder')
parser.add_argument('--destination_folder', type=str, help='Path to the destination folder')
parser.add_argument('--csv_folder', type=str, help='Path to the folder containing the CSV file')
args = parser.parse_args()

# Function to list CSV files in a directory
def list_csv_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

# Interactive input if paths are not provided as arguments
if not args.source_folder:
    args.source_folder = input("Please enter the path to the source folder: ").strip()

if not args.destination_folder:
    args.destination_folder = input("Please enter the path to the destination folder: ").strip()

if not args.csv_folder:
    args.csv_folder = input("Please enter the path to the folder containing the CSV file: ").strip()

# Print the paths to ensure they are correct
print(f"Source folder: {args.source_folder}")
print(f"Destination folder: {args.destination_folder}")
print(f"CSV folder: {args.csv_folder}")

# Verify the folder paths
if not os.path.isdir(args.source_folder):
    raise FileNotFoundError(f"Source folder does not exist: {args.source_folder}")

if not os.path.isdir(args.destination_folder):
    os.makedirs(args.destination_folder, exist_ok=True)

if not os.path.isdir(args.csv_folder):
    raise FileNotFoundError(f"CSV folder does not exist: {args.csv_folder}")

# List available CSV files in the folder
csv_files = list_csv_files(args.csv_folder)
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in the directory: {args.csv_folder}")

print("Available CSV files:")
for i, file in enumerate(csv_files):
    print(f"{i+1}. {file}")

# Prompt user to select a CSV file
file_choice = int(input("Select the CSV file by number: ")) - 1
if file_choice < 0 or file_choice >= len(csv_files):
    raise ValueError("Invalid selection. Please select a valid number.")

args.csv_file = os.path.join(args.csv_folder, csv_files[file_choice])

# Print the selected CSV file path
print(f"Selected CSV file: {args.csv_file}")

# Verify the CSV file path
if not os.path.isfile(args.csv_file):
    raise FileNotFoundError(f"CSV file does not exist: {args.csv_file}")

# Try loading the CSV file with different encodings
try:
    csv_data = pd.read_csv(args.csv_file, encoding='utf-8')
except UnicodeDecodeError:
    print("Failed to decode with utf-8. Trying dynamic encoding detection...")
    # Detect encoding
    with open(args.csv_file, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    print(f"Detected encoding: {encoding}")

    # Load the CSV file with detected encoding
    csv_data = pd.read_csv(args.csv_file, encoding=encoding)

# Extract the matched filenames
matched_filenames = csv_data['Matched Filename'].str.strip()

# Function to create a new filename if the file already exists
def generate_new_filename(destination_file_path):
    base, ext = os.path.splitext(destination_file_path)
    counter = 1
    new_file_path = f"{base} - Copy{ext}"
    while os.path.exists(new_file_path):
        counter += 1
        new_file_path = f"{base} - Copy {counter}{ext}"
    return new_file_path

# Copy the files by searching recursively in subdirectories
for filename in matched_filenames:
    file_found = False
    for root, dirs, files in os.walk(args.source_folder):
        if filename in files:
            source_file_path = os.path.join(root, filename)
            destination_file_path = os.path.join(args.destination_folder, filename)
            if os.path.exists(destination_file_path):
                # Generate a new filename if the file already exists
                destination_file_path = generate_new_filename(destination_file_path)
            shutil.copy2(source_file_path, destination_file_path)
            print(f"Copied: {filename} to {os.path.basename(destination_file_path)}")
            file_found = True
            break  # Stop searching once the file is found
    if not file_found:
        print(f"File not found: {filename}")

print("File copying completed.")
