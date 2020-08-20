# -*- coding: utf-8 -*-

# Copyright (c) 2016-2020 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# Advanced MAME Launcher miscellaneous MAME functions.
#
# Functions in this module only depend on the Python standard library.
# This module can be loaded anywhere without creating circular dependencies.
# Optionally this module can include utils.py to use the log_*() functions.

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------
# Builds a string separated by a | character. Replaces | occurrences with _
# The string can be separated with str.split('|')
def misc_build_db_str_3(str1, str2, str3):
    if str1.find('|') >= 0: str1 = str1.replace('|', '_')
    if str2.find('|') >= 0: str2 = str2.replace('|', '_')
    if str3.find('|') >= 0: str3 = str3.replace('|', '_')

    return '{}|{}|{}'.format(str1, str2, str3)

# Used in mame_build_MAME_plots()
def misc_get_mame_control_str(control_type_list):
    control_set = set()
    improved_c_type_list = misc_improve_mame_control_type_list(control_type_list)
    for control in improved_c_type_list: control_set.add(control)
    control_str = ', '.join(list(sorted(control_set)))

    return control_str

# Used here in misc_get_mame_screen_str()
def misc_get_mame_screen_rotation_str(display_rotate):
    if display_rotate == '0' or display_rotate == '180':
        screen_str = 'horizontal'
    elif display_rotate == '90' or display_rotate == '270':
        screen_str = 'vertical'
    else:
        raise TypeError

    return screen_str

# Used in mame_build_MAME_plots()
def misc_get_mame_screen_str(machine_name, machine):
    d_list = machine['display_type']
    if d_list:
        if len(d_list) == 1:
            rotation_str = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
            screen_str = 'One {} {} screen'.format(d_list[0], rotation_str)
        elif len(d_list) == 2:
            if d_list[0] == 'lcd' and d_list[1] == 'raster':
                r_str_1 = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
                r_str_2 = misc_get_mame_screen_rotation_str(machine['display_rotate'][1])
                screen_str = 'One LCD {} screen and one raster {} screen'.format(r_str_1, r_str_2)
            elif d_list[0] == 'raster' and d_list[1] == 'raster':
                r_str = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Two raster {} screens'.format(r_str)
            elif d_list[0] == 'svg' and d_list[1] == 'svg':
                r_str = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Two SVG {} screens'.format(r_str)
            elif d_list[0] == 'unknown' and d_list[1] == 'unknown':
                screen_str = 'Two unknown screens'
            else:
                screen_str = 'Two unrecognised screens'
        elif len(d_list) == 3:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster':
                r_str = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Three raster {} screens'.format(r_str)
            elif d_list[0] == 'raster' and d_list[1] == 'lcd' and d_list[2] == 'lcd':
                screen_str = 'Three screens special case'
            else:
                screen_str = 'Three unrecognised screens'
        elif len(d_list) == 4:
            if d_list[0] == 'raster' and d_list[1] == 'raster' and d_list[2] == 'raster' and d_list[3] == 'raster':
                r_str = misc_get_mame_screen_rotation_str(machine['display_rotate'][0])
                screen_str = 'Four raster {} screens'.format(r_str)
            else:
                screen_str = 'Four unrecognised screens'
        elif len(d_list) == 5:
            screen_str = 'Five unrecognised screens'
        elif len(d_list) == 6:
            screen_str = 'Six unrecognised screens'
        else:
            log_error('mame_get_screen_str() d_list = {}'.format(str(d_list)))
            raise TypeError
    else:
        screen_str = 'No screen'

    return screen_str

def misc_get_mame_display_type(display_str):
    if   display_str == 'lcd':    display_name = 'LCD'
    elif display_str == 'raster': display_name = 'Raster'
    elif display_str == 'svg':    display_name = 'SVG'
    elif display_str == 'vector': display_name = 'Vector'
    else:                         display_name = display_str

    return display_name

def misc_get_mame_display_rotation(d_str):
    if d_str == '0' or d_str == '180':
        rotation_letter = 'Hor'
    elif d_str == '90' or d_str == '270':
        rotation_letter = 'Ver'
    else:
        raise TypeError('Wrong display rotate "{}"'.format(d_str))

    return rotation_letter

def misc_get_display_type_catalog_key(display_type_list, display_rotate_list):
    if len(display_type_list) == 0:
        catalog_key = '[ No display ]'
    else:
        display_list = []
        for dis_index in range(len(display_type_list)):
            display_name = misc_get_mame_display_type(display_type_list[dis_index])
            display_rotation = misc_get_mame_display_rotation(display_rotate_list[dis_index])
            display_list.append('{} {}'.format(display_name, display_rotation))
        catalog_key = " / ".join(display_list)

    return catalog_key

def misc_get_display_resolution_catalog_key(display_width, display_height):
    if len(display_width) > 1 or len(display_height) > 1:
        catalog_key = '{} displays'.format(len(display_width))
    elif len(display_width) == 0 and len(display_height) == 1:
        catalog_key = 'Empty x {}'.format(display_height[0])
    elif len(display_width) == 1 and len(display_height) == 0:
        catalog_key = '{} x Empty'.format(display_width[0])
    elif len(display_width) == 0 and len(display_height) == 0:
        catalog_key = 'Empty x Empty'
    else:
        catalog_key = '{} x {}'.format(display_width[0], display_height[0])

    return catalog_key

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
        # log_debug('{} | item_count {} | previous_item "{2:>8}" | current_item "{3:>8}"'.format(i, item_count, previous_item, current_item))
        if current_item == previous_item:
            item_count += 1
        else:
            if item_count == 1: reduced_list.append('{}'.format(previous_item))
            else:               reduced_list.append('{} {}'.format(item_count, previous_item))
            item_count = 1
            previous_item = current_item
        # >> Last elemnt of the list
        if i == num_items - 1:
            if current_item == previous_item:
                if item_count == 1: reduced_list.append('{}'.format(current_item))
                else:               reduced_list.append('{} {}'.format(item_count, current_item))
            else:
               reduced_list.append('{}'.format(current_item))

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

# -------------------------------------------------------------------------------------------------
def misc_extract_MAME_version(PATHS, mame_prog_FN):
    (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
    log_info('fs_extract_MAME_version() mame_prog_FN "{}"'.format(mame_prog_FN.getPath()))
    log_debug('fs_extract_MAME_version() mame_dir     "{}"'.format(mame_dir))
    log_debug('fs_extract_MAME_version() mame_exec    "{}"'.format(mame_exec))
    with open(PATHS.MAME_STDOUT_VER_PATH.getPath(), 'wb') as out, open(PATHS.MAME_STDERR_VER_PATH.getPath(), 'wb') as err:
        p = subprocess.Popen([mame_prog_FN.getPath(), '-?'], stdout=out, stderr=err, cwd=mame_dir)
        p.wait()

    # --- Check if everything OK ---
    # statinfo = os.stat(PATHS.MAME_XML_PATH.getPath())
    # filesize = statinfo.st_size

    # --- Read version ---
    lines = utils_load_file_to_slist(PATHS.MAME_STDOUT_VER_PATH.getPath()):
    version_str = ''
    for line in lines:
        m = re.search('^MAME v([0-9\.]+?) \(([a-z0-9]+?)\)$', line.strip())
        if m:
            version_str = m.group(1)
            break

    return version_str

#
# Counts MAME machines in a modern MAME XML file.
#
def misc_count_MAME_machines_modern(XML_path_FN):
    log_debug('fs_count_MAME_machines_modern() BEGIN...')
    log_debug('XML "{}"'.format(XML_path_FN.getPath()))
    pDialog = KodiProgressDialog()
    pDialog.startProgress('Counting number of MAME machines...')
    num_machines = 0
    with open(XML_path_FN.getPath(), 'rt') as f:
        for line in f:
            if line.find('<machine name=') > 0: num_machines += 1
    pDialog.endProgress()

    return num_machines

#
# Older versions of MAME use <game> instead of <machine>
#
def misc_count_MAME_machines_archaic(XML_path_FN):
    log_debug('fs_count_MAME_machines_archaic() BEGIN...')
    log_debug('XML "{}"'.format(XML_path_FN.getPath()))
    pDialog = KodiProgressDialog()
    pDialog.startProgress('Counting number of MAME machines...')
    num_machines = 0
    with open(XML_path_FN.getPath(), 'rt') as f:
        for line in f:
            if line.find('<game name=') > 0: num_machines += 1
    pDialog.endProgress()

    return num_machines

#
# Creates a new control_dic and updates the number of machines.
# Returns:
# options_dic['abort']
# options_dic['msg']            Only valid if options_dic['abort'] is True
# options_dic['filesize']       In bytes
# options_dic['total_machines'] Integer
#
def misc_extract_MAME_XML(PATHS, settings, AML_version_str, options_dic):
    options_dic['abort'] = False

    # --- Check for errors ---
    if not settings['mame_prog']:
        options_dic['abort'] = True
        options_dic['msg'] = 'MAME executable is not set.'
        return

    # Extract XML from MAME executable.
    mame_prog_FN = FileName(settings['mame_prog'])
    (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
    log_info('fs_extract_MAME_XML() mame_prog_FN "{}"'.format(mame_prog_FN.getPath()))
    log_info('fs_extract_MAME_XML() Saving XML   "{}"'.format(PATHS.MAME_XML_PATH.getPath()))
    log_debug('fs_extract_MAME_XML() mame_dir     "{}"'.format(mame_dir))
    log_debug('fs_extract_MAME_XML() mame_exec    "{}"'.format(mame_exec))
    pDialog = KodiProgressDialog()
    pDialog.startProgress('Extracting MAME XML database. Progress bar is not accurate.')
    with open(PATHS.MAME_XML_PATH.getPath(), 'wb') as out, open(PATHS.MAME_STDERR_PATH.getPath(), 'wb') as err:
        p = subprocess.Popen([mame_prog_FN.getPath(), '-listxml'], stdout=out, stderr=err, cwd=mame_dir)
        count = 0
        while p.poll() is None:
            time.sleep(1)
            count += 1
            pDialog.updateProgress(count)
    pDialog.endProgress()

    # --- Check if everything OK ---
    statinfo = os.stat(PATHS.MAME_XML_PATH.getPath())
    filesize = statinfo.st_size
    options_dic['filesize'] = filesize

    # --- Count number of machines. Useful for progress dialogs ---
    log_info('fs_extract_MAME_XML() Counting number of machines ...')
    total_machines = fs_count_MAME_machines_modern(PATHS.MAME_XML_PATH)
    options_dic['total_machines'] = total_machines
    log_info('fs_extract_MAME_XML() Found {} machines.'.format(total_machines))

    # -----------------------------------------------------------------------------
    # Reset MAME control dictionary completely
    # -----------------------------------------------------------------------------
    AML_version_int = fs_AML_version_str_to_int(AML_version_str)
    log_info('fs_extract_MAME_XML() AML version str "{}"'.format(AML_version_str))
    log_info('fs_extract_MAME_XML() AML version int {}'.format(AML_version_int))
    control_dic = fs_new_control_dic()
    change_control_dic(control_dic, 'ver_AML', AML_version_int)
    change_control_dic(control_dic, 'ver_AML_str', AML_version_str)
    change_control_dic(control_dic, 'stats_total_machines', total_machines)
    change_control_dic(control_dic, 't_XML_extraction', time.time())
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic, verbose = True)

def misc_process_RETRO_MAME2003PLUS(PATHS, settings, AML_version_str, options_dic):
    options_dic['abort'] = False

    # --- Check for errors ---
    if not settings['xml_2003_path']:
        options_dic['abort'] = True
        kodi_dialog_OK('MAME 2003 Plus XML path is not set.')
        return

    # --- Count number of machines. Useful for progress dialogs ---
    XML_path_FN = FileName(settings['xml_2003_path'])
    log_info('fs_process_RETRO_MAME2003PLUS() Counting number of machines ...')
    total_machines = fs_count_MAME_machines_archaic(XML_path_FN)
    options_dic['total_machines'] = total_machines
    log_info('fs_process_RETRO_MAME2003PLUS() Found {} machines.'.format(total_machines))

    # -----------------------------------------------------------------------------
    # Reset MAME control dictionary completely
    # -----------------------------------------------------------------------------
    AML_version_int = fs_AML_version_str_to_int(AML_version_str)
    log_info('fs_process_RETRO_MAME2003PLUS() AML version str "{}"'.format(AML_version_str))
    log_info('fs_process_RETRO_MAME2003PLUS() AML version int {}'.format(AML_version_int))
    control_dic = fs_new_control_dic()
    change_control_dic(control_dic, 'ver_AML', AML_version_int)
    change_control_dic(control_dic, 'ver_AML_str', AML_version_str)
    change_control_dic(control_dic, 'stats_total_machines', total_machines)
    change_control_dic(control_dic, 't_XML_extraction', time.time())
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic, verbose = True)
