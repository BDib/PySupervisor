import sys
import os
import subprocess
import ctypes
import argparse
import traceback
from datetime import datetime
from utils import is_admin
from paths import get_admin_log_path


LOG_FILE = get_admin_log_path()

def log_message(message):
    with open(LOG_FILE, 'a') as f: f.write(f"[{datetime.now()}] {message}\n")

def log_error(exception_info):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now()}] --- ERROR ---\n")
        f.write(traceback.format_exc())
        f.write("-----------------\n")

# Hides the console window
try:
    import win32gui, win32console
    win = win32console.GetConsoleWindow()
    if win: win32gui.ShowWindow(win, 0)
except ImportError: pass

def run_service_command(command):
    python_console_exe = sys.executable.replace("pythonw.exe", "python.exe")
    service_script_path = os.path.join(os.path.dirname(__file__), "service.py")
    cmd_list = [python_console_exe, service_script_path, command]
    log_message(f"Running command: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, check=True, capture_output=True, text=True)
    if result.stdout: log_message(f"STDOUT: {result.stdout.strip()}")
    if result.stderr: log_message(f"STDERR: {result.stderr.strip()}")

def add_to_scheduler():
    task_name = "PySupervisor"
    main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
    command = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{pythonw_path}" "{main_script_path}"', '/sc', 'ONLOGON', '/rl', 'HIGHEST', '/f']
    log_message(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=True, capture_output=True, text=True)

def remove_from_scheduler():
    task_name = "PySupervisor"
    command = ['schtasks', '/delete', '/tn', task_name, '/f']
    log_message(f"Running command: {' '.join(command)}")
    subprocess.run(command, check=True, capture_output=True, text=True)

if __name__ == '__main__':
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 0)
        sys.exit(0)

    parser = argparse.ArgumentParser(description="PySupervisor Admin Actions")
    parser.add_argument('action', choices=['install-service', 'start-service', 'stop-service', 'remove-service', 'add-task', 'remove-task'])
    args = parser.parse_args()

    try:
        log_message(f"Received action: {args.action}")
        if args.action == 'install-service': run_service_command('install')
        elif args.action == 'start-service': run_service_command('start')
        elif args.action == 'stop-service': run_service_command('stop')
        elif args.action == 'remove-service': run_service_command('remove')
        elif args.action == 'add-task': add_to_scheduler()
        elif args.action == 'remove-task': remove_from_scheduler()
        log_message(f"Action '{args.action}' completed successfully.")
    except Exception as e:
        log_error(traceback.format_exc())
        if hasattr(e, 'stdout') and e.stdout: log_message(f"FAILED STDOUT: {e.stdout.strip()}")
        if hasattr(e, 'stderr') and e.stderr: log_message(f"FAILED STDERR: {e.stderr.strip()}")
        sys.exit(1)
