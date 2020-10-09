#!/usr/bin/python3 -B

import re
import sys

# -------------------------------------------------------------------------------------------------
# Fake functions when running outisde the Kodi Python runtime
# -------------------------------------------------------------------------------------------------
def log_debug(str): print(str)

def log_info(str): print(str)

# -------------------------------------------------------------------------------------------------
# Year Parser (YP) engine. Grammar token objects.
# Parser inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# See also test_parser_SP.py for more documentation.
#
# YP operators: ==, !=, >, <, >=, <=, and, or, not, '(', ')', literal.
# literal may be the special variable 'year' or a MAME number.
# -------------------------------------------------------------------------------------------------
debug_YP_parser = False
debug_YP_parse_exec = False

class YP_literal_token:
    def __init__(self, value): self.value = value
    def nud(self): return self
    def exec_token(self):
        if self.value == 'year':
            ret = YP_year
        else:
            ret = int(self.value)
        if debug_YP_parser: log_debug('Token LITERAL returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return '[LITERAL "{}"]'.format(self.value)

def YP_advance(id = None):
    global YP_token

    if id and type(YP_token) != id:
        raise SyntaxError("Expected {}".format(type(YP_token)))
    YP_token = YP_next()

class YP_operator_open_par_token:
    lbp = 0
    def __init__(self): pass
    def nud(self):
        expr = YP_expression()
        YP_advance(YP_operator_close_par_token)
        return expr
    def __repr__(self): return "[OP (]"

class YP_operator_close_par_token:
    lbp = 0
    def __init__(self): pass
    def __repr__(self): return "[OP )]"

class YP_operator_not_token:
    lbp = 60
    def __init__(self): pass
    def nud(self):
        self.first = YP_expression(50)
        return self
    def exec_token(self):
        ret = not self.first.exec_token()
        if debug_YP_parser: log_debug('Token NOT returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP not]"

class YP_operator_and_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() and self.second.exec_token()
        if debug_YP_parser: log_debug('Token AND returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP and]"

class YP_operator_or_token:
    lbp = 10
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() or self.second.exec_token()
        if debug_YP_parser: log_debug('Token OR returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP or]"

class YP_operator_equal_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() == self.second.exec_token()
        if debug_YP_parser: log_debug('Token == returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP ==]"

class YP_operator_not_equal_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() != self.second.exec_token()
        if debug_YP_parser: log_debug('Token != returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP !=]"

class YP_operator_great_than_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() > self.second.exec_token()
        if debug_YP_parser: log_debug('Token > returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP >]"

class YP_operator_less_than_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() < self.second.exec_token()
        if debug_YP_parser: log_debug('Token < returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP <]"

class YP_operator_great_or_equal_than_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() >= self.second.exec_token()
        if debug_YP_parser: log_debug('Token >= returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP >=]"

class YP_operator_less_or_equal_than_token:
    lbp = 50
    def __init__(self): pass
    def led(self, left):
        self.first = left
        self.second = YP_expression(10)
        return self
    def exec_token(self):
        ret = self.first.exec_token() <= self.second.exec_token()
        if debug_YP_parser: log_debug('Token <= returns {} "{}"'.format(type(ret), str(ret)))
        return ret
    def __repr__(self): return "[OP <=]"

class YP_end_token:
    lbp = 0
    def __init__(self): pass
    def __repr__(self): return "[END token]"

# -------------------------------------------------------------------------------------------------
# Year Parser Tokenizer
# See http://jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/
# -------------------------------------------------------------------------------------------------
YP_token_pat = re.compile("\s*(?:(==|!=|>=|<=|>|<|and|or|not|\(|\))|([\w]+))")

def YP_tokenize(program):
    for operator, n_string in YP_token_pat.findall(program):
        if n_string:            yield YP_literal_token(n_string)
        elif operator == "==":  yield YP_operator_equal_token()
        elif operator == "!=":  yield YP_operator_not_equal_token()
        elif operator == ">":   yield YP_operator_great_than_token()
        elif operator == "<":   yield YP_operator_less_than_token()
        elif operator == ">=":  yield YP_operator_great_or_equal_than_token()
        elif operator == "<=":  yield YP_operator_less_or_equal_than_token()
        elif operator == "and": yield YP_operator_and_token()
        elif operator == "or":  yield YP_operator_or_token()
        elif operator == "not": yield YP_operator_not_token()
        elif operator == "(":   yield YP_operator_open_par_token()
        elif operator == ")":   yield YP_operator_close_par_token()
        else:                   raise SyntaxError("Unknown operator: '{}'".format(operator))
    yield YP_end_token()

# -------------------------------------------------------------------------------------------------
# Year Parser (YP) inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# -------------------------------------------------------------------------------------------------
def YP_expression(rbp = 0):
    global YP_token

    t = YP_token
    YP_token = YP_next()
    left = t.nud()
    while rbp < YP_token.lbp:
        t = YP_token
        YP_token = YP_next()
        left = t.led(left)
    return left

def YP_parse_exec(program, year_str):
    global YP_token, YP_next, YP_year

    # --- Transform year_str to an integer. year_str may be ill formed ---
    if re.findall(r'^[0-9]{4}$', year_str):
        year = int(year_str)
    elif re.findall(r'^[0-9]{4}\?$', year_str):
        year = int(year_str[0:4])
    else:
        year = 0

    if debug_YP_parse_exec:
        log_debug('YP_parse_exec() Initialising program execution')
        log_debug('YP_parse_exec() year     "{}"'.format(year))
        log_debug('YP_parse_exec() Program  "{}"'.format(program))
    YP_year = year
    YP_next = YP_tokenize(program).__next__
    YP_token = YP_next()

    # Old function parse_exec().
    rbp = 0
    t = YP_token
    YP_token = YP_next()
    left = t.nud()
    while rbp < YP_token.lbp:
        t = YP_token
        YP_token = YP_next()
        left = t.led(left)
    if debug_YP_parse_exec:
        log_debug('YP_parse_exec() Init exec program in token {}'.format(left))

    return left.exec_token()

# --- main code -----------------------------------------------------------------------------------
# --- Input strings ---
# Consider all ill-formed year strings in MAME like incomplete years.
# year_str = '1992'

# This year string is converted 1992? to int 1992
year_str = '1992?'

# All this year strings to int 0
# year_str = 'None'
# year_str = '????'
# year_str = '198?'
# year_str = '199?'
# year_str = '200?'
# year_str = '201?'
# year_str = '19??'
# year_str = '20??'

# --- Programs ---
# p_str = 'year == 1992'
# p_str = 'year == 1995'
# p_str = 'year != 1992'
# p_str = 'year != 1995'
# p_str = 'year > 1992'
# p_str = 'year < 1992'
# p_str = 'year >= 1992'
# p_str = 'year <= 1992'
# p_str = 'year < 1992 and (year != 1970 or year != 1960)'
# p_str = 'year < 1980'
p_str = 'year >= 1980 and year < 1990'
# p_str = 'year >= 1990 and year < 2000'
# p_str = 'year >= 2000'

# --- Tests ---
single_test = True
if single_test:
    log_info("year_str '{}'".format(year_str))
    log_info("Program  '{}'".format(p_str))
    for i, token in enumerate(YP_tokenize(p_str)):
        log_info("Token {:02d} '{}'".format(i, token))
    result = YP_parse_exec(p_str, year_str)
    log_info('Result {}'.format(result))

# --- Batch tests ---
# Year str, program str, expected result.
test_list = [
    # Invalid years
    ('None', 'year == 0', True),
    ('????', 'year == 0', True),
    # Valid years
    ('1992', 'year == 1992', True),
    ('1992?', 'year == 1992', True),
    ('1992', 'year != 1992', False),
    ('1985', 'year >= 1980 and year < 1990', True),
    ('1995', 'year >= 1980 and year < 1990', False),
    ('1995', 'year == 1990 or year == 1995', True),
    ('1985', '(year >= 1970 and year < 1980) or (year >= 1990 and year < 2000)', False),
    ('1975', '(year >= 1970 and year < 1980) or (year >= 1990 and year < 2000)', True),
    ('1995', '(year >= 1970 and year < 1980) or (year >= 1990 and year < 2000)', True),
    # Next test tests the short circuit Python or operator. Compare debug output with previous test.
    ('1975', '(year >= 1970 and year < 1980) or (year >= 1990 and year < 2000)', True),
]
batch_tests = True
if batch_tests:
    for test_index in range(len(test_list)):
        test_tuple = test_list[test_index]
        log_info('Test number {}'.format(test_index))
        log_info("year '{}' / program '{}'".format(test_tuple[0], test_tuple[1]))
        # for i, token in enumerate(YP_tokenize(test_tuple[1])):
        #     log_info("Token {:02d} '{}'".format(i, token))
        result = YP_parse_exec(test_tuple[1], test_tuple[0])
        log_info('Result {}'.format(result))
        if result == test_tuple[2]:
            log_info('Test PASSED')
            log_info('')
            continue
        log_info('Test FAILED')
        sys.exit(1)
    log_info('All {} tests PASSED'.format(len(test_list)))
