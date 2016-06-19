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
SL_dir          = '/cygdrive/e/Temp/Mame 0173b/hash/'
SL_cat_filename = 'cat_SoftwareLists.json'
SL_database_dir = './db_SoftwareLists/'

# -------------------------------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------------------------------
def fs_write_JSON(json_filename, json_data):
    # >> Write JSON data
    print(u'fs_write_JSON() Saving "{0}"'.format(json_filename))
    try:
        with io.open(json_filename, 'wt', encoding='utf-8') as file:
          file.write(unicode(json.dumps(json_data, ensure_ascii = False, sort_keys = True, indent = 2, separators = (',', ': '))))
    except OSError:
        # gui_kodi_notify('Advanced Emulator Launcher - Error', 'Cannot write {0} file (OSError)'.format(roms_json_file))
        pass
    except IOError:
        # gui_kodi_notify('Advanced Emulator Launcher - Error', 'Cannot write {0} file (IOError)'.format(roms_json_file))
        pass

def fs_new_SL_ROM():        
    R = {
        'description'   : u'',
        'year'          : u'',
        'publisher'     : u''
    }

    return R

def fs_load_SL_XML(xml_filename):
    __debug_xml_parser = False
    roms = {}
    num_roms = 0
    display_name = u''

    # --- If file does not exist return empty dictionary ---
    if not os.path.isfile(xml_filename):
        return (roms, num_roms, display_name)

    # --- Parse using cElementTree ---
    print(u'fs_load_SL_XML() Loading XML file "{0}"'.format(xml_filename))
    # If XML has errors (invalid characters, etc.) this will rais exception 'err'
    try:
        xml_tree = ET.parse(xml_filename)
    except:
        return {}
    xml_root = xml_tree.getroot()
    display_name = xml_root.attrib['description']
    for root_element in xml_root:
        if __debug_xml_parser: print(u'Root child {0}'.format(root_element.tag))

        if root_element.tag == 'software':
            num_roms += 1
            rom = fs_new_SL_ROM()
            rom_name = root_element.attrib['name']
            for rom_child in root_element:
                # By default read strings
                xml_text = rom_child.text if rom_child.text is not None else ''
                xml_tag  = rom_child.tag
                if __debug_xml_parser: print(u'{0} --> {1}'.format(xml_tag, xml_text))
                
                # Only pick tags we want
                if xml_tag == 'description' or xml_tag == 'year' or xml_tag == 'publisher':
                    rom[xml_tag] = xml_text
            roms[rom_name] = rom

    return (roms, num_roms, display_name)

# -------------------------------------------------------------------------------------------------
# Filenames
# -------------------------------------------------------------------------------------------------
#
# Full decomposes a file name path or directory into its constituents
# In theory this is indepedent of the operating system.
# Returns a FileName object:
#   F.path        Full path                                     /home/Wintermute/Sonic.zip
#   F.path_noext  Full path with no extension                   /home/Wintermute/Sonic
#   F.dirname     Directory name of file. Does not end in '/'   /home/Wintermute
#   F.base        File name with no path                        Sonic.zip
#   F.base_noext  File name with no path and no extension       Sonic
#   F.ext         File extension                                .zip
#
class FileName:
    pass

def misc_split_path(f_path):
    F = FileName()

    F.path       = f_path
    (root, ext)  = os.path.splitext(F.path)
    F.path_noext = root
    F.dirname    = os.path.dirname(f_path)
    F.base       = os.path.basename(F.path)
    (root, ext)  = os.path.splitext(F.base)
    F.base_noext = root
    F.ext        = ext

    return F

# -------------------------------------------------------------------------------------------------
# Scan all XML files in Software Lists directory
# -------------------------------------------------------------------------------------------------
# SL_catalog = { 'name' : {'display_name': u'', 'rom_count' : int, 'rom_DB_noext' : u'' }, ...}
SL_catalog = {}
for file in os.listdir(SL_dir):
    if file.endswith('.xml'):
        # >> Open software list XML and parse it. Then, save data fields we want in JSON.
        F = misc_split_path(file)
        SL_path = os.path.join(SL_dir, file)
        (roms, num_roms, display_name) = fs_load_SL_XML(SL_path)
        output_filename = os.path.join(SL_database_dir, F.base_noext + '.json')
        fs_write_JSON(output_filename, roms)

        # >> Add software list to catalog
        SL = {'display_name': display_name, 'rom_count' : num_roms, 'rom_DB_noext' : F.base_noext }
        SL_catalog[F.base_noext] = SL

# -------------------------------------------------------------------------------------------------
# Save Software List catalog
# -------------------------------------------------------------------------------------------------
print('Writing SL catalog...')
fs_write_JSON(SL_cat_filename, SL_catalog)
