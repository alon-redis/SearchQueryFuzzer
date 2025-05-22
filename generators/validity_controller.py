from typing import List, Dict, Optional, Set, Tuple, Any
from ..config.dialect_config import DialectConfig
from .mutation_engine import MutationEngine


class ValidityController:
    """Controls the generation of valid and invalid queries."""
    
    def __init__(self, dialect_config: DialectConfig, mutation_engine: MutationEngine):
        """Initialize the validity controller.
        
        Args:
            dialect_config: Dialect configuration instance.
            mutation_engine: Mutation engine instance.
        """
        self.dialect_config = dialect_config
        self.mutation_engine = mutation_engine
        self.valid_queries: Set[str] = set()
        self.invalid_queries: Set[str] = set()
        self.feature_coverage: Dict[str, int] = {}
    
    def validate_query(self, query: str) -> bool:
        """Validate a query against the dialect configuration.
        
        Args:
            query: The query to validate.
            
        Returns:
            True if the query is valid, False otherwise.
        """
        return self.dialect_config.is_query_valid(query)
    
    def register_valid_query(self, query: str) -> None:
        """Register a valid query.
        
        Args:
            query: The valid query to register.
        """
        self.valid_queries.add(query)
        self._update_feature_coverage(query)
    
    def register_invalid_query(self, query: str) -> None:
        """Register an invalid query.
        
        Args:
            query: The invalid query to register.
        """
        self.invalid_queries.add(query)
    
    def _update_feature_coverage(self, query: str) -> None:
        """Update feature coverage statistics for a query.
        
        Args:
            query: The query to analyze.
        """
        # TODO: Implement feature detection in queries
        # This would require parsing the query to identify used features
        pass
    
    def get_validity_stats(self) -> Dict[str, Any]:
        """Get statistics about query validity.
        
        Returns:
            Dictionary with validity statistics.
        """
        return {
            "valid_queries": len(self.valid_queries),
            "invalid_queries": len(self.invalid_queries),
            "validity_ratio": len(self.valid_queries) / (len(self.valid_queries) + len(self.invalid_queries))
            if (len(self.valid_queries) + len(self.invalid_queries)) > 0 else 0,
            "feature_coverage": self.feature_coverage
        }
    
    def clear_history(self) -> None:
        """Clear the query history and statistics."""
        self.valid_queries.clear()
        self.invalid_queries.clear()
        self.feature_coverage.clear()
        self.mutation_engine.clear_history()
    
    def generate_validity_batch(self, batch_size: int, valid_ratio: float = 0.7) -> List[Tuple[str, bool]]:
        """Generate a batch of queries with controlled validity ratio.
        
        Args:
            batch_size: Number of queries to generate.
            valid_ratio: Desired ratio of valid queries.
            
        Returns:
            List of tuples containing (query, is_valid).
        """
        valid_count = int(batch_size * valid_ratio)
        invalid_count = batch_size - valid_count
        
        # Generate valid queries
        valid_queries = list(self.valid_queries)[:valid_count]
        while len(valid_queries) < valid_count:
            # TODO: Generate new valid queries
            pass
        
        # Generate invalid queries
        invalid_queries = list(self.invalid_queries)[:invalid_count]
        while len(invalid_queries) < invalid_count:
            # Generate invalid queries by mutating valid ones
            if valid_queries:
                original = valid_queries[0]
                mutated = self.mutation_engine.mutate_query(original)
                if not self.validate_query(mutated):
                    invalid_queries.append(mutated)
                    self.register_invalid_query(mutated)
        
        # Combine and shuffle
        all_queries = [(q, True) for q in valid_queries] + [(q, False) for q in invalid_queries]
        random.shuffle(all_queries)
        
        return all_queries
    
    def get_feature_coverage(self) -> Dict[str, float]:
        """Get the coverage of each feature in the generated queries.
        
        Returns:
            Dictionary mapping features to their coverage ratio.
        """
        total_queries = len(self.valid_queries)
        if total_queries == 0:
            return {}
        
        return {
            feature: count / total_queries
            for feature, count in self.feature_coverage.items()
        }
    
    def get_missing_features(self) -> List[str]:
        """Get the list of features that haven't been covered.
        
        Returns:
            List of features with zero coverage.
        """
        all_features = set(self.dialect_config.get_supported_features())
        covered_features = set(self.feature_coverage.keys())
        return list(all_features - covered_features)
    
    def get_least_covered_features(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get the features with the lowest coverage.
        
        Args:
            limit: Maximum number of features to return.
            
        Returns:
            List of tuples containing (feature, coverage_ratio).
        """
        coverage = self.get_feature_coverage()
        sorted_features = sorted(coverage.items(), key=lambda x: x[1])
        return sorted_features[:limit]
