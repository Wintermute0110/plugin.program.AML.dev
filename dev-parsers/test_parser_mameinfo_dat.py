#!/usr/bin/python3 -B

import io
import json
# import pprint
import re
# import sys

# --- compatibility functions ---------------------------------------------------------------------
def log_error(str): print(str)
def log_warning(str): print(str)
def log_info(str): print(str)
def log_debug(str): print(str)

# --- BEGIN code in dev-parsers/test_parser_mameinfo_dat.py ---------------------------------------
# mameinfo.dat has information for both MAME machines and MAME drivers.
#
# idx_dic  = {
#     'mame' : {
#         '88games' : 'beautiful_name',
#         'flagrall' : 'beautiful_name',
#     },
#     'drv' : {
#         '88games.cpp' : 'beautiful_name'],
#         'flagrall.cpp' : 'beautiful_name'],
#     }
# }
# data_dic = {
#    'mame' : {
#        '88games' : string,
#        'flagrall' : string,
#     },
#    'drv' : {
#        '1942.cpp' : string,
#        '1943.cpp' : string,
#    }
# }
def mame_load_MameInfo_DAT(filename):
    log_info('mame_load_MameInfo_DAT() Parsing "{}"'.format(filename))
    ret_dic = {
        'version' : 'Unknown',
        'index' : {
            'mame' : {},
            'drv' : {},
        },
        'data' : {},
    }
    __debug_function = False
    line_counter = 0

    # --- read_status FSM values ---
    # 0 -> Looking for '$(xxxx)=(machine_name)'
    # 1 -> Looking for $bio
    # 2 -> Reading information. If '$end' found go to 0.
    # 3 -> Ignoring information. If '$end' found go to 0.
    read_status = 0
    try:
        f = io.open(filename, 'rt', encoding = 'utf-8')
    except IOError:
        log_info('mame_load_MameInfo_DAT() (IOError) opening "{}"'.format(filename))
        return ret_dic
    for file_line in f:
        line_counter += 1
        line_uni = file_line.strip()
        # if __debug_function: log_debug('Line "{}"'.format(line_uni))
        if read_status == 0:
            # Skip comments: lines starting with '#'
            # Look for version string in comments
            if re.search(r'^#', line_uni):
                m = re.search(r'# MAMEINFO.DAT v([0-9\.]+)', line_uni)
                if m: ret_dic['version'] = m.group(1)
                continue
            if line_uni == '': continue
            # New machine or driver information
            m = re.search(r'^\$info=(.+?)$', line_uni)
            if m:
                machine_name = m.group(1)
                if __debug_function: log_debug('Machine "{}"'.format(machine_name))
                read_status = 1
        elif read_status == 1:
            if __debug_function: log_debug('Second line "{}"'.format(line_uni))
            if line_uni == '$mame':
                read_status = 2
                info_str_list = []
                list_name = 'mame'
                ret_dic['index'][list_name][machine_name] = machine_name
            elif line_uni == '$drv':
                read_status = 2
                info_str_list = []
                list_name = 'drv'
                ret_dic['index'][list_name][machine_name] = machine_name
            # Ignore empty lines between "$info=xxxxx" and "$mame" or "$drv"
            elif line_uni == '':
                continue
            else:
                raise TypeError('Wrong second line = "{}" (line {:,})'.format(line_uni, line_counter))
        elif read_status == 2:
            if line_uni == '$end':
                if list_name not in ret_dic['data']: ret_dic['data'][list_name] = {}
                ret_dic['data'][list_name][machine_name] = '\n'.join(info_str_list).strip()
                read_status = 0
            else:
                info_str_list.append(line_uni)
        else:
            raise TypeError('Wrong read_status = {} (line {:,})'.format(read_status, line_counter))
    f.close()
    log_info('mame_load_MameInfo_DAT() Version "{}"'.format(ret_dic['version']))
    log_info('mame_load_MameInfo_DAT() Rows in index {}'.format(len(ret_dic['index'])))
    log_info('mame_load_MameInfo_DAT() Rows in data {}'.format(len(ret_dic['data'])))
    return ret_dic
# --- END code in dev-parsers/test_parser_mameinfo_dat.py -----------------------------------------

# --- main code -----------------------------------------------------------------------------------
print('*** Testing function mame_load_MameInfo_DAT()')
(idx_dic, data_dic, version_str) = mame_load_MameInfo_DAT('mameinfo.dat')
print('version_str {}'.format(version_str))
with open('mameinfo_idx_dic.json', 'w') as f:
    f.write(json.dumps(idx_dic, sort_keys = True, indent = 2))
with open('mameinfo_dic.json', 'w') as f:
    f.write(json.dumps(data_dic, sort_keys = True, indent = 2))
