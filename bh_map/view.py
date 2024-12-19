from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog, QPushButton, QLabel, QWidget, QMessageBox, QComboBox, QLineEdit, QHBoxLayout
from service import fetch_neighborhoods, generate_gpx

class BHMap(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BH Map")
        self.setGeometry(200, 200, 400, 300)

        icon_path = "assets/icon.ico"
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        self.label = QLabel("Choose a neighborhood and click 'Generate GPX'.")
        self.combo_neighborhoods = QComboBox()
        self.generate_gpx_button = QPushButton("Generate GPX")

        layout.addWidget(self.label)
        layout.addWidget(self.combo_neighborhoods)
        layout.addWidget(self.generate_gpx_button)

        self.generate_gpx_button.clicked.connect(self.generate_gpx)

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
        if not selected_neighborhood:
            QMessageBox.warning(self, "Warning", "Please select a neighborhood.")
            return

        coordinates = self.neighborhoods_data.get(selected_neighborhood)
        if not coordinates:
            QMessageBox.critical(self, "Error", "Coordinates not found for the selected neighborhood.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save GPX File", f"{selected_neighborhood.replace(' ', '_')}.gpx", "GPX Files (*.gpx)")

        if file_path:
            try:
                result = generate_gpx(selected_neighborhood, coordinates, file_path)
                QMessageBox.information(self, "Success", f"GPX file saved successfully at {file_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save GPX file: {e}")
        else:
            QMessageBox.information(self, "Information", "Save operation was canceled.")
