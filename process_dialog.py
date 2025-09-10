from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QCheckBox, QDialogButtonBox, QPushButton
)

class ProcessDialog(QDialog):
    """A dialog for adding or editing a single process configuration."""
    def __init__(self, parent=None, process_config=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Process")
        
        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Create form widgets
        self.name_edit = QLineEdit()
        self.command_edit = QLineEdit()
        self.output_edit = QLineEdit()
        self.restart_check = QCheckBox()
        self.restart_on_failure_check = QCheckBox()

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Command:", self.command_edit)
        form_layout.addRow("Output Log:", self.output_edit)
        form_layout.addRow("Always Restart:", self.restart_check)
        form_layout.addRow("Restart on Failure:", self.restart_on_failure_check)
        
        self.layout.addLayout(form_layout)

        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # Populate form if editing an existing process
        if process_config:
            self.name_edit.setText(process_config.get("name", ""))
            self.command_edit.setText(' '.join(process_config.get("command", [])))
            self.output_edit.setText(process_config.get("output", ""))
            self.restart_check.setChecked(process_config.get("restart", False))
            self.restart_on_failure_check.setChecked(process_config.get("restart_on_failure", False))

    def get_data(self):
        """Returns the process configuration as a dictionary."""
        return {
            "name": self.name_edit.text(),
            "command": self.command_edit.text().split(),
            "output": self.output_edit.text(),
            "restart": self.restart_check.isChecked(),
            "restart_on_failure": self.restart_on_failure_check.isChecked()
        }
