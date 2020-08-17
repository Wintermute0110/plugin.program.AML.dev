#!/usr/bin/python3 -B

import re

# -------------------------------------------------------------------------------------------------
# Fake functions when running outisde the Kodi Python runtime
# -------------------------------------------------------------------------------------------------
def log_debug(str): print(str)

def log_info(str): print(str)

# -------------------------------------------------------------------------------------------------
# List of String Parser (LSP) engine. Grammar token objects.
# Parser inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# Also see test_parser_SP.py for more documentation.
#
# LSP operators: and, or, not, has, lacks, '(', ')', literal.
# -------------------------------------------------------------------------------------------------
debug_LSP_parser = False
debug_LSP_parse_exec = False

class LSP_literal_token:
    def __init__(self, value): self.value = value
    def nud(self):
        if debug_LSP_parser: log_debug('Call LITERAL token nud()')
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing LITERAL token value "{}"'.format(self.value))
        ret = self.value
        if debug_LSP_parser: log_debug('Token LITERAL returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return '<LITERAL "{}">'.format(self.value)

# id is a type object as return by type()
def LSP_advance(id = None):
    global LSP_token

    if id and type(LSP_token) != id:
        raise SyntaxError("Expected {}".format(type(LSP_token)))
    LSP_token = LSP_next()

class LSP_operator_open_par_token:
    lbp = 0
    def __init__(self): pass
    def nud(self):
        if debug_LSP_parser: log_debug('Call ( token nud()')
        expr = LSP_expression()
        LSP_advance(LSP_operator_close_par_token)
        return expr
    def __repr__(self): return "<OP (>"

class LSP_operator_close_par_token:
    lbp = 0
    def __init__(self): pass
    def __repr__(self): return "<OP )>"

class LSP_operator_has_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_LSP_parser: log_debug('Call HAS token nud()')
        self.first = LSP_expression(50)
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing HAS token')
        literal_str = self.first.exec_token()
        if type(literal_str) is not str:
            raise SyntaxError("HAS token exec; expected string, got {}".format(type(literal_str)))
        ret = literal_str in LSP_parser_search_list
        if debug_LSP_parser: log_debug('Token HAS returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP has>"

class LSP_operator_lacks_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_LSP_parser: log_debug('Call LACKS token nud()')
        self.first = LSP_expression(50)
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing LACKS token')
        literal_str = self.first.exec_token()
        if type(literal_str) is not str:
            raise SyntaxError("LACKS token exec; expected string, got {}".format(type(literal_str)))
        ret = literal_str not in LSP_parser_search_list
        if debug_LSP_parser: log_debug('Token LACKS returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP lacks>"

class LSP_operator_not_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_LSP_parser: log_debug('Call NOT token nud()')
        self.first = LSP_expression(50)
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing NOT token')
        exp_bool = self.first.exec_token()
        if type(exp_bool) is not bool:
            raise SyntaxError("NOT token exec; expected string, got {}".format(type(exp_bool)))
        ret = not exp_bool
        if debug_LSP_parser: log_debug('Token NOT returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP not>"

class LSP_operator_and_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        if debug_LSP_parser: log_debug('Call AND token led()')
        self.first = left
        self.second = LSP_expression(10)
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing AND token')
        ret = self.first.exec_token() and self.second.exec_token()
        if debug_LSP_parser: log_debug('Token AND returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP and>"

class LSP_operator_or_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        if debug_LSP_parser: log_debug('Call OR token led()')
        self.first = left
        self.second = LSP_expression(10)
        return self
    def exec_token(self):
        if debug_LSP_parser: log_debug('Executing OR token')
        ret = self.first.exec_token() or self.second.exec_token()
        if debug_LSP_parser: log_debug('Token OR returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP or>"

class LSP_end_token:
    lbp = 0
    def __init__(self): pass
    def __repr__(self): return "<END token>"

# -------------------------------------------------------------------------------------------------
# List of String Parser (LSP) Tokenizer
# See http://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/
# -------------------------------------------------------------------------------------------------
LSP_token_pat = re.compile("\s*(?:(and|or|not|has|lacks|\(|\))|(\"[ \.\w_\-\&\/]+\")|([\.\w_\-\&]+))")

def LSP_tokenize(program):
    for operator, q_string, string in LSP_token_pat.findall(program):
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
        elif operator == "has":
            yield LSP_operator_has_token()
        elif operator == "lacks":
            yield LSP_operator_lacks_token()
        elif operator == "(":
            yield LSP_operator_open_par_token()
        elif operator == ")":
            yield LSP_operator_close_par_token()
        else:
            raise SyntaxError("Unknown operator: '{}'".format(operator))
    yield LSP_end_token()

# -------------------------------------------------------------------------------------------------
# List of String Parser (LSP) inspired by http://effbot.org/zone/simple-top-down-parsing.htm
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

def LSP_parse_exec(program, search_list):
    global LSP_token, LSP_next, LSP_parser_search_list

    if debug_LSP_parse_exec:
        log_debug('LSP_parse_exec() Initialising program execution')
        log_debug('LSP_parse_exec() Search  "{}"'.format(str(search_list)))
        log_debug('LSP_parse_exec() Program "{}"'.format(program))
    LSP_parser_search_list = search_list
    LSP_next = LSP_tokenize(program).__next__
    LSP_token = LSP_next()

    # Old function parse_exec().
    rbp = 0
    t = LSP_token
    LSP_token = LSP_next()
    left = t.nud()
    while rbp < LSP_token.lbp:
        t = LSP_token
        LSP_token = LSP_next()
        left = t.led(left)
    if debug_LSP_parse_exec:
        log_debug('LSP_parse_exec() Init exec program in token {}'.format(left))

    return left.exec_token()

# --- main code -----------------------------------------------------------------------------------
# --- Input strings ---
i_list = ['Konami', 'Capcom']

# --- Programs ---
# p_str = 'has Konami'
# p_str = 'lacks Konami'
# p_str = 'has Konami or has Namco'
# p_str = 'has Konami and has Namco'
# p_str = 'has Namco or (has Konami or has Capcom)'
# p_str = 'has Namco or (has Konami or not has Capcom)'
p_str = 'has Namco or (has Konami or not (has Capcom and has Kaneko))'
# p_str = 'has "Capcom / Kaneko"'
# p_str = 'has "Capcom / Kaneko" or Namco'
# p_str = 'lacks Capcom and lacks Kaneko and lacks Namco'
# p_str = 'lacks Capcom or lacks Kaneko or lacks Namco'

# Single program test
log_info("String  '{}'".format(str(i_list)))
log_info("Program '{}'".format(p_str))
for i, token in enumerate(LSP_tokenize(p_str)):
    log_info("Token {:02d} '{}'".format(i, token))
result = LSP_parse_exec(p_str, i_list)
log_info('Program result {}'.format(result))

# Batch test (complete)
