# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher MAME filter engine.
#

# Copyright (c) 2016-2018 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
# Division operator: https://www.python.org/dev/peps/pep-0238/
from __future__ import unicode_literals
from __future__ import division

# --- Modules/packages in this plugin ---
from constants import *
from utils import *
from utils_kodi import *

# -------------------------------------------------------------------------------------------------
# Filter parser engine (copied from NARS)
# -------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Search engine and parser
# -----------------------------------------------------------------------------
# --- Global variables for parser ---
def set_parser_search_list(search_list):
    global parser_search_list
  
    parser_search_list = search_list

# --- Token objects ---
class literal_token:
    def __init__(self, value):
        self.value = value
        self.id = "STRING"
    def nud(self):
        return self
    # --- Actual implementation
    def exec_token(self):
        global parser_search_list

        return self.value in parser_search_list

def advance(id = None):
    global token
    if id and token.id != id:
        raise SyntaxError("Expected %r" % id)
    token = next()

class operator_open_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP ("
    def nud(self):
        expr = expression()
        advance("OP )")
        return expr

class operator_close_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP )"

class operator_not_token:
    lbp = 50
    def __init__(self):
        self.id = "OP NOT"
    def nud(self):
        self.first = expression(50)
        return self
    # --- Actual implementation
    def exec_token(self):
        return not self.first.exec_token()

class operator_and_token:
    lbp = 10
    def __init__(self):
        self.id = "OP AND"
    def led(self, left):
        self.first = left
        self.second = expression(10)
        return self
    # --- Actual implementation
    def exec_token(self):
        return self.first.exec_token() and self.second.exec_token()

class operator_or_token:
    lbp = 10
    def __init__(self):
        self.id = "OP OR"
    def led(self, left):
        self.first = left
        self.second = expression(10)
        return self
    # --- Actual implementation
    def exec_token(self):
        return self.first.exec_token() or self.second.exec_token()

class end_token:
    lbp = 0
    def __init__(self):
        self.id = "END TOKEN"

# ----------------------------------------------------------------------------
# Tokenizer
# ----------------------------------------------------------------------------
# jeffknupp.com/blog/2013/04/07/improve-your-python-yield-and-generators-explained/
#
# - If the body of the function contains a 'yield', then the function becames
#   a generator function. Generator functions create generator iterators, also
#   named "generators". Just remember that a generator is a special type of 
#   iterator.
#   To be considered an iterator, generators must define a few methods, one of 
#   which is __next__(). To get the next value from a generator, we use the 
#   same built-in function as for iterators: next().
#
def tokenize(program):
    # \s* -> Matches any number of blanks [ \t\n\r\f\v].
    # (?:...) -> A non-capturing version of regular parentheses.
    # \b -> Matches the empty string, but only at the beginning or end of a word.
    # \w -> Matches [a-zA-Z0-9_]
    for operator, string in re.findall("\s*(?:(and|or|not|\(|\))|([\.\w_]+))", program):
        # print 'Tokenize >> Program -> "' + program + \
        #       '", String -> "' + string + '", Operator -> "' + operator + '"\n';
        if string:
            yield literal_token(string)
        elif operator == "and":
            yield operator_and_token()
        elif operator == "or":
            yield operator_or_token()
        elif operator == "not":
            yield operator_not_token()
        elif operator == "(":
            yield operator_open_par_token()
        elif operator == ")":
            yield operator_close_par_token()
        else:
            raise SyntaxError("Unknown operator: %r".format(operator))
    yield end_token()

# ----------------------------------------------------------------------------
# Parser
# Inspired by http://effbot.org/zone/simple-top-down-parsing.htm
# ----------------------------------------------------------------------------
def expression(rbp = 0):
    global token
    t = token
    token = next()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next()
        left = t.led(left)
    return left

def expression_exec(rbp = 0):
    global token
    t = token
    token = next()
    left = t.nud()
    while rbp < token.lbp:
        t = token
        token = next()
        left = t.led(left)
    return left.exec_token()

def parse_exec(program):
    global token, next
    next = tokenize(program).next
    token = next()

    return expression_exec()

# -------------------------------------------------------------------------------------------------
# MAME machine filters
# -------------------------------------------------------------------------------------------------
def mame_filter_Driver_tag(mame_xml_dic, driver_filter_expression):
    log_debug('mame_filter_Driver_tag() <Driver filter>')
  
    if not driver_filter_expression:
        log_debug('mame_filter_Driver_tag() User wants all drivers')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    log_debug('Expression "{0}"'.format(driver_filter_expression))
    for key in sorted(mame_xml_dic):
        driver_str = mame_xml_dic[key]['sourcefile']
        driver_name_list = [ driver_str ]

        # --- Update search variable and call parser to evaluate expression
        set_parser_search_list(driver_name_list)
        boolean_result = parse_exec(driver_filter_expression)

        # --- Filter ROM or not
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[key] = mame_xml_dic[key]
    log_debug('mame_filter_Driver_tag() Intial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic
