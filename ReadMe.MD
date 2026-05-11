# PySupervisor: A Robust Windows Process Supervisor with GUI

PySupervisor is a full-featured application designed to run, manage, and supervise background processes on Windows. It provides a user-friendly graphical interface for interactive management, a powerful command-line mode for scripting, and a reliable background Windows Service for 24/7 operation.

## Features

  * **Dual-Mode Operation:** Launch a full GUI for interactive management or run in a headless, command-line mode.
  * **Process Management:**
      * View status, CPU usage, and Memory consumption of all configured applications in real-time.
      * Start and stop all processes with a single click.
      * Start and stop individual processes directly from the process list.
  * **Intelligent Restarts:**
      * Configure processes to always restart or to restart only if they exit with an error code.
      * Includes an exponential backoff delay to prevent CPU spinning on repeatedly failing processes.
  * **Configuration Editor:** A built-in GUI editor to add, edit, and remove applications, including support for custom working directories and environment variables.
  * **System Tray Integration:**
      * Runs silently in the system tray.
      * Left-click shows the main window; right-click opens a full context menu.
  * **Windows Integration:**
      * **Windows Service:** Install and manage a background service that runs even without a user logged in. Includes automatic configuration reloading.
      * **Task Scheduler:** Automatically launch the GUI at user logon.
  * **Modern UI:** Styled log viewer and intuitive layout for easy process monitoring.

## Installation

1.  **Prerequisites:** Python 3.8+
2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/PySupervisor.git
    cd PySupervisor
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### GUI Mode
Run the script with no arguments to launch the graphical interface.
```powershell
python main.py
```

### Standalone CLI Mode
Run a single command without the GUI.
```powershell
python main.py --name my-ping --restart -- ping google.com -t
```

### Windows Service
Manage the background service from an **Administrator Terminal**.
```powershell
python service.py [install|start|stop|remove|status]
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
