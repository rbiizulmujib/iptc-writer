import sys
import piexif
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
import os

class MinimalEXIFTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal EXIF Test")
        self.setGeometry(100, 100, 300, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Add button to select image
        button = QPushButton("Select JPG File")
        button.clicked.connect(self.select_image)
        layout.addWidget(button)
    
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JPG File", "", "JPG Files (*.jpg *.jpeg)")
        if file_path:
            print(f"Selected file: {file_path}")
            self.process_image(file_path)
    
    def process_image(self, image_path):
        try:
            # Load existing EXIF data
            print("Loading EXIF data...")
            exif_dict = piexif.load(image_path)
            print(f"EXIF data loaded: {exif_dict}")
            
            # Modify EXIF data
            print("Modifying EXIF data...")
            exif_dict["0th"][piexif.ImageIFD.ImageDescription] = "Test Title".encode('utf-8')
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = "Test Description".encode('utf-8')
            exif_dict["0th"][piexif.ImageIFD.XPKeywords] = "test,keyword".encode('utf-16le')
            
            # Convert to bytes
            print("Converting to bytes...")
            exif_bytes = piexif.dump(exif_dict)
            print(f"EXIF bytes created: {len(exif_bytes)} bytes")
            
            # Insert into image
            print("Inserting EXIF data into image...")
            piexif.insert(exif_bytes, image_path)
            print("EXIF data inserted successfully")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    app = QApplication(sys.argv)
    window = MinimalEXIFTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
