import os
import sys
from pathlib import Path

def get_user_data_dir() -> Path:
    """
    Returns the path to the user-specific data directory (for the GUI).
    Creates the directory if it doesn't exist.
    On Windows: C:\\Users\\<user>\\AppData\\Roaming\\PySupervisor
    On Linux/macOS: /home/<user>/.pysupervisor
    """
    if sys.platform == "win32":
        base_dir = Path(os.getenv('APPDATA'))
        app_data_dir = base_dir / "PySupervisor"
    else:
        base_dir = Path.home()
        app_data_dir = base_dir / ".pysupervisor"
    
    app_data_dir.mkdir(exist_ok=True)
    return app_data_dir

def get_system_data_dir() -> Path:
    """
    Returns the path to the system-wide data directory (for the Service).
    Creates the directory if it doesn't exist.
    On Windows: C:\\ProgramData\\PySupervisor
    On Linux/macOS: /etc/pysupervisor
    """
    if sys.platform == "win32":
        base_dir = Path(os.getenv('PROGRAMDATA'))
        app_data_dir = base_dir / "PySupervisor"
    else:
        app_data_dir = Path("/etc/pysupervisor")
    
    app_data_dir.mkdir(exist_ok=True, parents=True)
    return app_data_dir

# --- NEW FUNCTION ---
def get_admin_log_path() -> Path:
    """Returns the path for the admin actions log file."""
    return get_user_data_dir() / "admin_actions.log"