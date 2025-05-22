import random
from typing import List, Dict, Optional, Set, Tuple, Any
from ..grammar.parser import GrammarParser
from ..grammar.rule_expander import RuleExpander
from ..config.dialect_config import DialectConfig


class QueryGenerator:
    """Generates Redis Search queries using grammar-based fuzzing."""
    
    def __init__(self, grammar_file: str, dialect_config: DialectConfig, max_depth: int = 10):
        """Initialize the query generator.
        
        Args:
            grammar_file: Path to the grammar file.
            dialect_config: Dialect configuration instance.
            max_depth: Maximum depth for rule expansion.
        """
        self.parser = GrammarParser(grammar_file)
        self.expander = RuleExpander(self.parser, max_depth)
        self.dialect_config = dialect_config
        self.generated_queries: Set[str] = set()
    
    def generate_valid_query(self) -> str:
        """Generate a valid query for the current dialect.
        
        Returns:
            A valid Redis Search query.
        """
        while True:
            query = self.expander.generate_random_query()
            if self._is_valid_query(query):
                self.generated_queries.add(query)
                return query
    
    def generate_invalid_query(self) -> str:
        """Generate an invalid query for the current dialect.
        
        Returns:
            An invalid Redis Search query.
        """
        while True:
            query = self.expander.generate_random_query()
            if not self._is_valid_query(query):
                self.generated_queries.add(query)
                return query
    
    def generate_mixed_queries(self, count: int, valid_ratio: float = 0.7) -> List[str]:
        """Generate a mix of valid and invalid queries.
        
        Args:
            count: Number of queries to generate.
            valid_ratio: Ratio of valid queries to generate.
            
        Returns:
            List of generated queries.
        """
        queries = []
        valid_count = int(count * valid_ratio)
        
        for _ in range(valid_count):
            queries.append(self.generate_valid_query())
        
        for _ in range(count - valid_count):
            queries.append(self.generate_invalid_query())
        
        random.shuffle(queries)
        return queries
    
    def _is_valid_query(self, query: str) -> bool:
        """Check if a query is valid for the current dialect.
        
        Args:
            query: The query to check.
            
        Returns:
            True if the query is valid, False otherwise.
        """
        return self.dialect_config.is_query_valid(query)
    
    def generate_feature_specific_query(self, feature: str) -> Optional[str]:
        """Generate a query that uses a specific feature.
        
        Args:
            feature: The feature to generate a query for.
            
        Returns:
            A query using the specified feature, or None if the feature is not supported.
        """
        if not self.dialect_config.is_feature_supported(feature):
            return None
        
        # TODO: Implement feature-specific query generation
        # This would require mapping features to specific non-terminals in the grammar
        return None
    
    def get_supported_features(self) -> List[str]:
        """Get the list of supported features for the current dialect.
        
        Returns:
            List of supported features.
        """
        return self.dialect_config.get_supported_features()
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about query generation.
        
        Returns:
            Dictionary with generation statistics.
        """
        return {
            "total_queries": len(self.generated_queries),
            "unique_queries": len(set(self.generated_queries)),
            "dialect": self.dialect_config.get_dialect_name(),
            "supported_features": self.get_supported_features(),
            "expansion_stats": self.expander.get_expansion_stats()
        }
    
    def clear_history(self) -> None:
        """Clear the history of generated queries."""
        self.generated_queries.clear()
        self.expander.clear_cache()
    
    def generate_query_batch(self, batch_size: int, valid_ratio: float = 0.7) -> List[Tuple[str, bool]]:
        """Generate a batch of queries with their validity status.
        
        Args:
            batch_size: Number of queries to generate.
            valid_ratio: Ratio of valid queries to generate.
            
        Returns:
            List of tuples containing (query, is_valid).
        """
        queries = self.generate_mixed_queries(batch_size, valid_ratio)
        return [(query, self._is_valid_query(query)) for query in queries]
    
    def generate_targeted_invalid_query(self, feature: str) -> Optional[str]:
        """Generate an invalid query targeting a specific feature.
        
        Args:
            feature: The feature to target.
            
        Returns:
            An invalid query targeting the feature, or None if the feature is not supported.
        """
        if not self.dialect_config.is_feature_supported(feature):
            return None
        
        # TODO: Implement targeted invalid query generation
        # This would require knowledge of how to break each feature
        return None
