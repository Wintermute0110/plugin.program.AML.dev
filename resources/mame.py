# -*- coding: utf-8 -*-
# Advanced MAME Launcher MAME specific stuff
#

# Copyright (c) 2016-2017 Wintermute0110 <wintermute0110@gmail.com>
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
from __future__ import unicode_literals
import zipfile as z

# --- AEL packages ---
from utils import *
try:
    from utils_kodi import *
except:
    from utils_kodi_standalone import *

# -------------------------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------------------------
# >> Substitute notable drivers with a proper name
mame_driver_name_dic = {
    # --- Capcom ---
    'cps1.cpp'     : 'Capcom Play System 1',
    'cps2.cpp'     : 'Capcom Play System 2',
    'cps3.cpp'     : 'Capcom Play System 3',

    # --- Namco ---
    'galaxian.cpp' : 'Namco Galaxian-derived hardware',
    'namcops2.cpp' : 'Namco System 246 / System 256 (Sony PS2 based)',
    'neodriv.hxx'  : 'SNK NeoGeo MVS',
    'neogeo.cpp'   : 'SNK NeoGeo',
    'seta.cpp'     : 'Seta Hardware',

    # --- SEGA ---
    'chihiro.cpp'  : 'SEGA Chihiro (Xbox-based)',
    'model2.cpp'   : 'SEGA Model 2',
    'naomi.cpp'    : 'SEGA Naomi / Naomi 2 / Atomiswave',
    'segac2.cpp'   : 'SEGA System C (System 14)',
    'segae.cpp'    : 'SEGA System E',
    'segaorun.cpp' : 'SEGA Out Run hardware',
    'segas16a.cpp' : 'SEGA System 16A',
    'segas16b.cpp' : 'SEGA System 16B',
    'segas18.cpp'  : 'SEGA System 18',
    'segas24.cpp'  : 'SEGA System 24',
    'segas32.cpp'  : 'SEGA System 32',
    'segasp.cpp'   : 'SEGA System SP (Spider)',
    'segaxbd.cpp'  : 'SEGA X-board',
    'system1.cpp'  : 'SEGA System1 / System 2',

    # --- Taito ---
    'taito_b.cpp'  : 'Taito B System',
    'taito_l.cpp'  : 'Taito L System',
    'taito_f3.cpp' : 'Taito F3 System',
    'taito_f2.cpp' : 'Taito F2 System',

    # --- SONY ---
    'zn.cpp'       : 'Sony ZN1/ZN2 (Arcade PSX)',
}

#
# Numerical MAME version. Allows for comparisons like ver_mame >= MAME_VERSION_0190
# Support MAME versions higher than 0.53 August 12th 2001.
# See header of MAMEINFO.dat for a list of all MAME versions.
# a.bbb.ccc gets transformed into an uint a,bbb,ccc
# Examples:
#   '0.53'   ->  53000
#   '0.70'   ->  70000
#   '0.70u1' ->  70001
#   '0.150'  -> 150000
#   '0.190'  -> 190000
#
# mame_version_raw examples:
#   a) '0.194 (mame0194)' from '<mame build="0.194 (mame0194)" debug="no" mameconfig="10">'
#
# re.search() returns a MatchObject https://docs.python.org/2/library/re.html#re.MatchObject
def mame_get_numerical_version(mame_version_str):
    log_verb('mame_get_numerical_version() mame_version_str = "{0}"'.format(mame_version_str))
    version_int = 0
    m_obj = re.search('^(\d+?)\.(\d+?) \(', mame_version_str)
    if m_obj:
        major = int(m_obj.group(1))
        minor = int(m_obj.group(2))
        log_verb('mame_get_numerical_version() major = {0}'.format(major))
        log_verb('mame_get_numerical_version() minor = {0}'.format(minor))
        version_int = major * 100000 + minor * 1000
    log_verb('mame_get_numerical_version() version_int = {0}'.format(version_int))

    return version_int

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------
def mame_get_control_str(control_type_list):
    control_set = set()
    improved_c_type_list = mame_improve_control_type_list(control_type_list)
    for control in improved_c_type_list: control_set.add(control)
    control_str = ', '.join(list(sorted(control_set)))

    return control_str

def mame_get_screen_rotation_str(display_rotate):
    if display_rotate == '0' or display_rotate == '180':
        screen_str = 'horizontal'
    elif display_rotate == '90' or display_rotate == '270':
        screen_str = 'vertical'
    else:
        raise TypeError

    return screen_str

def mame_get_screen_str(machine_name, machine):
    d_list = machine['display_type']
    if d_list:
        if len(d_list) == 1:
            rotation_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
            screen_str = 'One {0} {1} screen'.format(d_list[0], rotation_str)
        elif len(d_list) == 2:
            if d_list[0] == 'lcd' and d_list[1] == 'raster':
                r_str_1 = mame_get_screen_rotation_str(machine['display_rotate'][0])
                r_str_2 = mame_get_screen_rotation_str(machine['display_rotate'][1])
                screen_str = 'One LCD {0} screen and one raster {1} screen'.format(r_str_1, r_str_2)
            elif d_list[0] == 'raster' and d_list[1] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Two raster {0} screens'.format(r_str)
            elif d_list[0] == 'svg' and d_list[1] == 'svg':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Two SVG {0} screens'.format(r_str)
            elif d_list[0] == 'unknown' and d_list[1] == 'unknown':
                screen_str = 'Two unknown screens'
            else:
                log_error('Machine "{0}" d_list = {1}'.format(machine_name, unicode(d_list)))
                raise TypeError
        elif len(d_list) == 3:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Three raster {1} screens'.format(d_list[0], r_str)
            elif d_list[0] == 'raster' and d_list[1] == 'lcd' and d_list[2] == 'lcd':
                screen_str = 'Three screens special case'
            else:
                log_error('Machine "{0}" d_list = {1}'.format(machine_name, unicode(d_list)))
                raise TypeError
        else:
            raise TypeError
    else:
        screen_str = 'No screen'

    return screen_str

#
# A) Capitalise every list item
# B) Substitute Only_buttons -> Only buttons
#
def mame_improve_control_type_list(control_type_list):
    out_list = []
    for control_str in control_type_list:
        capital_str = control_str.title()
        if capital_str == 'Only_Buttons': capital_str = 'Only Buttons'
        out_list.append(capital_str)

    return out_list

#
# A) Capitalise every list item
#
def mame_improve_device_list(control_type_list):
    out_list = []
    for control_str in control_type_list: out_list.append(control_str.title())

    return out_list

#
# See tools/test_compress_item_list.py for reference
# Input/Output examples:
# 1) ['dial']                 ->  ['dial']
# 2) ['dial', 'dial']         ->  ['2 x dial']
# 3) ['dial', 'dial', 'joy']  ->  ['2 x dial', 'joy']
# 4) ['joy', 'dial', 'dial']  ->  ['joy', '2 x dial']
#
def mame_compress_item_list(item_list):
    reduced_list = []
    num_items = len(item_list)
    if num_items == 0 or num_items == 1: return item_list
    previous_item = item_list[0]
    item_count = 1
    for i in range(1, num_items):
        current_item = item_list[i]
        # print('{0} | item_count {1} | previous_item "{2:>8}" | current_item "{3:>8}"'.format(i, item_count, previous_item, current_item))
        if current_item == previous_item:
            item_count += 1
        else:
            if item_count == 1: reduced_list.append('{0}'.format(previous_item))
            else:               reduced_list.append('{0} {1}'.format(item_count, previous_item))
            item_count = 1
            previous_item = current_item
        # >> Last elemnt of the list
        if i == num_items - 1:
            if current_item == previous_item:
                if item_count == 1: reduced_list.append('{0}'.format(current_item))
                else:               reduced_list.append('{0} {1}'.format(item_count, current_item))
            else:
               reduced_list.append('{0}'.format(current_item))

    return reduced_list

#
# See tools/test_compress_item_list.py for reference
# Output is sorted alphabetically
# Input/Output examples:
# 1) ['dial']                 ->  ['dial']
# 2) ['dial', 'dial']         ->  ['dial']
# 3) ['dial', 'dial', 'joy']  ->  ['dial', 'joy']
# 4) ['joy', 'dial', 'dial']  ->  ['dial', 'joy']
#
def mame_compress_item_list_compact(item_list):
    num_items = len(item_list)
    if num_items == 0 or num_items == 1: return item_list
    item_set = set(item_list)
    reduced_list = list(item_set)
    reduced_list_sorted = sorted(reduced_list)

    return reduced_list_sorted

# -------------------------------------------------------------------------------------------------
# Loading of data files
# -------------------------------------------------------------------------------------------------
def mame_load_Catver_ini(filename):
    log_info('mame_load_Catver_ini() Parsing "{0}"'.format(filename))
    catver_version = 'Not found'
    categories_dic = {}
    categories_set = set()
    __debug_do_list_categories = False
    read_status = 0
    # read_status FSM values
    # 0 -> Looking for '[Category]' tag
    # 1 -> Reading categories
    # 2 -> Categories finished. STOP
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_Catver_ini() (IOError) opening "{0}"'.format(filename))
        return (categories_dic, catver_version)
    for cat_line in f:
        stripped_line = cat_line.strip()
        if __debug_do_list_categories: print('Line "' + stripped_line + '"')
        if read_status == 0:
            # >> Look for Catver version
            m = re.search(r'^;; CatVer ([0-9\.]+) / ', stripped_line)
            if m: catver_version = m.group(1)
            m = re.search(r'^;; CATVER.ini ([0-9\.]+) / ', stripped_line)
            if m: catver_version = m.group(1)
            if stripped_line == '[Category]':
                if __debug_do_list_categories: print('Found [Category]')
                read_status = 1
        elif read_status == 1:
            line_list = stripped_line.split("=")
            if len(line_list) == 1:
                read_status = 2
                continue
            else:
                if __debug_do_list_categories: print(line_list)
                machine_name = line_list[0]
                category = line_list[1]
                if machine_name not in categories_dic:
                    categories_dic[machine_name] = category
                categories_set.add(category)
        elif read_status == 2:
            log_info('mame_load_Catver_ini() Reached end of categories parsing.')
            break
        else:
            raise CriticalError('Unknown read_status FSM value')
    f.close()
    log_info('mame_load_Catver_ini() Version "{0}"'.format(catver_version))
    log_info('mame_load_Catver_ini() Number of machines   {0:6d}'.format(len(categories_dic)))
    log_info('mame_load_Catver_ini() Number of categories {0:6d}'.format(len(categories_set)))

    return (categories_dic, catver_version)

# -------------------------------------------------------------------------------------------------
# Load nplayers.ini. Structure similar to catver.ini
# -------------------------------------------------------------------------------------------------
def mame_load_nplayers_ini(filename):
    log_info('mame_load_nplayers_ini() Parsing "{0}"'.format(filename))
    nplayers_version = 'Not found'
    categories_dic = {}
    categories_set = set()
    __debug_do_list_categories = False
    # --- read_status FSM values ---
    # 0 -> Looking for '[NPlayers]' tag
    # 1 -> Reading categories
    # 2 -> Categories finished. STOP
    read_status = 0
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_nplayers_ini() (IOError) opening "{0}"'.format(filename))
        return (categories_dic, nplayers_version)
    for cat_line in f:
        stripped_line = cat_line.strip()
        if __debug_do_list_categories: print('Line "' + stripped_line + '"')
        if read_status == 0:
            m = re.search(r'NPlayers ([0-9\.]+) / ', stripped_line)
            if m: nplayers_version = m.group(1)
            if stripped_line == '[NPlayers]':
                if __debug_do_list_categories: print('Found [NPlayers]')
                read_status = 1
        elif read_status == 1:
            line_list = stripped_line.split("=")
            if len(line_list) == 1:
                read_status = 2
                continue
            else:
                if __debug_do_list_categories: print(line_list)
                machine_name = line_list[0]
                category = line_list[1]
                if machine_name not in categories_dic:
                    categories_dic[machine_name] = category
                categories_set.add(category)
        elif read_status == 2:
            log_info('mame_load_nplayers_ini() Reached end of nplayers parsing.')
            break
        else:
            raise CriticalError('Unknown read_status FSM value')
    f.close()
    log_info('mame_load_nplayers_ini() Version "{0}"'.format(nplayers_version))
    log_info('mame_load_nplayers_ini() Number of machines   {0:6d}'.format(len(categories_dic)))
    log_info('mame_load_nplayers_ini() Number of categories {0:6d}'.format(len(categories_set)))

    return (categories_dic, nplayers_version)

#
# Generic MAME INI file loader.
# Supports Catlist.ini, Genre.ini, Bestgames.ini and Series.ini
#
def mame_load_INI_datfile(filename):
    log_info('mame_load_INI_datfile() Parsing "{0}"'.format(filename))
    ini_version = 'Not found'
    ini_dic = {}
    ini_set = set()
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_INI_datfile() (IOError) opening "{0}"'.format(filename))
        return (ini_dic, ini_version)
    for file_line in f:
        stripped_line = file_line.strip()
        # >> Skip comments: lines starting with ';;'
        # >> Look for version string in comments
        if re.search(r'^;;', stripped_line):
            m = re.search(r';; (\w+)\.ini ([0-9\.]+) / ', stripped_line)
            if m: ini_version = m.group(2)
            continue
        # >> Skip blanks
        if stripped_line == '': continue
        # >> New category
        searchObj = re.search(r'^\[(.*)\]', stripped_line)
        if searchObj:
            current_category = searchObj.group(1)
            ini_set.add(current_category)
        else:
            machine_name = stripped_line
            ini_dic[machine_name] = current_category
    f.close()
    log_info('mame_load_INI_datfile() Version "{0}"'.format(ini_version))
    log_info('mame_load_INI_datfile() Number of machines   {0:6d}'.format(len(ini_dic)))
    log_info('mame_load_INI_datfile() Number of categories {0:6d}'.format(len(ini_set)))

    return (ini_dic, ini_version)

#
# Loads History.dat
#
# history_idx_dic = {
#    'nes' : {
#        'name': string,
#        'machines' : [['100mandk', 'beautiful_name'], ['89denku', 'beautiful_name'], ...],
#    }
#    'mame' : {
#        'name' : string,
#        'machines': [['88games', 'beautiful_name'], ['flagrall', 'beautiful_name'], ...],
#    }
# }
#
# history_dic = {
#    'nes' : {'100mandk' : string, '89denku' : string, ...},
#    'mame' : {'88games' : string, 'flagrall' : string, ...},
# }
def mame_load_History_DAT(filename):
    log_info('mame_load_History_DAT() Parsing "{0}"'.format(filename))
    history_idx_dic = {}
    history_dic = {}
    __debug_function = False

    # --- read_status FSM values ---
    # 0 -> Looking for '$(xxxx)=(machine_name),'
    # 1 -> Looking for $bio
    # 2 -> Reading information. If '$end' found go to 0.
    read_status = 0

    # >> Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_History_DAT() (IOError) opening "{0}"'.format(filename))
        return (history_idx_dic, history_dic)

    # >> Parse file
    for file_line in f:
        stripped_line = file_line.strip()
        line_uni = stripped_line.decode('utf-8', 'replace')
        if __debug_function: log_debug('Line "{0}"'.format(line_uni))
        if read_status == 0:
            # >> Skip comments: lines starting with '##'
            if re.search(r'^##', line_uni):
                continue
            if line_uni == '': continue
            # >> New machine history
            m = re.search(r'^\$(.+?)=(.+?),', line_uni)
            if m:
                list_name = m.group(1)
                machine_name = m.group(2)
                # >> Transform some special list names
                if   list_name == 'info':          list_name = 'mame'
                elif list_name == 'info,megatech': list_name = 'mame'
                elif list_name == 'info,stv':      list_name = 'mame'
                if __debug_function: log_debug('List "{0}" / Machine "{1}"'.format(list_name, machine_name))
                if list_name in history_idx_dic:
                    history_idx_dic[list_name]['machines'].append([machine_name, machine_name])
                else:
                    history_idx_dic[list_name] = {'name' : list_name, 'machines' : []}
                    history_idx_dic[list_name]['machines'].append([machine_name, machine_name])
            read_status = 1
        elif read_status == 1:
            if __debug_function: log_debug('Second line "{0}"'.format(line_uni))
            if line_uni == '$bio':
                read_status = 2
                info_str_list = []
            else:
                raise TypeError('Wrong second line = "{0}"'.format(line_uni))
        elif read_status == 2:
            if line_uni == '$end':
                if list_name in history_dic:
                    history_dic[list_name][machine_name] = '\n'.join(info_str_list)
                else:
                    history_dic[list_name] = {}
                    history_dic[list_name][machine_name] = '\n'.join(info_str_list)
                read_status = 0
            else:
                info_str_list.append(line_uni)
        else:
            raise TypeError('Wrong read_status = {0}'.format(read_status))
    f.close()
    log_info('mame_load_History_DAT() Number of rows in history_idx_dic {0:6d}'.format(len(history_idx_dic)))
    log_info('mame_load_History_DAT() Number of rows in history_dic     {0:6d}'.format(len(history_dic)))

    return (history_idx_dic, history_dic)

#
# Looks that mameinfo.dat has information for both machines and drivers.
#
# idx_dic  = { 
#     'mame' : [['88games', 'beautiful_name'], ['flagrall', 'beautiful_name'], ...],
#     'drv' : [['88games.cpp', 'beautiful_name'], ['flagrall.cpp', 'beautiful_name'], ...],
# }
# data_dic = {
#    'mame' : {'88games' : string, 'flagrall' : string, ...},
#    'drv' : {'1942.cpp' : string, '1943.cpp' : string, ...},
# }
#
def mame_load_MameInfo_DAT(filename):
    log_info('mame_load_MameInfo_DAT() Parsing "{0}"'.format(filename))
    idx_dic = {}
    data_dic = {}
    __debug_function = False

    # --- read_status FSM values ---
    # 0 -> Looking for '$(xxxx)=(machine_name)'
    # 1 -> Looking for $bio
    # 2 -> Reading information. If '$end' found go to 0.
    # 3 -> Ignoring information. If '$end' found go to 0.
    read_status = 0

    # >> Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_MameInfo_DAT() (IOError) opening "{0}"'.format(filename))
        return (idx_dic, data_dic)

    # >> Parse file
    for file_line in f:
        stripped_line = file_line.strip()
        line_uni = stripped_line.decode('utf-8', 'replace')
        # if __debug_function: log_debug('Line "{0}"'.format(line_uni))
        if read_status == 0:
            # >> Skip comments: lines starting with '#'
            if re.search(r'^#', line_uni):
                continue
            if line_uni == '': continue
            # >> New machine or driver information
            m = re.search(r'^\$info=(.+?)$', line_uni)
            if m:
                machine_name = m.group(1)
                if __debug_function: log_debug('Machine "{1}"'.format(machine_name))
                read_status = 1
        elif read_status == 1:
            if __debug_function: log_debug('Second line "{0}"'.format(line_uni))
            if line_uni == '$mame':
                read_status = 2
                info_str_list = []
                list_name = 'mame'
                if 'mame' in idx_dic:
                    idx_dic['mame'].append([machine_name, machine_name])
                else:
                    idx_dic['mame'] = []
                    idx_dic['mame'].append([machine_name, machine_name])
            elif line_uni == '$drv':
                read_status = 2
                info_str_list = []
                list_name = 'drv'
                if 'drv' in idx_dic:
                    idx_dic['drv'].append([machine_name, machine_name])
                else:
                    idx_dic['drv'] = []
                    idx_dic['drv'].append([machine_name, machine_name])
            else:
                raise TypeError('Wrong second line = "{0}"'.format(line_uni))
        elif read_status == 2:
            if line_uni == '$end':
                if list_name in data_dic:
                    data_dic[list_name][machine_name] = '\n'.join(info_str_list)
                else:
                    data_dic[list_name] = {}
                    data_dic[list_name][machine_name] = '\n'.join(info_str_list)
                read_status = 0
            else:
                info_str_list.append(line_uni)
        else:
            raise TypeError('Wrong read_status = {0}'.format(read_status))
    f.close()
    log_info('mame_load_MameInfo_DAT() Number of rows in idx_dic  {0:6d}'.format(len(idx_dic)))
    log_info('mame_load_MameInfo_DAT() Number of rows in data_dic {0:6d}'.format(len(data_dic)))

    return (idx_dic, data_dic)

#
# NOTE set objects are not JSON-serializable. Use lists and transform lists to sets if
#      necessary after loading the JSON file.
#
# idx_list  = [['88games', 'beautiful_name'], ['flagrall', 'beautiful_name'], ...],
# data_dic = { '88games' : 'string', 'flagrall' : 'string', ... }
#
def mame_load_GameInit_DAT(filename):
    log_info('mame_load_GameInit_DAT() Parsing "{0}"'.format(filename))
    idx_list = []
    data_dic = {}
    __debug_function = False

    # --- read_status FSM values ---
    # 0 -> Looking for '$info=(machine_name)'
    # 1 -> Looking for $mame
    # 2 -> Reading information. If '$end' found go to 0.
    # 3 -> Ignoring information. If '$end' found go to 0.
    read_status = 0

    # >> Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_GameInit_DAT() (IOError) opening "{0}"'.format(filename))
        return (idx_list, data_dic)

    # >> Parse file
    for file_line in f:
        stripped_line = file_line.strip()
        line_uni = stripped_line.decode('utf-8', 'replace')
        # if __debug_function: log_debug('Line "{0}"'.format(line_uni))
        if read_status == 0:
            # >> Skip comments: lines starting with '#'
            if re.search(r'^#', line_uni):
                continue
            if line_uni == '': continue
            # >> New machine or driver information
            m = re.search(r'^\$info=(.+?)$', line_uni)
            if m:
                machine_name = m.group(1)
                if __debug_function: log_debug('Machine "{0}"'.format(machine_name))
                idx_list.append([machine_name, machine_name])
                read_status = 1
        elif read_status == 1:
            if __debug_function: log_debug('Second line "{0}"'.format(line_uni))
            if line_uni == '$mame':
                read_status = 2
                info_str_list = []
            else:
                raise TypeError('Wrong second line = "{0}"'.format(line_uni))
        elif read_status == 2:
            if line_uni == '$end':
                data_dic[machine_name] = '\n'.join(info_str_list)
                info_str_list = []
                read_status = 0
            else:
                info_str_list.append(line_uni)
        else:
            raise TypeError('Wrong read_status = {0}'.format(read_status))
    f.close()
    log_info('mame_load_GameInit_DAT() Number of rows in idx_list {0:6d}'.format(len(idx_list)))
    log_info('mame_load_GameInit_DAT() Number of rows in data_dic {0:6d}'.format(len(data_dic)))

    return (idx_list, data_dic)

#
# NOTE set objects are not JSON-serializable. Use lists and transform lists to sets if
#      necessary after loading the JSON file.
#
# idx_list = [['88games', 'beautiful_name'], ['flagrall', 'beautiful_name'], ...],
# data_dic = { '88games' : 'string', 'flagrall' : 'string', ... }
#
def mame_load_Command_DAT(filename):
    log_info('mame_load_Command_DAT() Parsing "{0}"'.format(filename))
    idx_list = []
    data_dic = {}
    proper_idx_list = []
    proper_data_dic = {}
    __debug_function = False

    # --- read_status FSM values ---
    # 0 -> Looking for '$info=(machine_name)'
    # 1 -> Looking for $cmd
    # 2 -> Reading information. If '$end' found go to 0.
    read_status = 0

    # >> Open file
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('mame_load_Command_DAT() (IOError) opening "{0}"'.format(filename))
        return (proper_idx_list, proper_data_dic)

    # >> Parse file
    for file_line in f:
        stripped_line = file_line.strip()
        line_uni = stripped_line.decode('utf-8', 'replace')
        # if __debug_function: log_debug('Line "{0}"'.format(line_uni))
        if read_status == 0:
            # >> Skip comments: lines starting with '#'
            if re.search(r'^#', line_uni):
                continue
            if line_uni == '': continue
            # >> New machine or driver information
            m = re.search(r'^\$info=(.+?)$', line_uni)
            if m:
                machine_name = m.group(1)
                if __debug_function: log_debug('Machine "{0}"'.format(machine_name))
                idx_list.append(machine_name)
                read_status = 1
        elif read_status == 1:
            if __debug_function: log_debug('Second line "{0}"'.format(line_uni))
            if line_uni == '$cmd':
                read_status = 2
                info_str_list = []
            else:
                raise TypeError('Wrong second line = "{0}"'.format(line_uni))
        elif read_status == 2:
            if line_uni == '$end':
                data_dic[machine_name] = '\n'.join(info_str_list)
                info_str_list = []
                read_status = 0
            else:
                info_str_list.append(line_uni)
        else:
            raise TypeError('Wrong read_status = {0}'.format(read_status))
    f.close()
    log_info('mame_load_Command_DAT() Number of rows in idx_list {0:6d}'.format(len(idx_list)))
    log_info('mame_load_Command_DAT() Number of rows in data_dic {0:6d}'.format(len(data_dic)))

    # >> Expand database. Many machines share the same entry. Expand the database.
    for original_name in idx_list:
        original_name_list = original_name.split(',')
        for expanded_name in original_name_list:
            # Skip empty strings
            if not expanded_name: continue
            expanded_name = expanded_name.strip()
            proper_idx_list.append([expanded_name, expanded_name])
            proper_data_dic[expanded_name] = data_dic[original_name]
    log_info('mame_load_Command_DAT() Number of entries on proper_idx_list {0:6d}'.format(len(proper_idx_list)))
    log_info('mame_load_Command_DAT() Number of entries on proper_data_dic {0:6d}'.format(len(proper_data_dic)))

    return (proper_idx_list, proper_data_dic)

# -------------------------------------------------------------------------------------------------
# MAME ROM/CHD audit code
# -------------------------------------------------------------------------------------------------
# This code is very un-optimised! But it is better to get something that works
# and then optimise. "Premature optimization is the root of all evil" -- Donald Knuth
# Add new field 'status' : 'OK', 'OK (invalid ROM)', 'ZIP not found', 'Bad ZIP file', 
#                          'ROM not in ZIP', 'ROM bad size', 'ROM bad CRC'.
# Also adds fields 'status_colour'.
#
# rom_list = [
#     {'name' : 'avph.03d', 'crc' : '01234567', 'location' : 'avsp/avph.03d'}, ...
# ]
#
def mame_audit_machine_roms(settings, rom_list):
    for m_rom in rom_list:
        zip_name = m_rom['location'].split('/')[0]
        rom_name = m_rom['location'].split('/')[1]
        # log_debug('Testing ROM {0}'.format(m_rom['name']))
        # log_debug('location {0}'.format(m_rom['location']))
        # log_debug('zip_name {0}'.format(zip_name))
        # log_debug('rom_name {0}'.format(rom_name))

        # >> Invalid ROMs are not in the ZIP file
        if not m_rom['crc']:
            m_rom['status'] = 'OK (invalid ROM)'
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Test if ZIP file exists
        zip_FN = FileName(settings['rom_path']).pjoin(zip_name + '.zip')
        # log_debug('ZIP {0}'.format(zip_FN.getPath()))
        if not zip_FN.exists():
            m_rom['status'] = 'ZIP not found'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Open ZIP file and get list of files
        try:
            zip_f = z.ZipFile(zip_FN.getPath(), 'r')
        except z.BadZipfile as e:
            m_rom['status'] = 'Bad ZIP file'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue
        z_file_list = zip_f.namelist()
        # log_debug('ZIP {0} files {1}'.format(m_rom['location'], z_file_list))
        if not rom_name in z_file_list:
            zip_f.close()
            m_rom['status'] = 'ROM not in ZIP'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Get ZIP file object and test size and CRC
        # >> NOTE CRC32 in Python is a decimal number: CRC32 4225815809
        # >> However, MAME encodes it as an hexadecimal number: CRC32 0123abcd
        z_info = zip_f.getinfo(rom_name)
        z_info_file_size = z_info.file_size
        z_info_crc_hex_str = '{0:08x}'.format(z_info.CRC)
        zip_f.close()
        # log_debug('ZIP CRC32 {0} | CRC hex {1} | size {2}'.format(z_info.CRC, z_crc_hex, z_info.file_size))
        # log_debug('ROM CRC hex {0} | size {1}'.format(m_rom['crc'], 0))
        if z_info_crc_hex_str != m_rom['crc']:
            m_rom['status'] = 'ROM bad CRC'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue
        if z_info_file_size != m_rom['size']:
            m_rom['status'] = 'ROM bad size'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> ROM is OK
        m_rom['status'] = 'OK'
        m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])

# Add new field 'status' : 'OK', 'OK (invalid CHD)', 'CHD not found', 'CHD bad SHA1'
# Also adds fields 'status_colour'.
#
# chd_list = [
#     {'name' : 'avph.03d', 'sha1' : '012...', 'location' : 'avsp/avph.03d'}, ...
# ]
#
# I'm not sure if the CHD sha1 value in MAME XML is the sha1 of the uncompressed data OR
# the sha1 of the CHD file. If the formaer, then AEL can open the CHD file, get the sha1 from the
# header and verify it. See
# http://www.mameworld.info/ubbthreads/showflat.php?Cat=&Number=342940&page=0&view=expanded&sb=5&o=&vc=1
#
def mame_audit_machine_chds(settings, chd_list):
    for m_chd in chd_list:
        if not m_chd['sha1']:
            m_chd['status'] = 'OK (invalid CHD)'
            m_chd['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_chd['status'])
            continue
        chd_name = m_chd['name']
        chd_FN = FileName(settings['chd_path']).pjoin(chd_name + '.chd')
        if not chd_FN.exists():
            m_chd['status'] = 'CHD not found'
            m_chd['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_chd['status'])
            continue
        m_chd['status'] = 'OK'
        m_chd['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_chd['status'])

# -------------------------------------------------------------------------------------------------
# SL ROM/CHD audit code
# -------------------------------------------------------------------------------------------------
def mame_SL_audit_machine_roms(settings, rom_list):
    for m_rom in rom_list:
        log_debug('Testing ROM {0}'.format(m_rom['name']))
        log_debug('location {0}'.format(m_rom['location']))
        SL_name  = m_rom['location'].split('/')[0]
        zip_name = m_rom['location'].split('/')[1] + '.zip'
        rom_name = m_rom['location'].split('/')[2]
        log_debug('SL_name  "{0}"'.format(SL_name))
        log_debug('zip_name "{0}"'.format(zip_name))
        log_debug('rom_name "{0}"'.format(rom_name))

        # >> Invalid ROMs are not in the ZIP file
        if not m_rom['crc']:
            m_rom['status'] = 'OK (invalid ROM)'
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Test if ZIP file exists
        zip_FN = FileName(settings['SL_rom_path']).pjoin(SL_name).pjoin(zip_name)
        log_debug('zip_FN P {0}'.format(zip_FN.getPath()))
        if not zip_FN.exists():
            m_rom['status'] = 'ZIP not found'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Open ZIP file and get list of files
        try:
            zip_f = z.ZipFile(zip_FN.getPath(), 'r')
        except z.BadZipfile as e:
            m_rom['status'] = 'Bad ZIP file'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue
        z_file_list = zip_f.namelist()
        # log_debug('ZIP {0} files {1}'.format(m_rom['location'], z_file_list))
        if not rom_name in z_file_list:
            zip_f.close()
            m_rom['status'] = 'ROM not in ZIP'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> Get ZIP file object and test size and CRC
        # >> NOTE CRC32 in Python is a decimal number: CRC32 4225815809
        # >> However, MAME encodes it as an hexadecimal number: CRC32 0123abcd
        z_info = zip_f.getinfo(rom_name)
        z_info_file_size = z_info.file_size
        z_info_crc_hex_str = '{0:08x}'.format(z_info.CRC)
        zip_f.close()
        # log_debug('ZIP CRC32 {0} | CRC hex {1} | size {2}'.format(z_info.CRC, z_crc_hex, z_info.file_size))
        # log_debug('ROM CRC hex {0} | size {1}'.format(m_rom['crc'], 0))
        if z_info_crc_hex_str != m_rom['crc']:
            m_rom['status'] = 'ROM bad CRC'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue
        if z_info_file_size != m_rom['size']:
            m_rom['status'] = 'ROM bad size'
            m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
            continue

        # >> ROM is OK
        m_rom['status'] = 'OK'
        m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])

def mame_SL_audit_machine_chds(settings, chd_list):
    for m_chd in chd_list:
        log_debug('Testing CHD {0}'.format(m_chd['name']))
        log_debug('location {0}'.format(m_chd['location']))
        SL_name   = m_chd['location'].split('/')[0]
        rom_name  = m_chd['location'].split('/')[1]
        disk_name = m_chd['location'].split('/')[2]
        log_debug('SL_name   "{0}"'.format(SL_name))
        log_debug('rom_name  "{0}"'.format(rom_name))
        log_debug('disk_name "{0}"'.format(disk_name))

        # >> Invalid CHDs
        if not m_chd['sha1']:
            m_chd['status'] = 'OK (invalid CHD)'
            m_chd['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_chd['status'])
            continue

        # >> Test if DISK file exists
        chd_FN = FileName(settings['SL_chd_path']).pjoin(SL_name).pjoin(rom_name).pjoin(disk_name)
        log_debug('chd_FN P {0}'.format(chd_FN.getPath()))
        if not chd_FN.exists():
            m_chd['status'] = 'CHD not found'
            m_chd['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_chd['status'])
            continue

        # >> DISK is OK
        m_chd['status'] = 'OK'
        m_chd['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_chd['status'])
