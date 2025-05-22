"""
Redis Search Query Grammar

This file defines the grammar rules for Redis Search queries across different dialects.
The grammar is defined using a simple format where each rule is specified as:
"lhs ::= rhs" where lhs is a non-terminal and rhs is a sequence of terminals and non-terminals.
"""

# Root symbol
root = "query"

# Grammar rules
rules = [
    # Basic query structure
    "query ::= expr",
    "query ::= expr expr",
    "query ::= expr expr expr",
    
    # Expressions
    "expr ::= term",
    "expr ::= term operator term",
    "expr ::= ( expr )",
    "expr ::= -expr",
    
    # Terms
    "term ::= field",
    "term ::= value",
    "term ::= range",
    "term ::= geo",
    "term ::= vector",
    
    # Fields
    "field ::= @field_name",
    "field ::= @field_name:",
    
    # Values
    "value ::= string",
    "value ::= number",
    "value ::= boolean",
    
    # Ranges
    "range ::= [ number number ]",
    "range ::= ( number number )",
    "range ::= { number number }",
    
    # Geo queries
    "geo ::= @geo_field:[ longitude latitude radius unit ]",
    
    # Vector queries
    "vector ::= *=>[KNN number @vector_field $BLOB ]",
    
    # Operators
    "operator ::= +",
    "operator ::= -",
    "operator ::= |",
    "operator ::= &",
    
    # Dialect-specific rules
    "query ::= DIALECT number query",  # Dialect 2+
    "value ::= $param",  # Dialect 2+
    "term ::= wildcard",  # Dialect 2+
    "wildcard ::= *",
    "wildcard ::= ?",
    "wildcard ::= [chars]",
]

# Terminals
terminals = {
    "field_name": [
        "title", "body", "tags", "price", "date", "location",
        "vector", "score", "category", "status"
    ],
    "string": [
        "hello", "world", "test", "example", "redis", "search",
        "query", "fuzzer", "grammar", "parser"
    ],
    "number": [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "10", "100", "1000", "0.5", "1.5", "2.5", "-1", "-10"
    ],
    "boolean": [
        "true", "false"
    ],
    "unit": [
        "m", "km", "mi", "ft"
    ],
    "param": [
        "$BLOB", "$VECTOR", "$RADIUS", "$QUERY", "$DIALECT"
    ],
    "chars": [
        "a-z", "A-Z", "0-9", "a-zA-Z", "a-z0-9"
    ]
}

# Feature mapping
feature_mapping = {
    "full_text": ["term", "value", "string"],
    "numeric": ["range", "number"],
    "geo": ["geo"],
    "vector": ["vector"],
    "aggregation": ["operator"],
    "wildcard": ["wildcard"],
    "parameterized": ["param"],
    "dialect_specifier": ["DIALECT"]
} 