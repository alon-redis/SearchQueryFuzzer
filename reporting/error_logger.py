import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set, Tuple, Any, Union
from pathlib import Path


class ErrorLogger:
    """Handles logging of errors and issues during fuzzing."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize the error logger.
        
        Args:
            log_dir: Directory to store log files.
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("redisearch_fuzzer")
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        self._setup_handlers()
        
        # Initialize error tracking
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.crashes: List[Dict[str, Any]] = []
    
    def _setup_handlers(self) -> None:
        """Set up logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # File handler
        log_file = self.log_dir / f"fuzzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
    
    def log_error(self, error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log an error.
        
        Args:
            error_type: Type of error.
            message: Error message.
            details: Additional error details.
        """
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": message,
            "details": details or {}
        }
        
        self.errors.append(error_info)
        self.logger.error(f"{error_type}: {message}")
        
        if details:
            self.logger.debug(f"Error details: {json.dumps(details, indent=2)}")
    
    def log_warning(self, warning_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning.
        
        Args:
            warning_type: Type of warning.
            message: Warning message.
            details: Additional warning details.
        """
        warning_info = {
            "timestamp": datetime.now().isoformat(),
            "type": warning_type,
            "message": message,
            "details": details or {}
        }
        
        self.warnings.append(warning_info)
        self.logger.warning(f"{warning_type}: {message}")
        
        if details:
            self.logger.debug(f"Warning details: {json.dumps(details, indent=2)}")
    
    def log_crash(self, crash_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log a crash.
        
        Args:
            crash_type: Type of crash.
            message: Crash message.
            details: Additional crash details.
        """
        crash_info = {
            "timestamp": datetime.now().isoformat(),
            "type": crash_type,
            "message": message,
            "details": details or {}
        }
        
        self.crashes.append(crash_info)
        self.logger.critical(f"CRASH - {crash_type}: {message}")
        
        if details:
            self.logger.debug(f"Crash details: {json.dumps(details, indent=2)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of logged errors.
        
        Returns:
            Dictionary containing error summary.
        """
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "total_crashes": len(self.crashes),
            "error_types": self._count_types(self.errors),
            "warning_types": self._count_types(self.warnings),
            "crash_types": self._count_types(self.crashes)
        }
    
    def _count_types(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count occurrences of each type in a list of items.
        
        Args:
            items: List of items to count.
            
        Returns:
            Dictionary mapping types to counts.
        """
        type_counts = {}
        for item in items:
            error_type = item["type"]
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
        return type_counts
    
    def get_errors_by_type(self, error_type: str) -> List[Dict[str, Any]]:
        """Get all errors of a specific type.
        
        Args:
            error_type: Type of errors to retrieve.
            
        Returns:
            List of error dictionaries.
        """
        return [e for e in self.errors if e["type"] == error_type]
    
    def get_warnings_by_type(self, warning_type: str) -> List[Dict[str, Any]]:
        """Get all warnings of a specific type.
        
        Args:
            warning_type: Type of warnings to retrieve.
            
        Returns:
            List of warning dictionaries.
        """
        return [w for w in self.warnings if w["type"] == warning_type]
    
    def get_crashes_by_type(self, crash_type: str) -> List[Dict[str, Any]]:
        """Get all crashes of a specific type.
        
        Args:
            crash_type: Type of crashes to retrieve.
            
        Returns:
            List of crash dictionaries.
        """
        return [c for c in self.crashes if c["type"] == crash_type]
    
    def save_error_report(self, filename: Optional[str] = None) -> str:
        """Save error report to a file.
        
        Args:
            filename: Name of the report file. If None, a timestamp-based name is used.
            
        Returns:
            Path to the saved report file.
        """
        if filename is None:
            filename = f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = self.log_dir / filename
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "errors": self.errors,
            "warnings": self.warnings,
            "crashes": self.crashes
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)
    
    def clear_history(self) -> None:
        """Clear the error history."""
        self.errors.clear()
        self.warnings.clear()
        self.crashes.clear()
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent errors.
        
        Args:
            limit: Maximum number of errors to return.
            
        Returns:
            List of recent error dictionaries.
        """
        return sorted(
            self.errors,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
    
    def get_recent_warnings(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent warnings.
        
        Args:
            limit: Maximum number of warnings to return.
            
        Returns:
            List of recent warning dictionaries.
        """
        return sorted(
            self.warnings,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
    
    def get_recent_crashes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent crashes.
        
        Args:
            limit: Maximum number of crashes to return.
            
        Returns:
            List of recent crash dictionaries.
        """
        return sorted(
            self.crashes,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:limit]
