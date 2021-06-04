#!/usr/bin/python3 -B

# --- Addon modules ---
import os
import sys
if __name__ == "__main__" and __package__ is None:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('Adding to sys.path "{}"'.format(path))
    sys.path.append(path)
from resources.constants import *
# from resources.utils import *
# from resources.misc import *

# --- Python standard library ---
import io
import json
import pprint
import re
import xml.etree.ElementTree

# --- From utils.py ------------------------------------------------------------------------------
def utils_load_XML_to_ET(filename):
    log_debug('utils_load_XML_to_ET() Loading {}'.format(filename))
    xml_tree = None
    try:
        xml_tree = xml.etree.ElementTree.parse(filename)
    except IOError as ex:
        log_debug('utils_load_XML_to_ET() (IOError) errno = {}'.format(ex.errno))
        # log_debug(text_type(ex.errno.errorcode))
        # No such file or directory
        if ex.errno == errno.ENOENT:
            log_error('utils_load_XML_to_ET() (IOError) ENOENT No such file or directory.')
        else:
            log_error('utils_load_XML_to_ET() (IOError) Unhandled errno value.')
    except xml.etree.ElementTree.ParseError as ex:
        log_error('utils_load_XML_to_ET() (ParseError) Exception parsing {}'.format(filename))
        log_error('utils_load_XML_to_ET() (ParseError) {}'.format(text_type(ex)))
    return xml_tree
# ------------------------------------------------------------------------------------------------

# --- compatibility functions ---------------------------------------------------------------------
def log_variable(var_name, var): print('Dumping variable "{}"\n{}'.format(var_name, pprint.pformat(var)))
def log_error(mystr): print(mystr)
def log_warning(mystr): print(mystr)
def log_info(mystr): print(mystr)
def log_debug(mystr): print(mystr)

# Aux function to test REs
def test_re(re_str, line_str):
    m = re.search(re_str, line_str)
    if m:
        print('RE "{}", str "{}"'.format(re_str, line_str))
        print('MATCHES {}'.format(m.groups()))
    else:
        print('RE "{}", str "{}"'.format(re_str, line_str))
        print('FAILS')
    print('')

# --- functions -----------------------------------------------------------------------------------
# Builds a string separated by a | character. Replaces | ocurrences with _
# The string can be separated with str.split('|')
def misc_build_db_str_3(str1, str2, str3):
    if str1.find('|') >= 0: str1 = str1.replace('|', '_')
    if str2.find('|') >= 0: str2 = str2.replace('|', '_')
    if str3.find('|') >= 0: str3 = str3.replace('|', '_')

    return '{}|{}|{}'.format(str1, str2, str3)

# --- BEGIN code in dev-parsers/test_parser_history_xml.py ----------------------------------------
# Loads History.xml, a new XML version of History.dat
#
# MAME machine:
# <entry>
#     <systems>
#     <system name="dino" />
#     <system name="dinou" />
#     </systems>
#     <text />
# </entry>
#
# One description can be for several SL items and several SL lists:
# <entry>
#     <software>
#         <item list="snes" name="smw2jb" />
#         <item list="snes" name="smw2ja" />
#         <item list="snes" name="smw2j" />
#     </software>
#     <text />
# </entry>
#
# Example of a problematic entry:
# <entry>
#     <systems>
#         <system name="10yardj" />
#     </systems>
#     <software>
#         <item list="vgmplay" name="10yard" />
#     </software>
#     <text />
# </entry>
#
# The key in the data dictionary is the first machine found on history.xml
#
# history_dic = {
#     'version' : '2.32', # string
#     'date' : '2021-05-28', # string
#     'index' : {
#         'nes' : {
#             'name': 'nes', # string, later changed with beautiful name
#             'machines' : {
#                 'machine_name' : "beautiful_name|db_list_name|db_machine_name",
#                 '100mandk' : "beautiful_name|nes|100mandk",
#                 '89denku' : "beautiful_name|nes|89denku",
#             },
#         },
#         'mame' : {
#             'name' : string,
#             'machines': {
#                 '88games' : "beautiful_name|db_list_name|db_machine_name",
#                 'flagrall' : "beautiful_name|db_list_name|db_machine_name",
#             },
#         },
#     },
#     'data' = {
#         'nes' : {
#             '100mandk' : string,
#             '89denku' : string,
#         },
#         'mame' : {
#             '88games' : string,
#             'flagrall' : string,
#         },
#     }
# }
def mame_load_History_xml(filename):
    log_info('mame_load_History_xml() Parsing "{}"'.format(filename))
    history_dic = {
        'version' : 'Unknown',
        'date' : 'Unknown',
        'index' : {},
        'data' : {},
    }
    __debug_xml_parser = False
    entry_counter = 0
    # Convenience variables.
    history_idx = history_dic['index']
    history_data = history_dic['data']

    xml_tree = utils_load_XML_to_ET(filename)
    if not xml_tree: return history_dic
    xml_root = xml_tree.getroot()
    history_dic['version'] = xml_root.attrib['version'] + ' XML ' + xml_root.attrib['date']
    history_dic['date'] = xml_root.attrib['date']
    for root_el in xml_root:
        if __debug_xml_parser: log_debug('Root child tag "{}"'.format(root_el.tag))
        if root_el.tag != 'entry':
            log_error('Unknown tag <{}>'.format(root_el.tag))
            raise TypeError
        entry_counter += 1
        item_list = []
        for entry_el in root_el:
            if __debug_xml_parser: log_debug('Entry child tag "{}"'.format(entry_el.tag))
            if entry_el.tag == 'software':
                for software_el in entry_el:
                    if software_el.tag != 'item':
                        log_error('Unknown <software> child tag <{}>'.format(software_el.tag))
                        raise TypeError
                    item_list.append((software_el.attrib['list'], software_el.attrib['name']))
            elif entry_el.tag == 'systems':
                for system_el in entry_el:
                    if system_el.tag != 'system':
                        log_error('Unknown <systems> child tag <{}>'.format(software_el.tag))
                        raise TypeError
                    item_list.append(('mame', software_el.attrib['name']))
            elif entry_el.tag == 'text':
                # Generate biography text.
                bio_str = entry_el.text
                bio_str = bio_str[1:] if bio_str[0] == '\n' else bio_str
                bio_str = bio_str[:-1] if bio_str[-1] == '\n' else bio_str
                bio_str = bio_str.replace('\n\t\t', '')

                # Add list and machine names to index database.
                if len(item_list) < 1:
                    log_warning('Empty item_list in entry_counter = {}'.format(entry_counter))
                    continue
                db_list_name = item_list[0][0]
                db_machine_name = item_list[0][1]
                for list_name, machine_name in item_list:
                    m_str = misc_build_db_str_3(machine_name, db_list_name, db_machine_name)
                    try:
                        history_idx[list_name]['machines'][machine_name] = m_str
                    except:
                        history_idx[list_name] = {'name' : list_name, 'machines' : {}}
                        history_idx[list_name]['machines'][machine_name] = m_str

                # Add biography string to main database.
                try:
                    history_data[db_list_name][db_machine_name] = bio_str
                except:
                    history_data[db_list_name] = {}
                    history_data[db_list_name][db_machine_name] = bio_str
            else:
                log_error('Unknown tag <{}>'.format(root_el.tag))
                raise TypeError
        if __debug_xml_parser and entry_counter > 100: break
    log_info('mame_load_History_xml() Version "{}"'.format(history_dic['version']))
    log_info('mame_load_History_xml() Date "{}"'.format(history_dic['date']))
    log_info('mame_load_History_xml() Rows in index {}'.format(len(history_dic['index'])))
    log_info('mame_load_History_xml() Rows in data {}'.format(len(history_dic['data'])))
    return history_dic
# --- END code in dev-parsers/test_parser_history_dat.py ------------------------------------------

# --- main code -----------------------------------------------------------------------------------
print('*** Testing function mame_load_History_XML() ***')
history_dic = mame_load_History_xml('history.xml')
print('version "{}"'.format(history_dic['version']))
print('date "{}"'.format(history_dic['date']))

filename = 'history_idx_xml.json'
print('Writing "{}"'.format(filename))
with open(filename, 'w') as file:
    file.write(json.dumps(history_dic['index'], sort_keys = True, indent = 2))

filename = 'history_data_xml.json'
print('Writing "{}"'.format(filename))
with open(filename, 'w') as file:
    file.write(json.dumps(history_dic['data'], sort_keys = True, indent = 2))
