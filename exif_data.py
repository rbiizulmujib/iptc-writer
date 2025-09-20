import sys
import os
import csv
import piexif
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QLabel, QComboBox, QTextEdit, QHeaderView, QAbstractItemView, 
    QMessageBox
)
from PyQt6.QtCore import Qt


class EXIFWriterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EXIF Writer")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Selected Folder: None")
        self.folder_button = QPushButton("Select Folder with JPG Files")
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)
        
        # CSV file selection
        csv_layout = QHBoxLayout()
        self.csv_label = QLabel("Selected CSV: None")
        self.csv_button = QPushButton("Select CSV File")
        self.csv_button.clicked.connect(self.select_csv)
        csv_layout.addWidget(self.csv_label)
        csv_layout.addWidget(self.csv_button)
        main_layout.addLayout(csv_layout)
        
        # Column mapping
        mapping_layout = QHBoxLayout()
        self.title_combo = QComboBox()
        self.description_combo = QComboBox()
        self.keywords_combo = QComboBox()
        
        mapping_layout.addWidget(QLabel("Title Column:"))
        mapping_layout.addWidget(self.title_combo)
        mapping_layout.addWidget(QLabel("Description Column:"))
        mapping_layout.addWidget(self.description_combo)
        mapping_layout.addWidget(QLabel("Keywords Column:"))
        mapping_layout.addWidget(self.keywords_combo)
        
        main_layout.addLayout(mapping_layout)
        
        # Process button
        self.process_button = QPushButton("Process Images")
        self.process_button.clicked.connect(self.process_images)
        self.process_button.setEnabled(False)
        main_layout.addWidget(self.process_button)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        main_layout.addWidget(QLabel("Log:"))
        main_layout.addWidget(self.log_display)
        
        # CSV data table
        self.csv_table = QTableWidget()
        self.csv_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        main_layout.addWidget(QLabel("CSV Data Preview:"))
        main_layout.addWidget(self.csv_table)
        
        # Store selected paths
        self.selected_folder = None
        self.selected_csv = None
        self.csv_data = []
        self.headers = []
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with JPG Files")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.log(f"Selected folder: {folder}")
            self.check_process_ready()
    
    def select_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.selected_csv = file_path
            self.csv_label.setText(f"Selected CSV: {file_path}")
            self.log(f"Selected CSV: {file_path}")
            
            # Load CSV data
            self.load_csv_data(file_path)
            self.check_process_ready()
    
    def load_csv_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                self.csv_data = list(reader)
                
            if not self.csv_data:
                self.log("CSV file is empty")
                return
                
            # Set headers (first row)
            self.headers = self.csv_data[0]
            
            # Update combo boxes
            self.title_combo.clear()
            self.description_combo.clear()
            self.keywords_combo.clear()
            
            self.title_combo.addItems(self.headers)
            self.description_combo.addItems(self.headers)
            self.keywords_combo.addItems(self.headers)
            
            # Set default selections if columns exist
            if 'Title' in self.headers:
                self.title_combo.setCurrentText('Title')
            if 'Description' in self.headers:
                self.description_combo.setCurrentText('Description')
            if 'Keywords' in self.headers:
                self.keywords_combo.setCurrentText('Keywords')
                
            # Populate table
            self.populate_table()
            
        except Exception as e:
            self.log(f"Error loading CSV: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load CSV file:\n{str(e)}")
    
    def populate_table(self):
        if not self.csv_data:
            return
            
        rows = len(self.csv_data) - 1  # Exclude header row
        cols = len(self.headers)
        
        self.csv_table.setRowCount(rows)
        self.csv_table.setColumnCount(cols)
        self.csv_table.setHorizontalHeaderLabels(self.headers)
        
        # Populate data rows
        for i, row in enumerate(self.csv_data[1:]):  # Skip header row
            for j, cell in enumerate(row):
                if j < cols:  # Ensure we don't exceed column count
                    item = QTableWidgetItem(cell)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
                    self.csv_table.setItem(i, j, item)
        
        # Resize columns to content
        self.csv_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def check_process_ready(self):
        ready = bool(self.selected_folder and self.selected_csv)
        self.process_button.setEnabled(ready)
    
    def log(self, message):
        self.log_display.append(message)
        QApplication.processEvents()  # Ensure the log is updated immediately
    
    def process_images(self):
        if not self.selected_folder or not self.selected_csv:
            return
            
        # Get selected column indices
        title_col = self.title_combo.currentIndex()
        description_col = self.description_combo.currentIndex()
        keywords_col = self.keywords_combo.currentIndex()
        
        # Validate that we have a filename column
        if 'Filename' not in self.headers:
            self.log("Error: CSV must contain a 'Filename' column")
            QMessageBox.critical(self, "Error", "CSV file must contain a 'Filename' column")
            return
            
        filename_col = self.headers.index('Filename')
        
        # Process each row in the CSV
        processed_count = 0
        error_count = 0
        
        for i, row in enumerate(self.csv_data[1:]):  # Skip header row
            if len(row) <= max(filename_col, title_col, description_col, keywords_col):
                self.log(f"Warning: Row {i+1} doesn't have enough columns, skipping")
                error_count += 1
                continue
                
            filename = row[filename_col]
            title = row[title_col] if title_col < len(row) else ""
            description = row[description_col] if description_col < len(row) else ""
            keywords = row[keywords_col] if keywords_col < len(row) else ""
            
            # Create full file path
            file_path = os.path.join(self.selected_folder, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                self.log(f"Warning: File {filename} not found in folder, skipping")
                error_count += 1
                continue
                
            # Check if file is JPG
            if not filename.lower().endswith(('.jpg', '.jpeg')):
                self.log(f"Warning: File {filename} is not a JPG file, skipping")
                error_count += 1
                continue
                
            # Process the image
            try:
                self.write_exif_data(file_path, title, description, keywords)
                self.log(f"Successfully processed: {filename}")
                processed_count += 1
            except Exception as e:
                self.log(f"Error processing {filename}: {str(e)}")
                error_count += 1
                
        self.log(f"Processing complete. {processed_count} files processed successfully, {error_count} errors.")
        QMessageBox.information(self, "Processing Complete", 
                               f"Successfully processed: {processed_count} files\nErrors: {error_count}")
    
    def write_exif_data(self, image_path, title, description, keywords):
        try:
            # Load existing EXIF data
            exif_dict = piexif.load(image_path)
            
            # Set EXIF data
            if title:
                # ImageDescription (270) - ASCII
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = title.encode('utf-8')
                
            if description:
                # UserComment (37510) - ASCII
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = description.encode('utf-8')
                
            if keywords:
                # XPKeywords (40094) - Windows-specific, but commonly used
                # This is a Unicode string in UTF-16LE format
                exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keywords.encode('utf-16le')
                
                # Also set Keywords in UserComment if not already set
                if not description:
                    exif_dict["Exif"][piexif.ExifIFD.UserComment] = keywords.encode('utf-8')
                
            # Convert the dictionary to bytes and insert into the image
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            
        except Exception as e:
            raise Exception(f"Failed to write EXIF data: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = EXIFWriterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
