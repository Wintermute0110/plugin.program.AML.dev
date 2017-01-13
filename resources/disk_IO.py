# -*- coding: utf-8 -*-
# Advanced Emulator Launcher filesystem I/O functions
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

# --- XML stuff ---
# ~~~ cElementTree sometimes fails to parse XML in Kodi's Python interpreter... I don't know why
# import xml.etree.cElementTree as ET

# ~~~ Using ElementTree seems to solve the problem
import xml.etree.ElementTree as ET
import json
import io
import codecs, time

# --- AEL packages ---
try:
    from utils_kodi import *
except:
    from utils_kodi_standalone import *

#
# Loads a JSON file
#
def fs_load_JSON_file(json_filename):
    # --- If file does not exist return empty dictionary ---
    data_dic = {}
    if not os.path.isfile(json_filename):
        return data_dic

    # --- Parse using json module ---
    log_verb('fs_load_ROMs_JSON() Loading JSON file {0}'.format(json_filename))
    with open(json_filename) as file:    
        data_dic = json.load(file)

    return data_dic

# -------------------------------------------------------------------------------------------------
# MAME_XML_PATH -> (FileName object) path of MAME XML output file.
# mame_prog_FN  -> (FileName object) path to MAME executable.
# Returns filesize -> (int) file size of output MAME.xml
#
def filesize = fs_extract_MAME_XML(MAME_XML_PATH, mame_prog_FN):
    (mame_dir, mame_exec) = os.path.split(mame_prog)
    log_debug('_command_setup_plugin() mame_exec = {0}'.format(mame_exec))
    with open(MAME_XML_PATH, 'wb') as out, open(MAME_STDERR_FILE_PATH, 'wb') as err:
        p = subprocess.Popen([mame_exec, '-listxml'], stdout=out,stderr=err,cwd=mame_dir)
        count = 0
        while p.poll() is None:
            pDialog.update(count * 100 / 100)
            time.sleep(1)
            count = count + 1
    pDialog.close()

    # --- Check if everything OK ---
    statinfo = os.stat(MAME_XML_PATH)
    filesize = statinfo.st_size

    return filesize

def fs_count_MAME_Machines(MAME_XML_PATH):
    pDialog = xbmcgui.DialogProgress()
    pDialog_canceled = False
    pDialog.create('Advanced MAME Launcher',
                   'Counting number of MAME machines...')
    pDialog.update(0)
    num_machines = 0
    with open(MAME_XML_PATH, 'rt') as f:
        for line in f:
            if line.decode('utf-8').find('<machine name=') > 0: num_machines = num_machines + 1
    pDialog.update(100)
    pDialog.close()

    return num_machines
