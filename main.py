import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, QThread, Signal, Slot
from supervisor_app import MainWindow
from supervisor_logic import SupervisorWorker
from paths import get_user_data_dir

def run_gui_mode():
    """Launches the full graphical user interface."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MainWindow()
    sys.exit(app.exec())

def run_standalone_mode():
    """Runs a single process in a headless, command-line-only mode."""
    parser = argparse.ArgumentParser(
        description="PySupervisor - Standalone Mode. Run a single command without the GUI."
    )
    parser.add_argument('-n', '--name', type=str, help="A unique name for the process instance.")
    parser.add_argument('-r', '--restart', action='store_true', help="Always restart the process when it exits.")
    parser.add_argument('--restart-on-failure', action='store_true', help="Restart only if it fails (non-zero exit code).")
    parser.add_argument('-o', '--output', type=str, metavar='FILE', help="Redirect process stdout/stderr to a file.")
    parser.add_argument('command', nargs=argparse.REMAINDER, help="The command and its arguments to run.")
    args = parser.parse_args()

    if not args.command:
        parser.error("You must provide a command to run.")
        return

    command_to_run = args.command
    if command_to_run and command_to_run[0] == '--':
        command_to_run = command_to_run[1:]

    app = QCoreApplication(sys.argv)
    proc_name = args.name if args.name else os.path.basename(command_to_run[0])
    
    proc_config = {
        "name": proc_name,
        "command": command_to_run,
        "restart": args.restart,
        "restart_on_failure": args.restart_on_failure,
    }

    if args.output:
        user_data_dir = get_user_data_dir()
        output_log_path = user_data_dir / args.output
        proc_config['output'] = str(output_log_path)


    print(f"--- Starting Standalone Supervisor for '{proc_name}' ---")
    print(f"--- Press Ctrl+C to stop. ---")

    worker = SupervisorWorker(proc_config)
    thread = QThread()
    worker.moveToThread(thread)

    worker.log_message.connect(print)
    worker.status_update.connect(lambda name, status: print(f"STATUS UPDATE for '{name}': {status}"))
    
    thread.started.connect(worker.run)
    worker.status_update.connect(lambda name, status: app.quit() if status.startswith("STOPPED") else None)
    
    # --- MODIFICATION: Improved shutdown logic ---
    def stop_on_interrupt(*args):
        """A more robust shutdown handler for Ctrl+C."""
        print("\n--- Ctrl+C detected. Shutting down... ---")
        # Tell the worker's internal loop to stop
        worker.stop()
        # Tell the QThread's event loop to quit
        thread.quit()
        # Wait for the thread to finish all its cleanup
        thread.wait()
    
    from PySide6.QtCore import QTimer
    import signal
    signal.signal(signal.SIGINT, stop_on_interrupt)
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    thread.start()
    sys.exit(app.exec())

if __name__ == '__main__':
    get_user_data_dir()

    if len(sys.argv) > 1:
        run_standalone_mode()
    else:
        run_gui_mode()