#!/usr/bin/python
#
# A simple List of Strings Parser (LSP) test file.
# Operators: literal, or.
#
import re

# -------------------------------------------------------------------------------------------------
# LSP engine. Grammar token objects.
# Parser inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
# --- Token objects ---
class LSP_literal_token:
    def __init__(self, value):
        self.value = value
        self.id = "STRING"
    def nud(self):
        return self
    # --- Actual implementation ---
    def exec_token(self):
        print('Executing literal token {0}'.format(self.value))
        return self.value
    def __repr__(self):
        return "[literal {0}]".format(self.value)

def LSP_advance(id = None):
    global LSP_token

    if id and LSP_token.id != id:
        raise SyntaxError("Expected {0}".format(id))
    LSP_token = LSP_next()

class LSP_operator_open_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP ("
    # def nud(self):
    #     expr = LSP_expression()
    #     advance("OP )")
    #     return expr
    # >> By treating the left parentesis as a binary operator, parsing this is straight-forward.
    def led(self, left):
        self.first = left
        self.second = LSP_expression(10)
        advance("OP )")
        return self
    def exec_token(self):
        print('Executing function token "{0}" argument {1}'.format(self.first, self.second))
        return True
    def __repr__(self):
        return "[OP (]"

class LSP_operator_close_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP )"
    def __repr__(self):
        return "[OP )]"

class LSP_operator_not_token:
    lbp = 50
    def __init__(self):
        self.id = "OP NOT"
    def nud(self):
        self.first = LSP_expression(50)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        print('Executing NOT token')
        return not self.first.exec_token()
    def __repr__(self):
        return "[OP not]"

class LSP_operator_and_token:
    lbp = 10
    def __init__(self):
        self.id = "OP AND"
    def led(self, left):
        print('Executing AND token')
        self.first = left
        self.second = LSP_expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        return self.first.exec_token() and self.second.exec_token()
    def __repr__(self):
        return "[OP and]"

class LSP_operator_or_token:
    lbp = 10
    def __init__(self):
        self.id = "OP OR"
    def led(self, left):
        self.first = left
        self.second = LSP_expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        print('Executing OR token')
        return self.first.exec_token() or self.second.exec_token()
    def __repr__(self):
        return "[OP or]"

class LSP_end_token:
    lbp = 0
    def __init__(self):
        self.id = "END TOKEN"
    def __repr__(self):
        return "[END token]"

# -------------------------------------------------------------------------------------------------
# Tokenizer
# -------------------------------------------------------------------------------------------------
# jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/
#
# If the body of the function contains a 'yield', then the function becames
# a generator function. Generator functions create generator iterators, also
# named "generators". Just remember that a generator is a special type of iterator.
#
# To be considered an iterator, generators must define a few methods, one of 
# which is __next__(). To get the next value from a generator, we use the 
# same built-in function as for iterators: next().
#
def LSP_tokenize(program):
    # \s* -> Matches any number of blanks [ \t\n\r\f\v].
    # (?:...) -> A non-capturing version of regular parentheses.
    # \b -> Matches the empty string, but only at the beginning or end of a word.
    # \w -> Matches [a-zA-Z0-9_]
    reg = "\s*(?:(and|or|not|\(|\))|(\"[ \.\w_\-\&]+\")|([\.\w_\-\&]+))"
    for operator, q_string, string in re.findall(reg, program):
        if string:
            yield LSP_literal_token(string)
        elif q_string:
            if q_string[0] == '"': q_string = q_string[1:]
            if q_string[-1] == '"': q_string = q_string[:-1]
            yield LSP_literal_token(q_string)
        elif operator == "and":
            yield LSP_operator_and_token()
        elif operator == "or":
            yield LSP_operator_or_token()
        elif operator == "not":
            yield LSP_operator_not_token()
        elif operator == "(":
            yield LSP_operator_open_par_token()
        elif operator == ")":
            yield LSP_operator_close_par_token()
        else:
            raise SyntaxError("Unknown operator: %r".format(operator))
    yield LSP_end_token()

# -------------------------------------------------------------------------------------------------
# Manufacturer Parser (LSP) inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
def LSP_expression(rbp = 0):
    global LSP_token

    t = LSP_token
    LSP_token = LSP_next()
    left = t.nud()
    while rbp < LSP_token.lbp:
        t = LSP_token
        LSP_token = LSP_next()
        left = t.led(left)
    return left

def LSP_expression_exec(rbp = 0):
    global LSP_token

    t = LSP_token
    LSP_token = LSP_next()
    left = t.nud()
    while rbp < LSP_token.lbp:
        t = LSP_token
        LSP_token = LSP_next()
        left = t.led(left)
    print('Init exec program in token {0}'.format(left))
    return left.exec_token()

def LSP_parse_exec(program, search_list):
    global LSP_token, LSP_next, LSP_parser_search_list

    print('LSP_parse_exec() Initialising program execution')
    print('Search string "{0}"'.format(search_list))
    print('Program       "{0}"'.format(program))
    LSP_parser_search_list = search_list
    LSP_next = LSP_tokenize(program).next
    LSP_token = LSP_next()

    return LSP_expression_exec()

# --- main code ---
s_str = 'Konami or Namco or Sega'
print("String '{0}'".format(s_str))
t_counter = 0
for token in LSP_tokenize(s_str):
    print("Token {0:02d} '{1}'".format(t_counter, token))
    t_counter += 1
LSP_parse_exec(s_str, 'Konami')
