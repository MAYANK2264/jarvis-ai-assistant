"""Retry and transaction utilities."""

import functools
import logging
import time
from typing import Any, Callable, List, Optional, Type, TypeVar, Union
from contextlib import contextmanager
import shutil
import os
from typing import Dict
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TransactionError(Exception):
    """Error during transaction execution"""

    pass


class Transaction:
    """Class for managing atomic operations with rollback support."""
    
    def __init__(self, parent: Optional["Transaction"] = None):
        """Initialize transaction.
        
        Args:
            parent: Optional parent transaction
        """
        self.operations = []
        self.parent = parent
        self.committed = False
        self.rolled_back = False
        self.backup_files: Dict[str, str] = {}

    def __enter__(self) -> "Transaction":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if exc_type is None and not self.committed and not self.rolled_back:
            self.commit()
        elif exc_type is not None and not self.rolled_back:
            self.rollback()

    def add_operation(
        self,
        forward: Callable[[], Any],
        backward: Callable[[], Any],
        file_path: Optional[str] = None
    ) -> None:
        """Add an operation to the transaction.
        
        Args:
            forward: Function to execute
            backward: Function to rollback
            file_path: Optional file path for backup
        """
        if not callable(forward) or not callable(backward):
            raise ValueError("Forward and backward operations must be callable")
        self.operations.append((forward, backward, file_path))

    def commit(self) -> bool:
        """Commit all operations in the transaction.
        
        Returns:
            bool: True if commit was successful
        """
        if self.committed or self.rolled_back:
            return False

        try:
            # Backup files that will be modified
            for op in self.operations:
                if op[2]:  # If file_path is provided
                    self._backup_file(op[2])

            # Execute all forward operations
            for forward, _, _ in self.operations:
                forward()

            # If we have a parent, add our operations to it
            if self.parent:
                for op in self.operations:
                    self.parent.add_operation(op[0], op[1], op[2])
            
            self.committed = True
            return True
            
        except Exception as e:
            self.rollback()
            raise

    def rollback(self) -> None:
        """Rollback all operations in the transaction."""
        if self.rolled_back:
            return

        # Execute backward operations in reverse order
        for _, backward, _ in reversed(self.operations):
            try:
                backward()
            except Exception as e:
                logger.error(f"Error during rollback: {str(e)}")

        # Restore any backed up files
        self._restore_backups()
        self.rolled_back = True

    def _backup_file(self, file_path: str) -> str:
        """Create a backup of a file"""
        if not os.path.exists(file_path):
            return ""

        # Create temp file
        temp_file = tempfile.mktemp()
        shutil.copy2(file_path, temp_file)
        self.backup_files[file_path] = temp_file
        return temp_file

    def _restore_backups(self):
        """Restore all backed up files"""
        for original, backup in self.backup_files.items():
            if os.path.exists(backup):
                if os.path.exists(original):
                    os.remove(original)
                shutil.copy2(backup, original)
                os.remove(backup)


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    retry_on: Optional[List[Type[Exception]]] = None
) -> Callable:
    """Decorator for retrying functions that may fail.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Delay between retries in seconds
        retry_on: List of exceptions to retry on
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            last_exception = None
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if retry_on and not any(isinstance(e, exc) for exc in retry_on):
                        raise
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed: {str(e)}. "
                            f"Retrying in {delay_seconds} seconds..."
                        )
                        time.sleep(delay_seconds)
                    attempt += 1
            
            logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
            
        return wrapper
    return decorator


def transactional(func: Callable) -> Callable:
    """Decorator for making functions transactional.
    
    Args:
        func: Function to make transactional
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        transaction = Transaction()
        try:
            result = func(*args, transaction=transaction, **kwargs)
            transaction.commit()
            return result
        except Exception as e:
            transaction.rollback()
            raise
    return wrapper
