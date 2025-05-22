import re
from typing import Dict, List, Set, Tuple, Optional, Any


class GrammarRule:
    """Represents a grammar rule in the Redis Search query grammar."""
    
    def __init__(self, lhs: str, rhs: List[str]):
        """Initialize a grammar rule.
        
        Args:
            lhs: Left-hand side of the rule (non-terminal).
            rhs: Right-hand side of the rule (sequence of terminals and non-terminals).
        """
        self.lhs = lhs
        self.rhs = rhs
    
    def __str__(self) -> str:
        """String representation of the rule."""
        return f"{self.lhs} ::= {' '.join(self.rhs)}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the rule."""
        return f"GrammarRule(lhs='{self.lhs}', rhs={self.rhs})"


class GrammarParser:
    """Parser for the Redis Search query grammar."""
    
    def __init__(self, grammar_file: str):
        """Initialize the grammar parser.
        
        Args:
            grammar_file: Path to the grammar file (query_generator.py).
        """
        self.grammar_file = grammar_file
        self.rules: Dict[str, List[GrammarRule]] = {}
        self.terminals: Dict[str, List[str]] = {}
        self.non_terminals: Set[str] = set()
        self.root: Optional[str] = None
        
        self._parse_grammar_file()
    
    def _parse_grammar_file(self) -> None:
        """Parse the grammar file and extract rules and terminals."""
        with open(self.grammar_file, 'r') as f:
            content = f.read()
        
        # Extract root symbol
        root_match = re.search(r'root\s*=\s*"([^"]+)"', content)
        if root_match:
            self.root = root_match.group(1)
        
        # Extract rules
        rule_pattern = r'"([^"]+)\s*::=\s*([^"]+)"'
        for match in re.finditer(rule_pattern, content):
            lhs, rhs_str = match.groups()
            rhs = rhs_str.strip().split()
            
            rule = GrammarRule(lhs, rhs)
            
            if lhs not in self.rules:
                self.rules[lhs] = []
            self.rules[lhs].append(rule)
            
            self.non_terminals.add(lhs)
        
        # Extract terminals
        terminal_pattern = r'"([^"]+)":\s*\[(.*?)\]'
        for match in re.finditer(terminal_pattern, content):
            terminal_name, values_str = match.groups()
            values = [v.strip().strip('"') for v in values_str.split(',')]
            self.terminals[terminal_name] = values
    
    def get_rules_for_non_terminal(self, non_terminal: str) -> List[GrammarRule]:
        """Get all rules for a non-terminal.
        
        Args:
            non_terminal: The non-terminal to get rules for.
            
        Returns:
            List of grammar rules for the non-terminal.
        """
        return self.rules.get(non_terminal, [])
    
    def get_terminals(self) -> Dict[str, List[str]]:
        """Get all terminals in the grammar.
        
        Returns:
            Dictionary mapping terminal names to their possible values.
        """
        return self.terminals
    
    def get_non_terminals(self) -> Set[str]:
        """Get all non-terminals in the grammar.
        
        Returns:
            Set of non-terminal names.
        """
        return self.non_terminals
    
    def get_root(self) -> Optional[str]:
        """Get the root symbol of the grammar.
        
        Returns:
            The root symbol, or None if not found.
        """
        return self.root
    
    def is_terminal(self, symbol: str) -> bool:
        """Check if a symbol is a terminal.
        
        Args:
            symbol: The symbol to check.
            
        Returns:
            True if the symbol is a terminal, False otherwise.
        """
        return symbol in self.terminals
    
    def is_non_terminal(self, symbol: str) -> bool:
        """Check if a symbol is a non-terminal.
        
        Args:
            symbol: The symbol to check.
            
        Returns:
            True if the symbol is a non-terminal, False otherwise.
        """
        return symbol in self.non_terminals
    
    def get_terminal_values(self, terminal: str) -> List[str]:
        """Get the possible values for a terminal.
        
        Args:
            terminal: The terminal to get values for.
            
        Returns:
            List of possible values for the terminal.
        """
        return self.terminals.get(terminal, [])
    
    def get_rule_table(self) -> Dict[str, List[List[str]]]:
        """Get a rule table for query generation.
        
        Returns:
            Dictionary mapping non-terminals to lists of right-hand sides.
        """
        rule_table = {}
        for non_terminal, rules in self.rules.items():
            rule_table[non_terminal] = [rule.rhs for rule in rules]
        return rule_table
    
    def get_grammar_info(self) -> Dict[str, Any]:
        """Get information about the grammar.
        
        Returns:
            Dictionary with grammar information.
        """
        return {
            "root": self.root,
            "non_terminals": list(self.non_terminals),
            "terminals": list(self.terminals.keys()),
            "rule_count": sum(len(rules) for rules in self.rules.values()),
            "terminal_value_count": sum(len(values) for values in self.terminals.values())
        }
