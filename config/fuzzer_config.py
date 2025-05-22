import os
import yaml
from typing import Dict, List, Any, Optional


class FuzzerConfig:
    """Configuration for the Redis Search Grammar-Based Fuzzer."""
    
    DEFAULT_CONFIG = {
        # Redis connection
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_password": None,
        
        # Generation control
        "dialect_versions": [1, 2, 3, 4],  # Dialects to test
        "valid_query_ratio": 0.7,  # Percentage of valid queries
        "max_query_length": 1000,  # Maximum query length
        "max_generation_depth": 20,  # Rule expansion depth
        
        # Execution control
        "queries_per_second": 100,  # Query rate limit
        "timeout_ms": 5000,  # Query timeout
        "test_duration_seconds": 3600,  # Total test duration
        
        # Feature weights (higher = more frequent generation)
        "feature_weights": {
            "full_text": 1.0,
            "numeric": 0.8,
            "vector": 0.7,
            "geo": 0.5,
            "aggregation": 0.4
        },
        
        # Reporting
        "log_file": "fuzzer_errors.json",
        "log_level": "INFO"
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the fuzzer configuration.
        
        Args:
            config_path: Path to a YAML configuration file. If None, default config is used.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file.
        """
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            
        # Update default config with user values
        if user_config:
            self._update_config(self.config, user_config)
    
    def _update_config(self, base_config: Dict[str, Any], update_config: Dict[str, Any]) -> None:
        """Recursively update the base configuration with user values.
        
        Args:
            base_config: The base configuration dictionary to update.
            update_config: The user configuration dictionary with updates.
        """
        for key, value in update_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._update_config(base_config[key], value)
            else:
                base_config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: The configuration key to retrieve.
            default: Default value if key is not found.
            
        Returns:
            The configuration value or default if not found.
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: The configuration key to set.
            value: The value to set.
        """
        self.config[key] = value
    
    def get_dialect_versions(self) -> List[int]:
        """Get the list of dialect versions to test.
        
        Returns:
            List of dialect version numbers.
        """
        return self.config["dialect_versions"]
    
    def get_feature_weights(self) -> Dict[str, float]:
        """Get the feature weights for query generation.
        
        Returns:
            Dictionary mapping feature names to weights.
        """
        return self.config["feature_weights"]
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get the Redis connection configuration.
        
        Returns:
            Dictionary with Redis connection parameters.
        """
        return {
            "host": self.config["redis_host"],
            "port": self.config["redis_port"],
            "password": self.config["redis_password"]
        }
    
    def get_execution_config(self) -> Dict[str, Any]:
        """Get the execution configuration.
        
        Returns:
            Dictionary with execution parameters.
        """
        return {
            "queries_per_second": self.config["queries_per_second"],
            "timeout_ms": self.config["timeout_ms"],
            "test_duration_seconds": self.config["test_duration_seconds"]
        }
    
    def get_generation_config(self) -> Dict[str, Any]:
        """Get the query generation configuration.
        
        Returns:
            Dictionary with generation parameters.
        """
        return {
            "valid_query_ratio": self.config["valid_query_ratio"],
            "max_query_length": self.config["max_query_length"],
            "max_generation_depth": self.config["max_generation_depth"]
        }
    
    def get_reporting_config(self) -> Dict[str, Any]:
        """Get the reporting configuration.
        
        Returns:
            Dictionary with reporting parameters.
        """
        return {
            "log_file": self.config["log_file"],
            "log_level": self.config["log_level"]
        }
