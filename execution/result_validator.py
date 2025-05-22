from typing import List, Dict, Optional, Set, Tuple, Any, Union
from ..config.dialect_config import DialectConfig


class ResultValidator:
    """Validates Redis Search query execution results."""
    
    def __init__(self, dialect_config: DialectConfig):
        """Initialize the result validator.
        
        Args:
            dialect_config: Dialect configuration instance.
        """
        self.dialect_config = dialect_config
        self.validation_history: Dict[str, Dict[str, Any]] = {}
    
    def validate_result(self, query: str, result: Dict[str, Any], expected_valid: bool) -> Dict[str, Any]:
        """Validate a query execution result.
        
        Args:
            query: The executed query.
            result: The execution result.
            expected_valid: Whether the query was expected to be valid.
            
        Returns:
            Dictionary containing validation results and metadata.
        """
        validation_info = {
            "query": query,
            "expected_valid": expected_valid,
            "actual_valid": result["success"],
            "execution_time": result.get("execution_time", 0),
            "error": result.get("error"),
            "validation_errors": []
        }
        
        # Check if the result matches expectations
        if expected_valid != result["success"]:
            validation_info["validation_errors"].append(
                f"Unexpected {'success' if result['success'] else 'failure'}"
            )
        
        # Validate execution time
        if result["success"] and result.get("execution_time", 0) > 1000:  # 1 second threshold
            validation_info["validation_errors"].append(
                f"Slow execution time: {result['execution_time']}ms"
            )
        
        # Validate error messages for invalid queries
        if not result["success"] and expected_valid:
            validation_info["validation_errors"].append(
                f"Unexpected error: {result.get('error', 'Unknown error')}"
            )
        
        # Record validation history
        self.validation_history[query] = validation_info
        
        return validation_info
    
    def validate_result_batch(self, results: List[Tuple[str, Dict[str, Any], bool]]) -> List[Dict[str, Any]]:
        """Validate a batch of query execution results.
        
        Args:
            results: List of tuples containing (query, result, expected_valid).
            
        Returns:
            List of validation results.
        """
        return [
            self.validate_result(query, result, expected_valid)
            for query, result, expected_valid in results
        ]
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get statistics about result validation.
        
        Returns:
            Dictionary with validation statistics.
        """
        total_validations = len(self.validation_history)
        if total_validations == 0:
            return {
                "total_validations": 0,
                "matching_expectations": 0,
                "mismatching_expectations": 0,
                "match_rate": 0
            }
        
        matching_expectations = sum(
            1 for info in self.validation_history.values()
            if info["expected_valid"] == info["actual_valid"]
        )
        mismatching_expectations = total_validations - matching_expectations
        
        return {
            "total_validations": total_validations,
            "matching_expectations": matching_expectations,
            "mismatching_expectations": mismatching_expectations,
            "match_rate": matching_expectations / total_validations
        }
    
    def clear_history(self) -> None:
        """Clear the validation history."""
        self.validation_history.clear()
    
    def get_validation_errors(self) -> List[Dict[str, Any]]:
        """Get information about validation errors.
        
        Returns:
            List of dictionaries containing validation error information.
        """
        return [
            {
                "query": query,
                "expected_valid": info["expected_valid"],
                "actual_valid": info["actual_valid"],
                "errors": info["validation_errors"]
            }
            for query, info in self.validation_history.items()
            if info["validation_errors"]
        ]
    
    def get_unexpected_successes(self) -> List[Dict[str, Any]]:
        """Get information about queries that succeeded unexpectedly.
        
        Returns:
            List of dictionaries containing unexpected success information.
        """
        return [
            {
                "query": query,
                "execution_time": info["execution_time"],
                "error": info["error"]
            }
            for query, info in self.validation_history.items()
            if not info["expected_valid"] and info["actual_valid"]
        ]
    
    def get_unexpected_failures(self) -> List[Dict[str, Any]]:
        """Get information about queries that failed unexpectedly.
        
        Returns:
            List of dictionaries containing unexpected failure information.
        """
        return [
            {
                "query": query,
                "error": info["error"]
            }
            for query, info in self.validation_history.items()
            if info["expected_valid"] and not info["actual_valid"]
        ]
    
    def get_validation_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get the validation result for a specific query.
        
        Args:
            query: The query to look up.
            
        Returns:
            Validation result dictionary, or None if not found.
        """
        return self.validation_history.get(query)
