"""Memory manager module for monitoring and managing memory usage."""

import os
import psutil
import threading
import time
from typing import Dict, List, Optional
import logging
import shutil

logger = logging.getLogger(__name__)

class MemoryManager:
    """Singleton class for managing memory usage."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, threshold_mb: Optional[int] = None):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, threshold_mb: Optional[int] = None):
        """Initialize memory manager.
        
        Args:
            threshold_mb: Memory threshold in MB
            
        Raises:
            ValueError: If threshold_mb is not positive
        """
        if not self._initialized:
            if threshold_mb is not None:
                if threshold_mb <= 0:
                    raise ValueError("threshold_mb must be positive")
                self.threshold_mb = threshold_mb
            else:
                self.threshold_mb = 1024  # Default 1GB
                
            self.cleanup_files: List[str] = []
            self.monitoring_data: List[Dict] = []
            self.is_monitoring = False
            self._monitor_thread = None
            self._initialized = True

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB.
        
        Returns:
            float: Current memory usage in MB
        """
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    def check_memory(self) -> bool:
        """Check if memory usage is below threshold.
        
        Returns:
            bool: True if memory usage is below threshold
        """
        return self.get_memory_usage() < self.threshold_mb

    def add_to_cleanup(self, file_path: str) -> None:
        """Add file to cleanup list.
        
        Args:
            file_path: Path to file to add
        """
        if file_path not in self.cleanup_files:
            self.cleanup_files.append(file_path)

    def remove_from_cleanup(self, file_path: str) -> None:
        """Remove file from cleanup list.
        
        Args:
            file_path: Path to file to remove
        """
        if file_path in self.cleanup_files:
            self.cleanup_files.remove(file_path)

    def cleanup(self) -> None:
        """Clean up files to free memory."""
        for file_path in self.cleanup_files[:]:
            try:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    self.cleanup_files.remove(file_path)
            except OSError as e:
                logger.error(f"Failed to remove {file_path}: {str(e)}")

    def get_process_info(self) -> Dict:
        """Get current process information.
        
        Returns:
            dict: Process information including CPU and memory usage
        """
        process = psutil.Process()
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads()
        }

    def _monitor(self) -> None:
        """Monitor process and collect data."""
        while self.is_monitoring:
            info = self.get_process_info()
            info["timestamp"] = time.time()
            self.monitoring_data.append(info)
            
            # Check memory and cleanup if needed
            if not self.check_memory():
                self.cleanup()
                
            time.sleep(1)  # Monitor every second

    def start_monitoring(self) -> None:
        """Start monitoring process."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self._monitor_thread = threading.Thread(target=self._monitor)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring process."""
        self.is_monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join()
            self._monitor_thread = None

# Global instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get the global MemoryManager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
