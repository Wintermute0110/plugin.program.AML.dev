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
