from typing import Dict, List, Set, Any, Optional
import re


class DialectConfig:
    """Configuration for Redis Search dialects."""
    
    # Define dialect-specific features and constraints
    DIALECT_FEATURES = {
        1: {
            "name": "Legacy",
            "features": {
                "full_text": True,
                "numeric": True,
                "geo": True,
                "vector": False,
                "aggregation": True,
                "wildcard": False,
                "parameterized": False,
                "dialect_specifier": False
            },
            "forbidden_patterns": [
                r"\*=>\[KNN",  # Vector search not supported
                r"\$[a-zA-Z0-9_]+",  # Parameters not supported
                r"DIALECT\s+\d+",  # Dialect specifier not supported
                r"@field:@numeric:\[",  # Field-specific numeric ranges not supported
                r"@field:\(@numeric:\[",  # Nested numeric ranges not supported
                r"@field:\{.*\}\}\}\}",  # Extra closing braces not supported
                r"@field:\(w'\*'\)",  # Wildcard with w prefix not supported
                r"@field:\(w'[^']*'\)",  # Wildcard with w prefix not supported
                r"@field:\([^)]*\)",  # Complex field expressions not supported
            ]
        },
        2: {
            "name": "Modern",
            "features": {
                "full_text": True,
                "numeric": True,
                "geo": True,
                "vector": True,
                "aggregation": True,
                "wildcard": True,
                "parameterized": True,
                "dialect_specifier": True
            },
            "forbidden_patterns": [
                r"@field:@numeric:\[",  # Field-specific numeric ranges not supported
                r"@field:\(@numeric:\[",  # Nested numeric ranges not supported
                r"@field:\{.*\}\}\}\}",  # Extra closing braces not supported
                r"@field:\([^)]*\)",  # Complex field expressions not supported
            ]
        },
        3: {
            "name": "Extended",
            "features": {
                "full_text": True,
                "numeric": True,
                "geo": True,
                "vector": True,
                "aggregation": True,
                "wildcard": True,
                "parameterized": True,
                "dialect_specifier": True
            },
            "forbidden_patterns": [
                r"@field:\{.*\}\}\}\}",  # Extra closing braces not supported
            ]
        },
        4: {
            "name": "Latest",
            "features": {
                "full_text": True,
                "numeric": True,
                "geo": True,
                "vector": True,
                "aggregation": True,
                "wildcard": True,
                "parameterized": True,
                "dialect_specifier": True
            },
            "forbidden_patterns": []
        }
    }
    
    def __init__(self, dialect_version: int):
        """Initialize the dialect configuration.
        
        Args:
            dialect_version: The Redis Search dialect version (1-4).
        """
        if dialect_version not in self.DIALECT_FEATURES:
            raise ValueError(f"Unsupported dialect version: {dialect_version}")
        
        self.dialect_version = dialect_version
        self.dialect_info = self.DIALECT_FEATURES[dialect_version]
        self._compile_forbidden_patterns()
    
    def _compile_forbidden_patterns(self) -> None:
        """Compile the forbidden patterns for efficient matching."""
        self.forbidden_regexes = [
            re.compile(pattern) for pattern in self.dialect_info["forbidden_patterns"]
        ]
    
    def is_feature_supported(self, feature: str) -> bool:
        """Check if a feature is supported in this dialect.
        
        Args:
            feature: The feature to check.
            
        Returns:
            True if the feature is supported, False otherwise.
        """
        return self.dialect_info["features"].get(feature, False)
    
    def get_supported_features(self) -> List[str]:
        """Get the list of supported features for this dialect.
        
        Returns:
            List of supported feature names.
        """
        return [
            feature for feature, supported in self.dialect_info["features"].items()
            if supported
        ]
    
    def is_query_valid(self, query: str) -> bool:
        """Check if a query is valid for this dialect.
        
        Args:
            query: The query to validate.
            
        Returns:
            True if the query is valid, False otherwise.
        """
        # Check for forbidden patterns
        for pattern in self.forbidden_regexes:
            if pattern.search(query):
                return False
        
        return True
    
    def get_dialect_name(self) -> str:
        """Get the name of this dialect.
        
        Returns:
            The dialect name.
        """
        return self.dialect_info["name"]
    
    def get_dialect_version(self) -> int:
        """Get the dialect version.
        
        Returns:
            The dialect version number.
        """
        return self.dialect_version
    
    def get_forbidden_patterns(self) -> List[str]:
        """Get the list of forbidden patterns for this dialect.
        
        Returns:
            List of forbidden pattern strings.
        """
        return self.dialect_info["forbidden_patterns"]
    
    @classmethod
    def get_supported_dialects(cls) -> List[int]:
        """Get the list of supported dialect versions.
        
        Returns:
            List of supported dialect version numbers.
        """
        return list(cls.DIALECT_FEATURES.keys())
    
    @classmethod
    def get_dialect_info(cls, dialect_version: int) -> Dict[str, Any]:
        """Get information about a specific dialect.
        
        Args:
            dialect_version: The dialect version to get info for.
            
        Returns:
            Dictionary with dialect information.
            
        Raises:
            ValueError: If the dialect version is not supported.
        """
        if dialect_version not in cls.DIALECT_FEATURES:
            raise ValueError(f"Unsupported dialect version: {dialect_version}")
        
        return cls.DIALECT_FEATURES[dialect_version]
