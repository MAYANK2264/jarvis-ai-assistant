"""Database manager module for handling SQLite operations."""

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Singleton class for managing SQLite database operations."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, db_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: Optional[str] = None):
        if not self._initialized:
            self.db_path = db_path or os.path.join(os.getcwd(), "jarvis.db")
            self._init_db()
            self._initialized = True

    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic closing."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        finally:
            if conn:
                conn.close()

    def _init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # File metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    size INTEGER,
                    created_at TIMESTAMP,
                    modified_at TIMESTAMP,
                    file_type TEXT,
                    is_directory BOOLEAN,
                    tags TEXT,
                    metadata TEXT
                )
            """)

            # File operations log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS operation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    source_path TEXT,
                    target_path TEXT,
                    status TEXT,
                    error TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Performance metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    duration_ms INTEGER,
                    memory_usage INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def update_file_metadata(self, file_path: str, metadata: Dict[str, Any]):
        """Update or insert file metadata"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Convert metadata dict to JSON for storage
                metadata_json = json.dumps(metadata.get("metadata", {}))
                tags_json = json.dumps(metadata.get("tags", []))

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO file_metadata 
                    (path, name, size, created_at, modified_at, file_type, is_directory, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_path,
                        metadata["name"],
                        metadata.get("size", 0),
                        metadata.get("created_at"),
                        metadata.get("modified_at"),
                        metadata.get("file_type"),
                        metadata.get("is_directory", False),
                        tags_json,
                        metadata_json,
                    ),
                )

                conn.commit()

        except Exception as e:
            logger.error(f"Error updating file metadata: {str(e)}")
            raise

    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by path"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM file_metadata WHERE path = ?", (file_path,)
                )
                row = cursor.fetchone()

                if row:
                    return {
                        "path": row[1],
                        "name": row[2],
                        "size": row[3],
                        "created_at": row[4],
                        "modified_at": row[5],
                        "file_type": row[6],
                        "is_directory": bool(row[7]),
                        "tags": json.loads(row[8]),
                        "metadata": json.loads(row[9]),
                    }
                return None

        except Exception as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return None

    def log_operation(self, operation: str, source_path: str, target_path: str, status: str, error: str = None):
        """Log a file operation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO operation_log 
                (operation, source_path, target_path, status, error)
                VALUES (?, ?, ?, ?, ?)
            """, (operation, source_path, target_path, status, error))
            conn.commit()

    def log_performance(self, operation: str, duration_ms: int, memory_usage: int):
        """Log performance metrics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics 
                (operation, duration_ms, memory_usage)
                VALUES (?, ?, ?)
            """, (operation, duration_ms, memory_usage))
            conn.commit()

    def search_files(self, query: str) -> List[Dict[str, Any]]:
        """Search files by name, tags, or metadata."""
        if query is None:
            return []
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM file_metadata 
                WHERE name LIKE ? OR tags LIKE ? OR metadata LIKE ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "path": row[1],
                    "name": row[2],
                    "size": row[3],
                    "created_at": row[4],
                    "modified_at": row[5],
                    "file_type": row[6],
                    "is_directory": bool(row[7]),
                    "tags": json.loads(row[8] or "[]"),
                    "metadata": json.loads(row[9] or "{}")
                })
            return results

# Global instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get the global DatabaseManager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
