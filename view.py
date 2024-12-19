from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QMessageBox, QComboBox, QLineEdit, QHBoxLayout
from service import fetch_neighborhoods, generate_gpx
import json
import os

class BHMap(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BH Map")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Select a neighborhood and click 'Generate GPX'")
        self.combo_neighborhoods = QComboBox()
        self.save_json_button = QPushButton("Update Neighborhoods")
        self.generate_gpx_button = QPushButton("Generate GPX")

        layout.addWidget(self.label)
        layout.addWidget(self.save_json_button)
        layout.addWidget(self.combo_neighborhoods)
        layout.addWidget(self.generate_gpx_button)

        self.generate_gpx_button.clicked.connect(self.generate_gpx)
        self.save_json_button.clicked.connect(self.save_json)

        self.setLayout(layout)

        self.load_neighborhoods()

    def load_neighborhoods(self):
        try:
            neighborhoods = fetch_neighborhoods()
            if neighborhoods:
                self.combo_neighborhoods.clear()
                self.combo_neighborhoods.setEditable(True)
                self.combo_neighborhoods.addItems(neighborhoods.keys())
                self.neighborhoods_data = neighborhoods
                self.label.setText("Choose a neighborhood and click Generate GPX")
                self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.label.setStyleSheet("""
                    font-size: 16px; 
                    font-weight: bold; 
                    text-align: center;
                    margin: 10px 0;
                """)

            else:
                self.label.setText("No neighborhoods found.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))

    def generate_gpx(self):
        selected_neighborhood = self.combo_neighborhoods.currentText()
        if selected_neighborhood:
            coordinates = self.neighborhoods_data.get(selected_neighborhood)
            if coordinates:
                result = generate_gpx(selected_neighborhood, coordinates)
                QMessageBox.information(self, "Success", result)
            else:
                QMessageBox.critical(self, "Error", "Coordinates not found for the selected neighborhood.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a neighborhood.")

    def save_json(self):
        if hasattr(self, 'neighborhoods_data') and self.neighborhoods_data:
            file_path = "neighborhoods.json"

            if os.path.exists(file_path):
                reply = QMessageBox.question(self, 'Confirm',
                                             f"The file {file_path} already exists. Do you want to replace it?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.neighborhoods_data, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Success", f"File {file_path} saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving the file: {str(e)}")
        else:
            QMessageBox.warning(self, "Warning", "No data to save.")
