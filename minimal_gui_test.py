import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

class MinimalGUITest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal GUI Test")
        self.setGeometry(100, 100, 300, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Add button
        button = QPushButton("Test Button")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)
    
    def on_button_click(self):
        print("Button clicked!")

def main():
    app = QApplication(sys.argv)
    window = MinimalGUITest()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
