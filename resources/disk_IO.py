# -*- coding: utf-8 -*-
# Advanced MAME Launcher filesystem I/O functions
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
import json
import io
import codecs, time
import subprocess
import re

# --- XML stuff ---
# ~~~ cElementTree sometimes fails to parse XML in Kodi's Python interpreter... I don't know why
# import xml.etree.cElementTree as ET

# ~~~ Using ElementTree seems to solve the problem
import xml.etree.ElementTree as ET

# --- AEL packages ---
from utils import *
try:
    from utils_kodi import *
except:
    from utils_kodi_standalone import *

# -------------------------------------------------------------------------------------------------
# Advanced MAME Launcher data model
# -------------------------------------------------------------------------------------------------
# Status flags meaning:
#   -  Machine doesn't have ROMs | Machine doesn't have Software Lists
#   ?  Machine has own ROMs and ROMs not been scanned
#   r  Machine has own ROMs and ROMs doesn't exist
#   R  Machine has own ROMs and ROMs exists | Machine has Software Lists
#   *  Machine has merged ROMs
#
# Status device flag:
#   -  Machine has no devices
#   d  Machine has device/s but are not mandatory (can be booted without the device).
#   D  Machine has device/s and must be plugged in order to boot.
#
def fs_new_machine():
    m = {
        'sourcefile'     : '',
        'isBIOS'         : False,
        'isDevice'       : False,
        'isMechanical'   : False,
        'cloneof'        : '',
        'romof'          : '',
        'sampleof'       : '',
        'description'    : '',
        'year'           : '',
        'manufacturer'   : '',
        'catver'         : '',
        'catlist'        : '',
        'genre'          : '',
        'nplayers'       : '',
        'display_tag'    : [],
        'display_type'   : [], # (raster|vector|lcd|unknown) #REQUIRED>
        'display_rotate' : [], # (0|90|180|270) #REQUIRED>
        'control_type'   : [],
        'hasCoin'        : False,
        'coins'          : 0,
        'driver_status'  : '',
        'CHDs'           : [],
        'CHDs_merged'    : [],
        'softwarelists'  : [],
        'isDead'         : False,
        'hasROMs'        : False,
        'hasROMs_merged' : False,
        'status_ROM'     : '-',
        'status_CHD'     : '-',
        'status_SAM'     : '-',
        'status_SL'      : '-',
        'status_Device'  : '-',
        'device_list'    : [],  # List of <instance name="cartridge1">. Ignore briefname
        'device_tags'    : [],
        'bios_name'      : [],  # List of <biosset name="" >
        'bios_desc'      : [],  # List of <biosset description="" >
    }

    return m

ASSET_MAME_KEY_LIST  = ['cabinet',  'cpanel',  'flyer',  'marquee',  'PCB',  'snap',  'title',  'clearlogo']
ASSET_MAME_PATH_LIST = ['cabinets', 'cpanels', 'flyers', 'marquees', 'PCBs', 'snaps', 'titles', 'clearlogos']
def fs_new_MAME_asset():
    a = {
        'cabinet'   : '',
        'cpanel'    : '',
        'flyer'     : '',
        'marquee'   : '',
        'PCB'       : '',
        'snap'      : '',
        'title'     : '',
        'clearlogo' : '',
    }

    return a

# Status flags meaning:
#   ?  SL ROM not scanned
#   r  Missing ROM
#   R  Have ROM
def fs_new_SL_ROM():
    R = {
        'description'    : '',
        'year'           : '',
        'publisher'      : '',
        'cloneof'        : '',
        'part_name'      : [],
        'part_interface' : [],
        'num_roms'       : 0,
        'CHDs'           : [],
        'status_ROM'     : '-',
        'status_CHD'     : '-',
    }

    return R

ASSET_SL_KEY_LIST  = ['title',     'snap',     'boxfront']
ASSET_SL_PATH_LIST = ['titles_SL', 'snaps_SL', 'covers_SL']
def fs_new_SL_asset():
    a = {
        'title'    : '',
        'snap'     : '',
        'boxfront' : '',
    }

    return a

def fs_new_control_dic():
    C = {
        # >> Filed in when extracting MAME XML
        'total_machines' : 0,
        # >> Files in when building main MAME database
        'mame_version'        : 'Unknown. MAME database not built',
        'catver_version'      : 'Unknown. MAME database not built',
        'catlist_version'     : 'Unknown. MAME database not built',
        'genre_version'       : 'Unknown. MAME database not built',
        'nplayers_version'    : 'Unknown. MAME database not built',
        'processed_machines'  : 0,
        'parent_machines'     : 0,
        'clone_machines'      : 0,
        'devices_machines'    : 0,
        'BIOS_machines'       : 0,
        'coin_machines'       : 0,
        'nocoin_machines'     : 0,
        'mechanical_machines' : 0,
        'dead_machines'       : 0,
        'Own_ROM_machines'    : 0,
        'Merged_ROM_machines' : 0,
        'No_ROM_machines'     : 0,
        'Own_CHD_machines'    : 0,
        'Merged_CHD_machines' : 0,
        'samples_machines'    : 0,
        # >> Filed in when building SL index
        'num_SL_files' : 0,
        'num_SL_ROMs'  : 0,
        'num_SL_CHDs'  : 0,
        # >> Filed in by the MAME ROM/CHD/Samples scanner
        'ROMs_have'       : 0,
        'ROMs_total'      : 0,
        'ROMs_missing'    : 0,
        'CHDs_have'       : 0,
        'CHDs_total'      : 0,
        'CHDs_missing'    : 0,
        'Samples_have'    : 0,
        'Samples_total'   : 0,
        'Samples_missing' : 0,

        # >> Filed in by the SL ROM scanner
        'SL_ROMs_have'    : 0,
        'SL_ROMs_total'   : 0,
        'SL_ROMs_missing' : 0,
        'SL_CHDs_have'    : 0,
        'SL_CHDs_total'   : 0,
        'SL_CHDs_missing' : 0,
    }
    
    return C

# --- Constants ---
VIEW_MODE_NORMAL = 'Normal'
VIEW_MODE_ALL    = 'All'

# >> Used to build the properties list. 
#    1) Must match names in main.py @_render_root_list()
#    2) Must match names in disk_IO.py @fs_build_MAME_catalogs()
CATALOG_NAME_LIST  = ['None', 'Catver', 'Catlist', 'Genre', 'NPlayers', 'Manufacturer', 
                      'Year', 'Driver', 'Controls', 
                      'Display_Tag', 'Display_Type', 'Display_Rotate',
                      'Devices', 'BySL']

def fs_get_cataloged_dic_parents(PATHS, catalog_name):
    if   catalog_name == 'None':           catalog_dic = fs_load_JSON_file(PATHS.CATALOG_NONE_PARENT_PATH.getPath())
    elif catalog_name == 'Catver':         catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATVER_PARENT_PATH.getPath())
    elif catalog_name == 'Catlist':        catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATLIST_PATH.getPath())
    elif catalog_name == 'Genre':          catalog_dic = fs_load_JSON_file(PATHS.CATALOG_GENRE_PATH.getPath())
    elif catalog_name == 'NPlayers':       catalog_dic = fs_load_JSON_file(PATHS.CATALOG_NPLAYERS_PATH.getPath())
    elif catalog_name == 'Manufacturer':   catalog_dic = fs_load_JSON_file(PATHS.CATALOG_MANUFACTURER_PATH.getPath())
    elif catalog_name == 'Year':           catalog_dic = fs_load_JSON_file(PATHS.CATALOG_YEAR_PATH.getPath())
    elif catalog_name == 'Driver':         catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DRIVER_PATH.getPath())
    elif catalog_name == 'Controls':       catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CONTROL_PATH.getPath())
    elif catalog_name == 'Display_Tag':    catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TAG_PATH.getPath())
    elif catalog_name == 'Display_Type':   catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TYPE_PATH.getPath())
    elif catalog_name == 'Display_Rotate': catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_ROTATE_PATH.getPath())
    elif catalog_name == 'Devices':        catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DEVICE_LIST_PATH.getPath())
    elif catalog_name == 'BySL':           catalog_dic = fs_load_JSON_file(PATHS.CATALOG_SL_PATH.getPath())

    return catalog_dic

# -------------------------------------------------------------------------------------------------
# Exceptions raised by this module
# -------------------------------------------------------------------------------------------------
class DiskError(Exception):
    """Base class for exceptions in this module."""
    pass

class CriticalError(DiskError):
    def __init__(self, msg):
        self.msg = msg

# -------------------------------------------------------------------------------------------------
# JSON write/load
# -------------------------------------------------------------------------------------------------
def fs_load_JSON_file(json_filename):
    # --- If file does not exist return empty dictionary ---
    data_dic = {}
    if not os.path.isfile(json_filename): return data_dic
    log_verb('fs_load_ROMs_JSON() "{0}"'.format(json_filename))
    with open(json_filename) as file:
        data_dic = json.load(file)

    return data_dic

def fs_write_JSON_file(json_filename, json_data):
    log_verb('fs_write_JSON_file() "{0}"'.format(json_filename))
    try:
        with io.open(json_filename, 'wt', encoding='utf-8') as file:
          file.write(unicode(json.dumps(json_data, ensure_ascii = False, sort_keys = True,
                                        indent = 2, separators = (',', ': '))))
    except OSError:
        gui_kodi_notify('Advanced MAME Launcher - Error', 'Cannot write {0} file (OSError)'.format(roms_json_file))
    except IOError:
        gui_kodi_notify('Advanced MAME Launcher - Error', 'Cannot write {0} file (IOError)'.format(roms_json_file))

# -------------------------------------------------------------------------------------------------
# MAME_XML_PATH -> (FileName object) path of MAME XML output file.
# mame_prog_FN  -> (FileName object) path to MAME executable.
# Returns filesize -> (int) file size of output MAME.xml
#
def fs_extract_MAME_XML(PATHS, mame_prog_FN):
    (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
    log_info('fs_extract_MAME_XML() mame_prog_FN "{0}"'.format(mame_prog_FN.getPath()))
    log_debug('fs_extract_MAME_XML() mame_dir     "{0}"'.format(mame_dir))
    log_debug('fs_extract_MAME_XML() mame_exec    "{0}"'.format(mame_exec))
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher',
                   'Extracting MAME XML database. Progress bar is not accurate.')
    with open(PATHS.MAME_XML_PATH.getPath(), 'wb') as out, open(PATHS.MAME_STDERR_PATH.getPath(), 'wb') as err:
        p = subprocess.Popen([mame_prog_FN.getPath(), '-listxml'], stdout=out, stderr=err, cwd=mame_dir)
        count = 0
        while p.poll() is None:
            pDialog.update(count * 100 / 100)
            time.sleep(1)
            count = count + 1
    pDialog.close()

    # --- Check if everything OK ---
    statinfo = os.stat(PATHS.MAME_XML_PATH.getPath())
    filesize = statinfo.st_size

    # --- Count number of machines. Useful for progress dialogs ---
    log_info('fs_extract_MAME_XML() Counting number of machines...')
    total_machines = fs_count_MAME_Machines(PATHS)
    log_info('fs_extract_MAME_XML() Found {0} machines.'.format(total_machines))
    # kodi_dialog_OK('Found {0} machines in MAME.xml.'.format(total_machines))

    # -----------------------------------------------------------------------------
    # Create MAME control dictionary
    # -----------------------------------------------------------------------------
    control_dic = fs_new_control_dic()
    control_dic['total_machines'] = total_machines
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)

    return (filesize, total_machines)

# -------------------------------------------------------------------------------------------------
#
def fs_count_MAME_Machines(PATHS):
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher', 'Counting number of MAME machines...')
    pDialog.update(0)
    num_machines = 0
    with open(PATHS.MAME_XML_PATH.getPath(), 'rt') as f:
        for line in f:
            if line.decode('utf-8').find('<machine name=') > 0: num_machines = num_machines + 1
    pDialog.update(100)
    pDialog.close()

    return num_machines

# -------------------------------------------------------------------------------------------------
# Load Catver.ini/Catlist.ini/Genre.ini
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
        log_info('fs_load_Catver_ini() IOError opening "{0}"'.format(filename))
        return {}
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

def fs_load_Catlist_ini(filename):
    log_info('fs_load_Catlist_ini() Parsing "{0}"'.format(filename))
    catlist_version = 'Not found'
    catlist_dic = {}
    catlist_set = set()
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('fs_load_Catlist_ini() IOError opening "{0}"'.format(filename))
        return {}
    for file_line in f:
        stripped_line = file_line.strip()
        # Skip comments: lines starting with ';;'
        # Look for version in comments
        if re.search(r'^;;', stripped_line):
            m = re.search(r'Catlist.ini ([0-9\.]+) / ', stripped_line)
            if m: catlist_version = m.group(1)
            continue
        # Skip blanks
        if stripped_line == '': continue
        # New category
        searchObj = re.search(r'^\[(.*)\]', stripped_line)
        if searchObj:
            current_category = searchObj.group(1)
            catlist_set.add(current_category)
        else:
            machine_name = stripped_line
            catlist_dic[machine_name] = current_category
    f.close()
    log_info('fs_load_Catlist_ini() Version "{0}"'.format(catlist_version))
    log_info('fs_load_Catlist_ini() Number of machines   {0:6d}'.format(len(catlist_dic)))
    log_info('fs_load_Catlist_ini() Number of categories {0:6d}'.format(len(catlist_set)))

    return (catlist_dic, catlist_version)

def fs_load_Genre_ini(filename):
    log_info('fs_load_Genre_ini() Parsing "{0}"'.format(filename))
    genre_version = 'Not found'
    genre_dic = {}
    genre_set = set()
    try:
        f = open(filename, 'rt')
    except IOError:
        log_info('fs_load_Genre_ini() IOError opening "{0}"'.format(filename))
        return {}
    for file_line in f:
        stripped_line = file_line.strip()
        # Skip comments: lines starting with ';;'
        if re.search(r'^;;', stripped_line):
            m = re.search(r'Genre.ini ([0-9\.]+) / ', stripped_line)
            if m: genre_version = m.group(1)
            continue
        # Skip blanks
        if stripped_line == '': continue
        # New category
        searchObj = re.search(r'^\[(.*)\]', stripped_line)
        if searchObj:
            current_category = searchObj.group(1)
            genre_set.add(current_category)
        else:
            machine_name = stripped_line
            genre_dic[machine_name] = current_category
    f.close
    log_info('fs_load_Genre_ini() Version "{0}"'.format(genre_version))
    log_info('fs_load_Genre_ini() Number of machines   {0:6d}'.format(len(genre_dic)))
    log_info('fs_load_Genre_ini() Number of categories {0:6d}'.format(len(genre_set)))

    return (genre_dic, genre_version)

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
        log_info('fs_load_nplayers_ini() IOError opening "{0}"'.format(filename))
        return {}
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
    log_info('fs_load_nplayers_ini() Number of machines           {0:6d}'.format(len(categories_dic)))
    log_info('fs_load_nplayers_ini() Number of nplayer categories {0:6d}'.format(len(categories_set)))

    return (categories_dic, nplayers_version)

# -------------------------------------------------------------------------------------------------
# Saves MAIN_DB_PATH, MAIN_PCLONE_DIC_PATH, MAIN_CONTROL_PATH, MAIN_ASSETS_DB_PATH
#
STOP_AFTER_MACHINES = 100000
def fs_build_MAME_main_database(PATHS, settings, control_dic):
    # --- Load Catver.ini to include cateogory information ---
    (categories_dic, catver_version)   = fs_load_Catver_ini(settings['catver_path'])
    (catlist_dic,    catlist_version)  = fs_load_Catlist_ini(settings['catlist_path'])
    (genre_dic,      genre_version)    = fs_load_Genre_ini(settings['genre_path'])
    (nplayers_dic,   nplayers_version) = fs_load_nplayers_ini(settings['nplayers_path'])

    # --- Progress dialog ---
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher', 'Building main MAME database...')

    # ---------------------------------------------------------------------------------------------
    # Incremental Parsing approach B (from [1])
    # ---------------------------------------------------------------------------------------------
    # Do not load whole MAME XML into memory! Use an iterative parser to
    # grab only the information we want and discard the rest.
    # See http://effbot.org/zone/element-iterparse.htm [1]
    #
    log_info('fs_build_MAME_main_database() Loading "{0}"'.format(PATHS.MAME_XML_PATH.getPath()))
    context = ET.iterparse(PATHS.MAME_XML_PATH.getPath(), events=("start", "end"))
    context = iter(context)
    event, root = context.next()
    mame_version_raw = root.attrib['build']
    log_info('fs_build_MAME_main_database() MAME version is "{0}"'.format(mame_version_raw))

    # --- Process MAME XML ---
    total_machines = control_dic['total_machines']
    machines       = {}
    machine_name   = ''
    num_iteration  = 0

    processed_machines  = 0
    parent_machines     = 0
    clone_machines      = 0
    devices_machines    = 0
    BIOS_machines       = 0
    coin_machines       = 0
    nocoin_machines     = 0
    mechanical_machines = 0
    dead_machines       = 0
    Own_ROM_machines    = 0
    Merged_ROM_machines = 0
    No_ROM_machines     = 0
    Own_CHD_machines    = 0
    Merged_CHD_machines = 0
    samples_machines    = 0

    log_info('fs_build_MAME_main_database() Parsing MAME XML file ...')
    for event, elem in context:
        # --- Debug the elements we are iterating from the XML file ---
        # print('Event     {0:6s} | Elem.tag    "{1}"'.format(event, elem.tag))
        # print('                   Elem.text   "{0}"'.format(elem.text))
        # print('                   Elem.attrib "{0}"'.format(elem.attrib))

        # <machine> tag start event includes <machine> attributes
        if event == 'start' and elem.tag == 'machine':
            machine  = fs_new_machine()
            runnable = False
            num_displays = 0

            # --- Process <machine> attributes ---
            # name is #REQUIRED attribute
            if 'name' not in elem.attrib:
                log_error('name attribute not found in <machine> tag.')
                raise CriticalError('name attribute not found in <machine> tag')
            else:
                machine_name = elem.attrib['name']

            # sourcefile #IMPLIED attribute
            if 'sourcefile' not in elem.attrib:
                log_error('sourcefile attribute not found in <machine> tag.')
                raise CriticalError('sourcefile attribute not found in <machine> tag.')
            else:
                # >> Remove trailing '.cpp' from driver name
                raw_driver_name = elem.attrib['sourcefile']

                # >> In MAME 0.174 some driver end with .cpp and others with .hxx
                # if raw_driver_name[-4:] == '.cpp':
                #     driver_name = raw_driver_name[0:-4]
                # else:
                #     print('Unrecognised driver name "{0}"'.format(raw_driver_name))

                # >> Assign driver name
                machine['sourcefile'] = raw_driver_name

            # Optional, default no
            if 'isbios' not in elem.attrib:       machine['isBIOS'] = False
            else:                                 machine['isBIOS'] = True if elem.attrib['isbios'] == 'yes' else False
            if 'isdevice' not in elem.attrib:     machine['isDevice'] = False
            else:                                 machine['isDevice'] = True if elem.attrib['isdevice'] == 'yes' else False
            if 'ismechanical' not in elem.attrib: machine['isMechanical'] = False
            else:                                 machine['isMechanical'] = True if elem.attrib['ismechanical'] == 'yes' else False
            # Optional, default yes
            if 'runnable' not in elem.attrib:     runnable = True
            else:                                 runnable = False if elem.attrib['runnable'] == 'no' else True

            # cloneof is #IMPLIED attribute
            if 'cloneof' in elem.attrib:
                machine['cloneof'] = elem.attrib['cloneof']

            # romof is #IMPLIED attribute
            if 'romof' in elem.attrib:
                machine['romof'] = elem.attrib['romof']

            # sampleof is #IMPLIED attribute
            if 'sampleof' in elem.attrib:
                machine['sampleof'] = elem.attrib['sampleof']

            # >> Add catver/catlist/genre
            if machine_name in categories_dic: machine['catver']   = categories_dic[machine_name]
            else:                              machine['catver']   = '[ Not set ]'
            if machine_name in catlist_dic:    machine['catlist']  = catlist_dic[machine_name]
            else:                              machine['catlist']  = '[ Not set ]'
            if machine_name in genre_dic:      machine['genre']    = genre_dic[machine_name]
            else:                              machine['genre']    = '[ Not set ]'
            if machine_name in nplayers_dic:   machine['nplayers'] = nplayers_dic[machine_name]
            else:                              machine['nplayers'] = '[ Not set ]'

            # >> Increment number of machines
            processed_machines += 1

        elif event == 'start' and elem.tag == 'description':
            machine['description'] = unicode(elem.text)

        elif event == 'start' and elem.tag == 'year':
            machine['year'] = unicode(elem.text)

        elif event == 'start' and elem.tag == 'manufacturer':
            machine['manufacturer'] = unicode(elem.text)

        # >> Check in machine has BIOS
        # <biosset> name and description attributes are mandatory
        elif event == 'start' and elem.tag == 'biosset':
            machine['bios_name'].append(unicode(elem.attrib['name']))
            machine['bios_desc'].append(unicode(elem.attrib['description']))

        # >> Check in machine has ROMs
        # ROM is considered to be valid if sha1 has exists. Keep in mind that a machine may have
        # many ROMs, some valid, some invalid: just 1 valid ROM is enough.
        # NOTE A ROM is unique to that machine if the <rom> tag does not have the 'merge' attribute.
        #      For example, snes and snespal both have <rom> tags that point to exactly the same
        #      BIOS. However, in a split set only snes.zip ROM set exists.
        #      snes    -> <rom name="spc700.rom" size="64" crc="44bb3a40" ... >
        #      snespal -> <rom name="spc700.rom" merge="spc700.rom" size="64" crc="44bb3a40" ... >
        # In AML, hasROM actually means "machine has it own ROMs not found somewhere else".
        elif event == 'start' and elem.tag == 'rom':
            if 'sha1' in elem.attrib and 'merge' in elem.attrib:     machine['hasROMs_merged'] = True
            if 'sha1' in elem.attrib and 'merge' not in elem.attrib: machine['hasROMs']        = True

        # >> Check in machine has CHDs
        # CHD is considered valid if SHA1 hash exists only. Keep in mind that there can be multiple
        # disks per machine, some valid, some invalid: just one valid CHD is OK.
        elif event == 'start' and elem.tag == 'disk':
            # <!ATTLIST disk name CDATA #REQUIRED>
            if 'sha1' in elem.attrib and 'merge' in elem.attrib:     machine['CHDs_merged'].append(elem.attrib['name'])
            if 'sha1' in elem.attrib and 'merge' not in elem.attrib: machine['CHDs'].append(elem.attrib['name'])

        # Some machines have more than one display tag (for example aquastge has 2).
        # Other machines have no display tag (18w)
        elif event == 'start' and elem.tag == 'display':
            machine['display_tag'].append(elem.attrib['tag'])
            machine['display_type'].append(elem.attrib['type'])
            machine['display_rotate'].append(elem.attrib['rotate'])
            num_displays += 1

        # Some machines have no controls at all.
        elif event == 'start' and elem.tag == 'input':
            # coins is #IMPLIED attribute
            if 'coins' in elem.attrib:
                machine['coins'] = int(elem.attrib['coins'])
                machine['hasCoin'] = True if machine['coins'] > 0 else False

            # >> Iterate children of <input> and search for <control> tags
            for control_child in elem:
                if control_child.tag == 'control':
                    machine['control_type'].append(control_child.attrib['type'])

        elif event == 'start' and elem.tag == 'driver':
            # status is #REQUIRED attribute
            machine['driver_status'] = unicode(elem.attrib['status'])

        elif event == 'start' and elem.tag == 'softwarelist':
            # name is #REQUIRED attribute
            machine['softwarelists'].append(elem.attrib['name'])

        # >> Device tag for machines that support loading external files
        elif event == 'start' and elem.tag == 'device':
            device_type      = elem.attrib['type'] # Mandatory attribute
            device_tag       = elem.attrib['tag']       if 'tag'       in elem.attrib else ''
            device_mandatory = elem.attrib['mandatory'] if 'mandatory' in elem.attrib else ''
            device_interface = elem.attrib['interface'] if 'interface' in elem.attrib else ''
            # >> Transform device_mandatory into bool
            if device_mandatory and device_mandatory == '1': device_mandatory = True
            else:                                            device_mandatory = False

            # >> Iterate children of <device> and search for <instance> tags
            instance_tag_found = False
            i_name = i_briefname = ''
            exts_list   = []
            for device_child in elem:
                if device_child.tag == 'instance':
                    i_name      = device_child.attrib['name']
                    i_briefname = device_child.attrib['briefname']
                    instance_tag_found = True
                elif device_child.tag == 'extension':
                    exts_list.append(device_child.attrib['name'])

            # >> NOTE Some machines have no instance inside <device>, for example 2020bb
            # >>      I don't know how to launch those machines
            if not instance_tag_found:
                # log_warning('<instance> tag not found inside <device> tag (machine {0})'.format(machine_name))
                device_type = '{0} (NI)'.format(device_type)

            # >> Add device to database
            # Extensions not needed now: 'exts' : exts_list
            device_tags_dic = {'d_tag'       : device_tag,       'd_mandatory' : device_mandatory,
                               'd_interface' : device_interface, 'i_name'      : i_name,
                               'i_briefname' : i_briefname }
            machine['device_list'].append(device_type)
            machine['device_tags'].append(device_tags_dic)

        # --- <machine> tag closing. Add new machine to database ---
        elif event == 'end' and elem.tag == 'machine':
            # >> Assumption 1: isdevice = True if and only if runnable = False
            if machine['isDevice'] == runnable:
                print("Machine {0}: machine['isDevice'] == runnable".format(machine_name))
                sys.exit(10)

            # >> Are there machines with more than 1 <display> tag. Answer: YES
            # if num_displays > 1:
            #     print("Machine {0}: num_displays = {1}".format(machine_name, num_displays))
            #     sys.exit(10)

            # >> All machines with 0 displays are mechanical? NO, 24cdjuke has no screen and is not mechanical. However
            # >> 24cdjuke is a preliminary driver.
            # if num_displays == 0 and not machine['ismechanical']:
            #     print("Machine {0}: num_displays == 0 and not machine['ismechanical']".format(machine_name))
            #     sys.exit(10)

            # >> Mark dead machines. A machine is dead if Status is preliminary AND have no controls
            if machine['driver_status'] == 'preliminary' and not machine['control_type']:
                machine['isDead'] = True

            # >> Delete XML element once it has been processed
            elem.clear()

            # >> Fill machine status
            # r/R flag takes precedence over * flag
            if machine['hasROMs']: machine['status_ROM'] = '?'
            else:
                if machine['hasROMs_merged']: machine['status_ROM'] = '*'
                else:                         machine['status_ROM'] = '-'
            if machine['CHDs']: machine['status_CHD'] = '?'
            else:
                if machine['CHDs_merged']: machine['status_CHD'] = '*'
                else:                      machine['status_CHD'] = '-'
            if machine['sampleof']:      machine['status_SAM'] = '?'
            else:                        machine['status_SAM'] = '-'
            if machine['softwarelists']: machine['status_SL']  = 'L'
            else:                        machine['status_SL']  = '-'
            if machine['device_list']:
                num_dev_mandatory = 0
                for i in range(len(machine['device_list'])):
                    device = machine['device_list'][i]
                    tags   = machine['device_tags'][i]
                    if tags['d_mandatory']: 
                        machine['status_Device']  = 'D'
                        num_dev_mandatory += 1
                    else: 
                        machine['status_Device']  = 'd'
                if num_dev_mandatory > 2:
                    message = 'Machine {0} has {1} mandatory devices'.format(machine_name, num_dev_mandatory)
                    raise CriticalError(message)
            else:
                machine['status_Device']  = '-'

            # >> Compute statistics
            if machine['cloneof']:            parent_machines += 1
            else:                             clone_machines += 1
            if machine['isDevice']:           devices_machines += 1
            if machine['isBIOS']:             BIOS_machines += 1
            if machine['hasCoin']:            coin_machines += 1
            else:                             nocoin_machines += 1
            if machine['isMechanical']:       mechanical_machines += 1            
            if machine['isDead']:             dead_machines += 1
            if machine['hasROMs']:            Own_ROM_machines += 1
            else:
                if machine['hasROMs_merged']: Merged_ROM_machines += 1
                else:                         No_ROM_machines += 1
            if machine['CHDs']:               Own_CHD_machines += 1
            elif machine['CHDs_merged']:      Merged_CHD_machines += 1
            if machine['sampleof']:           samples_machines += 1

            # >> Add new machine
            machines[machine_name] = machine

        # --- Print something to prove we are doing stuff ---
        num_iteration += 1
        if num_iteration % 1000 == 0:
            update_number = (float(processed_machines) / float(total_machines)) * 100
            pDialog.update(int(update_number))
            # log_debug('Processed {0:10d} events ({1:6d} machines so far) ...'.format(num_iteration, processed_machines))
            # log_debug('processed_machines   = {0}'.format(processed_machines))
            # log_debug('total_machines = {0}'.format(total_machines))
            # log_debug('Update number  = {0}'.format(update_number))

        # --- Stop after STOP_AFTER_MACHINES machines have been processed for debug ---
        if processed_machines >= STOP_AFTER_MACHINES: break
    pDialog.update(100)
    pDialog.close()
    log_info('Processed {0} MAME XML events'.format(num_iteration))
    log_info('Processed machines {0}'.format(processed_machines))
    log_info('Parents            {0}'.format(parent_machines))
    log_info('Clones             {0}'.format(clone_machines))
    log_info('Dead machines      {0}'.format(dead_machines))

    # -----------------------------------------------------------------------------
    # Main parent-clone list
    # -----------------------------------------------------------------------------
    # Create a couple of data struct for quickly know the parent of a clone game and
    # all clones of a parent.
    #
    # main_pclone_dic          = { 'parent_name' : ['clone_name', 'clone_name', ... ] , ... }
    # main_clone_to_parent_dic = { 'clone_name' : 'parent_name', ... }
    log_info('Making PClone list...')
    main_pclone_dic = {}
    main_clone_to_parent_dic = {}
    for machine_name in machines:
        machine = machines[machine_name]
        # >> Exclude devices
        if machine['isDevice']: continue

        # >> Machine is a clone
        if machine['cloneof']:
            # >> Add clone machine to main_clone_to_parent_dic
            parent_name = machine['cloneof']
            main_clone_to_parent_dic[machine_name] = parent_name
            # >> If parent already in main_pclone_dic then add clone to parent list.
            # >> If parent not there, then add parent first and then add clone.
            if parent_name in main_pclone_dic:
                main_pclone_dic[parent_name].append(machine_name)
            else:
                main_pclone_dic[parent_name] = []
                main_pclone_dic[parent_name].append(machine_name)
        # >> Machine is a parent. Add to main_pclone_dic if not already there.
        else:
            if machine_name not in main_pclone_dic: main_pclone_dic[machine_name] = []

    # -----------------------------------------------------------------------------
    # Make empty asset list
    # -----------------------------------------------------------------------------
    assets_dic = {}
    for key in machines: assets_dic[key] = fs_new_MAME_asset()

    # -----------------------------------------------------------------------------
    # Update MAME control dictionary
    # -----------------------------------------------------------------------------
    control_dic['mame_version']        = mame_version_raw
    control_dic['catver_version']      = catver_version
    control_dic['catlist_version']     = catlist_version
    control_dic['genre_version']       = genre_version
    control_dic['nplayers_version']    = nplayers_version
    # >> Statistics
    control_dic['processed_machines']  = processed_machines
    control_dic['parent_machines']     = parent_machines
    control_dic['clone_machines']      = clone_machines
    control_dic['devices_machines']    = devices_machines
    control_dic['BIOS_machines']       = BIOS_machines    
    control_dic['coin_machines']       = coin_machines
    control_dic['nocoin_machines']     = nocoin_machines
    control_dic['mechanical_machines'] = mechanical_machines
    control_dic['dead_machines']       = dead_machines
    control_dic['Own_ROM_machines']    = Own_ROM_machines    
    control_dic['Merged_ROM_machines'] = Merged_ROM_machines
    control_dic['No_ROM_machines']     = No_ROM_machines
    control_dic['Own_CHD_machines']    = Own_CHD_machines    
    control_dic['Merged_CHD_machines'] = Merged_CHD_machines
    control_dic['samples_machines']    = samples_machines

    # -----------------------------------------------------------------------------
    # Now write simplified JSON
    # -----------------------------------------------------------------------------
    kodi_busydialog_ON()
    fs_write_JSON_file(PATHS.MAIN_DB_PATH.getPath(), machines)
    fs_write_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath(), main_pclone_dic)
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
    fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
    kodi_busydialog_OFF()

def fs_build_MAME_catalogs(PATHS, machines, main_pclone_dic):
    # >> Progress dialog
    NUM_CATALOGS = len(CATALOG_NAME_LIST)
    pDialog_line1 = 'Building catalogs ...'
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Advanced MAME Launcher', pDialog_line1)
    processed_filters = 0
    update_number = 0

    # None catalog --------------------------------------------------------------------------------
    # --- Main machine list ---
    # Machines with Coin Slot and Non Mechanical and not Dead
    none_catalog_parents = {}
    none_catalog_all = {}
    log_info('Making None catalog - Coin index ...')
    parent_list = []
    all_list = []
    pDialog.update(update_number, pDialog_line1, 'Making None Catalog ...')
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if machine['isMechanical']: continue
        if not machine['hasCoin']: continue
        if machine['isDead']: continue
        # >> Add parent to parent list
        parent_list.append(parent_name)
        # >> Add parent and clones to all list
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['Machines'] = {'parents'  : parent_list, 'num_parents'  : len(parent_list)}
    none_catalog_all['Machines']     = {'machines' : all_list,    'num_machines' : len(all_list)}

    # --- NoCoin list ---
    # A) Machines with No Coin Slot and Non Mechanical and not Dead
    log_info('Making NoCoin index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if machine['isMechanical']: continue
        if machine['hasCoin']: continue
        if machine['isDead']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['NoCoin'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['NoCoin']     = {'machines' : all_list,    'num_machines' : len(all_list)}

    # --- Mechanical machines ---
    # A) Mechanical Machines and not Dead
    log_info('Making Mechanical index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['isMechanical']: continue
        if machine['isDead']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['Mechanical'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['Mechanical']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- Dead machines ---
    log_info('Making Dead Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['isDead']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['Dead'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['Dead']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- No ROMs machines ---
    log_info('Making No-ROMs Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if machine['hasROMs'] or machine['hasROMs_merged']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['NoROMs'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['NoROMs']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- CHD machines ---
    log_info('Making CHD Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['CHDs'] and not machine['CHDs_merged']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['CHDs'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['CHDs']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- Machines with samples ---
    log_info('Making Samples Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['sampleof']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['Samples'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['Samples']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- BIOS ---
    log_info('Making BIOS Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['isBIOS']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['BIOS'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['BIOS']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    
    # --- Devices ---
    log_info('Making Devices Machines index ...')
    parent_list = []
    all_list = []
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        if not machine['isDevice']: continue
        parent_list.append(parent_name)
        all_list.append(parent_name)
        for clone in main_pclone_dic[parent_name]: all_list.append(clone)
    none_catalog_parents['Devices'] = {'parents' : parent_list, 'num_parents' : len(parent_list)}
    none_catalog_all['Devices']     = {'machines' : all_list,    'num_machines' : len(all_list)}
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # >> Save None catalog JSON file
    fs_write_JSON_file(PATHS.CATALOG_NONE_PARENT_PATH.getPath(), none_catalog_parents)
    fs_write_JSON_file(PATHS.CATALOG_NONE_ALL_PATH.getPath(), none_catalog_all)

    # Cataloged machine lists ---------------------------------------------------------------------
    # --- Catver catalog ---
    log_info('Making Catver catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Catver catalog ...')
    catver_catalog_parents = {}
    catver_catalog_all = {}
    for parent_name in main_pclone_dic:
        catalog_key = machines[parent_name]['catver']
        if catalog_key in catver_catalog_parents:
            catver_catalog_parents[catalog_key]['parents'].append(parent_name)
            catver_catalog_parents[catalog_key]['num_parents'] = len(catver_catalog_parents[catalog_key]['parents'])

            catver_catalog_all[catalog_key]['machines'].append(parent_name)
            for clone in main_pclone_dic[parent_name]: catver_catalog_all[catalog_key]['machines'].append(clone)
            catver_catalog_all[catalog_key]['num_machines'] = len(catver_catalog_all[catalog_key]['machines'])
        else:
            catver_catalog_parents[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
            all_list = [parent_name]
            for clone in main_pclone_dic[parent_name]: all_list.append(clone)
            catver_catalog_all[catalog_key] = {'machines' : all_list, 'num_machines' : len(all_list)}
    fs_write_JSON_file(PATHS.CATALOG_CATVER_PARENT_PATH.getPath(), catver_catalog_parents)
    fs_write_JSON_file(PATHS.CATALOG_CATVER_ALL_PATH.getPath(), catver_catalog_all)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Catlist catalog ---
    log_info('Making Catlist catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Catlist catalog ...')
    catlist_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['catlist']
        if catalog_key in catlist_catalog:
            catlist_catalog[catalog_key]['parents'].append(parent_name)
            catlist_catalog[catalog_key]['num_parents'] = len(catlist_catalog[catalog_key]['parents'])
        else:
            catlist_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_CATLIST_PATH.getPath(), catlist_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Genre catalog ---
    log_info('Making Genre catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Genre catalog ...')
    genre_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['genre']
        if catalog_key in genre_catalog:
            genre_catalog[catalog_key]['parents'].append(parent_name)
            genre_catalog[catalog_key]['num_parents'] = len(genre_catalog[catalog_key]['parents'])
        else:
            genre_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_GENRE_PATH.getPath(), genre_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Nplayers catalog ---
    log_info('Making Nplayers catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Nplayers catalog ...')
    nplayers_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['nplayers']
        if catalog_key in nplayers_catalog:
            nplayers_catalog[catalog_key]['parents'].append(parent_name)
            nplayers_catalog[catalog_key]['num_parents'] = len(nplayers_catalog[catalog_key]['parents'])
        else:
            nplayers_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_NPLAYERS_PATH.getPath(), nplayers_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Manufacturer catalog ---
    log_info('Making Manufacturer catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Manufacturer catalog ...')
    manufacturer_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['manufacturer']
        if catalog_key in manufacturer_catalog:
            manufacturer_catalog[catalog_key]['parents'].append(parent_name)
            manufacturer_catalog[catalog_key]['num_parents'] = len(manufacturer_catalog[catalog_key]['parents'])
        else:
            manufacturer_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_MANUFACTURER_PATH.getPath(), manufacturer_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Year catalog ---
    log_info('Making Year catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Year catalog ...')
    year_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['year']
        if catalog_key in year_catalog:
            year_catalog[catalog_key]['parents'].append(parent_name)
            year_catalog[catalog_key]['num_parents'] = len(year_catalog[catalog_key]['parents'])
        else:
            year_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_YEAR_PATH.getPath(), year_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Driver catalog ---
    log_info('Making Driver catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Driver catalog ...')
    # >> Substitute notable drivers with a proper name
    driver_name_dic = {
        'cps1.cpp'     : 'Capcom Play System 1',
        'cps2.cpp'     : 'Capcom Play System 2',
        'cps3.cpp'     : 'Capcom Play System 3',
        'galaxian.cpp' : 'Namco Galaxian-derived hardware',
        'model2.cpp'   : 'Sega Model 2',
        'namcops2.cpp' : 'Namco System 246 / System 256 (Sony PS2 based)',
        'naomi.cpp'    : 'Sega Naomi / Naomi 2',
        'neodriv.hxx'  : 'SNK NeoGeo',
        'seta.cpp'     : 'Seta Hardware',
        'segas16b.cpp' : 'Sega System 16B',
        'system1.cpp'  : 'System1 / System 2',
        'taito_f3.cpp' : 'Taito F3 System',
        'taito_f2.cpp' : 'Taito F2 System',
        'zn.cpp'       : 'Sony ZN1/ZN2 (Arcade PSX)',
    }
    driver_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = machine['sourcefile']
        if catalog_key in driver_name_dic: catalog_key = driver_name_dic[catalog_key]
        if catalog_key in driver_catalog:
            driver_catalog[catalog_key]['parents'].append(parent_name)
            driver_catalog[catalog_key]['num_parents'] = len(driver_catalog[catalog_key]['parents'])
        else:
            driver_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_DRIVER_PATH.getPath(), driver_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Control catalog ---
    log_info('Making Control catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Control catalog ...')
    control_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        # >> Order alphabetically the list
        pretty_control_type_list = fs_improve_control_type_list(machine['control_type'])
        sorted_control_type_list = sorted(pretty_control_type_list)
        sorted_control_type_list = fs_compress_item_list(sorted_control_type_list)
        catalog_key = " / ".join(sorted_control_type_list)
        # >> Change category name for machines with no controls
        if catalog_key == '': catalog_key = '[ No controls ]'
        if catalog_key in control_catalog:
            control_catalog[catalog_key]['parents'].append(parent_name)
            control_catalog[catalog_key]['num_parents'] = len(control_catalog[catalog_key]['parents'])
        else:
            control_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_CONTROL_PATH.getPath(), control_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Display tag catalog ---
    log_info('Making Display tag catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Display tag catalog ...')
    display_tag_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = " / ".join(machine['display_tag'])
        # >> Change category name for machines with no display
        if catalog_key == '': catalog_key = '[ No display ]'
        if catalog_key in display_tag_catalog:
            display_tag_catalog[catalog_key]['parents'].append(parent_name)
            display_tag_catalog[catalog_key]['num_parents'] = len(display_tag_catalog[catalog_key]['parents'])
        else:
            display_tag_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_DISPLAY_TAG_PATH.getPath(), display_tag_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Display type catalog ---
    log_info('Making Display type catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Display type catalog ...')
    display_type_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = " / ".join(machine['display_type'])
        # >> Change category name for machines with no display
        if catalog_key == '': catalog_key = '[ No display ]'
        if catalog_key in display_type_catalog:
            display_type_catalog[catalog_key]['parents'].append(parent_name)
            display_type_catalog[catalog_key]['num_parents'] = len(display_type_catalog[catalog_key]['parents'])
        else:
            display_type_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_DISPLAY_TYPE_PATH.getPath(), display_type_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Display rotate catalog ---
    log_info('Making Display rotate catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Display rotate catalog ...')
    display_rotate_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        catalog_key = " / ".join(machine['display_rotate'])
        # >> Change category name for machines with no display
        if catalog_key == '': catalog_key = '[ No display ]'
        if catalog_key in display_rotate_catalog:
            display_rotate_catalog[catalog_key]['parents'].append(parent_name)
            display_rotate_catalog[catalog_key]['num_parents'] = len(display_rotate_catalog[catalog_key]['parents'])
        else:
            display_rotate_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_DISPLAY_ROTATE_PATH.getPath(), display_rotate_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- <device> catalog ---
    log_info('Making <device> catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making <device> catalog ...')
    device_list_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        # >> Order alphabetically the list
        pretty_device_list = fs_improve_device_list(machine['device_list'])
        sorted_device_list = sorted(pretty_device_list)
        sorted_device_list = fs_compress_item_list(sorted_device_list)
        catalog_key = " / ".join(sorted_device_list)
        # >> Change category name for machines with no devices
        if catalog_key == '': catalog_key = '[ No devices ]'
        if catalog_key in device_list_catalog:
            device_list_catalog[catalog_key]['parents'].append(parent_name)
            device_list_catalog[catalog_key]['num_parents'] = len(device_list_catalog[catalog_key]['parents'])
        else:
            device_list_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_DEVICE_LIST_PATH.getPath(), device_list_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)

    # --- Software List catalog ---
    log_info('Making Software List catalog ...')
    pDialog.update(update_number, pDialog_line1, 'Making Software List catalog ...')
    SL_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        # >> A machine may have more than 1 software lists
        for sl_name in machine['softwarelists']:
            catalog_key = sl_name
            if catalog_key in SL_catalog:
                SL_catalog[catalog_key]['parents'].append(parent_name)
                SL_catalog[catalog_key]['num_parents'] = len(SL_catalog[catalog_key]['parents'])
            else:
                SL_catalog[catalog_key] = {'parents' : [parent_name], 'num_parents' : 1}
    fs_write_JSON_file(PATHS.CATALOG_SL_PATH.getPath(), SL_catalog)
    processed_filters += 1
    update_number = int((float(processed_filters) / float(NUM_CATALOGS)) * 100)
    pDialog.update(update_number)
    pDialog.close()

    # --- Create properties database with default values ---
    # >> Now overwrites all properties when the catalog is rebuilt.
    #    New versions must kept user set properties!
    mame_properties_dic = {}
    for catalog_name in CATALOG_NAME_LIST:
        # >> Get categories for this catalog name
        catalog_dic = fs_get_cataloged_dic_parents(PATHS, catalog_name)
        for category_name in sorted(catalog_dic):
            prop_key = '{0} - {1}'.format(catalog_name, category_name)
            mame_properties_dic[prop_key] = {'vm' : VIEW_MODE_NORMAL}
    fs_write_JSON_file(PATHS.MAIN_PROPERTIES_PATH.getPath(), mame_properties_dic)
    log_info('mame_properties_dic has {0} entries'.format(len(mame_properties_dic)))

#
# A) Capitalise every list item
# B) Substitute Only_buttons -> Only buttons
#
def fs_improve_control_type_list(control_type_list):
    out_list = []
    for control_str in control_type_list:
        capital_str = control_str.title()
        if capital_str == 'Only_Buttons': capital_str = 'Only Buttons'
        out_list.append(capital_str)

    return out_list

#
# A) Capitalise every list item
#
def fs_improve_device_list(control_type_list):
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
def fs_compress_item_list(item_list):
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
#
class SLData:
    def __init__(self):
        self.roms = {}
        self.display_name = ''
        self.num_roms = 0
        self.num_CHDs = 0

def fs_load_SL_XML(xml_filename):
    __debug_xml_parser = False
    ret_obj = SLData()

    # --- If file does not exist return empty dictionary ---
    if not os.path.isfile(xml_filename): return ret_obj

    # --- Parse using cElementTree ---
    log_debug('fs_load_SL_XML() Loading XML file "{0}"'.format(xml_filename))
    # If XML has errors (invalid characters, etc.) this will rais exception 'err'
    try:
        xml_tree = ET.parse(xml_filename)
    except:
        return ret_obj
    xml_root = xml_tree.getroot()
    ret_obj.display_name = xml_root.attrib['description']
    for root_element in xml_root:
        if __debug_xml_parser: print('Root child {0}'.format(root_element.tag))

        if root_element.tag == 'software':
            rom = fs_new_SL_ROM()
            num_roms = 0
            rom_name = root_element.attrib['name']
            if 'cloneof' in root_element.attrib: rom['cloneof'] = root_element.attrib['cloneof']
            if 'romof' in root_element.attrib:
                log_error('{0} -> "romof" in root_element.attrib'.format(rom_name))
                raise CriticalError('DEBUG')

            for rom_child in root_element:
                # >> By default read strings
                xml_text = rom_child.text if rom_child.text is not None else ''
                xml_tag  = rom_child.tag
                if __debug_xml_parser: print('{0} --> {1}'.format(xml_tag, xml_text))

                # --- Only pick tags we want ---
                if xml_tag == 'description' or xml_tag == 'year' or xml_tag == 'publisher':
                    rom[xml_tag] = xml_text
                elif xml_tag == 'part':
                    # Example 1: 32x.xml-chaotix
                    # Stored as: SL_ROMS/32x/chaotix.zip
                    # <part name="cart" interface="_32x_cart">
                    #   <dataarea name="rom" size="3145728">
                    #     <rom name="knuckles' chaotix (europe).bin" size="3145728" crc="41d63572" sha1="5c1...922" offset="000000" />
                    #   </dataarea>
                    # </part>
                    #
                    # Example 2: 32x.xml-doom
                    # Stored as: SL_ROMS/32x/doom.zip
                    # <part name="cart" interface="_32x_cart">
                    #   <feature name="pcb" value="171-6885A" />
                    #   <dataarea name="rom" size="3145728">
                    #     <rom name="mpr-17351-f.ic1" size="2097152" crc="e0ef6ebc" sha1="302...79d" offset="000000" />
                    #     <rom name="mpr-17352-f.ic2" size="1048576" crc="c7079709" sha1="0f2...33b" offset="0x200000" />
                    #   </dataarea>
                    # </part>
                    #
                    # Example 3: a800.xml-diamond3
                    # Stored as: SL_ROMS/a800/diamond3.zip (all ROMs from all parts)
                    # <part name="cart" interface="a8bit_cart">
                    #   <feature name="slot" value="a800_diamond" />
                    #   <dataarea name="rom" size="65536">
                    #     <rom name="diamond gos v3.0.rom" size="65536" crc="0ead07f8" sha1="e92...730" offset="0" />
                    #   </dataarea>
                    # </part>
                    # <part name="flop1" interface="floppy_5_25">
                    #   <dataarea name="flop" size="92176">
                    #     <rom name="diamond paint.atr" size="92176" crc="d2994282" sha1="be8...287" offset="0" />
                    #   </dataarea>
                    # </part>
                    # <part name="flop2" interface="floppy_5_25">
                    #   <dataarea name="flop" size="92176">
                    #     <rom name="diamond write.atr" size="92176" crc="e1e5b235" sha1="c3c...db5" offset="0" />
                    #   </dataarea>
                    # </part>
                    # <part name="flop3" interface="floppy_5_25">
                    #   <dataarea name="flop" size="92176">
                    #     <rom name="diamond utilities.atr" size="92176" crc="bb48082d" sha1="eb7...4e4" offset="0" />
                    #   </dataarea>
                    # </part>
                    #
                    # Example 4: a2600.xml-harmbios
                    # Stored as: SL_ROMS/a2600/harmbios.zip (all ROMs from all dataareas)
                    # <part name="cart" interface="a2600_cart">
                    #   <feature name="slot" value="a26_harmony" />
                    #   <dataarea name="rom" size="0x8000">
                    #     <rom name="bios_updater_NTSC.cu" size="0x8000" crc="03153eb2" sha1="cd9...009" offset="0" />
                    #   </dataarea>
                    #   <dataarea name="bios" size="0x21400">
                    #     <rom name="hbios_106_NTSC_official_beta.bin" size="0x21400" crc="1e1d237b" sha1="8fd...1da" offset="0" />
                    #     <rom name="hbios_106_NTSC_beta_2.bin"        size="0x21400" crc="807b86bd" sha1="633...e9d" offset="0" />
                    #     <rom name="eeloader_104e_PAL60.bin" size="0x36f8" crc="58845532" sha1="255...71c" offset="0" />
                    #   </dataarea>
                    # </part>
                    #
                    # Example 5: psx.xml-traid
                    # Stored as: SL_CHDS/psx/traid/tomb raider (usa) (v1.6).chd
                    # <part name="cdrom" interface="psx_cdrom">
                    #   <diskarea name="cdrom">
                    #     <disk name="tomb raider (usa) (v1.6)" sha1="697...3ac"/>
                    #   </diskarea>
                    # </part>
                    #
                    # Example 6: psx.xml-traida cloneof=traid
                    # <part name="cdrom" interface="psx_cdrom">
                    #   <diskarea name="cdrom">
                    #     <disk name="tomb raider (usa) (v1.5)" sha1="d48...0a9"/>
                    #   </diskarea>
                    # </part>
                    #
                    # Example 7: pico.xml-sanouk5
                    # Stored as: SL_ROMS/pico/sanouk5.zip (mpr-18458-t.ic1 ROM)
                    # Stored as: SL_CHDS/pico/sanouk5/imgpico-001.chd
                    # <part name="cart" interface="pico_cart">
                    #   <dataarea name="rom" size="524288">
                    #     <rom name="mpr-18458-t.ic1" size="524288" crc="6340c18a" sha1="101...58a" offset="000000" loadflag="load16_word_swap" />
                    #   </dataarea>
                    #   <diskarea name="cdrom">
                    #     <disk name="imgpico-001" sha1="c93...10d" />
                    #   </diskarea>
                    # </part>
                    rom['part_name'].append(rom_child.attrib['name'])
                    rom['part_interface'].append(rom_child.attrib['interface'])

                    # --- Count number of <dataarea> and <diskarea> tags inside this <part tag> ---
                    num_dataarea = num_diskarea = 0
                    dataarea_num_roms = []
                    for part_child in rom_child:
                        if part_child.tag == 'dataarea':
                            # >> Dataarea is valid ONLY if it contains valid ROMs
                            dataarea_num_roms = 0
                            for dataarea_child in part_child:
                                if dataarea_child.tag == 'rom' and 'sha1' in dataarea_child.attrib:
                                    dataarea_num_roms += 1
                                    num_roms += 1
                            if dataarea_num_roms > 0: num_dataarea += 1
                        elif part_child.tag == 'diskarea':
                            # >> Dataarea is valid ONLY if it contains valid ROMs
                            diskarea_num_disks = 0
                            for dataarea_child in part_child:
                                if dataarea_child.tag == 'disk' and 'sha1' in dataarea_child.attrib:
                                    diskarea_num_disks += 1
                                    rom['CHDs'].append(dataarea_child.attrib['name'])
                            if diskarea_num_disks > 0: num_diskarea += 1
                        elif part_child.tag == 'feature':
                            pass
                        elif part_child.tag == 'dipswitch':
                            pass
                        else:
                            log_error('{0} -> Inside <part>, unrecognised tag <{0}>'.format(rom_name, part_child.tag))
                            raise CriticalError('DEBUG')
                    # if num_dataarea > 1:
                    #     log_error('{0} -> num_dataarea = {1}'.format(rom_name, num_dataarea))
                    #     raise CriticalError('DEBUG')
                    # if num_diskarea > 1:
                    #     log_error('{0} -> num_diskarea = {1}'.format(rom_name, num_diskarea))
                    #     raise CriticalError('DEBUG')
                    # if num_dataarea and num_diskarea:
                    #     log_error('{0} -> num_dataarea = {1}'.format(rom_name, num_dataarea))
                    #     log_error('{0} -> num_diskarea = {1}'.format(rom_name, num_diskarea))
                    #     raise CriticalError('DEBUG')

            # >> If ROM has more than 1 ROM increase number of total ROMs (ZIP files).
            # >> If ROM has CHDs count the CHDs.
            rom['num_roms'] = num_roms

            if rom['num_roms']: rom['status_ROM'] = '?'
            else:               rom['status_ROM'] = '-'
            if rom['CHDs']:     rom['status_CHD'] = '?'
            else:               rom['status_CHD'] = '-'

            # >> Statistics
            if rom['CHDs']:     ret_obj.num_CHDs += len(rom['CHDs'])
            if rom['num_roms']: ret_obj.num_roms += 1

            # >> Add ROM to database
            ret_obj.roms[rom_name] = rom

    return ret_obj

# -------------------------------------------------------------------------------------------------
# SL_catalog = { 'name' : {'display_name': u'', 'rom_count' : int, 'rom_DB_noext' : u'' }, ...}
#
# Saves SL_INDEX_PATH, SL_MACHINES_PATH, CATALOG_SL_PATH, MAIN_CONTROL_PATH, SL JSON files.
#
def fs_build_SoftwareLists_index(PATHS, settings, machines, main_pclone_dic, control_dic):
    SL_dir_FN = FileName(settings['SL_hash_path'])
    log_debug('fs_build_SoftwareLists_index() SL_dir_FN "{0}"'.format(SL_dir_FN.getPath()))

    # --- Scan all XML files in Software Lists directory and save DB ---
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pdialog_line1 = 'Building Sofware Lists indices/catalogs ...'
    pDialog.create('Advanced MAME Launcher', pdialog_line1)
    SL_file_list = SL_dir_FN.scanFilesInPath('*.xml')
    total_files = len(SL_file_list)
    processed_files = num_SL_ROMs = num_SL_CHDs = 0
    SL_catalog_dic = {}
    for file in SL_file_list:
        # log_debug('fs_build_SoftwareLists_index() Processing "{0}"'.format(file))
        FN = FileName(file)

        # >> Open software list XML and parse it. Then, save data fields we want in JSON.
        SL_path_FN = FileName(file)
        SL_obj = fs_load_SL_XML(SL_path_FN.getPath())
        output_FN = PATHS.SL_DB_DIR.pjoin(FN.getBase_noext() + '.json')
        fs_write_JSON_file(output_FN.getPath(), SL_obj.roms)
        
        # >> Add software list to catalog
        num_SL_ROMs += SL_obj.num_roms
        num_SL_CHDs += SL_obj.num_CHDs
        SL = {'display_name' : SL_obj.display_name, 
              'rom_count'    : SL_obj.num_roms,
              'chd_count'    : SL_obj.num_CHDs,
              'rom_DB_noext' : FN.getBase_noext()
        }
        SL_catalog_dic[FN.getBase_noext()] = SL

        # >> Update progress
        processed_files += 1
        pDialog.update(100 * processed_files / total_files, pdialog_line1, 'File {0} ...'.format(FN.getBase()))
    fs_write_JSON_file(PATHS.SL_INDEX_PATH.getPath(), SL_catalog_dic)

    # --- Make SL Parent/Clone DB ---
    SL_PClone_dic = {}
    for sl_name in SL_catalog_dic:
        pclone_dic = {}
        SL_database_FN = PATHS.SL_DB_DIR.pjoin(sl_name + '.json')
        ROMs = fs_load_JSON_file(SL_database_FN.getPath())
        for rom_name in ROMs:
            ROM = ROMs[rom_name]
            if ROM['cloneof'] == '' and rom_name not in pclone_dic:
                pclone_dic[rom_name] = []
            else:
                parent_name = machine['cloneof']
                if parent_name in pclone_dic: pclone_dic[parent_name].append(rom_name)
                else:                         pclone_dic[parent_name] = list(rom_name)
        SL_PClone_dic[sl_name] = pclone_dic
    fs_write_JSON_file(PATHS.SL_PCLONE_DIC_PATH.getPath(), SL_PClone_dic)

    # --- Make SL properties DB ---
    # >> Allows customisation of every SL list window
    SL_properties_dic = {}
    for sl_name in SL_catalog_dic:
        # 'view_mode' : VIEW_MODE_NORMAL or VIEW_MODE_PCLONE
        prop_dic = {'view_mode' : VIEW_MODE_NORMAL}
        SL_properties_dic[sl_name] = prop_dic
    fs_write_JSON_file(PATHS.SL_MACHINES_PROP_PATH.getPath(), SL_properties_dic)

    # --- Make a list of machines that can launch each SL ---
    log_info('Making Software List machine list ...')
    pdialog_line1 = 'Rebuilding Software List machine list ...'
    pDialog.update(0, pdialog_line1)
    total_SL = len(SL_catalog_dic)
    processed_SL = 0
    SL_machines_dic = {}
    # Revise this algortihm! I think is not working well...
    for SL_name in SL_catalog_dic:
        SL_machine_list = []
        for machine_name, machine_dic in machines.iteritems():
            if not machine_dic['softwarelists']: continue
            for machine_SL_name in machine_dic['softwarelists']:
                if machine_SL_name == SL_name:
                    SL_machine_dic = {'machine'     : machine_name,
                                      'description' : machine_dic['description'],
                                      'device_tags' : machine_dic['device_tags']}
                    SL_machine_list.append(SL_machine_dic)
        SL_machines_dic[SL_name] = SL_machine_list

        # >> Update progress
        processed_SL += 1
        pDialog.update(100 * processed_SL / total_SL, pdialog_line1, 'SL {0} ...'.format(SL_name))
    fs_write_JSON_file(PATHS.SL_MACHINES_PATH.getPath(), SL_machines_dic)

    # --- Rebuild Machine by Software List catalog with knowledge of the SL proper name ---
    log_info('Making Software List catalog ...')
    pDialog.update(0, 'Rebuilding Software List catalog ...')
    SL_catalog = {}
    for parent_name in main_pclone_dic:
        machine = machines[parent_name]
        # >> A machine may have more than 1 software lists
        for sl_name in machine['softwarelists']:
            if sl_name in SL_catalog_dic: sl_name = SL_catalog_dic[sl_name]['display_name']
            catalog_key = sl_name
            if catalog_key in SL_catalog:
                SL_catalog[catalog_key]['machines'].append(parent_name)
                SL_catalog[catalog_key]['num_machines'] = len(SL_catalog[catalog_key]['machines'])
            else:
                SL_catalog[catalog_key] = {'num_machines' : 1, 'machines' : [parent_name]}
    pDialog.update(100)
    fs_write_JSON_file(PATHS.CATALOG_SL_PATH.getPath(), SL_catalog)
    pDialog.close()

    # --- SL statistics and save control_dic ---
    control_dic['num_SL_files'] = processed_files
    control_dic['num_SL_ROMs']  = num_SL_ROMs
    control_dic['num_SL_CHDs']  = num_SL_CHDs
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)

# -------------------------------------------------------------------------------------------------
# Does not save any file. machines and control_dic modified by assigment
#
def fs_scan_MAME_ROMs(PATHS, machines, control_dic, ROM_path_FN, CHD_path_FN, Samples_path_FN, scan_CHDs, scan_Samples):
    # >> Scan ROMs
    log_info('Opening ROMs report file "{0}"'.format(PATHS.REPORT_MAME_SCAN_ROMS_PATH.getPath()))
    file = open(PATHS.REPORT_MAME_SCAN_ROMS_PATH.getPath(), 'w')
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher', 'Scanning MAME ROMs...')
    total_machines = len(machines)
    processed_machines = 0
    ROMs_have = ROMs_missing = ROMs_total = 0
    for key in sorted(machines):
        machine = machines[key]
        # log_info('_command_setup_plugin() Checking machine {0}'.format(key))
        if machine['hasROMs']:
            ROMs_total += 1
            # >> Machine has ROM. Get ROM filename and check if file exist
            ROM_FN = ROM_path_FN.pjoin(key + '.zip')
            if ROM_FN.exists():
                machine['status_ROM'] = 'R'
                ROMs_have += 1
            else:
                machine['status_ROM'] = 'r'
                ROMs_missing += 1
                file.write('Missing ROM {0}\n'.format(ROM_FN.getPath()))
        else:
            if machine['hasROMs_merged']: machine['status_ROM'] = '*'
            else:                         machine['status_ROM'] = '-'

        # >> Progress dialog
        processed_machines = processed_machines + 1
        pDialog.update(100 * processed_machines / total_machines)
    pDialog.close()
    file.close()

    # >> Scan CHDs
    log_info('Opening CHDs report file "{0}"'.format(PATHS.REPORT_MAME_SCAN_CHDS_PATH.getPath()))
    file = open(PATHS.REPORT_MAME_SCAN_CHDS_PATH.getPath(), 'w')
    CHDs_have = CHDs_missing = CHDs_total = 0
    for key in sorted(machines):
        machine = machines[key]
        if machine['CHDs']:
            CHDs_total += len(machine['CHDs'])
            if scan_CHDs:
                hasOwnCHD_list = [False] * len(machine['CHDs'])
                for idx, CHD_name in enumerate(machine['CHDs']):
                    CHD_FN = CHD_path_FN.pjoin(key).pjoin(CHD_name + '.chd')
                    # log_debug('Testing CHD OP "{0}"'.format(CHD_FN.getOriginalPath()))
                    if CHD_FN.exists():
                        hasOwnCHD_list[idx] = True
                        CHDs_have += 1
                    else:
                        file.write('Missing CHD {0}\n'.format(CHD_FN.getPath()))
                        CHDs_missing += 1
                if all(hasOwnCHD_list): machine['status_CHD'] = 'C'
                else:                   machine['status_CHD'] = 'c'
            else:
                machine['status_CHD'] = 'c'
                CHDs_missing += len(machine['CHDs'])
        else:
            if machine['CHDs_merged']: machine['status_CHD'] = '*'
            else:                      machine['status_CHD'] = '-'
    file.close()

    # >> Scan Samples
    log_info('Opening Samples report file "{0}"'.format(PATHS.REPORT_MAME_SCAN_SAMP_PATH.getPath()))
    file = open(PATHS.REPORT_MAME_SCAN_SAMP_PATH.getPath(), 'w')
    Samples_have = Samples_missing = Samples_total = 0
    for key in sorted(machines):
        machine = machines[key]
        if machine['sampleof']:
            Samples_total += 1
            if scan_Samples:
                Sample_FN = Samples_path_FN.pjoin(key + '.zip')
                # log_debug('Testing Sample OP "{0}"'.format(Sample_FN.getOriginalPath()))
                if Sample_FN.exists():
                    machine['status_SAM'] = 'S'
                    Samples_have += 1
                else:
                    machine['status_SAM'] = 's'
                    Samples_missing += 1
                    file.write('Missing Sample {0}\n'.format(Sample_FN.getPath()))
            else:
                machine['status_SAM'] = 's'
                Samples_missing += 1
        else:
            machine['status_SAM'] = '-'
    file.close()    

    # >> Update statistics
    control_dic['ROMs_have']       = ROMs_have
    control_dic['ROMs_missing']    = ROMs_missing
    control_dic['ROMs_total']      = ROMs_total
    control_dic['CHDs_have']       = CHDs_have
    control_dic['CHDs_missing']    = CHDs_missing
    control_dic['CHDs_total']      = CHDs_total
    control_dic['Samples_have']    = Samples_have
    control_dic['Samples_missing'] = Samples_missing
    control_dic['Samples_total']   = Samples_total

# -------------------------------------------------------------------------------------------------
# Saves SL JSON databases, MAIN_CONTROL_PATH.
#
def fs_scan_SL_ROMs(PATHS, SL_catalog_dic, control_dic, SL_hash_dir_FN, SL_ROM_dir_FN):
    # >> SL ROMs: Traverse Software List, check if ROM exists, update and save database
    log_info('Opening SL ROMs report file "{0}"'.format(PATHS.REPORT_SL_SCAN_ROMS_PATH.getPath()))
    file = open(PATHS.REPORT_SL_SCAN_ROMS_PATH.getPath(), 'w')
    pDialog = xbmcgui.DialogProgress()
    pdialog_line1 = 'Scanning Sofware Lists ROMs ...'
    pDialog.create('Advanced MAME Launcher', pdialog_line1)
    pDialog.update(0)
    total_files = len(SL_catalog_dic)
    processed_files = 0
    SL_ROMs_have = SL_ROMs_missing = SL_ROMs_total = 0
    for SL_name in sorted(SL_catalog_dic):
        SL_DB_FN = SL_hash_dir_FN.pjoin(SL_name + '.json')
        # log_debug('File "{0}"'.format(SL_DB_FN.getPath()))
        roms = fs_load_JSON_file(SL_DB_FN.getPath())
        for rom_key in sorted(roms):
            rom = roms[rom_key]
            if rom['num_roms']:
                SL_ROMs_total += 1
                SL_ROM_FN = SL_ROM_dir_FN.pjoin(SL_name).pjoin(rom_key + '.zip')
                # log_debug('Scanning "{0}"'.format(SL_ROM_FN.getPath()))
                if SL_ROM_FN.exists():
                    rom['status_ROM'] = 'R'
                    SL_ROMs_have += 1
                else:
                    rom['status_ROM'] = 'r'
                    SL_ROMs_missing += 1
                    file.write('Missing SL ROM {0}\n'.format(SL_ROM_FN.getPath()))
            else:
                rom['status_ROM'] = '-'
        fs_write_JSON_file(SL_DB_FN.getPath(), roms)
        processed_files += 1
        update_number = 100 * processed_files / total_files
        pDialog.update(update_number, pdialog_line1, 'Software List {0} ...'.format(SL_name))
    pDialog.close()
    file.close()

    # >> SL CHDs: Traverse Software List, check if ROM exists, update and save database
    log_info('Opening SL CHDs report file "{0}"'.format(PATHS.REPORT_SL_SCAN_CHDS_PATH.getPath()))
    file = open(PATHS.REPORT_SL_SCAN_CHDS_PATH.getPath(), 'w')
    pDialog = xbmcgui.DialogProgress()
    pdialog_line1 = 'Scanning Sofware Lists CHDs ...'
    pDialog.create('Advanced MAME Launcher', pdialog_line1)
    pDialog.update(0)
    total_files = len(SL_catalog_dic)
    processed_files = 0
    SL_CHDs_have = SL_CHDs_missing = SL_CHDs_total = 0
    for SL_name in sorted(SL_catalog_dic):
        SL_DB_FN = SL_hash_dir_FN.pjoin(SL_name + '.json')
        # log_debug('File "{0}"'.format(SL_DB_FN.getPath()))
        roms = fs_load_JSON_file(SL_DB_FN.getPath())
        for rom_key in sorted(roms):
            rom = roms[rom_key]
            if rom['CHDs']:
                for CHD_name in rom['CHDs']:
                    SL_CHDs_total += 1
                    SL_CHD_FN = SL_ROM_dir_FN.pjoin(SL_name).pjoin(rom_key).pjoin(CHD_name + '.chd')
                    # log_debug('Scanning "{0}"'.format(SL_CHD_FN.getPath()))
                    if SL_CHD_FN.exists():
                        rom['status_CHD'] = 'C'
                        SL_CHDs_have += 1
                    else:
                        rom['status_CHD'] = 'c'
                        SL_CHDs_missing += 1
                        file.write('Missing SL CHD {0}\n'.format(SL_CHD_FN.getPath()))
            else:
                rom['status_CHD'] = '-'
        fs_write_JSON_file(SL_DB_FN.getPath(), roms)
        processed_files += 1
        update_number = 100 * processed_files / total_files
        pDialog.update(update_number, pdialog_line1, 'Software List {0} ...'.format(SL_name))
    pDialog.close()
    file.close()

    # >> Update statistics
    control_dic['SL_ROMs_have']    = SL_ROMs_have
    control_dic['SL_ROMs_missing'] = SL_ROMs_missing
    control_dic['SL_ROMs_total']   = SL_ROMs_total
    control_dic['SL_CHDs_have']    = SL_CHDs_have
    control_dic['SL_CHDs_missing'] = SL_CHDs_missing
    control_dic['SL_CHDs_total']   = SL_CHDs_total

    # >> Save databases
    fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)

def fs_scan_MAME_assets(PATHS, machines, Asset_path_FN):
    # >> Iterate machines, check if assets/artwork exist.
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher', 'Scanning MAME assets/artwork...')
    total_machines = len(machines)
    processed_machines = 0
    assets_dic = {}
    for key in sorted(machines):
        machine = machines[key]

        # >> Scan assets
        machine_assets = fs_new_MAME_asset()
        for idx, asset_key in enumerate(ASSET_MAME_KEY_LIST):
            full_asset_dir_FN = Asset_path_FN.pjoin(ASSET_MAME_PATH_LIST[idx])
            asset_FN = full_asset_dir_FN.pjoin(key + '.png')
            if asset_FN.exists(): machine_assets[asset_key] = asset_FN.getOriginalPath()
            else:                 machine_assets[asset_key] = ''
        assets_dic[key] = machine_assets

        # >> Progress dialog
        processed_machines = processed_machines + 1
        pDialog.update(100 * processed_machines / total_machines)
    pDialog.close()

    # >> Asset statistics
    
    # >> Save asset database and control_dic
    kodi_busydialog_ON()
    fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
    kodi_busydialog_OFF()

def fs_scan_SL_assets(PATHS, SL_catalog_dic, Asset_path_FN):
    # >> Traverse Software List, check if ROM exists, update and save database
    pDialog = xbmcgui.DialogProgress()
    pdialog_line1 = 'Scanning Sofware Lists ROMs ...'
    pDialog.create('Advanced MAME Launcher', pdialog_line1)
    pDialog.update(0)
    total_files = len(SL_catalog_dic)
    processed_files = 0
    for SL_name in sorted(SL_catalog_dic):
        # >> Open database
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        # log_debug('Processing "{0}" ({1})'.format(SL_name, SL_catalog_dic[SL_name]['display_name']))
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())

        # >> Scan for assets
        assets_file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
        SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
        # log_info('Assets JSON "{0}"'.format(SL_asset_DB_FN.getPath()))
        SL_assets_dic = {}
        for rom_key in sorted(SL_roms):
            rom = SL_roms[rom_key]
            SL_assets = fs_new_SL_asset()
            for idx, asset_key in enumerate(ASSET_SL_KEY_LIST):
                full_asset_dir_FN = Asset_path_FN.pjoin(ASSET_SL_PATH_LIST[idx]).pjoin(SL_name)
                asset_FN = full_asset_dir_FN.pjoin(rom_key + '.png')
                # log_info('Testing P "{0}"'.format(asset_FN.getPath()))
                if asset_FN.exists(): SL_assets[asset_key] = asset_FN.getOriginalPath()
                else:                 SL_assets[asset_key] = ''
            SL_assets_dic[rom_key] = SL_assets

        # >> Save SL ROMs and asset DB
        # fs_write_JSON_file(SL_DB_FN.getPath(), SL_assets_dic)
        fs_write_JSON_file(SL_asset_DB_FN.getPath(), SL_assets_dic)

        # >> Update progress
        processed_files += 1
        update_number = 100 * processed_files / total_files
        pDialog.update(update_number, pdialog_line1, 'Software List {0} ...'.format(SL_name))
    pDialog.close()

    # >> Asset statistics
    
    # >> Save control_dic (with updated statistics)
