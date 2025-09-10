import json
import sys
import os
import ctypes
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QTextEdit, QHeaderView,
    QGroupBox, QMessageBox, QMenu
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtCore import QThread, Slot, Qt
from about_dialog import AboutDialog
from supervisor_logic import SupervisorWorker
from config_editor import ConfigEditor
from paths import get_user_data_dir
from utils import is_admin

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_data_dir = get_user_data_dir()
        self.config_path = self.user_data_dir / "config.json"
        
        # --- MODIFICATION: Consistent App Name ---
        self.setWindowTitle("PySupervisor")
        self.setGeometry(100, 100, 900, 650)
        self.threads = {}
        self.workers = {}
        
        self.init_ui()
        self.load_config()
        self.init_tray_icon()
        
    def init_ui(self):
        # This method is unchanged
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(["Name", "Status", "Command", "Actions"])
        self.process_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.process_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.process_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.process_table)
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        main_layout.addWidget(self.log_viewer)
        button_layout = QHBoxLayout()
        self.start_all_button = QPushButton("Start All")
        self.stop_all_button = QPushButton("Stop All")
        self.edit_config_button = QPushButton("Edit Configuration")
        button_layout.addWidget(self.start_all_button)
        button_layout.addWidget(self.stop_all_button)
        button_layout.addStretch()
        button_layout.addWidget(self.edit_config_button)
        main_layout.addLayout(button_layout)
        self.start_all_button.clicked.connect(self.start_all_processes)
        self.stop_all_button.clicked.connect(self.stop_all_processes)
        self.edit_config_button.clicked.connect(self.open_config_editor)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        tray_menu = QMenu()
        
        # --- MODIFICATION: Reordered menu entries per your request ---
        
        # 1. About Action
        about_action = QAction("About PySupervisor", self)
        about_action.triggered.connect(self.show_about_dialog)
        tray_menu.addAction(about_action)

        # 2. Separator
        tray_menu.addSeparator()

        # 3. Show Action
        show_action = QAction("Show PySupervisor", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        # 4. Separator
        tray_menu.addSeparator()
        
        # 5. Windows-specific actions (if on Windows)
        if sys.platform == "win32":
            service_submenu = QMenu("Windows Service", self)
            install_action, start_action, stop_action, remove_action = QAction("Install Service", self), QAction("Start Service", self), QAction("Stop Service", self), QAction("Remove Service", self)
            install_action.triggered.connect(lambda: self.run_admin_action("install-service"))
            start_action.triggered.connect(lambda: self.run_admin_action("start-service"))
            stop_action.triggered.connect(lambda: self.run_admin_action("stop-service"))
            remove_action.triggered.connect(lambda: self.run_admin_action("remove-service"))
            service_submenu.addAction(install_action)
            service_submenu.addAction(start_action)
            service_submenu.addAction(stop_action)
            service_submenu.addAction(remove_action)
            tray_menu.addMenu(service_submenu)

            task_submenu = QMenu("Task Scheduler", self)
            add_task_action = QAction("Add to Startup (on Logon)", self)
            remove_task_action = QAction("Remove from Startup", self)
            add_task_action.triggered.connect(lambda: self.run_admin_action("add-task"))
            remove_task_action.triggered.connect(lambda: self.run_admin_action("remove-task"))
            task_submenu.addAction(add_task_action)
            task_submenu.addAction(remove_task_action)
            tray_menu.addMenu(task_submenu)

            tray_menu.addSeparator()

        # 6. Final Quit Action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.force_quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        self.tray_icon.setToolTip("PySupervisor")
        self.append_log_message("Supervisor started. Running in system tray.")

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    # ... (The rest of the file is unchanged)
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger: self.show_window()

    def show_window(self):
        self.show()
        self.activateWindow()

    def run_admin_action(self, action):
        self.append_log_message(f"Requesting admin action: {action}. Please check for UAC prompt.")
        try:
            pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
            helper_script = os.path.join(os.path.dirname(__file__), "admin_actions.py")
            subprocess.Popen([pythonw_exe, helper_script, action], creationflags=subprocess.CREATE_NO_WINDOW)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch admin helper script: {e}")
            self.append_log_message(f"Error launching admin helper: {e}")

    def load_config(self):
        try:
            if not self.config_path.exists():
                self.append_log_message(f"Config file not found. Creating default at: {self.config_path}")
                default_config = {"apps": []}
                with open(self.config_path, 'w') as f: json.dump(default_config, f, indent=2)
                self.config = default_config
            else:
                with open(self.config_path, 'r') as f: self.config = json.load(f)
        except Exception as e:
            self.append_log_message(f"ERROR: Could not load or create config file. {e}")
            self.config = {"apps": []}
        self.process_table.setRowCount(0)
        for i, app_config in enumerate(self.config.get('apps', [])):
            self.process_table.insertRow(i)
            self.process_table.setItem(i, 0, QTableWidgetItem(app_config['name']))
            self.process_table.setItem(i, 1, QTableWidgetItem("STOPPED"))
            self.process_table.setItem(i, 2, QTableWidgetItem(' '.join(app_config['command'])))
            self.add_action_buttons(i, app_config['name'])
            
    def add_action_buttons(self, row, name):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 0, 5, 0)
        start_button, stop_button = QPushButton("Start"), QPushButton("Stop")
        start_button.clicked.connect(lambda: self.start_process(name))
        stop_button.clicked.connect(lambda: self.stop_process(name))
        layout.addWidget(start_button)
        layout.addWidget(stop_button)
        self.process_table.setCellWidget(row, 3, widget)

    def start_process(self, name):
        if name in self.threads and self.threads[name].isRunning(): return
        app_config = next((app for app in self.config['apps'] if app['name'] == name), None)
        if not app_config: return
        effective_config = app_config.copy()
        if effective_config.get('output'):
            log_path = self.user_data_dir / effective_config['output']
            effective_config['output'] = str(log_path)
        worker = SupervisorWorker(effective_config)
        thread = QThread()
        worker.moveToThread(thread)
        worker.log_message.connect(self.append_log_message)
        worker.status_update.connect(self.update_process_status)
        thread.started.connect(worker.run)
        self.threads[name], self.workers[name] = thread, worker
        thread.start()

    def stop_process(self, name):
        if name in self.workers and name in self.threads and self.threads[name].isRunning(): self.workers[name].stop()

    def start_all_processes(self):
        for app in self.config.get('apps', []): self.start_process(app['name'])

    def stop_all_processes(self):
        for app in self.config.get('apps', []): self.stop_process(app['name'])

    def open_config_editor(self):
        dialog = ConfigEditor(self, self.config, self.config_path)
        if dialog.exec():
            self.stop_all_processes()
            self.load_config()
            self.append_log_message("Configuration reloaded.")
    
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage("PySupervisor", "Application was minimized to tray.", QSystemTrayIcon.Information, 2000)

    def force_quit(self):
        self.stop_all_processes()
        for thread in self.threads.values():
            if thread.isRunning(): thread.wait(5000)
        QApplication.instance().quit()
    
    @Slot(str)
    def append_log_message(self, message): self.log_viewer.append(message)

    @Slot(str, str)
    def update_process_status(self, name, status):
        for row in range(self.process_table.rowCount()):
            if self.process_table.item(row, 0).text() == name:
                self.process_table.setItem(row, 1, QTableWidgetItem(status))
                if (status.startswith("STOPPED") or status.startswith("ERROR")) and name in self.threads: self.threads[name].quit()
                break