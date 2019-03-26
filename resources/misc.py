# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher miscellaneous functions.
# Functions in this module only depend on the Python standard library.
# This module can be loaded anywhere without creating circular dependencies.
# These functions do not event use log_*().
#

# Copyright (c) 2016-2019 Wintermute0110 <wintermute0110@gmail.com>
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

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------
def misc_get_mame_control_str(control_type_list):
    control_set = set()
    improved_c_type_list = mame_improve_control_type_list(control_type_list)
    for control in improved_c_type_list: control_set.add(control)
    control_str = ', '.join(list(sorted(control_set)))

    return control_str

def misc_get_mame_screen_rotation_str(display_rotate):
    if display_rotate == '0' or display_rotate == '180':
        screen_str = 'horizontal'
    elif display_rotate == '90' or display_rotate == '270':
        screen_str = 'vertical'
    else:
        raise TypeError

    return screen_str

def misc_get_mame_screen_str(machine_name, machine):
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
                screen_str = 'Two unrecognised screens'
        elif len(d_list) == 3:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Three raster {0} screens'.format(r_str)
            elif d_list[0] == 'raster' and d_list[1] == 'lcd' and d_list[2] == 'lcd':
                screen_str = 'Three screens special case'
            else:
                screen_str = 'Three unrecognised screens'
        elif len(d_list) == 4:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster' and d_list[3] == 'raster':
                r_str = mame_get_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Four raster {0} screens'.format(r_str)
            else:
                screen_str = 'Four unrecognised screens'
        elif len(d_list) == 5:
            screen_str = 'Five unrecognised screens'
        elif len(d_list) == 6:
            screen_str = 'Six unrecognised screens'
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
def misc_improve_mame_control_type_list(control_type_list):
    out_list = []
    for control_str in control_type_list:
        capital_str = control_str.title()
        if capital_str == 'Only_Buttons': capital_str = 'Only Buttons'
        out_list.append(capital_str)

    return out_list

#
# A) Capitalise every list item
#
def misc_improve_mame_device_list(control_type_list):
    out_list = []
    for control_str in control_type_list: out_list.append(control_str.title())

    return out_list

#
# A) Substitute well know display types with fancier names.
#
def misc_improve_mame_display_type_list(display_type_list):
    out_list = []
    for dt in display_type_list:
        if   dt == 'lcd':    out_list.append('LCD')
        elif dt == 'raster': out_list.append('Raster')
        elif dt == 'svg':    out_list.append('SVG')
        elif dt == 'vector': out_list.append('Vector')
        else:                out_list.append(dt)

    return out_list

#
# See tools/test_compress_item_list.py for reference
# Input/Output examples:
# 1) ['dial']                 ->  ['dial']
# 2) ['dial', 'dial']         ->  ['2 x dial']
# 3) ['dial', 'dial', 'joy']  ->  ['2 x dial', 'joy']
# 4) ['joy', 'dial', 'dial']  ->  ['joy', '2 x dial']
#
def misc_compress_mame_item_list(item_list):
    reduced_list = []
    num_items = len(item_list)
    if num_items == 0 or num_items == 1: return item_list
    previous_item = item_list[0]
    item_count = 1
    for i in range(1, num_items):
        current_item = item_list[i]
        # log_debug('{0} | item_count {1} | previous_item "{2:>8}" | current_item "{3:>8}"'.format(i, item_count, previous_item, current_item))
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
def misc_compress_mame_item_list_compact(item_list):
    num_items = len(item_list)
    if num_items == 0 or num_items == 1: return item_list
    item_set = set(item_list)
    reduced_list = list(item_set)
    reduced_list_sorted = sorted(reduced_list)

    return reduced_list_sorted
