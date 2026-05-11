
import sys
import os
import time
from PySide6.QtCore import QCoreApplication, QTimer
from supervisor_logic import SupervisorWorker

def test_worker():
    app = QCoreApplication(sys.argv)

    config = {
        "name": "test-ping",
        "command": ["ping", "127.0.0.1", "-n", "3"],
        "restart": False
    }

    worker = SupervisorWorker(config)
    worker.log_message.connect(lambda msg: print(f"LOG: {msg}"))
    worker.status_update.connect(lambda name, status: print(f"STATUS: {name} -> {status}"))
    worker.stats_update.connect(lambda name, stats: print(f"STATS: {name} -> {stats}"))

    def on_status(name, status):
        if "STOPPED" in status:
            print("Process stopped as expected.")
            app.quit()

    worker.status_update.connect(on_status)

    QTimer.singleShot(0, worker.run)

    # Safety timeout
    QTimer.singleShot(10000, app.quit)

    sys.exit(app.exec())

if __name__ == "__main__":
    test_worker()
