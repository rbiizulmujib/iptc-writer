import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from iptcinfo3 import IPTCInfo
import os

class MinimalTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Test")
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
            # Try to create IPTCInfo object
            print("Attempting to create IPTCInfo object...")
            info = IPTCInfo(image_path, force=True)
            print("IPTCInfo object created successfully")
            
            # Print available attributes and methods
            print(f"Available attributes: {dir(info)}")
            
            # Try to access the data dictionary directly
            try:
                print(f"Data: {info.data}")
            except Exception as e:
                print(f"Error accessing data: {e}")
            
            # Set some test data with correct key names
            info['object name'] = 'Test Title'
            info['caption/abstract'] = 'Test Description'
            info['keywords'] = ['test', 'keyword']
            
            # Save the changes
            info.save()
            print("IPTC data saved successfully")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    app = QApplication(sys.argv)
    window = MinimalTest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
