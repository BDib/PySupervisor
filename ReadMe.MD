# PySupervisor: A Robust Cross-Platform Process Supervisor with GUI

PySupervisor is a full-featured, cross-platform application designed to run, manage, and supervise background processes. It provides a user-friendly graphical interface for interactive management, as well as a powerful command-line mode for scripting and automation.

Originally conceived as a Python-based replacement for a C++ command-line tool, this project has evolved into a complete solution for developers and system administrators who need to ensure their applications and scripts are always running.

## Features

  * **Dual-Mode Operation:** Launch a full GUI for interactive management or run in a headless, command-line mode for scripting and single-task supervision.
  * **Cross-Platform GUI:** A modern user interface built with PySide6 that works on Windows, macOS, and Linux.
  * **Process Management:**
      * View the status of all configured applications in real-time.
      * Start and stop all processes with a single click.
      * Start and stop individual processes directly from the process list.
  * **Background Supervision:** Each supervised process runs in a dedicated background thread, ensuring the GUI or main console remains responsive.
  * **Intelligent Restarts:**
      * Configure processes to always restart or to restart only if they exit with an error code.
      * Includes an exponential backoff delay to prevent CPU spinning on repeatedly failing processes.
  * **Configuration Editor:** A built-in GUI editor to add, edit, and remove applications from the configuration file without manual editing.
  * **System Tray Integration:**
      * The application runs silently in the system tray for unobtrusive operation.
      * A left-click shows the main window; a right-click opens a full context menu.
  * **Advanced Windows Integration (Windows Only):**
      * **Windows Service:** Install, start, stop, and remove a background Windows Service directly from the tray menu. The service runs 24/7, even without a user logged in.
      * **Task Scheduler:** Add or remove a task to launch the application automatically at user logon.
  * **Robust Architecture:**
      * User configuration and logs are stored safely in the user's home directory (`AppData\Roaming` on Windows).
      * Privileged operations use a self-elevating helper script, which is the standard, secure way to handle UAC prompts.
  * **Professional Installer:** Comes with an Inno Setup script to create a user-friendly installer for easy distribution.

-----

## Installation and Setup (from Source)

To run the application from the source code for development:

1.  **Prerequisites:** Python 3.8+, Git
2.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd PySupervisorGUI
    ```
3.  **Create and Activate Virtual Environment:**
    ```powershell
    # On Windows
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

-----

## Usage Guide

PySupervisor can be run in two distinct modes.

### GUI Mode

This is the default mode for interactive use. It launches the full graphical application with its window, system tray icon, and visual controls.

**To Launch:**
Run the script with no arguments.

```powershell
python main.py
```

  * **Left-Click Tray Icon:** Shows the main window.
  * **Right-Click Tray Icon:** Opens the context menu for system-level tasks.
  * **Main Window:** Use the buttons to visually manage your processes, view logs, and edit the configuration file.

### Standalone Console Mode

This mode is designed for scripting, automation, or supervising a single process without needing a graphical interface.

**To Launch:**
Run the script with command-line options, followed by the command you wish to supervise.

**Example 1: Run a continuous ping and restart it if it stops.**

```powershell
python main.py --name my-ping --restart --output ping-log.txt -- ping google.com -t
```

**Example 2: Run a Python script and restart it only if it fails.**

```powershell
python main.py --name data-script --restart-on-failure -- python my_worker_script.py
```

To stop a process running in this mode, press **Ctrl+C** in the terminal.

-----

## Command-Line Interfaces

The project contains several scripts with command-line interfaces for different purposes.

### `main.py` (Standalone Mode)

This is the primary interface for headless supervision.

**Usage:** `python main.py [OPTIONS] -- [COMMAND] [ARGS...]`

| Option | Description |
| :--- | :--- |
| `-n`, `--name <NAME>` | A unique name for the process. If not provided, it's derived from the command. |
| `-r`, `--restart` | Always restart the process when it exits. |
| `--restart-on-failure`| Restart the process only if it fails (non-zero exit code). |
| `-o`, `--output <FILE>`| Redirect the process's console output to the specified file in the user data directory. |

### `service.py` (Windows Service Management)

This script manages the background Windows Service. It must be run from an **Administrator Terminal**.

**Usage:** `python service.py [command]`

| Command | Description |
| :--- | :--- |
| **`install`** | Registers the application as a Windows Service. |
| **`start`** | Starts the service after it has been installed. |
| **`stop`** | Stops the running service. |
| **`remove`** | Uninstalls the service. |
| **`status`**| Displays the current status of the service. |
