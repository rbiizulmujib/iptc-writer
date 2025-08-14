# IPTC Writer

A Python application using PyQt6 to write IPTC metadata (title, description, and keywords) to JPG images based on data from a CSV file.

## Features

- Select a folder containing JPG images
- Select a CSV file with metadata information
- Map CSV columns to IPTC fields (Title, Description, Keywords)
- Process images and write metadata
- Log all operations for tracking

## Requirements

- Python 3.6+
- PyQt6
- pillow
- iptcinfo3

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Select a folder containing JPG images using the "Select Folder with JPG Files" button

3. Select a CSV file with metadata using the "Select CSV File" button

4. Map the CSV columns to IPTC fields:
   - The CSV file must contain a "Filename" column with the names of the JPG files
   - Select which columns should be used for Title, Description, and Keywords

5. Click "Process Images" to write the metadata to the images

## CSV File Format

The CSV file should contain at least a "Filename" column. Other columns can be named as you like, but you'll need to map them to the appropriate IPTC fields in the application.

Example:
```csv
Filename,Title,Description,Keywords
image1.jpg,Beautiful Landscape,A stunning view of mountains and lakes,nature,landscape,water,mountains
image2.jpg,Street Photography,Urban life captured in black and white,street,urban,black and white,city
```

## Notes

- Only JPG/JPEG files are processed
- Keywords in the CSV should be comma-separated
- The application will show a preview of the CSV data in a table
- All operations are logged in the log display area
# iptc-writer
