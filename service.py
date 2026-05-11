import servicemanager
import win32service
import win32serviceutil
import win32event
import sys
import os
import json
from threading import Thread
from PySide6.QtCore import QCoreApplication

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
python_exe = sys.executable

from supervisor_logic import SupervisorWorker
from paths import get_system_data_dir # Use the system path for the service

class SupervisorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PySupervisorService"
    _svc_display_name_ = "Python Process Supervisor Service"
    _svc_description_ = "Monitors and manages background applications from config.json."
    _exe_name_ = python_exe

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.threads = {}
        self.workers = {}
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        servicemanager.LogInfoMsg("PySupervisorService - Received stop signal.")
        self.is_running = False
        for worker in self.workers.values():
            worker.stop()
        if hasattr(self, 'app'):
            self.app.quit()
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        system_data_dir = get_system_data_dir()
        os.chdir(system_data_dir) # Change working dir to the data dir
        
        # QCoreApplication is required because SupervisorWorker is a QObject
        self.app = QCoreApplication(sys.argv)

        servicemanager.LogInfoMsg(f"PySupervisorService - Service starting. Data directory: {system_data_dir}")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        self.run_workers(system_data_dir)

        servicemanager.LogInfoMsg("PySupervisorService - All workers started.")

        # Simple loop to check for config changes or just wait
        config_path = system_data_dir / 'config.json'
        last_mtime = config_path.stat().st_mtime if config_path.exists() else 0

        # Timer to check for config changes
        from PySide6.QtCore import QTimer
        self.config_timer = QTimer()
        self.config_timer.timeout.connect(lambda: self.check_config(config_path, system_data_dir))
        self.config_timer.start(10000)
        self.last_mtime = last_mtime

        self.app.exec()
        servicemanager.LogInfoMsg("PySupervisorService - Service has stopped.")

    def check_config(self, config_path, system_data_dir):
        if not self.is_running:
            self.app.quit()
            return
        if config_path.exists():
            current_mtime = config_path.stat().st_mtime
            if current_mtime > self.last_mtime:
                servicemanager.LogInfoMsg("PySupervisorService - Configuration change detected. Reloading...")
                self.reload_workers(system_data_dir)
                self.last_mtime = current_mtime

    def run_workers(self, system_data_dir):
        try:
            config_path = system_data_dir / 'config.json'
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            servicemanager.LogErrorMsg(f"PySupervisorService - CRITICAL: Could not load config.json from {config_path}. Error: {e}")
            return

        for app_config in config.get('apps', []):
            name = app_config['name']
            servicemanager.LogInfoMsg(f"PySupervisorService - Starting thread for '{name}'.")
            
            if app_config.get('output'):
                log_path = system_data_dir / app_config['output']
                app_config['output'] = str(log_path)

            worker = SupervisorWorker(app_config)
            worker.log_message.connect(lambda msg, n=name: servicemanager.LogInfoMsg(f"[{n}] {msg}"))
            thread = Thread(target=worker.run)
            self.workers[name] = worker
            self.threads[name] = thread
            thread.start()

    def reload_workers(self, system_data_dir):
        # Stop existing workers
        for worker in self.workers.values():
            worker.stop()
        for thread in self.threads.values():
            thread.join(timeout=5)

        self.workers = {}
        self.threads = {}

        # Start new workers
        self.run_workers(system_data_dir)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SupervisorService)
