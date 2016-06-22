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
Main_DB_filename                = 'MAME_info.json'
Machines_DB_filename            = 'idx_Machines.json'
Machines_NoCoin_DB_filename     = 'idx_Machines_NoCoin.json'
Machines_Mechanical_DB_filename = 'idx_Machines_Mechanical.json'
Machines_Dead_DB_filename       = 'idx_Machines_Dead.json'
NUM_MACHINES = 50000

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
machines = fs_load_JSON_file(Main_DB_filename)

# -----------------------------------------------------------------------------
# Transform data
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
    if machine['isdevice']: continue

    # >> Machine is a parent. Add to main_pclone_dic if not already there.
    # >> If already there a
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

# --- Machine list ---
# Machines with Coin Slot and Non Mechanical and not Dead
# machines_pclone_dic = { 'parent_name' : ['clone_name', 'clone_name', ...] , ...}
machines_pclone_dic = {}
print('Making Machine index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if machine['ismechanical']: continue
    if not machine['haveCoin']: continue
    if machine['isdead']: continue

    # Copy list of clones
    machines_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- NoCoin list ---
# A) Machines with No Coin Slot and Non Mechanical and not Dead
nocoin_pclone_dic = {}
print('Making NoCoin index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if machine['ismechanical']: continue
    if machine['haveCoin']: continue
    if machine['isdead']: continue

    # Copy list of clones
    nocoin_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- Mechanical machines ---
# A) Mechanical Machines and not Dead
mechanical_pclone_dic = {}
print('Making Mechanical index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if not machine['ismechanical']: continue
    if machine['isdead']: continue

    # Copy list of clones
    mechanical_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# --- Dead machines ---
dead_pclone_dic = {}
print('Making Dead Mechines index...')
for p_machine_name in main_pclone_dic:
    machine = machines[p_machine_name]
    if not machine['isdead']: continue
    
    # Copy list of clones
    dead_pclone_dic[p_machine_name] = main_pclone_dic[p_machine_name]

# -----------------------------------------------------------------------------
# Now write simplified JSON
# -----------------------------------------------------------------------------
print('Writing AML databases...')
fs_write_JSON_file(Main_DB_filename, machines)
fs_write_JSON_file(Machines_DB_filename, machines_pclone_dic)
fs_write_JSON_file(Machines_NoCoin_DB_filename, nocoin_pclone_dic)
fs_write_JSON_file(Machines_Mechanical_DB_filename, mechanical_pclone_dic)
fs_write_JSON_file(Machines_Dead_DB_filename, dead_pclone_dic)
