root = "query"
rules = [
    "query ::= expr",
    "query ::=",
    "query ::= star",
    "expr ::= text_expr",
    "expr ::= expr expr",
    "expr ::= text_expr expr",
    "expr ::= expr text_expr",
    "text_expr ::= text_expr text_expr",
    "expr ::= union",
    "union ::= expr OR expr",
    "union ::= union OR expr",
    "union ::= text_expr OR expr",
    "union ::= expr OR text_expr",
    "text_expr ::= text_union",
    "text_union ::= text_expr OR text_expr",
    "text_union ::= text_union OR text_expr",
    "expr ::= modifier COLON text_expr",
    "expr ::= modifierlist COLON text_expr",
    "expr ::= LP expr RP",
    "text_expr ::= LP text_expr RP",
    "attribute ::= ATTRIBUTE COLON param_term",
    "attribute_list ::= attribute",
    "attribute_list ::= attribute_list SEMICOLON attribute",
    "attribute_list ::= attribute_list SEMICOLON",
    "attribute_list ::=",
    "expr ::= expr ARROW LB attribute_list RB",
    "text_expr ::= text_expr ARROW LB attribute_list RB",
    "text_expr ::= QUOTE termlist QUOTE",
    "text_expr ::= QUOTE term QUOTE",
    "text_expr ::= QUOTE ATTRIBUTE QUOTE",
    "text_expr ::= param_term",
    "text_expr ::= affix",
    "text_expr ::= verbatim",
    "termlist ::= param_term param_term",
    "termlist ::= termlist param_term",
    "expr ::= MINUS expr",
    "text_expr ::= MINUS text_expr",
    "expr ::= TILDE expr",
    "text_expr ::= TILDE text_expr",
    "affix ::= PREFIX",
    "affix ::= SUFFIX",
    "affix ::= CONTAINS",
    "verbatim ::= WILDCARD",
    "text_expr ::= PERCENT param_term PERCENT",
    "text_expr ::= PERCENT PERCENT param_term PERCENT PERCENT",
    "text_expr ::= PERCENT PERCENT PERCENT param_term PERCENT PERCENT PERCENT",
    "modifier ::= MODIFIER",
    "modifierlist ::= modifier OR term",
    "modifierlist ::= modifierlist OR term",
    "expr ::= modifier COLON LB tag_list RB",
    "tag_list ::= param_term_case",
    "tag_list ::= affix",
    "tag_list ::= verbatim",
    "tag_list ::= termlist",
    "tag_list ::= tag_list OR param_term_case",
    "tag_list ::= tag_list OR affix",
    "tag_list ::= tag_list OR verbatim",
    "tag_list ::= tag_list OR termlist",
    "expr ::= modifier COLON numeric_range",
    "numeric_range ::= LSQB param_num param_num RSQB",
    "expr ::= modifier COLON geo_filter",
    "geo_filter ::= LSQB param_num param_num param_num param_term RSQB",
    "expr ::= modifier COLON geometry_query",
    "geometry_query ::= LSQB TERM ATTRIBUTE RSQB",
    "query ::= expr ARROW LSQB vector_query RSQB",
    "query ::= text_expr ARROW LSQB vector_query RSQB",
    "query ::= star ARROW LSQB vector_query RSQB",
    "vector_query ::= vector_command vector_attribute_list vector_score_field",
    "vector_query ::= vector_command vector_score_field",
    "vector_query ::= vector_command vector_attribute_list",
    "vector_query ::= vector_command",
    "vector_score_field ::= as param_term_case",
    "query ::= expr ARROW LSQB vector_query RSQB ARROW LB attribute_list RB",
    "query ::= text_expr ARROW LSQB vector_query RSQB ARROW LB attribute_list RB",
    "query ::= star ARROW LSQB vector_query RSQB ARROW LB attribute_list RB",
    "vector_command ::= TERM param_size modifier ATTRIBUTE",
    "vector_attribute ::= TERM param_term",
    "vector_attribute_list ::= vector_attribute_list vector_attribute",
    "vector_attribute_list ::= vector_attribute",
    "expr ::= modifier COLON LSQB vector_range_command RSQB",
    "vector_range_command ::= TERM param_num ATTRIBUTE",
    "num ::= SIZE",
    "num ::= NUMBER",
    "num ::= LP num",
    "num ::= MINUS num",
    "term ::= TERM",
    "term ::= NUMBER",
    "term ::= SIZE",
    "param_term ::= term",
    "param_term ::= ATTRIBUTE",
    "param_term_case ::= term",
    "param_term_case ::= ATTRIBUTE",
    "param_size ::= SIZE",
    "param_size ::= ATTRIBUTE",
    "param_num ::= ATTRIBUTE",
    "param_num ::= num",
    "param_num ::= LP ATTRIBUTE",
    "star ::= STAR",
    "star ::= LP star RP",
    "as ::= AS_T",
]

terminals = {
    "TERM": ["foo", "bar", "baz", "qux", "quux", "corge", "grault", "garply", "waldo", "fred", "plugh", "xyzzy", "thud"],
    "NUMBER": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    "SIZE": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    "MODIFIER": ["@."],
    "ATTRIBUTE": ["$."],
    "AS_T": ["as"],
    "STAR": ["*"],
    "QUOTE": ["\""],
    "OR": ["|"],
    "COLON": [":"],
    "SEMICOLON": [";"],
    "LP": ["("],
    "RP": [")"],
    "LB": ["["],
    "RB": ["]"],
    "LSQB": ["["],
    "RSQB": ["]"],
    "ARROW": ["=>"],
    "PERCENT": ["%"],
    "TILDE": ["~"],
    "MINUS": ["-"],
    "PREFIX": ["*."],
    "SUFFIX": [".*"],
    "CONTAINS": ["contains"],
    "WILDCARD": ["w"],

}

import numpy as np
import random

def generate_rule_table(rules):
    rule_table = {}
    for rule in rules:
        lhs, rhs = rule.split("::=")
        lhs = lhs.strip()
        if lhs not in rule_table:
            rule_table[lhs] = []
        rule_table[lhs].append(rhs.strip().split())
    return rule_table

if __name__ == "__main__":
    rule_table = generate_rule_table(rules)
    query = [root]
    while np.any([x in rule_table for x in query]):
        for i, x in enumerate(query):
            if x in rule_table:
                query.pop(i)
                query = query[:i] + random.choice(rule_table[x]) + query[i:]
                break
    print(" ".join([terminals[x][0] if x in terminals else x for x in query]))
