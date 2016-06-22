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

# --- "Constants" -------------------------------------------------------------
MAME_XML_filename               = 'MAME.xml'
Main_DB_filename                = 'MAME_info.json'
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

# -----------------------------------------------------------------------------
# Incremental Parsing approach B (from [1])
# -----------------------------------------------------------------------------
# Do not load whole MAME XML into memory! Use an iterative parser to
# grab only the information we want and discard the rest.
# See http://effbot.org/zone/element-iterparse.htm [1]
#
context = ET.iterparse(MAME_XML_filename, events=("start", "end"))
context = iter(context)
event, root = context.next()
mame_version_str = 'MAME ' + root.attrib['build']
print('MAME version is "{0}"'.format(mame_version_str))

# --- Data variables ---
# Create a dictionary of the form,
#   machines = { 'machine_name' : machine, ...}
#
def fs_new_machine():
    m = {'sourcefile'        : u'',
         'isbios'            : False,
         'isdevice'          : False,
         'ismechanical'      : False,
         'cloneof'           : u'',
         'romof'             : u'',
         'sampleof'          : u'',
         'description'       : u'', 
         'year'              : u'', 
         'manufacturer'      : u'',
         'display_tag'       : [],
         'control_type'      : [],
         'haveCoin'          : False,
         'coins'             : 0,
         'driver_status'     : u'',
         'softwarelist_name' : [],
         'isdead'            : False
    }

    return m

machines = {}
machine_name = ''
num_iteration = 0
num_machines = 0
num_dead = 0
print('Reading MAME XML file ...')
for event, elem in context:
    # --- Debug the elements we are iterating from the XML file ---
    # print('Event     {0:6s} | Elem.tag    "{1}"'.format(event, elem.tag))
    # print('                   Elem.text   "{0}"'.format(elem.text))
    # print('                   Elem.attrib "{0}"'.format(elem.attrib))

    # <machine> tag start event includes <machine> attributes
    if event == 'start' and elem.tag == 'machine':
        machine = fs_new_machine()
        runnable = False
        num_displays = 0

        # --- Process <machine> attributes ---
        # name is #REQUIRED attribute
        if 'name' not in elem.attrib:
            print('"name" attribute not found in <machine> tag. Aborting.')
            sys.exit(10)
        else:
            machine_name = elem.attrib['name']
        # sourcefile #IMPLIED attribute
        if 'sourcefile' not in elem.attrib:
            print('"sourcefile" attribute not found in <machine> tag. Aborting.')
            sys.exit(10)
        else:
            machine['sourcefile'] = elem.attrib['sourcefile']

        # Optional, default no
        if 'isbios' not in elem.attrib: machine['isbios'] = False
        else:                           machine['isbios'] = True if elem.attrib['isbios'] == u'yes' else False
        if 'isdevice' not in elem.attrib: machine['isdevice'] = False
        else:                             machine['isdevice'] = True if elem.attrib['isdevice'] == u'yes' else False
        if 'ismechanical' not in elem.attrib: machine['ismechanical'] = False
        else:                                 machine['ismechanical'] = True if elem.attrib['ismechanical'] == u'yes' else False
        # Optional, default yes
        if 'runnable' not in elem.attrib: runnable = True
        else:                             runnable = False if elem.attrib['runnable'] == u'no' else True

        # cloneof is #IMPLIED attribute
        if 'cloneof' in elem.attrib:
            machine['cloneof'] = elem.attrib['cloneof']

        # romof is #IMPLIED attribute
        if 'romof' in elem.attrib:
            machine['romof'] = elem.attrib['romof']

        # sampleof is #IMPLIED attribute
        if 'sampleof' in elem.attrib:
            machine['sampleof'] = elem.attrib['sampleof']

        num_machines += 1

    elif event == 'start' and elem.tag == 'description':
        machine['description'] = unicode(elem.text)

    elif event == 'start' and elem.tag == 'year':
        machine['year'] = unicode(elem.text)

    elif event == 'start' and elem.tag == 'manufacturer':
        machine['manufacturer'] = unicode(elem.text)

    # Some machines have more than one display tag (for example aquastge has 2).
    # Other machines have no display tag (18w)
    elif event == 'start' and elem.tag == 'display':
        machine['display_tag'].append(elem.attrib['tag'])
        num_displays += 1

    # Some machines have no controls at all.
    elif event == 'start' and elem.tag == 'input':
        # coins is #IMPLIED attribute
        if 'coins' in elem.attrib:
            machine['coins'] = int(elem.attrib['coins'])
            if machine['coins'] > 0: machine['haveCoin'] = True
            else:                    machine['haveCoin'] = False

        # >> Iterate children of <input> and search for <control> tags
        for control_child in elem:
            if control_child.tag == 'control':
                machine['control_type'].append(control_child.attrib['type']) 

    elif event == 'start' and elem.tag == 'driver':
        # status is #REQUIRED attribute
        machine['driver_status'] = unicode(elem.attrib['status'])

    elif event == 'start' and elem.tag == 'softwarelist':
        # name is #REQUIRED attribute
        machine['softwarelist_name'].append(elem.attrib['name'])

    elif event == 'end' and elem.tag == 'machine':
        # >> Assumption 1: isdevice = True if and only if runnable = False
        if machine['isdevice'] == runnable:
            print("Machine {0}: machine['isdevice'] == runnable".format(machine_name))
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

        # >> Mark dead machines. A machine is dead if,
        # >> A) Status is preliminary
        # >> B) Have no display OR Have no controls
        # if machine['driver_status'] == 'preliminary' and not (machine['display_tag'] and machine['control_type']):
        if machine['driver_status'] == 'preliminary' and not machine['display_tag'] and not machine['control_type']:
            machine['isdead'] = True
            num_dead += 1

        # >> Delete XML element once it has been processed
        elem.clear()
        # >> Add new machine
        machines[machine_name] = machine

    # --- Print something to prove we are doing stuff ---
    num_iteration += 1
    if num_iteration % 50000 == 0:
      print('Processed {0:10d} events ({1:6d} machines so far) ...'.format(num_iteration, num_machines))

    # --- Stop after NUM_MACHINES machines have been processed for debug ---
    if num_machines >= NUM_MACHINES: break
print('Processed {0} MAME XML events'.format(num_iteration))
print('Total number of machines {0}'.format(num_machines))
print('Dead machines            {0}'.format(num_dead))

# -----------------------------------------------------------------------------
# Now write simplified JSON
# -----------------------------------------------------------------------------
print('Writing AML database...')
fs_write_JSON_file(Main_DB_filename, machines)
