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

    'zn.cpp'       : 'Sony ZN1/ZN2 (Arcade PSX)',
}

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

def mame_get_screen_str(machine):
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
                screen_str = 'Two raster {1} screens'.format(d_list[0], r_str)
            else:
                raise TypeError
        elif len(d_list) == 3:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Three raster {1} screens'.format(d_list[0], r_str)
            elif d_list[0] == 'raster' and d_list[1] == 'lcd' and d_list[2] == 'lcd':
                screen_str = 'Three screens special case'
            else:
                log_error('d_list = {0}'.format(unicode(d_list)))
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

# -------------------------------------------------------------------------------------------------
# Loading of data files
# -------------------------------------------------------------------------------------------------
def fs_load_Catver_ini(filename):
    log_info('fs_load_Catver_ini() Parsing "{0}"'.format(filename))
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
        log_info('fs_load_Catver_ini() (IOError) opening "{0}"'.format(filename))
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
            log_info('fs_load_Catver_ini() Reached end of categories parsing.')
            break
        else:
            raise CriticalError('Unknown read_status FSM value')
    f.close()
    log_info('fs_load_Catver_ini() Version "{0}"'.format(catver_version))
    log_info('fs_load_Catver_ini() Number of machines   {0:6d}'.format(len(categories_dic)))
    log_info('fs_load_Catver_ini() Number of categories {0:6d}'.format(len(categories_set)))

    return (categories_dic, catver_version)

# -------------------------------------------------------------------------------------------------
# Load nplayers.ini. Structure similar to catver.ini
# -------------------------------------------------------------------------------------------------
def fs_load_nplayers_ini(filename):
    log_info('fs_load_nplayers_ini() Parsing "{0}"'.format(filename))
    nplayers_version = 'Not found'
    categories_dic = {}
    categories_set = set()
    __debug_do_list_categories = False
    read_status = 0
    # read_status FSM values
    # 0 -> Looking for '[NPlayers]' tag
    # 1 -> Reading categories
    # 2 -> Categories finished. STOP
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('fs_load_nplayers_ini() (IOError) opening "{0}"'.format(filename))
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
            log_info('fs_load_nplayers_ini() Reached end of nplayers parsing.')
            break
        else:
            raise CriticalError('Unknown read_status FSM value')
    f.close()
    log_info('fs_load_nplayers_ini() Version "{0}"'.format(nplayers_version))
    log_info('fs_load_nplayers_ini() Number of machines   {0:6d}'.format(len(categories_dic)))
    log_info('fs_load_nplayers_ini() Number of categories {0:6d}'.format(len(categories_set)))

    return (categories_dic, nplayers_version)

#
# Generic MAME INI file loader.
# Supports Catlist.ini, Genre.ini, Bestgames.ini and Series.ini
#
def fs_load_INI_datfile(filename):
    log_info('fs_load_INI_datfile() Parsing "{0}"'.format(filename))
    ini_version = 'Not found'
    ini_dic = {}
    ini_set = set()
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('fs_load_INI_datfile() (IOError) opening "{0}"'.format(filename))
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
    log_info('fs_load_INI_datfile() Version "{0}"'.format(ini_version))
    log_info('fs_load_INI_datfile() Number of machines   {0:6d}'.format(len(ini_dic)))
    log_info('fs_load_INI_datfile() Number of categories {0:6d}'.format(len(ini_set)))

    return (ini_dic, ini_version)
