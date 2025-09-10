import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from process_dialog import ProcessDialog

class ConfigEditor(QDialog):
    def __init__(self, parent=None, config_data=None, config_path=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Editor")
        self.setGeometry(150, 150, 700, 400)
        
        self.config_data = config_data if config_data else {"apps": []}
        self.config_path = config_path
        
        self.layout = QVBoxLayout(self)

        # Table to display processes
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Command", "Restart Policy"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.populate_table()
        self.layout.addWidget(self.table)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.remove_button = QPushButton("Remove")
        self.save_button = QPushButton("Save and Close")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        self.layout.addLayout(button_layout)

        # Connect signals
        self.add_button.clicked.connect(self.add_process)
        self.edit_button.clicked.connect(self.edit_process)
        self.remove_button.clicked.connect(self.remove_process)
        self.save_button.clicked.connect(self.save_config)

    def populate_table(self):
        self.table.setRowCount(0)
        for i, app in enumerate(self.config_data['apps']):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(app['name']))
            self.table.setItem(i, 1, QTableWidgetItem(' '.join(app['command'])))
            
            policy = "None"
            if app.get('restart'):
                policy = "Always"
            elif app.get('restart_on_failure'):
                policy = "On Failure"
            self.table.setItem(i, 2, QTableWidgetItem(policy))

    def add_process(self):
        dialog = ProcessDialog(self)
        if dialog.exec():
            self.config_data['apps'].append(dialog.get_data())
            self.populate_table()

    def edit_process(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a process to edit.")
            return
            
        process_config = self.config_data['apps'][current_row]
        dialog = ProcessDialog(self, process_config)
        if dialog.exec():
            self.config_data['apps'][current_row] = dialog.get_data()
            self.populate_table()

    def remove_process(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a process to remove.")
            return
            
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove this process?")
        if reply == QMessageBox.Yes:
            del self.config_data['apps'][current_row]
            self.populate_table()

    def save_config(self):
        if not self.config_path:
            QMessageBox.critical(self, "Error", "Configuration path not set. Cannot save.")
            return

        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config_data, f, indent=2)
            QMessageBox.information(self, "Success", "Configuration saved successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save configuration file: {e}")