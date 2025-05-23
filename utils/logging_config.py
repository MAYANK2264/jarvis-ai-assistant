import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional
import json
import threading
from queue import Queue
import atexit


class DatabaseLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.worker = threading.Thread(target=self._worker)
        self.worker.daemon = True
        self.worker.start()
        atexit.register(self.flush)

    def emit(self, record):
        self.queue.put(record)

    def flush(self):
        self.queue.join()

    def _worker(self):
        while True:
            try:
                record = self.queue.get()
                self._write_to_db(record)
                self.queue.task_done()
            except Exception:
                continue

    def _write_to_db(self, record):
        try:
            from utils.database import get_db_manager

            db = get_db_manager()

            # Convert record to dict for storage
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "module": record.module,
                "function": record.funcName,
                "message": record.getMessage(),
                "exception": record.exc_info[1] if record.exc_info else None,
            }

            # Store in database
            db.log_operation(
                operation="log_entry",
                source_path=record.module,
                status=record.levelname,
                error=str(log_entry.get("exception")),
            )

        except Exception as e:
            print(f"Error writing to log database: {str(e)}")


def setup_logging(log_dir: Optional[str] = None):
    """Setup centralized logging

    Args:
        log_dir: Optional directory for log files
    """
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # File handler for all logs
    all_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "jarvis.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    all_handler.setFormatter(file_formatter)
    all_handler.setLevel(logging.DEBUG)

    # File handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "errors.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Database handler
    db_handler = DatabaseLogHandler()
    db_handler.setLevel(logging.INFO)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    root_logger.handlers = []

    # Add handlers
    root_logger.addHandler(all_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(db_handler)

    # Log startup
    root_logger.info("Logging system initialized")
