# -*- coding: utf-8 -*-

# Advanced Emulator Launcher miscellaneous functions.

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

# --- AEL modules ---
# This module must not include any other AML/AEL modules to avoid circular dependencies.

# --- Kodi modules ---
try:
    import xbmc
    import xbmcgui
    KODI_RUNTIME_AVAILABLE_UTILS_KODI = True
except:
    KODI_RUNTIME_AVAILABLE_UTILS_KODI = False

# --- Python standard library ---
import hashlib
import json
import math
import os
import pprint
import random
import shutil
import sys
import time
import urllib.parse

# --- Constants -----------------------------------------------------------------------------------
LOG_ERROR   = 0
LOG_WARNING = 1
LOG_INFO    = 2
LOG_VERB    = 3
LOG_DEBUG   = 4

# --- Internal globals ----------------------------------------------------------------------------
current_log_level = LOG_INFO

# -------------------------------------------------------------------------------------------------
# Logging functions
# -------------------------------------------------------------------------------------------------
def set_log_level(level):
    global current_log_level

    current_log_level = level

def log_variable(var_name, var):
    if current_log_level < LOG_DEBUG: return
    log_text = 'AML DUMP : Dumping variable "{}"\n{}'.format(var_name, pprint.pformat(var))
    xbmc.log(log_text, level = xbmc.LOGERROR)

# For Unicode stuff in Kodi log see https://github.com/romanvm/kodi.six
def log_debug_KR(str_text):
    if current_log_level < LOG_DEBUG: return

    # if it is bytes we assume it's "utf-8" encoded.
    # will fail if called with other encodings (latin, etc).
    if isinstance(str_text, bytes): str_text = str_text.decode('utf-8')
                              
    # At this point we are sure str_text is a Unicode string.
    # Kodi functions require Unicode strings as arguments.
    log_text = 'AML DEBUG: ' + str_text
    xbmc.log(log_text, level = xbmc.LOGNOTICE)

def log_verb_KR(str_text):
    if current_log_level < LOG_VERB: return
    if isinstance(str_text, bytes): str_text = str_text.decode('utf-8')
    log_text = 'AML VERB : ' + str_text
    xbmc.log(log_text, level = xbmc.LOGNOTICE)

def log_info_KR(str_text):
    if current_log_level < LOG_INFO: return
    if isinstance(str_text, bytes): str_text = str_text.decode('utf-8')
    log_text = 'AML INFO : ' + str_text
    xbmc.log(log_text, level = xbmc.LOGNOTICE)

def log_warning_KR(str_text):
    if current_log_level < LOG_WARNING: return
    if isinstance(str_text, bytes): str_text = str_text.decode('utf-8')
    log_text = 'AML WARN : ' + str_text
    xbmc.log(log_text, level = xbmc.LOGWARNING)

def log_error_KR(str_text):
    if current_log_level < LOG_ERROR: return
    if isinstance(str_text, bytes): str_text = str_text.decode('utf-8')
    log_text = 'AML ERROR: ' + str_text
    xbmc.log(log_text, level = xbmc.LOGERROR)

#
# Replacement functions when running outside Kodi with the standard Python interpreter.
#
def log_debug_Python(str): print(str)

def log_verb_Python(str): print(str)

def log_info_Python(str): print(str)

def log_warning_Python(str): print(str)

def log_error_Python(str): print(str)

# -------------------------------------------------------------------------------------------------
# Kodi notifications and dialogs
# -------------------------------------------------------------------------------------------------
# Displays a modal dialog with an OK button. Dialog can have up to 3 rows of text, however first
# row is multiline.
# Call examples:
#  1) ret = kodi_dialog_OK('Launch ROM?')
#  2) ret = kodi_dialog_OK('Launch ROM?', title = 'AML - Launcher')
def kodi_dialog_OK(text, title = 'Advanced MAME Launcher'):
    xbmcgui.Dialog().ok(title, text)

# Returns True is YES was pressed, returns False if NO was pressed or dialog canceled.
def kodi_dialog_yesno(text, title = 'Advanced MAME Launcher'):
    return xbmcgui.Dialog().yesno(title, text)

# type 3 ShowAndGetWriteableDirectory
# shares  'files'  list file sources (added through filemanager)
# shares  'local'  list local drives
# shares  ''       list local drives and network shares
def kodi_dialog_get_wdirectory(dialog_heading):
    return xbmcgui.Dialog().browse(3, dialog_heading, '').decode('utf-8')

# Displays a small box in the bottom right corner
def kodi_notify(text, title = 'Advanced MAME Launcher', time = 5000):
    xbmcgui.Dialog().notification(title, text, xbmcgui.NOTIFICATION_INFO, time)

def kodi_notify_warn(text, title = 'Advanced MAME Launcher warning', time = 7000):
    xbmcgui.Dialog().notification(title, text, xbmcgui.NOTIFICATION_WARNING, time)

# Do not use this function much because it is the same icon displayed when Python fails
# with an exception and that may confuse the user.
def kodi_notify_error(text, title = 'Advanced MAME Launcher error', time = 7000):
    xbmcgui.Dialog().notification(title, text, xbmcgui.NOTIFICATION_ERROR, time)

def kodi_refresh_container():
    log_debug('kodi_refresh_container()')
    xbmc.executebuiltin('Container.Refresh')

# Progress dialog that can be closed and reopened.
# Messages and progress in the dialog are always remembered, even if closed and reopened.
# If the dialog is canceled this class remembers it forever.
# Kodi Matrix change: Renamed option line1 to message. Removed option line2. Removed option line3.
#
# --- Example 1 ---
# pDialog = KodiProgressDialog()
# pDialog.startProgress('Doing something...', step_total)
# for ...
#     pDialog.updateProgressInc()
#     # Do stuff...
# pDialog.endProgress()
class KodiProgressDialog(object):
    def __init__(self):
        self.heading = 'Advanced MAME Launcher'
        self.progress = 0
        self.flag_dialog_canceled = False
        self.dialog_active = False
        self.progressDialog = xbmcgui.DialogProgress()

    # Creates a new progress dialog.
    def startProgress(self, message, step_total = 100, step_counter = 0):
        if self.dialog_active: raise TypeError
        self.step_total = step_total
        self.step_counter = step_counter
        self.progress = math.floor((self.step_counter * 100) / self.step_total)
        self.dialog_active = True
        self.message = message
        self.progressDialog.create(self.heading, self.message)
        self.progressDialog.update(self.progress)

    # Changes message and resets progress.
    def resetProgress(self, message, step_total = 100, step_counter = 0):
        if not self.dialog_active: raise TypeError
        self.step_total = step_total
        self.step_counter = step_counter
        self.progress = math.floor((self.step_counter * 100) / self.step_total)
        self.message = message
        self.progressDialog.update(self.progress, self.message)

    # Update progress and optionally update message as well.
    def updateProgress(self, step_counter, message = None):
        if not self.dialog_active: raise TypeError
        self.step_counter = step_counter
        self.progress = math.floor((self.step_counter * 100) / self.step_total)
        if message is None:
            self.progressDialog.update(self.progress)
        else:
            if type(message) is not str: raise TypeError
            self.message = message
            self.progressDialog.update(self.progress, self.message)

    # Update progress, optionally update message as well, and autoincrements.
    # Progress is incremented AFTER dialog is updated.
    def updateProgressInc(self, message = None):
        if not self.dialog_active: raise TypeError
        self.progress = math.floor((self.step_counter * 100) / self.step_total)
        self.step_counter += 1
        if message is None:
            self.progressDialog.update(self.progress)
        else:
            if type(message) is not str: raise TypeError
            self.message = message
            self.progressDialog.update(self.progress, self.message)

    # Update dialog message but keep same progress.
    def updateMessage(self, message):
        if not self.dialog_active: raise TypeError
        if type(message) is not str: raise TypeError
        self.message = message
        self.progressDialog.update(self.progress, self.message)

    def isCanceled(self):
        # If the user pressed the cancel button before then return it now.
        if self.flag_dialog_canceled: return True
        # If not check and set the flag.
        if not self.dialog_active: raise TypeError
        self.flag_dialog_canceled = self.progressDialog.iscanceled()
        return self.flag_dialog_canceled

    # Before closing the dialog check if the user pressed the Cancel button and remember
    # the user decision.
    def endProgress(self):
        if not self.dialog_active: raise TypeError
        if self.progressDialog.iscanceled(): self.flag_dialog_canceled = True
        self.progressDialog.update(100)
        self.progressDialog.close()
        self.dialog_active = False

    # Reopens a previously closed dialog with endProgress(), remembering the messages
    # and the progress it had when it was closed.
    def reopen(self):
        if self.dialog_active: raise TypeError
        self.progressDialog.create(self.title, self.message)
        self.progressDialog.update(self.progress)
        self.dialog_active = True

def kodi_toogle_fullscreen():
    kodi_jsonrpc_dict('Input.ExecuteAction', {'action' : 'togglefullscreen'})

def kodi_get_screensaver_mode():
    r_dic = kodi_jsonrpc_dict('Settings.getSettingValue', {'setting' : 'screensaver.mode'})
    screensaver_mode = r_dic['value']
    return screensaver_mode

g_screensaver_mode = None # Global variable to store screensaver status.
def kodi_disable_screensaver():
    global g_screensaver_mode
    g_screensaver_mode = kodi_get_screensaver_mode()
    log_debug('kodi_disable_screensaver() g_screensaver_mode "{}"'.format(g_screensaver_mode))
    p_dic = {
        'setting' : 'screensaver.mode',
        'value' : '',
    }
    kodi_jsonrpc_dict('Settings.setSettingValue', p_dic)
    log_debug('kodi_disable_screensaver() Screensaver disabled.')

# kodi_disable_screensaver() must be called before this function or bad things will happen.
def kodi_restore_screensaver():
    if g_screensaver_mode is None:
        log_error('kodi_disable_screensaver() must be called before kodi_restore_screensaver()')
        raise RuntimeError
    log_debug('kodi_restore_screensaver() Screensaver mode "{}"'.format(g_screensaver_mode))
    p_dic = {
        'setting' : 'screensaver.mode',
        'value' : g_screensaver_mode,
    }
    kodi_jsonrpc_dict('Settings.setSettingValue', p_dic)
    log_debug('kodi_restore_screensaver() Restored previous screensaver status.')

# THIS FUNCTION IS DEPRECATED AND WILL BE REMOVED SOON.
def kodi_jsonrpc_query(method_str, params_str, verbose = False):
    if verbose:
        log_debug('kodi_jsonrpc_query() method_str "{}"'.format(method_str))
        log_debug('kodi_jsonrpc_query() params_str "{}"'.format(params_str))
        # params_dic = json.loads(params_str)
        # log_debug('kodi_jsonrpc_query() params_dic = \n{}'.format(pprint.pformat(params_dic)))

    # --- Do query ---
    query_str = '{{"id" : 1, "jsonrpc" : "2.0", "method" : "{0}", "params" : {1} }}'.format(
        method_str, params_str)
    # if verbose: log_debug('kodi_jsonrpc_query() query_str "{}"'.format(query_str))
    response_json_str = xbmc.executeJSONRPC(query_str)
    # if verbose: log_debug('kodi_jsonrpc_query() response "{}"'.format(response_json_str))

    # --- Parse JSON response ---
    response_dic = json.loads(response_json_str)
    # if verbose: log_debug('kodi_jsonrpc_query() response_dic = \n{}'.format(pprint.pformat(response_dic)))
    if 'error' in response_dic:
        result_dic = response_dic['error']
        log_warning('kodi_jsonrpc_query() JSONRPC ERROR {}'.format(result_dic['message']))
    else:
        result_dic = response_dic['result']
    if verbose:
        log_debug('kodi_jsonrpc_query() result_dic = \n{}'.format(pprint.pformat(result_dic)))

    return result_dic

# Access Kodi JSON-RPC interface in an easy way.
# Returns a dictionary with the parsed response 'result' field.
#
# Query input:
#
# {
#     "id" : 1,
#     "jsonrpc" : "2.0",
#     "method" : "Application.GetProperties",
#     "params" : { "properties" : ["name", "version"] }
# }
#
# Query response:
#
# {
#     "id" : 1,
#     "jsonrpc" : "2.0",
#     "result" : {
#         "name" : "Kodi",
#         "version" : {"major":17,"minor":6,"revision":"20171114-a9a7a20","tag":"stable"}
#     }
# }
#
# Query response ERROR:
# {
#     "id" : null,
#     "jsonrpc" : "2.0",
#     "error" : { "code":-32700, "message" : "Parse error."}
# }
#
def kodi_jsonrpc_dict(method_str, params_dic, verbose = False):
    params_str = json.dumps(params_dic)
    if verbose:
        log_debug('kodi_jsonrpc_dict() method_str "{}"'.format(method_str))
        log_debug('kodi_jsonrpc_dict() params_dic = \n{}'.format(pprint.pformat(params_dic)))
        log_debug('kodi_jsonrpc_dict() params_str "{}"'.format(params_str))

    # --- Do query ---
    header = '"id" : 1, "jsonrpc" : "2.0"'
    query_str = '{{{}, "method" : "{}", "params" : {} }}'.format(header, method_str, params_str)
    response_json_str = xbmc.executeJSONRPC(query_str)

    # --- Parse JSON response ---
    response_dic = json.loads(response_json_str)
    if 'error' in response_dic:
        result_dic = response_dic['error']
        log_warning('kodi_jsonrpc_dict() JSONRPC ERROR {}'.format(result_dic['message']))
    else:
        result_dic = response_dic['result']
    if verbose:
        log_debug('kodi_jsonrpc_dict() result_dic = \n{}'.format(pprint.pformat(result_dic)))

    return result_dic

# Displays a text window and requests a monospaced font.
# v18 Leia change: New optional param added usemono.
def kodi_display_text_window_mono(window_title, info_text):
    xbmcgui.Dialog().textviewer(window_title, info_text, True)

# Displays a text window with a proportional font (default).
def kodi_display_text_window(window_title, info_text):
    xbmcgui.Dialog().textviewer(window_title, info_text)

# -------------------------------------------------------------------------------------------------
# Determine Kodi version and create some constants to allow version-dependent code.
# This if useful to work around bugs in Kodi core.
# -------------------------------------------------------------------------------------------------
# Version constants. Minimum required version is Kodi Krypton.
KODI_VERSION_MATRIX = 19
KODI_VERSION_LEIA = 18
KODI_VERSION_KRYPTON = 17
KODI_VERSION_JARVIS = 16
KODI_VERSION_ISENGARD = 15

def kodi_get_Kodi_major_version():
    r_dic = kodi_jsonrpc_dict('Application.GetProperties', {'properties' : ['version']})
    return int(r_dic['version']['major'])

# Execute the Kodi version query when module is loaded and store results in global variable.
kodi_running_version = kodi_get_Kodi_major_version()

# -------------------------------------------------------------------------------------------------
# If runnining with Kodi Python interpreter use Kodi proper functions.
# If running with the standard Python interpreter use replacement functions.
# -------------------------------------------------------------------------------------------------
if KODI_RUNTIME_AVAILABLE_UTILS_KODI:
    log_debug   = log_debug_KR
    log_verb    = log_verb_KR
    log_info    = log_info_KR
    log_warning = log_warning_KR
    log_error   = log_error_KR
else:
    log_debug   = log_debug_Python
    log_verb    = log_verb_Python
    log_info    = log_info_Python
    log_warning = log_warning_Python
    log_error   = log_error_Python
