import time
import subprocess
import logging
import sys
import os
from PySide6.QtCore import QObject, Signal, Slot

class SupervisorWorker(QObject):
    """
    This worker runs in a separate thread and handles the actual
    process supervision. It communicates with the main GUI thread via signals.
    """
    log_message = Signal(str)
    status_update = Signal(str, str) # name, status

    def __init__(self, proc_config):
        super().__init__()
        self.proc_config = proc_config
        self.is_running = True
        self.process = None

    @Slot()
    def run(self):
        """Main supervision loop for a single process."""
        name = self.proc_config['name']
        command = self.proc_config['command']
        
        restart_delay = 1
        MAX_RESTART_DELAY = 60
        
        output_handle = None

        while self.is_running:
            process_start_time = time.time()
            try:
                self.log_message.emit(f"[{name}] Starting command: {' '.join(command)}")
                creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                output_handle = open(self.proc_config.get('output', os.devnull), 'ab', buffering=0)

                self.process = subprocess.Popen(
                    command, stdout=output_handle, stderr=subprocess.STDOUT, creationflags=creation_flags
                )
                self.status_update.emit(name, f"RUNNING (PID: {self.process.pid})")

                while self.is_running:
                    return_code = self.process.poll()
                    if return_code is not None:
                        self.log_message.emit(f"[{name}] Process exited with code {return_code}.")
                        self.status_update.emit(name, f"STOPPED (Code: {return_code})")
                        break
                    time.sleep(0.5)

            except Exception as e:
                self.log_message.emit(f"[{name}] Error: {e}")
                self.status_update.emit(name, "ERROR")
                self.is_running = False # Stop on critical errors
            finally:
                if self.process:
                    self.process.kill() # Ensure it's dead before loop continues
                if output_handle:
                    output_handle.close()
            
            if not self.is_running:
                break

            # Restart logic
            if self.proc_config.get('restart', False) or (self.proc_config.get('restart_on_failure', False) and return_code != 0):
                uptime = time.time() - process_start_time
                if uptime < 5: # Fast fail
                    self.log_message.emit(f"[{name}] Process failed quickly. Waiting {restart_delay}s.")
                    time.sleep(restart_delay)
                    restart_delay = min(restart_delay * 2, MAX_RESTART_DELAY)
                else:
                    restart_delay = 1
            else:
                self.log_message.emit(f"[{name}] Process finished and will not be restarted.")
                break # Exit the loop if no restart is configured

        self.status_update.emit(name, "STOPPED")
        self.log_message.emit(f"[{name}] Supervision finished.")

    def stop(self):
        """Stops the supervision loop and terminates the child process."""
        self.log_message.emit(f"[{self.proc_config['name']}] Received stop signal.")
        self.is_running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
