import servicemanager
import win32service
import win32serviceutil
import win32event
import sys
import os
import json
from threading import Thread

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
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        system_data_dir = get_system_data_dir()
        os.chdir(system_data_dir) # Change working dir to the data dir
        
        servicemanager.LogInfoMsg(f"PySupervisorService - Service starting. Data directory: {system_data_dir}")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
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
            thread = Thread(target=worker.run)
            self.workers[name] = worker
            self.threads[name] = thread
            thread.start()

        servicemanager.LogInfoMsg("PySupervisorService - All workers started.")
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        servicemanager.LogInfoMsg("PySupervisorService - Service has stopped.")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SupervisorService)
