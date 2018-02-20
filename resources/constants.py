# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher constants
#

# Copyright (c) 2018 Wintermute0110 <wintermute0110@gmail.com>
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
# A universal Addon error reporting exception
# This exception is raised to report errors in the GUI.
# Unhandled exceptions must not raise AEL_Error() so the addon crashes and the traceback is printed
# in the Kodi log file.
# -------------------------------------------------------------------------------------------------
# >> Top-level GUI code looks like this
# try:
#     autoconfig_export_category(category, export_FN)
# except Addon_Error as E:
#     kodi_notify_warn('{0}'.format(E))
# else:
#     kodi_notify('Exported Category "{0}" XML config'.format(category['m_name']))
#
# >> Low-level code looks like this
# def autoconfig_export_category(category, export_FN):
#     try:
#         do_something_that_may_fail()
#     except OSError:
#         log_error('(OSError) Cannot write {0} file'.format(export_FN.getBase()))
#         # >> Message to be printed in the GUI
#         raise AEL_Error('Error writing file (OSError)')
#
class Addon_Error(Exception):
    def __init__(self, err_str):
        self.err_str = err_str

    def __str__(self):
        return self.err_str

# -------------------------------------------------------------------------------------------------
# Advanced MAME Launcher constants
# -------------------------------------------------------------------------------------------------
# --- Used in the addon URLs so mark the location of machines/ROMs ---
LOCATION_STANDARD  = 'STANDARD'
LOCATION_MAME_FAVS = 'MAME_FAVS'
LOCATION_SL_FAVS   = 'SL_FAVS'

# --- ROM flags used by skins to display status icons ---
AEL_INFAV_BOOL_LABEL  = 'AEL_InFav'
AEL_PCLONE_STAT_LABEL = 'AEL_PClone_stat'

AEL_INFAV_BOOL_VALUE_TRUE    = 'InFav_True'
AEL_INFAV_BOOL_VALUE_FALSE   = 'InFav_False'
AEL_PCLONE_STAT_VALUE_PARENT = 'PClone_Parent'
AEL_PCLONE_STAT_VALUE_CLONE  = 'PClone_Clone'
AEL_PCLONE_STAT_VALUE_NONE   = 'PClone_None'

# --- SL ROM launching cases ---
SL_LAUNCH_CASE_A     = 'Case A'
SL_LAUNCH_CASE_B     = 'Case B'
SL_LAUNCH_CASE_C     = 'Case C'
SL_LAUNCH_CASE_D     = 'Case D'
SL_LAUNCH_CASE_ERROR = 'Case ERROR!'
