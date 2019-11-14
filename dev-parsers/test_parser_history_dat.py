#!/usr/bin/python -B
#
import json
import pprint
import re
import sys

# --- compatibility functions ---------------------------------------------------------------------
def log_variable(var_name, var):
    print('Dumping variable "{}"\n{}'.format(var_name, pprint.pformat(var)))

def log_error(str): print(str)
def log_warning(str): print(str)
def log_info(str): print(str)
def log_debug(str): print(str)

# --- functions -----------------------------------------------------------------------------------
#
# Loads History.dat
#
# One description can be for several MAME machines:
#     $info=99lstwar,99lstwara,99lstwarb,
#     $bio
#
# One description can be for several SL items and several SL lists:
#     $amigaocs_flop=alloallo,alloallo1,
#     $amigaaga_flop=alloallo,alloallo1,
#     $amiga_flop=alloallo,alloallo1,
#     $bio
#
# key_in_history_dic is the first machine on the list on the first line.
#
# history_idx_dic = {
#    'nes' : {
#        'name': string,
#        'machines' : {
#            'machine_name' : "beautiful_name,db_list_name,db_machine_name",
#            '100mandk' : "beautiful_name,nes,100mandk",
#            '89denku' : "beautiful_name,nes,89denku",
#        },
#    }
#    'mame' : {
#        'name' : string,
#        'machines': {
#            '88games' : "beautiful_name,db_list_name,db_machine_name",
#            'flagrall' : "beautiful_name,db_list_name,db_machine_name",
#        },
#    }
# }
#
# history_dic = {
#    'nes' : {
#        '100mandk' : string,
#        '89denku' : string,
#    },
#    'mame' : {
#        '88games' : string,
#        'flagrall' : string,
#    },
# }
def mame_load_History_DAT(filename):
    log_info('mame_load_History_DAT() Parsing "{0}"'.format(filename))
    version_str = 'Not found'
    history_idx_dic = {}
    history_dic = {}
    __debug_function = False
    line_number = 0
    num_header_line = 0
    ignore_this_bio = False

    # --- read_status FSM values ---
    # 0 -> Looking for '$info=machine_name_1,machine_name_2,' or '$SL_name=item_1,item_2,'
    #      If '$bio' found go to 1.
    # 1 -> Reading information. If '$end' found go to 0.
    read_status = 0

    # Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_History_DAT() (IOError) opening "{0}"'.format(filename))
        return (history_idx_dic, history_dic, version_str)

    # Parse file
    for file_line in f:
        line_number += 1
        stripped_line = file_line.strip()
        line_str = stripped_line.decode('utf-8', 'replace')
        if __debug_function: log_debug('Line "{0}"'.format(line_str))
        if read_status == 0:
            # Skip comments: lines starting with '##'
            # Look for version string in comments
            if re.search(r'^##', line_str):
                m = re.search(r'## REVISION\: ([0-9\.]+)$', line_str)
                if m: version_str = m.group(1)
                continue
            if line_str == '': continue
            # Machine list line
            # Parses lines like "$info=99lstwar,99lstwara,99lstwarb,"
            # Parses lines like "$info=99lstwar,99lstwara,99lstwarb"
            m = re.search(r'^\$(.+?)=(.+?),?$', line_str)
            if m:
                num_header_line += 1
                list_name = m.group(1)
                machine_name_raw = m.group(2)
                # Remove trailing ',' to fix history.dat syntactic errors like
                # "$snes_bspack=bsfami,,"
                if machine_name_raw[-1] == ',':
                    machine_name_raw = machine_name_raw[:-1]
                if not list_name:
                    ignore_this_bio = True
                    log_warning('On History.dat line {:,}, empty list_name "{}"'.format(
                        line_number, list_name))
                # History.dat has other syntactic errors like "$dc=,"
                # In this case ignore those biographies and do not add to the index.
                if not machine_name_raw:
                    ignore_this_bio = True
                    log_warning('On History.dat line {:,}, empty machine_name_raw "{}"'.format(
                        line_number, machine_name_raw))
                else:
                    # history.dat V2.15 has syntactic errors, for example "$snes_bspack=bsfami,,"
                    # The regular expression removes the trailing ',' but not the second one.
                    # At this point the error must have been fixed in previous code.
                    if machine_name_raw[-1] == ',':
                        log_debug('group 0 "{}"'.format(m.group(0)))
                        log_debug('group 1 "{}"'.format(list_name))
                        log_debug('group 2 "{}"'.format(machine_name_raw))
                        raise TypeError('machine_name_raw ends in ","')
                mname_list = machine_name_raw.split(',')
                num_machines = len(mname_list)
                # Transform some special list names
                if list_name in {'info', 'info,megatech', 'info,stv'}: list_name = 'mame'
                # First line in the header determines the list and key in the database.
                if num_header_line == 1:
                    db_list_name = list_name
                    db_machine_name = mname_list[0]
                # Check for errors.
                if not db_list_name:
                    log_warning('On History.dat line {:,}, empty db_list_name "{}"'.format(
                        line_number, db_list_name))
                if not db_machine_name:
                    log_warning('On History.dat line {:,}, empty db_machine_name "{}"'.format(
                        line_number, db_machine_name))
                # Add machines to index.
                if ignore_this_bio:
                    log_warning('Ignoring machine list at line {:,}'.format(line_number))
                else:
                    for machine_name in mname_list:
                        if list_name not in history_idx_dic:
                            history_idx_dic[list_name] = {'name' : list_name, 'machines' : {}}
                        # Check that there are no commas before building the CSV string.
                        if machine_name.find(',') >= 0:
                            raise TypeError('Comma in machine_name "{}"'.format(machine_name))
                        if db_list_name.find(',') >= 0:
                            raise TypeError('Comma in db_list_name "{}"'.format(db_list_name))
                        if db_machine_name.find(',') >= 0:
                            raise TypeError('Comma in db_machine_name "{}"'.format(db_machine_name))
                        m_str = '{},{},{}'.format(machine_name, db_list_name, db_machine_name)
                        history_idx_dic[list_name]['machines'][machine_name] = m_str
                continue
            if line_str == '$bio':
                read_status = 1
                info_str_list = []
                continue
            # If we reach this point it's an error.
            raise TypeError('Wrong header "{}" (line {:,})'.format(line_str, line_number))
        elif read_status == 1:
            if line_str == '$end':
                if ignore_this_bio:
                    log_warning('Not adding bio ending at line {:,}'.format(line_number))
                else:
                    if db_list_name not in history_dic: history_dic[db_list_name] = {}
                    h_str = '\n'.join(info_str_list)
                    if h_str[-1] == '\n': h_str = h_str[:-1]
                    history_dic[db_list_name][db_machine_name] = h_str
                read_status = 0
                num_header_line = 0
                ignore_this_bio = False
            else:
                info_str_list.append(line_str)
        else:
            raise TypeError('Wrong read_status = {} (line {:,})'.format(read_status, line_number))
    # Close file
    f.close()
    log_info('mame_load_History_DAT() Version "{0}"'.format(version_str))
    log_info('mame_load_History_DAT() Rows in history_idx_dic {0}'.format(len(history_idx_dic)))
    log_info('mame_load_History_DAT() Rows in history_dic {0}'.format(len(history_dic)))

    return (history_idx_dic, history_dic, version_str)

# --- main code -----------------------------------------------------------------------------------
print('Testing string.split() behaviour')
# Lesson learned: CSV strings MUST NOT END in a comma.
str_list = [
    '99lstwar,99lstwara,99lstwarb',
    '99lstwar,99lstwara,99lstwarb,',
]
for test_str in str_list:
    print('Str   "{}"'.format(test_str))
    print('Split {}\n'.format(test_str.split(',')))

print('Testing function mame_load_History_DAT()')
(history_idx_dic, history_dic, version_str) = mame_load_History_DAT('history.dat')
print('version_str {}'.format(version_str))
with open('history_idx_dic.json', 'w') as f:
    f.write(json.dumps(history_idx_dic, sort_keys = True, indent = 2))
with open('history_dic.json', 'w') as f:
    f.write(json.dumps(history_dic, sort_keys = True, indent = 2))
