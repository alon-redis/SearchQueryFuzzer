import random
from typing import List, Dict, Optional, Set, Tuple, Any
from ..config.dialect_config import DialectConfig


class MutationEngine:
    """Generates invalid queries by mutating valid ones."""
    
    def __init__(self, dialect_config: DialectConfig):
        """Initialize the mutation engine.
        
        Args:
            dialect_config: Dialect configuration instance.
        """
        self.dialect_config = dialect_config
        self.mutation_history: Dict[str, List[str]] = {}
    
    def mutate_query(self, query: str, mutation_type: Optional[str] = None) -> str:
        """Mutate a query to create an invalid version.
        
        Args:
            query: The query to mutate.
            mutation_type: Type of mutation to apply. If None, a random type is chosen.
            
        Returns:
            A mutated (potentially invalid) query.
        """
        if mutation_type is None:
            mutation_type = random.choice(self._get_available_mutations())
        
        if mutation_type == "syntax_error":
            return self._add_syntax_error(query)
        elif mutation_type == "feature_mismatch":
            return self._create_feature_mismatch(query)
        elif mutation_type == "parameter_error":
            return self._corrupt_parameter(query)
        elif mutation_type == "length_error":
            return self._create_length_error(query)
        else:
            raise ValueError(f"Unknown mutation type: {mutation_type}")
    
    def _get_available_mutations(self) -> List[str]:
        """Get the list of available mutation types.
        
        Returns:
            List of mutation type names.
        """
        return [
            "syntax_error",
            "feature_mismatch",
            "parameter_error",
            "length_error"
        ]
    
    def _add_syntax_error(self, query: str) -> str:
        """Add a syntax error to the query.
        
        Args:
            query: The query to mutate.
            
        Returns:
            A query with a syntax error.
        """
        # Randomly choose a syntax error to introduce
        error_type = random.choice([
            "missing_bracket",
            "extra_bracket",
            "invalid_operator",
            "missing_quote",
            "extra_quote"
        ])
        
        if error_type == "missing_bracket":
            # Remove a random bracket
            brackets = ["(", ")", "[", "]", "{", "}"]
            bracket = random.choice(brackets)
            return query.replace(bracket, "", 1)
        
        elif error_type == "extra_bracket":
            # Add a random bracket
            brackets = ["(", ")", "[", "]", "{", "}"]
            bracket = random.choice(brackets)
            pos = random.randint(0, len(query))
            return query[:pos] + bracket + query[pos:]
        
        elif error_type == "invalid_operator":
            # Replace a valid operator with an invalid one
            operators = ["+", "-", "*", "/", "%", "&", "|", "^", "~"]
            operator = random.choice(operators)
            pos = random.randint(0, len(query) - 1)
            return query[:pos] + operator + query[pos + 1:]
        
        elif error_type == "missing_quote":
            # Remove a quote
            quotes = ["'", '"']
            quote = random.choice(quotes)
            return query.replace(quote, "", 1)
        
        else:  # extra_quote
            # Add a quote
            quotes = ["'", '"']
            quote = random.choice(quotes)
            pos = random.randint(0, len(query))
            return query[:pos] + quote + query[pos:]
    
    def _create_feature_mismatch(self, query: str) -> str:
        """Create a feature mismatch in the query.
        
        Args:
            query: The query to mutate.
            
        Returns:
            A query with a feature mismatch.
        """
        # Get unsupported features for the current dialect
        supported_features = set(self.dialect_config.get_supported_features())
        all_features = {
            "full_text", "numeric", "geo", "vector", "aggregation",
            "wildcard", "parameterized", "dialect_specifier"
        }
        unsupported_features = all_features - supported_features
        
        if not unsupported_features:
            return self._add_syntax_error(query)
        
        # TODO: Implement feature-specific mutations
        # This would require knowledge of how each feature is represented in queries
        return self._add_syntax_error(query)
    
    def _corrupt_parameter(self, query: str) -> str:
        """Corrupt a parameter in the query.
        
        Args:
            query: The query to mutate.
            
        Returns:
            A query with a corrupted parameter.
        """
        # Randomly choose a parameter corruption method
        corruption_type = random.choice([
            "invalid_type",
            "out_of_range",
            "missing_required",
            "extra_parameter"
        ])
        
        # TODO: Implement parameter-specific corruptions
        # This would require knowledge of parameter types and valid ranges
        return self._add_syntax_error(query)
    
    def _create_length_error(self, query: str) -> str:
        """Create a length-related error in the query.
        
        Args:
            query: The query to mutate.
            
        Returns:
            A query with a length error.
        """
        # Randomly choose a length error to introduce
        error_type = random.choice([
            "too_long",
            "too_short",
            "empty"
        ])
        
        if error_type == "too_long":
            # Make the query too long by repeating parts
            return query * 10
        
        elif error_type == "too_short":
            # Make the query too short by truncating
            return query[:2]
        
        else:  # empty
            return ""
    
    def get_mutation_stats(self) -> Dict[str, Any]:
        """Get statistics about query mutations.
        
        Returns:
            Dictionary with mutation statistics.
        """
        return {
            "total_mutations": sum(len(mutations) for mutations in self.mutation_history.values()),
            "unique_original_queries": len(self.mutation_history),
            "mutation_types": self._get_available_mutations()
        }
    
    def clear_history(self) -> None:
        """Clear the mutation history."""
        self.mutation_history.clear()
    
    def mutate_query_batch(self, queries: List[str], mutation_ratio: float = 0.3) -> List[Tuple[str, str]]:
        """Mutate a batch of queries.
        
        Args:
            queries: List of queries to mutate.
            mutation_ratio: Ratio of queries to mutate.
            
        Returns:
            List of tuples containing (original_query, mutated_query).
        """
        results = []
        for query in queries:
            if random.random() < mutation_ratio:
                mutated = self.mutate_query(query)
                results.append((query, mutated))
                
                if query not in self.mutation_history:
                    self.mutation_history[query] = []
                self.mutation_history[query].append(mutated)
            else:
                results.append((query, query))
        
        return results
