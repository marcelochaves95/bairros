from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QMessageBox, QComboBox, QLineEdit, QHBoxLayout
import json
import os
from service import fetch_neighborhoods, generate_gpx

class BairrosBH(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Bairros BH")
        self.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Selecione um bairro e clique em 'Gerar GPX'")
        self.combo_neighborhoods = QComboBox()
        self.save_json_button = QPushButton("Atualizar Bairros")
        self.generate_gpx_button = QPushButton("Gerar GPX")

        layout.addWidget(self.label)
        layout.addWidget(self.combo_neighborhoods)
        layout.addWidget(self.generate_gpx_button)
        layout.addWidget(self.save_json_button)

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
                self.bairros_data = neighborhoods
                self.label.setText("Escolha um bairro e clique em 'Gerar GPX'.")
            else:
                self.label.setText("Nenhum bairro encontrado.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Erro", str(e))

    def generate_gpx(self):
        selected_bairro = self.combo_neighborhoods.currentText()
        if selected_bairro:
            coordinates = self.bairros_data.get(selected_bairro)
            if coordinates:
                result = generate_gpx(selected_bairro, coordinates)
                QMessageBox.information(self, "Sucesso", result)
            else:
                QMessageBox.critical(self, "Erro", "Coordenadas não encontradas para o bairro selecionado.")
        else:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um bairro.")

    def save_json(self):
        if hasattr(self, 'bairros_data') and self.bairros_data:
            file_path = "bairros.json"
            
            if os.path.exists(file_path):
                reply = QMessageBox.question(self, 'Confirmar', 
                                             f"O arquivo {file_path} já existe. Deseja substituir?", 
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.bairros_data, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Sucesso", f"Arquivo {file_path} salvo com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar o arquivo: {str(e)}")
        else:
            QMessageBox.warning(self, "Aviso", "Não há dados para salvar.")
