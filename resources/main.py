# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher main script file
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

# --- Main imports ---
import os
import urlparse

# --- Kodi stuff ---
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# --- Modules/packages in this plugin ---
from utils_kodi import *

# --- Addon object (used to access settings) ---
addon_obj      = xbmcaddon.Addon()
__addon_id__   = addon_obj.getAddonInfo('id')
__addon_name__ = addon_obj.getAddonInfo('name')
__version__    = addon_obj.getAddonInfo('version')
__author__     = addon_obj.getAddonInfo('author')
__profile__    = addon_obj.getAddonInfo('profile')
__type__       = addon_obj.getAddonInfo('type')

# --- Addon paths and constant definition ---
# _FILE_PATH is a filename | _DIR is a directory (with trailing /)
PLUGIN_DATA_DIR       = xbmc.translatePath(os.path.join('special://profile/addon_data', __addon_id__)).decode('utf-8')
BASE_DIR              = xbmc.translatePath(os.path.join('special://', 'profile')).decode('utf-8')
HOME_DIR              = xbmc.translatePath(os.path.join('special://', 'home')).decode('utf-8')
ADDONS_DIR            = xbmc.translatePath(os.path.join(HOME_DIR, 'addons')).decode('utf-8')
AML_ADDON_DIR         = xbmc.translatePath(os.path.join(ADDONS_DIR, __addon_id__)).decode('utf-8')
ICON_IMG_FILE_PATH    = os.path.join(AML_ADDON_DIR, 'icon.png').decode('utf-8')
FANART_IMG_FILE_PATH  = os.path.join(AML_ADDON_DIR, 'fanart.jpg').decode('utf-8')

# --- "Constants" ---


class Main:
    # ---------------------------------------------------------------------------------------------
    # This is the plugin entry point.
    # ---------------------------------------------------------------------------------------------
    def run_plugin(self):
        # --- Initialise log system ---
        # >> Force DEBUG log level for development.
        # >> Place it before setting loading so settings can be dumped during debugging.
        set_log_level(LOG_DEBUG)

        # --- Fill in settings dictionary using addon_obj.getSetting() ---
        # self._get_settings()
        # set_log_level(self.settings['log_level'])

        # --- Some debug stuff for development ---
        log_debug('---------- Called AML Main::run_plugin() ----------')
        log_debug(sys.version.replace('\n', ''))
        log_debug('__addon_id__   {0}'.format(__addon_id__))
        log_debug('__version__    {0}'.format(__version__))
        log_debug('__profile__    {0}'.format(__profile__))
        for i in range(len(sys.argv)):
            log_debug('sys.argv[{0}] = "{1}"'.format(i, sys.argv[i]))

        # --- Addon data paths creation ---

        # --- Process URL ---
        self.base_url     = sys.argv[0]
        self.addon_handle = int(sys.argv[1])
        args = urlparse.parse_qs(sys.argv[2][1:])
        log_debug('args = {0}'.format(args))

        # --- URL routing -------------------------------------------------------------------------
        # ~~~ Routing step 1 ~~~
        args_size = len(args)
        if args_size == 0:
            self._render_root_list()
            return

        # ~~~ Routing step 2 ~~~
        if 'list' in args:
            list_name = args['list'][0]
            if 'parent' in args:
                parent_name = args['parent'][0]
                if list_name == 'Machines':
                    self._render_machine_clone_list(parent_name)
            else:
                if list_name == 'Machines':
                    self._render_machine_parent_list()

        elif 'clist' in args:
            clist_name = args['clist'][0]
            if clist_name == 'Manufacturer':
                if 'manufacturer' in args:
                    manufacturer_name = args['manufacturer'][0]
                    if 'parent' in args:                        
                        self._render_manufacturer_clones_list(manufacturer_name, args['parent'][0])
                    else:
                        self._render_manufacturer_parents_list(manufacturer_name)
                else:
                    self._render_manufacturer_list()
                    
            elif clist_name == 'SL':
                if 'SL' in args:
                    SL_name = args['SL'][0]
                    self._render_SL_machine_ROM_list(SL_name)
                else:
                    self._render_SL_machine_list()

        elif 'command' in args:
            command = args['command'][0]
            if command == 'launch':
                mame_args = args['mame_args'][0]
                log_info('Launching mame with mame_args "{0}"'.format(mame_args))
            else:
                log_error('Unknown command "{0}"'.format(command))

        else:
            log_error('Error in URL routing')
            
        # --- So Long, and Thanks for All the Fish ---
        log_debug('Advanced MAME Launcher exit')

    # ---------------------------------------------------------------------------------------------
    # Menu rendering
    # ---------------------------------------------------------------------------------------------
    def _render_root_list(self):
        # >> Code Machines/Manufacturer/SF first. Rest are variations of those three.
        self._render_root_list_row('Machines',                   self._misc_url_root('Machines'))
        # self._render_root_list_row('Machines (no coin slot)',    self._misc_url_root('NoCoin'))
        # self._render_root_list_row('Mechanical Machines',        self._misc_url_root('Mechanical'))
        self._render_root_list_row('Machines by Manufacturer',   self._misc_url_root('Manufacturer'))
        # self._render_root_list_row('Machines by Year',           self._misc_url_root('Year'))
        # self._render_root_list_row('Machines by Driver',         self._misc_url_root('Driver'))
        # self._render_root_list_row('Machines by Control',        self._misc_url_root('Controls'))
        # self._render_root_list_row('Machines by Orientation',    self._misc_url_root('Orientation'))
        self._render_root_list_row('Software Lists',             self._misc_url_root('SL'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_root_list_row(self, root_name, root_URL):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(root_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : root_name,        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = root_URL, listitem = listitem, isFolder = True)

    #----------------------------------------------------------------------------------------------
    # Main machine list with coin slot and not mechanical
    # 1) Open machine index
    #----------------------------------------------------------------------------------------------
    def _render_machine_parent_list(self):
        machines = [
           {'display_name' : 'Cadillacs and Dinosaurs (World)', 'name' : 'dino' }
        ]
        
        for machine in machines:
            self._render_machine_row(machine, True)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Also render parent together with clones
    # If user clicks in this list then ROM is launched.
    #
    def _render_machine_clone_list(self, parent_name):
        machines = [
           {'display_name' : 'Cadillacs and Dinosaurs (World)',       'name' : 'dino' },        
           {'display_name' : 'Cadillacs and Dinosaurs (Japan clone)', 'name' : 'dinoj' }
        ]

        for machine in machines:
            self._render_machine_row(machine, False)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #----------------------------------------------------------------------------------------------
    # 1) There should be a precompiled JSON index with Manufacturers.
    # 2) Each manufacturer has a list of parents by that manufacturer.
    # 3) 
    #----------------------------------------------------------------------------------------------
    def _render_manufacturer_list(self):
        pass

    #----------------------------------------------------------------------------------------------
    #
    #----------------------------------------------------------------------------------------------
    def _render_SL_machine_list(self):
        software_list = [ 
            {'name' : 'Sega 32X cartridges', 'xml_file' : '32x.xml'},
            {'name' : 'MSX1 cartridges',     'xml_file' : 'msx1_cart.xml'},
            {'name' : 'MSX1 cassettes',      'xml_file' : 'msx1_cass.xml'},
            {'name' : 'MSX1 disk images',    'xml_file' : 'msx1_flop.xml'}
        ]

        for SL in software_list:
            self._render_SL_machine_row(SL)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_machine_row(self, SL):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(SL['name'], iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : SL['name'],        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_category_root('SL', 'sl', SL['xml_file'])
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    #----------------------------------------------------------------------------------------------
    # Render rows (ListItems) 
    #----------------------------------------------------------------------------------------------
    #
    # Render parent or clone machines.
    # Information and artwork/assets are the same for all machines.
    # URL is different: parent URL leads to clones, clone URL launchs machine.
    #
    def _render_machine_row(self, machine, parent_list):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(machine['display_name'], iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : machine['display_name'],        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        if parent_list:
            URL = self._misc_url_parent('Machines', machine['name'])
        else:
            URL = self._misc_url_command('launch', machine['name'])
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------
    def _misc_url_root(self, root_menu):
        return '{0}?root={1}'.format(self.base_url, root_menu)

    def _misc_url_parent(self, root_menu, parent_name):
        return '{0}?root={1}&parent={2}'.format(self.base_url, root_menu, parent_name)

    def _misc_url_category_root(self, root_menu, index_name, index_value):
        return '{0}?root={1}&{2}={3}'.format(self.base_url, root_menu, index_name, index_value)

    def _misc_url_category_clones(self, root_menu, index_name, index_value, parent_name):
        return '{0}?root={1}&{2}={3}&parent={4}'.format(self.base_url, root_menu, index_name, index_value, parent_name)

    def _misc_url_command(self, command, mame_args):
        return '{0}?command={1}&mame_args={2}'.format(self.base_url, command, mame_args)
