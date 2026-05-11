from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QCheckBox, QDialogButtonBox, QPushButton, QMessageBox
)

class ProcessDialog(QDialog):
    """A dialog for adding or editing a single process configuration."""
    def __init__(self, parent=None, process_config=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Process")
        self.setMinimumWidth(500)
        
        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Create form widgets
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. My Application")
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("e.g. python script.py")
        self.cwd_edit = QLineEdit()
        self.cwd_edit.setPlaceholderText("Working directory (optional)")
        self.env_edit = QLineEdit()
        self.env_edit.setPlaceholderText("KEY1=VAL1, KEY2=VAL2 (optional)")
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("e.g. my_app.log (optional)")
        self.restart_check = QCheckBox("Always restart when the process exits")
        self.restart_on_failure_check = QCheckBox("Only restart if it exits with an error code")

        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Command:", self.command_edit)
        form_layout.addRow("Working Dir:", self.cwd_edit)
        form_layout.addRow("Env Vars:", self.env_edit)
        form_layout.addRow("Output Log:", self.output_edit)
        form_layout.addRow(self.restart_check)
        form_layout.addRow(self.restart_on_failure_check)
        
        self.layout.addLayout(form_layout)

        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # Populate form if editing an existing process
        if process_config:
            self.name_edit.setText(process_config.get("name", ""))
            command = process_config.get("command", [])
            self.command_edit.setText(' '.join(command) if isinstance(command, list) else command)
            self.cwd_edit.setText(process_config.get("cwd", ""))

            env_vars = process_config.get("env", {})
            env_str = ", ".join([f"{k}={v}" for k, v in env_vars.items()])
            self.env_edit.setText(env_str)

            self.output_edit.setText(process_config.get("output", ""))
            self.restart_check.setChecked(process_config.get("restart", False))
            self.restart_on_failure_check.setChecked(process_config.get("restart_on_failure", False))

    def validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please provide a name for the process.")
            return
        if not self.command_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please provide a command to run.")
            return
        self.accept()

    def get_data(self):
        """Returns the process configuration as a dictionary."""
        env_dict = {}
        env_str = self.env_edit.text().strip()
        if env_str:
            # Better parsing for env vars (handles semi-colons as well)
            import re
            items = re.split('[;,]', env_str)
            for item in items:
                if '=' in item:
                    k, v = item.split('=', 1)
                    env_dict[k.strip()] = v.strip()

        return {
            "name": self.name_edit.text().strip(),
            "command": self.command_edit.text().strip().split(),
            "cwd": self.cwd_edit.text().strip(),
            "env": env_dict,
            "output": self.output_edit.text().strip(),
            "restart": self.restart_check.isChecked(),
            "restart_on_failure": self.restart_on_failure_check.isChecked()
        }
