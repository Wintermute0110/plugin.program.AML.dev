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
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except:
    PILLOW_AVAILABLE = False

# --- AEL packages ---
from constants import *
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
    'cps1.cpp' : 'Capcom Play System 1',
    'cps2.cpp' : 'Capcom Play System 2',
    'cps3.cpp' : 'Capcom Play System 3',

    # --- Konami ---
    'konamigx.cpp' : 'Konami System GX',
    'konamim2.cpp' : 'Konami M2 Hardware',

    # --- Namco ---
    'galaxian.cpp' : 'Namco Galaxian-derived hardware',
    'namcops2.cpp' : 'Namco System 246 / System 256 (Sony PS2 based)',

    # --- SNK ---
    'neodriv.hxx' : 'SNK NeoGeo AES',
    'neogeo.cpp'  : 'SNK NeoGeo MVS',

    # --- Misc important drivers (important enough to have a fancy name!) ---
    'seta.cpp' : 'Seta Hardware',

    # --- SEGA ---
    'zaxxon.cpp'    : 'SEGA Zaxxon hardware',
    'system1.cpp'   : 'SEGA System1 / System 2',
    'segac2.cpp'    : 'SEGA System C (System 14)',
    'segae.cpp'     : 'SEGA System E',
    'segas16a.cpp'  : 'SEGA System 16A',
    'segas16b.cpp'  : 'SEGA System 16B',
    'segas24.cpp'   : 'SEGA System 24',
    'segas18.cpp'   : 'SEGA System 18',
    'kyugo.cpp'     : 'SEGA Kyugo Hardware',
    'segahang.cpp'  : 'Sega Hang On hardware', # AKA Sega Space Harrier
    'segaorun.cpp'  : 'SEGA Out Run hardware',
    'segaxbd.cpp'   : 'SEGA X-board',
    'segaybd.cpp'   : 'SEGA Y-board',
    'segas32.cpp'   : 'SEGA System 32',
    'model1.cpp'    : 'SEGA Model 1',
    'model2.cpp'    : 'SEGA Model 2',
    'model3.cpp'    : 'SEGA Model 3',
    'stv.cpp'       : 'SEGA ST-V hardware',
    'naomi.cpp'     : 'SEGA Naomi / Naomi 2 / Atomiswave',
    'segasp.cpp'    : 'SEGA System SP (Spider)', # Naomi derived
    'chihiro.cpp'   : 'SEGA Chihiro (Xbox-based)',
    'triforce.cpp'  : 'SEGA Triforce Hardware',
    'lindbergh.cpp' : 'SEGA Lindbergh',

    # --- Taito ---
    'taito_b.cpp'  : 'Taito B System',
    'taito_l.cpp'  : 'Taito L System',
    'taito_f2.cpp' : 'Taito F2 System',
    'taito_f3.cpp' : 'Taito F3 System',

    # --- SONY ---
    'zn.cpp' : 'Sony ZN1/ZN2 (Arcade PSX)',
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
                screen_str = 'Three raster {0} screens'.format(r_str)
            elif d_list[0] == 'raster' and d_list[1] == 'lcd' and d_list[2] == 'lcd':
                screen_str = 'Three screens special case'
            else:
                log_error('Machine "{0}" d_list = {1}'.format(machine_name, unicode(d_list)))
                raise TypeError
        elif len(d_list) == 4:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster' and d_list[3] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Four raster {0} screens'.format(r_str)
            else:
                log_error('Machine "{0}" d_list = {1}'.format(machine_name, unicode(d_list)))
                raise TypeError
        else:
            log_error('mame_get_screen_str() d_list = {0}'.format(unicode(d_list)))
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
def mame_audit_machine(settings, rom_list):
    for m_rom in rom_list:
        if m_rom['type'] == ROM_TYPE_DISK:
            machine_name = m_rom['location'].split('/')[0]
            disk_name    = m_rom['location'].split('/')[1]
            # log_debug('Testing CHD {0}'.format(m_rom['name']))
            # log_debug('location {0}'.format(m_rom['location']))
            # log_debug('machine_name "{0}"'.format(machine_name))
            # log_debug('disk_name    "{0}"'.format(disk_name))

            # >> Invalid CHDs
            if not m_rom['sha1']:
                m_rom['status'] = AUDIT_STATUS_OK_INVALID_CHD
                m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Test if DISK file exists
            chd_FN = FileName(settings['chd_path']).pjoin(machine_name).pjoin(disk_name)
            # log_debug('chd_FN P {0}'.format(chd_FN.getPath()))
            if not chd_FN.exists():
                m_rom['status'] = AUDIT_STATUS_CHD_NO_FOUND
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> DISK is OK
            m_rom['status'] = AUDIT_STATUS_OK
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
        else:
            zip_name = m_rom['location'].split('/')[0]
            rom_name = m_rom['location'].split('/')[1]
            # log_debug('Testing ROM {0}'.format(m_rom['name']))
            # log_debug('location {0}'.format(m_rom['location']))
            # log_debug('zip_name {0}'.format(zip_name))
            # log_debug('rom_name {0}'.format(rom_name))

            # >> Invalid ROMs are not in the ZIP file
            if not m_rom['crc']:
                m_rom['status'] = AUDIT_STATUS_OK_INVALID_ROM
                m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Test if ZIP file exists
            zip_FN = FileName(settings['rom_path']).pjoin(zip_name + '.zip')
            # log_debug('ZIP {0}'.format(zip_FN.getPath()))
            if not zip_FN.exists():
                m_rom['status'] = AUDIT_STATUS_ZIP_NO_FOUND
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Open ZIP file and get list of files
            try:
                zip_f = z.ZipFile(zip_FN.getPath(), 'r')
            except z.BadZipfile as e:
                m_rom['status'] = AUDIT_STATUS_BAD_ZIP_FILE
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue
            z_file_list = zip_f.namelist()
            # log_debug('ZIP {0} files {1}'.format(m_rom['location'], z_file_list))
            if not rom_name in z_file_list:
                zip_f.close()
                m_rom['status'] = AUDIT_STATUS_ROM_NOT_IN_ZIP
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
                m_rom['status'] = AUDIT_STATUS_ROM_BAD_CRC
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue
            if z_info_file_size != m_rom['size']:
                m_rom['status'] = AUDIT_STATUS_ROM_BAD_SIZE
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> ROM is OK
            m_rom['status'] = AUDIT_STATUS_OK
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])

# -------------------------------------------------------------------------------------------------
# SL ROM/CHD audit code
# -------------------------------------------------------------------------------------------------
def mame_SL_audit_machine(settings, rom_list):
    for m_rom in rom_list:
        if m_rom['type'] == ROM_TYPE_DISK:
            SL_name   = m_rom['location'].split('/')[0]
            rom_name  = m_rom['location'].split('/')[1]
            disk_name = m_rom['location'].split('/')[2]
            # log_debug('Testing CHD {0}'.format(m_rom['name']))
            # log_debug('location {0}'.format(m_rom['location']))
            # log_debug('SL_name   "{0}"'.format(SL_name))
            # log_debug('rom_name  "{0}"'.format(rom_name))
            # log_debug('disk_name "{0}"'.format(disk_name))

            # >> Invalid CHDs
            if not m_rom['sha1']:
                m_rom['status'] = AUDIT_STATUS_OK_INVALID_CHD
                m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Test if DISK file exists
            chd_FN = FileName(settings['SL_chd_path']).pjoin(SL_name).pjoin(rom_name).pjoin(disk_name)
            # log_debug('chd_FN P {0}'.format(chd_FN.getPath()))
            if not chd_FN.exists():
                m_rom['status'] = AUDIT_STATUS_CHD_NO_FOUND
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> DISK is OK
            m_rom['status'] = AUDIT_STATUS_OK
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
        else:
            SL_name  = m_rom['location'].split('/')[0]
            zip_name = m_rom['location'].split('/')[1] + '.zip'
            rom_name = m_rom['location'].split('/')[2]
            # log_debug('Testing ROM {0}'.format(m_rom['name']))
            # log_debug('location {0}'.format(m_rom['location']))
            # log_debug('SL_name  "{0}"'.format(SL_name))
            # log_debug('zip_name "{0}"'.format(zip_name))
            # log_debug('rom_name "{0}"'.format(rom_name))

            # >> Invalid ROMs are not in the ZIP file
            if not m_rom['crc']:
                m_rom['status'] = AUDIT_STATUS_OK_INVALID_ROM
                m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Test if ZIP file exists
            zip_FN = FileName(settings['SL_rom_path']).pjoin(SL_name).pjoin(zip_name)
            # log_debug('zip_FN P {0}'.format(zip_FN.getPath()))
            if not zip_FN.exists():
                m_rom['status'] = AUDIT_STATUS_ZIP_NO_FOUND
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> Open ZIP file and get list of files
            try:
                zip_f = z.ZipFile(zip_FN.getPath(), 'r')
            except z.BadZipfile as e:
                m_rom['status'] = AUDIT_STATUS_BAD_ZIP_FILE
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue
            z_file_list = zip_f.namelist()
            # log_debug('ZIP {0} files {1}'.format(m_rom['location'], z_file_list))
            if not rom_name in z_file_list:
                zip_f.close()
                m_rom['status'] = AUDIT_STATUS_ROM_NOT_IN_ZIP
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
                m_rom['status'] = AUDIT_STATUS_ROM_BAD_CRC
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue
            if z_info_file_size != m_rom['size']:
                m_rom['status'] = AUDIT_STATUS_ROM_BAD_SIZE
                m_rom['status_colour'] = '[COLOR red]{0}[/COLOR]'.format(m_rom['status'])
                continue

            # >> ROM is OK
            m_rom['status'] = AUDIT_STATUS_OK
            m_rom['status_colour'] = '[COLOR green]{0}[/COLOR]'.format(m_rom['status'])

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

# -------------------------------------------------------------------------------------------------
# Fanart generation
# -------------------------------------------------------------------------------------------------
#
# Scales and centers img into a box of size (box_x_size, box_y_size).
# Scaling keeps original img aspect ratio.
# Returns an image of size (box_x_size, box_y_size)
#
def PIL_resize_proportional(img, layout, dic_key):
    # CANVAS_COLOR = (25, 255, 25)
    CANVAS_COLOR = (0, 0, 0)
    box_x_size = layout[dic_key]['x_size']
    box_y_size = layout[dic_key]['y_size']
    # print('PIL_resize_proportional() Initialising ...')
    # print('img X_size = {0} | Y_size = {1}'.format(img.size[0], img.size[1]))
    # print('box X_size = {0} | Y_size = {1}'.format(box_x_size, box_y_size))

    # --- First try to fit X dimension ---
    # print('PIL_resize_proportional() Fitting X dimension')
    wpercent = (box_x_size / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    r_x_size = box_x_size
    r_y_size = hsize
    x_offset = 0
    y_offset = (box_y_size - r_y_size) / 2
    # print('resize X_size = {0} | Y_size = {1}'.format(r_x_size, r_y_size))
    # print('resize x_offset = {0} | y_offset = {1}'.format(x_offset, y_offset))

    # --- Second try to fit Y dimension ---
    if y_offset < 0:
        # print('Fitting Y dimension')
        hpercent = (box_y_size / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        r_x_size = wsize
        r_y_size = box_y_size
        x_offset = (box_x_size - r_x_size) / 2
        y_offset = 0
        # print('resize X_size = {0} | Y_size = {1}'.format(r_x_size, r_y_size))
        # print('resize x_offset = {0} | y_offset = {1}'.format(x_offset, y_offset))

    # >> Create a new image and paste original image centered.
    canvas_img = Image.new('RGB', (box_x_size, box_y_size), CANVAS_COLOR)
    # >> Resize and paste
    img = img.resize((r_x_size, r_y_size), Image.ANTIALIAS)
    canvas_img.paste(img, (x_offset, y_offset, x_offset + r_x_size, y_offset + r_y_size))

    return canvas_img

def PIL_paste_image(img, img_title, layout, dic_key):
    box = (
        layout[dic_key]['x_pos'],
        layout[dic_key]['y_pos'], 
        layout[dic_key]['x_pos'] + layout[dic_key]['x_size'],
        layout[dic_key]['y_pos'] + layout[dic_key]['y_size']
    )
    img.paste(img_title, box)

    return img

# --- Fanart layout ---
layout = {
    'title'      : {'x_size' : 450, 'y_size' : 450, 'x_pos' : 50,   'y_pos' : 50},
    'snap'       : {'x_size' : 450, 'y_size' : 450, 'x_pos' : 50,   'y_pos' : 550},
    'flyer'      : {'x_size' : 450, 'y_size' : 450, 'x_pos' : 1420, 'y_pos' : 50},
    'cabinet'    : {'x_size' : 300, 'y_size' : 425, 'x_pos' : 1050, 'y_pos' : 625},
    'artpreview' : {'x_size' : 450, 'y_size' : 550, 'x_pos' : 550,  'y_pos' : 500},
    'PCB'        : {'x_size' : 300, 'y_size' : 300, 'x_pos' : 1500, 'y_pos' : 525},
    'clearlogo'  : {'x_size' : 450, 'y_size' : 200, 'x_pos' : 1400, 'y_pos' : 850},
    'cpanel'     : {'x_size' : 300, 'y_size' : 100, 'x_pos' : 1050, 'y_pos' : 500},
    'marquee'    : {'x_size' : 800, 'y_size' : 275, 'x_pos' : 550,  'y_pos' : 200},
    'text'       : {                                'x_pos' : 550,  'y_pos' : 50, 'size' : 72},
}

# >> Cache font object in global variable
font_mono = None
font_mono_SL = None
font_mono_item = None

#
# Rebuild Fanart for a given MAME machine
#
def mame_build_fanart(PATHS, m_name, assets_dic, Fanart_path_FN):
    # log_debug('mame_build_fanart() Building fanart for machine {0}'.format(m_name))

    # >> Quickly check if machine has valid assets, and skip fanart generation if not.
    machine_has_valid_assets = False
    for asset_key in layout:
        m_assets = assets_dic[m_name]
        if asset_key != 'text' and m_assets[asset_key]:
            machine_has_valid_assets = True
            break
    if not machine_has_valid_assets: return

    # >> If font object does not exists open font an cache it.
    if not font_mono:
        global font_mono
        log_debug('mame_build_fanart() Creating font_mono object')
        log_debug('mame_build_fanart() Loading "{0}"'.format(PATHS.MONO_FONT_PATH.getPath()))
        font_mono = ImageFont.truetype(PATHS.MONO_FONT_PATH.getPath(), layout['text']['size'])

    # >> Create fanart canvas
    fanart_img = Image.new('RGB', (1920, 1080), (0, 0, 0))
    draw = ImageDraw.Draw(fanart_img)

    # >> Draw assets according to layout
    for asset_key in layout:
        # log_debug('{0:<10} initialising'.format(asset_key))
        m_assets = assets_dic[m_name]
        if asset_key == 'text':
            draw.text((layout['text']['x_pos'], layout['text']['y_pos']), m_name,
                      (255, 255, 255), font = font_mono)
        else:
            if not m_assets[asset_key]:
                # log_debug('{0:<10} DB empty'.format(asset_key))
                continue
            Asset_FN = FileName(m_assets[asset_key])
            if not Asset_FN.exists():
                # log_debug('{0:<10} file not found'.format(asset_key))
                continue
            # log_debug('{0:<10} found'.format(asset_key))
            img_asset = Image.open(Asset_FN.getPath())
            img_asset = PIL_resize_proportional(img_asset, layout, asset_key)
            fanart_img = PIL_paste_image(fanart_img, img_asset, layout, asset_key)

    # >> Save fanart and update database
    Fanart_FN = Fanart_path_FN.pjoin('{0}.png'.format(m_name))
    # log_debug('mame_build_fanart() Saving Fanart "{0}"'.format(Fanart_FN.getPath()))
    fanart_img.save(Fanart_FN.getPath())
    assets_dic[m_name]['fanart'] = Fanart_FN.getPath()

layout_SL = {
    'title'     : {'x_size' : 600, 'y_size' : 600, 'x_pos' : 690,  'y_pos' : 430},
    'snap'      : {'x_size' : 600, 'y_size' : 600, 'x_pos' : 1300, 'y_pos' : 430},
    'boxfront'  : {'x_size' : 650, 'y_size' : 980, 'x_pos' : 30,   'y_pos' : 50},
    'text_SL'   : {                                'x_pos' : 730,  'y_pos' : 90, 'size' : 76},
    'text_item' : {                                'x_pos' : 730,  'y_pos' : 180, 'size' : 76},
}

#
# Rebuild Fanart for a given SL item
#
def mame_build_SL_fanart(PATHS, SL_name, m_name, assets_dic, Fanart_path_FN):
    # log_debug('mame_build_SL_fanart() Building fanart for SL {0} item {1}'.format(SL_name, m_name))

    # >> Quickly check if machine has valid assets, and skip fanart generation if not.
    machine_has_valid_assets = False
    for asset_key in layout_SL:
        if asset_key == 'text_SL' or asset_key == 'text_item': continue
        m_assets = assets_dic[m_name]
        if m_assets[asset_key]:
            machine_has_valid_assets = True
            break
    if not machine_has_valid_assets: return

    # >> If font object does not exists open font an cache it.
    if not font_mono_SL:
        global font_mono_SL
        log_debug('mame_build_SL_fanart() Creating font_mono_SL object')
        log_debug('mame_build_SL_fanart() Loading "{0}"'.format(PATHS.MONO_FONT_PATH.getPath()))
        font_mono_SL = ImageFont.truetype(PATHS.MONO_FONT_PATH.getPath(), layout_SL['text_SL']['size'])
    if not font_mono_item:
        global font_mono_item
        log_debug('mame_build_SL_fanart() Creating font_mono_item object')
        log_debug('mame_build_SL_fanart() Loading "{0}"'.format(PATHS.MONO_FONT_PATH.getPath()))
        font_mono_item = ImageFont.truetype(PATHS.MONO_FONT_PATH.getPath(), layout_SL['text_item']['size'])

    # >> Create fanart canvas
    fanart_img = Image.new('RGB', (1920, 1080), (0, 0, 0))
    draw = ImageDraw.Draw(fanart_img)

    # >> Draw assets according to layout_SL
    for asset_key in layout_SL:
        # log_debug('{0:<10} initialising'.format(asset_key))
        m_assets = assets_dic[m_name]
        if asset_key == 'text_SL':
            draw.text((layout_SL['text_SL']['x_pos'], layout_SL['text_SL']['y_pos']), SL_name,
                      (255, 255, 255), font = font_mono_SL)
        elif asset_key == 'text_item':
            draw.text((layout_SL['text_item']['x_pos'], layout_SL['text_item']['y_pos']), m_name,
                      (255, 255, 255), font = font_mono_item)
        else:
            if not m_assets[asset_key]:
                # log_debug('{0:<10} DB empty'.format(asset_key))
                continue
            Asset_FN = FileName(m_assets[asset_key])
            if not Asset_FN.exists():
                # log_debug('{0:<10} file not found'.format(asset_key))
                continue
            # log_debug('{0:<10} found'.format(asset_key))
            img_asset = Image.open(Asset_FN.getPath())
            img_asset = PIL_resize_proportional(img_asset, layout_SL, asset_key)
            fanart_img = PIL_paste_image(fanart_img, img_asset, layout_SL, asset_key)

    # >> Save fanart and update database
    Fanart_FN = Fanart_path_FN.pjoin('{0}.png'.format(m_name))
    # log_debug('mame_build_SL_fanart() Saving Fanart "{0}"'.format(Fanart_FN.getPath()))
    fanart_img.save(Fanart_FN.getPath())
    assets_dic[m_name]['fanart'] = Fanart_FN.getPath()
