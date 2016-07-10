#!/usr/bin/python
# -*- coding: utf-8 -*-
# Converts MAME output XML into AML database
#

# Copyright (c) 2016 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- INSTRUCTIONS -------------------------------------------------------------
#
# ------------------------------------------------------------------------------

# --- Python standard library ---
import xml.etree.ElementTree as ET 
import re
import sys
import json
import io
import os

# --- "Constants" -------------------------------------------------------------
MAIN_DB_FILE_PATH                = 'MAME_info.json'
MAIN_PCLONE_DIC_FILE_PATH        = 'MAME_PClone_dic.json'

MACHINES_IDX_FILE_PATH           = 'idx_Machines.json'
MACHINES_IDX_NOCOIN_FILE_PATH    = 'idx_Machines_NoCoin.json'
MACHINES_IDX_MECHA_FILE_PATH     = 'idx_Machines_Mechanical.json'
MACHINES_IDX_DEAD_FILE_PATH      = 'idx_Machines_Dead.json'
MACHINES_IDX_CHD_FILE_PATH       = 'idx_Machines_CHD.json'

CATALOG_CATVER_FILE_PATH         = 'catalog_catver.json'
CATALOG_CATLIST_FILE_PATH        = 'catalog_catlist.json'
CATALOG_GENRE_FILE_PATH          = 'catalog_genre.json'
CATALOG_MANUFACTURER_FILE_PATH   = 'catalog_manufacturer.json'
CATALOG_YEAR_FILE_PATH           = 'catalog_year.json'
CATALOG_DRIVER_FILE_PATH         = 'catalog_driver.json'
CATALOG_CONTROL_FILE_PATH        = 'catalog_control.json'
CATALOG_DISPLAY_TAG_FILE_PATH    = 'catalog_display_tag.json'
CATALOG_DISPLAY_TYPE_FILE_PATH   = 'catalog_display_type.json'
CATALOG_DISPLAY_ROTATE_FILE_PATH = 'catalog_display_rotate.json'
CATALOG_SL_FILE_PATH             = 'catalog_SL.json'

# -------------------------------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------------------------------
def fs_write_JSON_file(json_filename, json_data):
    # >> Write JSON data
    try:
        with io.open(json_filename, 'wt', encoding='utf-8') as file:
          file.write(unicode(json.dumps(json_data, ensure_ascii = False, sort_keys = True, indent = 2, separators = (',', ': '))))
    except OSError:
        # gui_kodi_notify('Advanced Emulator Launcher - Error', 'Cannot write {0} file (OSError)'.format(roms_json_file))
        pass
    except IOError:
        # gui_kodi_notify('Advanced Emulator Launcher - Error', 'Cannot write {0} file (IOError)'.format(roms_json_file))
        pass

def fs_load_JSON_file(json_filename):
    # --- If file does not exist return empty dictionary ---
    data_dic = {}
    if not os.path.isfile(json_filename):
        return data_dic

    # --- Parse using json module ---
    # log_verb('fs_load_ROMs_JSON() Loading JSON file {0}'.format(json_filename))
    with open(json_filename) as file:    
        data_dic = json.load(file)

    return data_dic

# -----------------------------------------------------------------------------
# Load MAME data
# -----------------------------------------------------------------------------
print('Reading main MAME database...')
machines = fs_load_JSON_file(MAIN_DB_FILE_PATH)

# -----------------------------------------------------------------------------
# Main parent-clone list
# -----------------------------------------------------------------------------
# Create a couple of data struct for quickly know the parent of a clone game and
# all clones of a parent.
#
# main_pclone_dic = { 'parent_name' : ['clone_name', 'clone_name', ...] , ...}
# main_parent_dic = { 'clone_name' : 'parent_name', ... }
print('Making PClone list...')
main_pclone_dic = {}
main_parent_dic = {}
for machine_name in machines:
    machine = machines[machine_name]
    # >> Exclude devices
    if machine['isDevice']: continue

    # >> Machine is a parent. Add to main_pclone_dic if not already there.
    if machine['cloneof'] == u'':
        if machine_name not in main_pclone_dic:
            main_pclone_dic[machine_name] = []

    # >> Machine is a clone
    else:
        parent_name = machine['cloneof']
        # >> Add clone machine to main_parent_dic
        main_parent_dic[machine_name] = parent_name

        # >> If parent already in main_pclone_dic then add clone to parent list.
        # >> If parent not there, then add parent first and then add clone.
        if parent_name in main_pclone_dic:
            main_pclone_dic[parent_name].append(machine_name)
        else:
            main_pclone_dic[parent_name] = []
            main_pclone_dic[parent_name].append(machine_name)

# -----------------------------------------------------------------------------
# Simple machine lists
# -----------------------------------------------------------------------------
# --- Machine list ---
# Machines with Coin Slot and Non Mechanical and not Dead
# machines_pclone_dic = { 'parent_name' : ['clone_name', 'clone_name', ...] , ...}
machines_pclone_dic = {}
print('Making Machine index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if machine['isMechanical']: continue
    if not machine['hasCoin']: continue
    if machine['isDead']: continue

    # Copy list of clones
    machines_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- NoCoin list ---
# A) Machines with No Coin Slot and Non Mechanical and not Dead
nocoin_pclone_dic = {}
print('Making NoCoin index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if machine['isMechanical']: continue
    if machine['hasCoin']: continue
    if machine['isDead']: continue

    # Copy list of clones
    nocoin_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- Mechanical machines ---
# A) Mechanical Machines and not Dead
mechanical_pclone_dic = {}
print('Making Mechanical index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if not machine['isMechanical']: continue
    if machine['isDead']: continue

    # Copy list of clones
    mechanical_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- Dead machines ---
dead_pclone_dic = {}
print('Making Dead Mechines index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if not machine['isDead']: continue
    
    # Copy list of clones
    dead_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- CHD machines ---
CHD_pclone_dic = {}
print('Making CHD Mechines index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if not machine['hasCHD']: continue
    
    # Copy list of clones
    CHD_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# -----------------------------------------------------------------------------
# Cataloged machine list
# -----------------------------------------------------------------------------
# >> Catalog dictionary: { 'catalog_name' : [parent_name, parent_name, ...], ... }

# --- Catver catalog ---
catver_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['catver']
    # >> Add to catalog
    if catalog_key in catver_catalog:
        catver_catalog[catalog_key].append(p_machine_name)
    else:
        catver_catalog[catalog_key] = [p_machine_name]

# --- Catlist catalog ---
catlist_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['catlist']
    if catalog_key in catlist_catalog:
        catlist_catalog[catalog_key].append(p_machine_name)
    else:
        catlist_catalog[catalog_key] = [p_machine_name]

# --- Genre catalog ---
genre_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['genre']
    if catalog_key in genre_catalog:
        genre_catalog[catalog_key].append(p_machine_name)
    else:
        genre_catalog[catalog_key] = [p_machine_name]

# --- Manufacturer catalog ---
manufacturer_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['manufacturer']
    if catalog_key in manufacturer_catalog:
        manufacturer_catalog[catalog_key].append(p_machine_name)
    else:
        manufacturer_catalog[catalog_key] = [p_machine_name]

# --- Year catalog ---
year_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['year']
    if catalog_key in year_catalog:
        year_catalog[catalog_key].append(p_machine_name)
    else:
        year_catalog[catalog_key] = [p_machine_name]

# --- Driver catalog ---
driver_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = machine['sourcefile']
    if catalog_key in driver_catalog:
        driver_catalog[catalog_key].append(p_machine_name)
    else:
        driver_catalog[catalog_key] = [p_machine_name]

# --- Control catalog ---
control_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = " / ".join(machine['control_type'])
    
    # >> Change category name for machines with no controls
    if catalog_key == '': catalog_key = '[ No controls ]'

    if catalog_key in control_catalog:
        control_catalog[catalog_key].append(p_machine_name)
    else:
        control_catalog[catalog_key] = [p_machine_name]

# --- Display tag catalog ---
display_tag_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = " / ".join(machine['display_tag'])

    # >> Change category name for machines with no display
    if catalog_key == '': catalog_key = '[ No display ]'

    if catalog_key in display_tag_catalog:
        display_tag_catalog[catalog_key].append(p_machine_name)
    else:
        display_tag_catalog[catalog_key] = [p_machine_name]

# --- Display type catalog ---
display_type_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = " / ".join(machine['display_type'])

    # >> Change category name for machines with no display
    if catalog_key == '': catalog_key = '[ No display ]'

    if catalog_key in display_type_catalog:
        display_type_catalog[catalog_key].append(p_machine_name)
    else:
        display_type_catalog[catalog_key] = [p_machine_name]

# --- Display rotate catalog ---
display_rotate_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    catalog_key = " / ".join(machine['display_rotate'])

    # >> Change category name for machines with no display
    if catalog_key == '': catalog_key = '[ No display ]'

    if catalog_key in display_rotate_catalog:
        display_rotate_catalog[catalog_key].append(p_machine_name)
    else:
        display_rotate_catalog[catalog_key] = [p_machine_name]

# --- Software List catalog ---
SL_catalog = {}
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    # >> A machine may have more than 1 software lists
    for sl_name in machine['softwarelists']:
        catalog_key = sl_name
        if catalog_key in SL_catalog:
            SL_catalog[catalog_key].append(p_machine_name)
        else:
            SL_catalog[catalog_key] = [p_machine_name]

# -----------------------------------------------------------------------------
# Now write simplified JSON
# -----------------------------------------------------------------------------
print('Writing AML main PClone dictionary...')
fs_write_JSON_file(MAIN_PCLONE_DIC_FILE_PATH, main_pclone_dic)

print('Writing AML simple databases...')
fs_write_JSON_file(MACHINES_IDX_FILE_PATH, machines_pclone_dic)
fs_write_JSON_file(MACHINES_IDX_NOCOIN_FILE_PATH, nocoin_pclone_dic)
fs_write_JSON_file(MACHINES_IDX_MECHA_FILE_PATH, mechanical_pclone_dic)
fs_write_JSON_file(MACHINES_IDX_DEAD_FILE_PATH, dead_pclone_dic)
fs_write_JSON_file(MACHINES_IDX_CHD_FILE_PATH, CHD_pclone_dic)

print('Writing AML cataloged databases...')
fs_write_JSON_file(CATALOG_CATVER_FILE_PATH, catver_catalog)
fs_write_JSON_file(CATALOG_CATLIST_FILE_PATH, catlist_catalog)
fs_write_JSON_file(CATALOG_GENRE_FILE_PATH, genre_catalog)
fs_write_JSON_file(CATALOG_MANUFACTURER_FILE_PATH, manufacturer_catalog)
fs_write_JSON_file(CATALOG_YEAR_FILE_PATH, year_catalog)
fs_write_JSON_file(CATALOG_DRIVER_FILE_PATH, driver_catalog)
fs_write_JSON_file(CATALOG_CONTROL_FILE_PATH, control_catalog)
fs_write_JSON_file(CATALOG_DISPLAY_TAG_FILE_PATH, display_tag_catalog)
fs_write_JSON_file(CATALOG_DISPLAY_TYPE_FILE_PATH, display_type_catalog)
fs_write_JSON_file(CATALOG_DISPLAY_ROTATE_FILE_PATH, display_rotate_catalog)
fs_write_JSON_file(CATALOG_SL_FILE_PATH, SL_catalog)
