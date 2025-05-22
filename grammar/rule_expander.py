import random
from typing import List, Dict, Optional, Set, Tuple
from .parser import GrammarParser, GrammarRule


class RuleExpander:
    """Handles the expansion of grammar rules into concrete queries."""
    
    def __init__(self, parser: GrammarParser, max_depth: int = 10):
        """Initialize the rule expander.
        
        Args:
            parser: The grammar parser instance.
            max_depth: Maximum depth for rule expansion to prevent infinite recursion.
        """
        self.parser = parser
        self.max_depth = max_depth
        self.expansion_cache: Dict[str, List[str]] = {}
        self.terminal_cache: Dict[str, List[str]] = {}
    
    def expand_rule(self, non_terminal: str, depth: int = 0) -> List[str]:
        """Expand a non-terminal into a list of possible expansions.
        
        Args:
            non_terminal: The non-terminal to expand.
            depth: Current expansion depth.
            
        Returns:
            List of possible expansions for the non-terminal.
        """
        if depth >= self.max_depth:
            return []
        
        # Check cache first
        cache_key = f"{non_terminal}_{depth}"
        if cache_key in self.expansion_cache:
            return self.expansion_cache[cache_key]
        
        expansions = []
        rules = self.parser.get_rules_for_non_terminal(non_terminal)
        
        for rule in rules:
            rule_expansions = self._expand_rule_rhs(rule.rhs, depth + 1)
            expansions.extend(rule_expansions)
        
        # Cache the results
        self.expansion_cache[cache_key] = expansions
        return expansions
    
    def _expand_rule_rhs(self, rhs: List[str], depth: int) -> List[str]:
        """Expand the right-hand side of a rule.
        
        Args:
            rhs: Right-hand side of the rule.
            depth: Current expansion depth.
            
        Returns:
            List of possible expansions for the right-hand side.
        """
        if not rhs:
            return [""]
        
        first_symbol = rhs[0]
        rest_symbols = rhs[1:]
        
        # Handle terminal
        if self.parser.is_terminal(first_symbol):
            terminal_values = self._get_terminal_values(first_symbol)
            rest_expansions = self._expand_rule_rhs(rest_symbols, depth)
            
            expansions = []
            for value in terminal_values:
                for rest_expansion in rest_expansions:
                    expansions.append(f"{value}{rest_expansion}")
            return expansions
        
        # Handle non-terminal
        first_expansions = self.expand_rule(first_symbol, depth)
        rest_expansions = self._expand_rule_rhs(rest_symbols, depth)
        
        expansions = []
        for first_expansion in first_expansions:
            for rest_expansion in rest_expansions:
                expansions.append(f"{first_expansion}{rest_expansion}")
        return expansions
    
    def _get_terminal_values(self, terminal: str) -> List[str]:
        """Get the possible values for a terminal, with caching.
        
        Args:
            terminal: The terminal to get values for.
            
        Returns:
            List of possible values for the terminal.
        """
        if terminal not in self.terminal_cache:
            self.terminal_cache[terminal] = self.parser.get_terminal_values(terminal)
        return self.terminal_cache[terminal]
    
    def generate_random_query(self, non_terminal: Optional[str] = None) -> str:
        """Generate a random query by expanding rules.
        
        Args:
            non_terminal: The non-terminal to start from. If None, uses the grammar root.
            
        Returns:
            A randomly generated query.
        """
        if non_terminal is None:
            non_terminal = self.parser.get_root()
            if non_terminal is None:
                raise ValueError("No root symbol found in grammar")
        
        return self._generate_random_expansion(non_terminal)
    
    def _generate_random_expansion(self, symbol: str, depth: int = 0) -> str:
        """Generate a random expansion for a symbol.
        
        Args:
            symbol: The symbol to expand.
            depth: Current expansion depth.
            
        Returns:
            A random expansion for the symbol.
        """
        if depth >= self.max_depth:
            return ""
        
        # Handle terminal
        if self.parser.is_terminal(symbol):
            values = self._get_terminal_values(symbol)
            return random.choice(values)
        
        # Handle non-terminal
        rules = self.parser.get_rules_for_non_terminal(symbol)
        if not rules:
            return ""
        
        rule = random.choice(rules)
        expansion = ""
        
        for rhs_symbol in rule.rhs:
            expansion += self._generate_random_expansion(rhs_symbol, depth + 1)
        
        return expansion
    
    def get_all_possible_queries(self, non_terminal: Optional[str] = None, max_queries: int = 1000) -> List[str]:
        """Get all possible queries up to a maximum number.
        
        Args:
            non_terminal: The non-terminal to start from. If None, uses the grammar root.
            max_queries: Maximum number of queries to generate.
            
        Returns:
            List of possible queries.
        """
        if non_terminal is None:
            non_terminal = self.parser.get_root()
            if non_terminal is None:
                raise ValueError("No root symbol found in grammar")
        
        queries = self.expand_rule(non_terminal)
        return queries[:max_queries]
    
    def clear_cache(self) -> None:
        """Clear the expansion and terminal caches."""
        self.expansion_cache.clear()
        self.terminal_cache.clear()
    
    def get_expansion_stats(self) -> Dict[str, int]:
        """Get statistics about rule expansions.
        
        Returns:
            Dictionary with expansion statistics.
        """
        return {
            "cached_expansions": len(self.expansion_cache),
            "cached_terminals": len(self.terminal_cache),
            "max_depth": self.max_depth
        }
