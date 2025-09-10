from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox
)
from PySide6.QtCore import Qt

class AboutDialog(QDialog):
    """A simple dialog to show application information."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About PySupervisor")
        
        layout = QVBoxLayout(self)
        
        # Application Title and Description
        title_label = QLabel("<h2>PySupervisor</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        
        description_text = (
            "<p>A robust, cross-platform process supervisor with a graphical user interface.</p>"
            "<p>This application allows you to run, manage, and monitor background processes, "
            "with support for automatic restarts and Windows Service integration.</p>"
            "<p><b>Version:</b> 1.0</p>"
        )
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignCenter)

        # OK Button
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(button_box)
        
        self.setLayout(layout)