#!/usr/bin/python -B
#
import pprint
import re

# --- compatibility functions ---------------------------------------------------------------------
def log_variable(var_name, var):
    print('Dumping variable "{}"\n{}'.format(var_name, pprint.pformat(var)))

def log_info(str): print(str)

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
#        'machines' : [
#            [machine_name, beautiful_name, db_list_name, db_machine_name],
#            ['100mandk', 'beautiful_name', '100mandk'],
#            ['89denku', 'beautiful_name', '89denku'],
#        ],
#    }
#    'mame' : {
#        'name' : string,
#        'machines': [
#            ['88games', 'beautiful_name', db_list_name, db_machine_name],
#            ['flagrall', 'beautiful_name', db_list_name, db_machine_name],
#        ],
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
            m = re.search(r'^\$(.+?)=(.+?),$', line_str)
            if m:
                num_header_line += 1
                list_name = m.group(1)
                mname_list = m.group(2).split(',')
                num_machines = len(mname_list)
                # Transform some special list names
                if list_name in {'info', 'info,megatech', 'info,stv'}: list_name = 'mame'
                # First line in the header determines the list and key in the database
                if num_header_line == 1:
                    db_list_name = list_name
                    db_machine_name = mname_list[0]
                for machine_name in mname_list:
                    if list_name not in history_idx_dic:
                        history_idx_dic[list_name] = {'name' : list_name, 'machines' : []}
                    m_list = [machine_name, machine_name, db_list_name, db_machine_name]
                    history_idx_dic[list_name]['machines'].append(m_list)
                continue
            # Machine list line
            m = re.search(r'^\$(.+?)=(.+?)$', line_str)
            if m:
                num_header_line += 1
                list_name = m.group(1)
                machine_name = m.group(2)
                if num_header_line == 1:
                    db_list_name = list_name
                    db_machine_name = machine_name
                if list_name not in history_idx_dic:
                    history_idx_dic[list_name] = {'name' : list_name, 'machines' : []}
                m_list = [machine_name, machine_name, db_list_name, db_machine_name]
                history_idx_dic[list_name]['machines'].append(m_list)
                continue
            if line_str == '$bio':
                read_status = 1
                info_str_list = []
                continue
            # If we reach this point it's an error.
            raise TypeError('Wrong header "{}" (line {})'.format(line_str, line_number))
        elif read_status == 1:
            if line_str == '$end':
                if db_list_name not in history_dic: history_dic[db_list_name] = {}
                history_dic[db_list_name][db_machine_name] = '\n'.join(info_str_list)
                read_status = 0
                num_header_line = 0
            else:
                info_str_list.append(line_str)
        else:
            raise TypeError('Wrong read_status = {} (line {})'.format(read_status, line_number))
    # Close file
    f.close()
    log_info('mame_load_History_DAT() Version "{0}"'.format(version_str))
    log_info('mame_load_History_DAT() Rows in history_idx_dic {0}'.format(len(history_idx_dic)))
    log_info('mame_load_History_DAT() Rows in history_dic {0}'.format(len(history_dic)))

    return (history_idx_dic, history_dic, version_str)

# --- main code -----------------------------------------------------------------------------------
print('Testing function mame_load_History_DAT()')
(history_idx_dic, history_dic, version_str) = mame_load_History_DAT('history.dat')
