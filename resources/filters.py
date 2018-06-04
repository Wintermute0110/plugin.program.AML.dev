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

import xml.etree.ElementTree as ET

# --- Modules/packages in this plugin ---
from constants import *
from utils import *
from utils_kodi import *

# -------------------------------------------------------------------------------------------------
# Parse filter XML definition
# -------------------------------------------------------------------------------------------------
def strip_str_list(t_list):
    for i, s_t in enumerate(t_list): t_list[i] = s_t.strip()

    return t_list

def _get_comma_separated_list(text_t):
    if not text_t:
        return []
    else:
        return strip_str_list(text_t.split(','))

#
# Parse a string 'XXXXXX with YYYYYY'
#
def _get_change_tuple(text_t):
    if not text_t:
        return ''
    tuple_list = re.findall(r'(\w+) with (\w+)', text_t)
    if tuple_list:
        return tuple_list
    else:
        log_error('_get_change_tuple() text_t = "{0}"'.format(text_t))
        m = '(Exception) Cannot parse <Change> "{0}"'.format(text_t)
        log_error(m)
        raise Addon_Error(m)

#
# Returns a list of dictionaries, each dictionary has the filer definition.
#
def filter_parse_XML(fname_str):
    __debug_xml_parser = False

    # If XML has errors (invalid characters, etc.) this will rais exception 'err'
    XML_FN = FileName(fname_str)
    if not XML_FN.exists():
        kodi_dialog_OK('Custom filter XML file not found.')
        return
    log_debug('filter_parse_XML() Reading XML OP "{0}"'.format(XML_FN.getOriginalPath()))
    log_debug('filter_parse_XML() Reading XML  P "{0}"'.format(XML_FN.getPath()))
    try:
        xml_tree = ET.parse(XML_FN.getPath())
    except IOError as ex:
        log_error('(Exception) {0}'.format(ex))
        log_error('(Exception) Syntax error in the XML file definition')
        raise Addon_Error('(Exception) ET.parse(XML_FN.getPath()) failed.')
    xml_root = xml_tree.getroot()
    define_dic = {}
    filters_list = []
    for root_element in xml_root:
        if __debug_xml_parser: log_debug('Root child {0}'.format(root_element.tag))

        if root_element.tag == 'DEFINE':
            name_str = root_element.attrib['name']
            define_str = root_element.text if root_element.text else ''
            log_debug('DEFINE "{0}" := "{1}"'.format(name_str, define_str))
            define_dic[name_str] = define_str
        elif root_element.tag == 'MAMEFilter':
            this_filter_dic = {
                'name'         : '',
                'plot'         : '',
                'options'      : [], # List of strings
                'driver'       : '',
                'manufacturer' : '',
                'genre'        : '',
                'controls'     : '',
                'devices'      : '',
                'year'         : '',
                'include'      : [], # List of strings
                'exclude'      : [], # List of strings
                'change'       : [], # List of tuples (change_orig, change_dest)
            }
            for filter_element in root_element:
                text_t = filter_element.text if filter_element.text else ''
                if filter_element.tag == 'Name':
                    this_filter_dic['name'] = text_t
                elif filter_element.tag == 'Plot':
                    this_filter_dic['plot'] = text_t
                elif filter_element.tag == 'Options':
                    t_list = _get_comma_separated_list(text_t)
                    if t_list:
                        this_filter_dic['options'].extend(t_list)
                elif filter_element.tag == 'Driver':
                    this_filter_dic['driver'] = text_t
                elif filter_element.tag == 'Manufacturer':
                    this_filter_dic['manufacturer'] = text_t
                elif filter_element.tag == 'Genre':
                    this_filter_dic['genre'] = text_t
                elif filter_element.tag == 'Controls':
                    this_filter_dic['controls'] = text_t
                elif filter_element.tag == 'Devices':
                    this_filter_dic['devices'] = text_t
                elif filter_element.tag == 'Year':
                    this_filter_dic['year'] = text_t
                elif filter_element.tag == 'Include':
                    t_list = _get_comma_separated_list(text_t)
                    if t_list:
                        this_filter_dic['include'].extend(t_list)
                elif filter_element.tag == 'Exclude':
                    t_list = _get_comma_separated_list(text_t)
                    if t_list:
                        this_filter_dic['exclude'].extend(t_list)
                elif filter_element.tag == 'Change':
                    tuple_t = _get_change_tuple(text_t)
                    if tuple_t: this_filter_dic['change'].append(tuple_t)
                else:
                    m = '(Exception) Unrecognised tag <{0}>'.format(filter_element.tag)
                    log_debug(m)
                    raise Addon_Error(m)
            log_debug('Adding filter "{0}"'.format(this_filter_dic['name']))
            filters_list.append(this_filter_dic)

    # >> Resolve DEFINE tags (substitute by the defined value)
    for f_definition in filters_list:
        for initial_str, final_str in define_dic.iteritems():
            f_definition['driver']       = f_definition['driver'].replace(initial_str, final_str)
            f_definition['manufacturer'] = f_definition['manufacturer'].replace(initial_str, final_str)
            f_definition['genre']        = f_definition['genre'].replace(initial_str, final_str)
            f_definition['controls']     = f_definition['controls'].replace(initial_str, final_str)
            f_definition['devices']      = f_definition['devices'].replace(initial_str, final_str)
            # f_definition['include']      = f_definition['include'].replace(initial_str, final_str)
            # f_definition['exclude']      = f_definition['exclude'].replace(initial_str, final_str)
            # f_definition['change']       = f_definition['change'].replace(initial_str, final_str)
    return filters_list

# -------------------------------------------------------------------------------------------------
# List of String Parser (LSP) engine (copied from NARS)
# Grammar token objects.
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
        global parser_search_list

        return self.value in parser_search_list

def LSP_advance(id = None):
    global LSP_token

    if id and LSP_token.id != id:
        raise SyntaxError("Expected {0}".format(id))
    LSP_token = LSP_next()

class LSP_operator_open_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP ("
    def nud(self):
        expr = expression()
        advance("OP )")
        return expr

class LSP_operator_close_par_token:
    lbp = 0
    def __init__(self):
        self.id = "OP )"

class LSP_operator_not_token:
    lbp = 50
    def __init__(self):
        self.id = "OP NOT"
    def nud(self):
        self.first = expression(50)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        return not self.first.exec_token()

class LSP_operator_and_token:
    lbp = 10
    def __init__(self):
        self.id = "OP AND"
    def led(self, left):
        self.first = left
        self.second = expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        return self.first.exec_token() and self.second.exec_token()

class LSP_operator_or_token:
    lbp = 10
    def __init__(self):
        self.id = "OP OR"
    def led(self, left):
        self.first = left
        self.second = expression(10)
        return self
    # --- Actual implementation ---
    def exec_token(self):
        return self.first.exec_token() or self.second.exec_token()

class LSP_end_token:
    lbp = 0
    def __init__(self):
        self.id = "END TOKEN"

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

def LSP_expression_exec(rbp = 0):
    global LSP_token

    t = LSP_token
    LSP_token = LSP_next()
    left = t.nud()
    while rbp < LSP_token.lbp:
        t = LSP_token
        LSP_token = LSP_next()
        left = t.led(left)
    return left.exec_token()

def LSP_parse_exec(program, search_list):
    global LSP_token, LSP_next, LSP_parser_search_list

    LSP_parser_search_list = search_list
    LSP_next = LSP_tokenize(program).next
    LSP_token = LSP_next()

    return LSP_expression_exec()

# -------------------------------------------------------------------------------------------------
# MAME machine filters
# -------------------------------------------------------------------------------------------------
#
# Default filter removes device machines
#
def mame_filter_Default(mame_xml_dic):
    log_debug('mame_filter_Default() Starting ...')
    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        if mame_xml_dic[m_name]['isDevice']:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Default() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Options_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Options_tag() Starting ...')
    options_list = f_definition['options']
    log_debug('Option list "{0}"'.format(options_list))

    if not options_list:
        log_debug('mame_filter_Options_tag() Option list is empty.')
        return mame_xml_dic

    # --- Compute bool variables ---
    NoCoin_bool       = True if 'NoCoin' in options_list else False
    NoCoinLess_bool   = True if 'NoCoinLess' in options_list else False
    NoROMs_bool       = True if 'NoROMs' in options_list else False
    NoCHDs_bool       = True if 'NoCHDs' in options_list else False
    NoSamples_bool    = True if 'NoSamples' in options_list else False
    NoMature_bool     = True if 'NoMature' in options_list else False
    NoBIOS_bool       = True if 'NoBIOS' in options_list else False
    NoMechanical_bool = True if 'NoMechanical' in options_list else False
    NoImperfect_bool  = True if 'NoImperfect' in options_list else False
    NoNonWorking_bool = True if 'NoNonworking' in options_list else False
    log_debug('NoCoin_bool       {0}'.format(NoCoin_bool))
    log_debug('NoCoinLess_bool   {0}'.format(NoCoinLess_bool))
    log_debug('NoROMs_bool       {0}'.format(NoROMs_bool))
    log_debug('NoCHDs_bool       {0}'.format(NoCHDs_bool))
    log_debug('NoSamples_bool    {0}'.format(NoSamples_bool))
    log_debug('NoMature_bool     {0}'.format(NoMature_bool))
    log_debug('NoBIOS_bool       {0}'.format(NoBIOS_bool))
    log_debug('NoMechanical_bool {0}'.format(NoMechanical_bool))
    log_debug('NoImperfect_bool  {0}'.format(NoImperfect_bool))
    log_debug('NoNonWorking_bool {0}'.format(NoNonWorking_bool))

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        # >> Remove Coin machines
        if NoCoin_bool:
            if mame_xml_dic[m_name]['coins'] > 0:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove CoinLess machines
        if NoCoinLess_bool:
            if mame_xml_dic[m_name]['coins'] == 0:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove ROM machines
        if NoROMs_bool:
            if mame_xml_dic[m_name]['hasROMs']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove CHD machines
        if NoCHDs_bool:
            if mame_xml_dic[m_name]['hasCHDs']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove Samples machines
        if NoSamples_bool:
            if mame_xml_dic[m_name]['hasSamples']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove Mature machines
        if NoMature_bool:
            if mame_xml_dic[m_name]['isMature']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove BIOS machines
        if NoBIOS_bool:
            if mame_xml_dic[m_name]['isBIOS']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove Mechanical machines
        if NoMechanical_bool:
            if mame_xml_dic[m_name]['isMechanical']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove Imperfect machines
        if NoImperfect_bool:
            if mame_xml_dic[m_name]['isImperfect']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> Remove NonWorking machines
        if NoNonWorking_bool:
            if mame_xml_dic[m_name]['isNonWorking']:
                filtered_out_games += 1
                continue
            else:
                machines_filtered_dic[m_name] = mame_xml_dic[m_name]
        # >> If machine was not removed then add it
        machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Options_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Driver_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Driver_tag() Starting ...')
    driver_filter_expression = f_definition['driver']
    log_debug('Expression "{0}"'.format(driver_filter_expression))

    if not driver_filter_expression:
        log_debug('mame_filter_Driver_tag() User wants all drivers')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        driver_str = mame_xml_dic[m_name]['sourcefile']
        driver_name_list = [ driver_str ]
        boolean_result = LSP_parse_exec(driver_filter_expression, driver_name_list)
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Driver_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Manufacturer_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Manufacturer_tag() Starting ...')
    driver_filter_expression = f_definition['manufacturer']
    log_debug('Expression "{0}"'.format(driver_filter_expression))

    if not driver_filter_expression:
        log_debug('mame_filter_Manufacturer_tag() User wants all manufacturers')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        bool_result = MP_parse_exec(driver_filter_expression, mame_xml_dic[m_name]['manufacturer'])
        if not bool_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Manufacturer_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Genre_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Genre_tag() Starting ...')
    filter_expression = f_definition['genre']
    log_debug('Expression "{0}"'.format(filter_expression))

    if not filter_expression:
        log_debug('mame_filter_Genre_tag() User wants all genres')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        item_str_list = [ mame_xml_dic[m_name]['genre'] ]
        set_parser_search_list(item_str_list)
        boolean_result = parse_exec(filter_expression)
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Genre_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Controls_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Controls_tag() Starting ...')
    filter_expression = f_definition['controls']
    log_debug('Expression "{0}"'.format(filter_expression))

    if not filter_expression:
        log_debug('mame_filter_Controls_tag() User wants all genres')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        item_str_list = [ mame_xml_dic[m_name]['controls'] ]
        set_parser_search_list(item_str_list)
        boolean_result = parse_exec(filter_expression)
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Controls_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Devices_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Devices_tag() Starting ...')
    filter_expression = f_definition['devices']
    log_debug('Expression "{0}"'.format(filter_expression))

    if not filter_expression:
        log_debug('mame_filter_Devices_tag() User wants all genres')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        # --- Update search list variable and call parser to evaluate expression ---
        item_str_list = [ mame_xml_dic[m_name]['devices'] ]
        set_parser_search_list(item_str_list)
        boolean_result = parse_exec(filter_expression)
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Devices_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic

def mame_filter_Year_tag(mame_xml_dic, f_definition):
    log_debug('mame_filter_Year_tag() Starting ...')
    filter_expression = f_definition['year']
    log_debug('Expression "{0}"'.format(filter_expression))

    if not filter_expression:
        log_debug('mame_filter_Year_tag() User wants all genres')
        return mame_xml_dic

    initial_num_games = len(mame_xml_dic)
    filtered_out_games = 0
    machines_filtered_dic = {}
    for m_name in sorted(mame_xml_dic):
        # --- Update search int variable and call parser to evaluate expression ---
        item_str_list = mame_xml_dic[m_name]['year']
        set_parser_search_list(item_str_list)
        boolean_result = parse_exec(filter_expression)
        if not boolean_result:
            filtered_out_games += 1
        else:
            machines_filtered_dic[m_name] = mame_xml_dic[m_name]
    log_debug('mame_filter_Year_tag() Initial {0} | '.format(initial_num_games) + \
              'Removed {0} | '.format(filtered_out_games) + \
              'Remaining {0}'.format(len(machines_filtered_dic)))

    return machines_filtered_dic
