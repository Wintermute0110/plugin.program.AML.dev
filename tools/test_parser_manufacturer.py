#!/usr/bin/python
#
import re

# -------------------------------------------------------------------------------------------------
# Manufacturer Parser (MP) engine. Grammar token objects.
# Parser inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
# --- Token objects ---
class MP_literal_token:
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
        return "<literal {0}>".format(self.value)

def MP_advance(id = None):
    global MP_token

    if id and MP_token.id != id:
        raise SyntaxError("Expected {0}".format(id))
    MP_token = MP_next()

class MP_operator_open_par_token:
    lbp = 10
    def __init__(self):
        self.id = "OP ("
    # >> By treating the left parentesis as a binary operator, parsing this is straight-forward.
    def led(self, left):
        self.first = left
        self.second = MP_expression(10)
        MP_advance("OP )")
        return self
    def exec_token(self):
        print('Executing function {0} argument {1}'.format(self.first, self.second))
        return True
    def __repr__(self):
        return "<OP (>"

class MP_operator_close_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP )"
    def __repr__(self):
        return "<OP )>"

class MP_operator_not_token:
    lbp = 50
    def __init__(self):
        self.id = "OP NOT"
    def nud(self):
        self.first = MP_expression(50)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        print('Executing NOT token')
        return not self.first.exec_token()
    def __repr__(self):
        return "<OP not>"

class MP_operator_and_token:
    lbp = 10
    def __init__(self):
        self.id = "OP AND"
    def led(self, left):
        print('Executing AND token')
        self.first = left
        self.second = MP_expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        return self.first.exec_token() and self.second.exec_token()
    def __repr__(self):
        return "<OP and>"

class MP_operator_or_token:
    lbp = 10
    def __init__(self):
        self.id = "OP OR"
    def led(self, left):
        self.first = left
        self.second = MP_expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        print('Executing OR token')
        return self.first.exec_token() or self.second.exec_token()
    def __repr__(self):
        return "<OP or>"

class MP_end_token:
    lbp = 0
    def __init__(self):
        self.id = "END TOKEN"
    def __repr__(self):
        return "<END token>"

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
def MP_tokenize(program):
    # \s* -> Matches any number of blanks [ \t\n\r\f\v].
    # (?:...) -> A non-capturing version of regular parentheses.
    # \b -> Matches the empty string, but only at the beginning or end of a word.
    # \w -> Matches [a-zA-Z0-9_]
    reg = "\s*(?:(and|or|not|\(|\))|(\"[ \.\w_\-\&\/]+\")|([\.\w_\-\&]+))"
    for operator, q_string, string in re.findall(reg, program):
        if string:
            yield MP_literal_token(string)
        elif q_string:
            if q_string[0] == '"': q_string = q_string[1:]
            if q_string[-1] == '"': q_string = q_string[:-1]
            yield MP_literal_token(q_string)
        elif operator == "and":
            yield MP_operator_and_token()
        elif operator == "or":
            yield MP_operator_or_token()
        elif operator == "not":
            yield MP_operator_not_token()
        elif operator == "(":
            yield MP_operator_open_par_token()
        elif operator == ")":
            yield MP_operator_close_par_token()
        else:
            raise SyntaxError("Unknown operator: %r".format(operator))
    yield MP_end_token()

# -------------------------------------------------------------------------------------------------
# Manufacturer Parser (MP) inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
def MP_expression(rbp = 0):
    global MP_token

    t = MP_token
    MP_token = MP_next()
    left = t.nud()
    while rbp < MP_token.lbp:
        t = MP_token
        MP_token = MP_next()
        left = t.led(left)
    return left

def MP_expression_exec(rbp = 0):
    global MP_token

    t = MP_token
    MP_token = MP_next()
    left = t.nud()
    while rbp < MP_token.lbp:
        t = MP_token
        MP_token = MP_next()
        left = t.led(left)
    print('MP_expression_exec() Init exec program in token {0}'.format(left))
    return left.exec_token()

def MP_parse_exec(program, search_list):
    global MP_token, MP_next, MP_parser_search_list

    print('MP_parse_exec() Initialising program execution')
    print('Search string "{0}"'.format(search_list))
    print('Program       "{0}"'.format(program))
    MP_parser_search_list = search_list
    MP_next = MP_tokenize(program).next
    MP_token = MP_next()

    return MP_expression_exec()

# --- main code ---
# p_str = 'contains(Konami)'
p_str = 'contains(Konami) or contains(Namco)'
# p_str = 'contains(Konami) or contains(Namco) or contains("Konami / Kaneko")'
print("String '{0}'".format(p_str))
t_counter = 0
for token in MP_tokenize(p_str):
    print("Token {0:02d} '{1}'".format(t_counter, token))
    t_counter += 1
MP_parse_exec(p_str, 'Konami')
