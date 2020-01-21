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
#            'machine_name' : "beautiful_name|db_list_name|db_machine_name",
#            '100mandk' : "beautiful_name|nes|100mandk",
#            '89denku' : "beautiful_name|nes|89denku",
#        },
#    }
#    'mame' : {
#        'name' : string,
#        'machines': {
#            '88games' : "beautiful_name|db_list_name|db_machine_name",
#            'flagrall' : "beautiful_name|db_list_name|db_machine_name",
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
    # Due to syntax errors in History.dat m_data may have invalid data, for example
    # exmpty strings as list_name and/or machine names.
    # m_data = [
    #     (line_number, list_name, [machine1, machine2, ...]),
    #     ...
    # ]
    m_data = []

    # --- read_status FSM values ---
    # History.dat has some syntax errors, like empty machine names. To fix this, do
    # the parsing on two stages: first read the raw data and the bio and then
    # check if the data is OK before adding it to the index and the DB.
    # 0 -> Looking for '$info=machine_name_1,machine_name_2,' or '$SL_name=item_1,item_2,'
    #      If '$bio' found go to 1.
    # 1 -> Reading information. If '$end' found go to 2.
    # 2 -> Add information to database if no errors. Then go to 0.
    read_status = 0

    # Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_History_DAT() (IOError) opening "{0}"'.format(filename))
        return (history_idx_dic, history_dic, version_str)
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
            if line_str == '':
                continue
            # Machine list line
            # Parses lines like "$info=99lstwar,99lstwara,99lstwarb,"
            # Parses lines like "$info=99lstwar,99lstwara,99lstwarb"
            # History.dat has syntactic errors like "$dc=,".
            # History.dat has syntactic errors like "$megadriv=".
            m = re.search(r'^\$(.+?)=(.*?),?$', line_str)
            if m:
                num_header_line += 1
                list_name = m.group(1)
                machine_name_raw = m.group(2)
                # Remove trailing ',' to fix history.dat syntactic errors like
                # "$snes_bspack=bsfami,,"
                if len(machine_name_raw) > 1 and machine_name_raw[-1] == ',':
                    machine_name_raw = machine_name_raw[:-1]
                # Transform some special list names
                if list_name in {'info', 'info,megatech', 'info,stv'}: list_name = 'mame'
                mname_list = machine_name_raw.split(',')
                m_data.append([num_header_line, list_name, mname_list])
                continue
            if line_str == '$bio':
                read_status = 1
                info_str_list = []
                continue
            # If we reach this point it's an error.
            raise TypeError('Wrong header "{}" (line {:,})'.format(line_str, line_number))
        elif read_status == 1:
            if line_str == '$end':
                # Generate biography text.
                bio_str = '\n'.join(info_str_list)
                if bio_str[0] == '\n': bio_str = bio_str[1:]
                if bio_str[-1] == '\n': bio_str = bio_str[:-1]

                # Clean m_data of bad data due to History.dat syntax errors, for example
                # empty machine names.
                # clean_m_data = [
                #     (list_name, [machine_name_1, machine_name_2, ...] ),
                #     ...,
                # ]
                clean_m_data = []
                for dtuple in m_data:
                    line_num, list_name, mname_list = dtuple
                    # If list_name is empty drop the full line
                    if not list_name: continue
                    # Clean empty machine names.
                    clean_mname_list = []
                    for machine_name in mname_list:
                        # Skip bad/wrong machine names.
                        if not machine_name: continue
                        if machine_name == ',': continue
                        clean_mname_list.append(machine_name)
                    clean_m_data.append((list_name, clean_mname_list))

                # Reset FSM status
                read_status = 2
                num_header_line = 0
                m_data = []
                info_str_list = []
            else:
                info_str_list.append(line_str)
        elif read_status == 2:
            # Go to state 0 of the FSM.
            read_status = 0

            # Ignore machine if no valid data at all.
            if len(clean_m_data) == 0:
                log_warning('On History.dat line {:,}'.format(line_number))
                log_warning('clean_m_data is empty.')
                log_warning('Ignoring entry in History.dat database')
                continue
            # Ignore if empty list name.
            if not clean_m_data[0][0]:
                log_warning('On History.dat line {:,}'.format(line_number))
                log_warning('clean_m_data empty list name.')
                log_warning('Ignoring entry in History.dat database')
                continue
            # Ignore if empty machine list.
            if not clean_m_data[0][1]:
                log_warning('On History.dat line {:,}'.format(line_number))
                log_warning('Empty machine name list.')
                log_warning('db_list_name "{}"'.format(clean_m_data[0][0]))
                log_warning('Ignoring entry in History.dat database')
                continue
            if not clean_m_data[0][1][0]:
                log_warning('On History.dat line {:,}'.format(line_number))
                log_warning('Empty machine name first element.')
                log_warning('db_list_name "{}"'.format(clean_m_data[0][0]))
                log_warning('Ignoring entry in History.dat database')
                continue
            db_list_name = clean_m_data[0][0]
            db_machine_name = clean_m_data[0][1][0]

            # Add list and machine names to index database.
            for dtuple in clean_m_data:
                list_name, machine_name_list = dtuple
                if list_name not in history_idx_dic:
                    history_idx_dic[list_name] = {'name' : list_name, 'machines' : {}}
                for machine_name in machine_name_list:
                    m_str = misc_build_db_str_3(machine_name, db_list_name, db_machine_name)
                    history_idx_dic[list_name]['machines'][machine_name] = m_str

            # Add biography string to main database.
            if db_list_name not in history_dic: history_dic[db_list_name] = {}
            history_dic[db_list_name][db_machine_name] = bio_str
        else:
            raise TypeError('Wrong read_status = {} (line {:,})'.format(read_status, line_number))
    # Close file
    f.close()
    log_info('mame_load_History_DAT() Version "{}"'.format(version_str))
    log_info('mame_load_History_DAT() Rows in history_idx_dic {}'.format(len(history_idx_dic)))
    log_info('mame_load_History_DAT() Rows in history_dic {}'.format(len(history_dic)))

    return (history_idx_dic, history_dic, version_str)

# --- main code -----------------------------------------------------------------------------------
# Test all possible sintactic errors in History.dat
print('*** Testing regular expressions')
re_str = r'^\$(.+?)=(.*?),?$' 
test_re(re_str, '$megadriv=sonic1')
test_re(re_str, '$megadriv=sonic1,')
test_re(re_str, '$megadriv=sonic1,,')
test_re(re_str, '$megadriv=sonic1,sonic2')
test_re(re_str, '$megadriv=sonic1,sonic2,')
test_re(re_str, '$megadriv=sonic1,sonic2,,')
test_re(re_str, '$megadriv=,,')
test_re(re_str, '$megadriv=,')
test_re(re_str, '$megadriv=')

print('*** Testing string.split() behaviour')
# Lesson learned: CSV strings MUST NOT END in a comma.
str_list = [
    '99lstwar,99lstwara,99lstwarb',
    '99lstwar,99lstwara,99lstwarb,',
]
for test_str in str_list:
    print('Str   "{}"'.format(test_str))
    print('Split {}\n'.format(test_str.split(',')))

print('*** Testing function mame_load_History_DAT()')
(history_idx_dic, history_dic, version_str) = mame_load_History_DAT('history.dat')
print('version_str {}'.format(version_str))
with open('history_idx_dic.json', 'w') as f:
    f.write(json.dumps(history_idx_dic, sort_keys = True, indent = 2))
with open('history_dic.json', 'w') as f:
    f.write(json.dumps(history_dic, sort_keys = True, indent = 2))
