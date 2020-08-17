#!/usr/bin/python3 -B

import re

# -------------------------------------------------------------------------------------------------
# Fake functions when running outisde the Kodi Python runtime
# -------------------------------------------------------------------------------------------------
def log_debug(str): print(str)

def log_info(str): print(str)

# -------------------------------------------------------------------------------------------------
# String Parser (SP) engine. Grammar token objects.
# Parser inspired by http://effbot.org/zone/simple-top-down-parsing.htm
#
# SP operators: and, or, not, has, lacks, literal.
# -------------------------------------------------------------------------------------------------
debug_SP_parser = False
debug_SP_parse_exec = False

class SP_literal_token:
    def __init__(self, value): self.value = value
    def nud(self):
        if debug_SP_parser: log_debug('Call LITERAL token nud()')
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing LITERAL token value "{}"'.format(self.value))
        ret = self.value
        if debug_SP_parser: log_debug('Token LITERAL returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return '<LITERAL "{}">'.format(self.value)

class SP_operator_has_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_SP_parser: log_debug('Call HAS token nud()')
        self.first = SP_expression(50)
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing HAS token')
        literal_str = self.first.exec_token()
        if type(literal_str) is not str:
            raise SyntaxError("HAS token exec; expected string, got {}".format(type(literal_str)))
        ret = True if SP_parser_search_string.find(literal_str) >= 0 else False
        if debug_SP_parser: log_debug('Token HAS returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP has>"

class SP_operator_lacks_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_SP_parser: log_debug('Call LACKS token nud()')
        self.first = SP_expression(50)
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing LACKS token')
        literal_str = self.first.exec_token()
        if type(literal_str) is not str:
            raise SyntaxError("LACKS token exec; expected string, got {}".format(type(literal_str)))
        ret = False if SP_parser_search_string.find(literal_str) >= 0 else True
        if debug_SP_parser: log_debug('Token LACKS returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP lacks>"

class SP_operator_not_token:
    lbp = 50
    def __init__(self): pass
    def nud(self):
        if debug_SP_parser: log_debug('Call NOT token nud()')
        self.first = SP_expression(50)
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing NOT token')
        exp_bool = self.first.exec_token()
        if type(exp_bool) is not bool:
            raise SyntaxError("NOT token exec; expected string, got {}".format(type(exp_bool)))
        ret = not exp_bool
        if debug_SP_parser: log_debug('Token NOT returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP not>"

class SP_operator_and_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        if debug_SP_parser: log_debug('Call AND token led()')
        self.first = left
        self.second = SP_expression(10)
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing AND token')
        ret = self.first.exec_token() and self.second.exec_token()
        if debug_SP_parser: log_debug('Token AND returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP and>"

class SP_operator_or_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        if debug_SP_parser: log_debug('Call OR token led()')
        self.first = left
        self.second = SP_expression(10)
        return self
    def exec_token(self):
        if debug_SP_parser: log_debug('Executing OR token')
        ret = self.first.exec_token() or self.second.exec_token()
        if debug_SP_parser: log_debug('Token OR returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "<OP or>"

class SP_end_token:
    lbp = 0
    def __init__(self): pass
    def __repr__(self): return "<END token>"

# -------------------------------------------------------------------------------------------------
# String Parser (SP) Tokenizer
# See http://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/
# -------------------------------------------------------------------------------------------------
SP_token_pat = re.compile("\s*(?:(and|or|not|has|lacks)|(\"[ \.\w_\-\&\/]+\")|([\.\w_\-\&]+))")

def SP_tokenize(program):
    # \s* -> Matches any number of blanks [ \t\n\r\f\v].
    # (?:...) -> A non-capturing version of regular parentheses.
    # \w -> Matches [a-zA-Z0-9_]
    for operator, q_string, string in SP_token_pat.findall(program):
        if string:
            yield SP_literal_token(string)
        elif q_string:
            if q_string[0] == '"': q_string = q_string[1:]
            if q_string[-1] == '"': q_string = q_string[:-1]
            yield SP_literal_token(q_string)
        elif operator == "and":
            yield SP_operator_and_token()
        elif operator == "or":
            yield SP_operator_or_token()
        elif operator == "not":
            yield SP_operator_not_token()
        elif operator == "has":
            yield SP_operator_has_token()
        elif operator == "lacks":
            yield SP_operator_lacks_token()
        else:
            raise SyntaxError("Unknown operator: '{}'".format(operator))
    yield SP_end_token()

# -------------------------------------------------------------------------------------------------
# String Parser (SP) inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
def SP_expression(rbp = 0):
    global SP_token

    t = SP_token
    SP_token = SP_next()
    left = t.nud()
    while rbp < SP_token.lbp:
        t = SP_token
        SP_token = SP_next()
        left = t.led(left)

    return left

def SP_parse_exec(program, search_string):
    global SP_token, SP_next, SP_parser_search_string

    if debug_SP_parse_exec:
        log_debug('SP_parse_exec() Initialising program execution')
        log_debug('SP_parse_exec() Search string "{}"'.format(search_string))
        log_debug('SP_parse_exec() Program       "{}"'.format(program))
    SP_parser_search_string = search_string
    SP_next = SP_tokenize(program).__next__
    SP_token = SP_next()

    # Old function parse_exec()
    rbp = 0
    t = SP_token
    SP_token = SP_next()
    left = t.nud()
    while rbp < SP_token.lbp:
        t = SP_token
        SP_token = SP_next()
        left = t.led(left)
    if debug_SP_parse_exec:
        log_debug('SP_parse_exec() Init exec program in token {}'.format(left))

    return left.exec_token()

# --- main code -----------------------------------------------------------------------------------
# --- Input strings ---
i_str = 'Konami'

# --- Programs ---
# p_str = 'has Konami'
# p_str = 'lacks Konami'
# p_str = 'not has Konami'
# p_str = 'has Konami or has Namco'
# p_str = 'has Namco or has Konami'
# p_str = 'has Konami or not has Namco'
# p_str = 'has Konami or has Namco or has "Capcom / Kaneko"'
# p_str = 'nothas Konami or nothas Namco or not has "Capcom / Kaneko"'
# p_str = 'lacks Konami and lacks Namco and lacks "Capcom / Kaneko"'
# p_str = 'lacks Konami or lacks Namco and lacks "Capcom / Kaneko"'
p_str = 'has Konami and not has Capcom'

# --- Test ---
log_info("String  '{}'".format(i_str))
log_info("Program '{}'".format(p_str))
for i, token in enumerate(SP_tokenize(p_str)):
    log_info("Token {:02d} '{}'".format(i, token))
result = SP_parse_exec(p_str, i_str)
log_info('Program result {}'.format(result))
