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
from disk_IO import *

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

# --- Plugin database indices ---
Main_DB_filename                = os.path.join(AML_ADDON_DIR, 'MAME_info.json').decode('utf-8')
Machines_DB_filename            = os.path.join(AML_ADDON_DIR, 'idx_Machines.json').decode('utf-8')
Machines_NoCoin_DB_filename     = os.path.join(AML_ADDON_DIR, 'idx_Machines_NoCoin.json').decode('utf-8')
Machines_Mechanical_DB_filename = os.path.join(AML_ADDON_DIR, 'idx_Machines_Mechanical.json').decode('utf-8')
SL_cat_filename                 = os.path.join(AML_ADDON_DIR, 'cat_SoftwareLists.json').decode('utf-8')

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
                if list_name == 'Machines':     self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'NoCoin':     self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'Mechanical': self._render_machine_clone_list(list_name, parent_name)
            else:
                if list_name == 'Machines':     self._render_machine_parent_list(list_name)
                elif list_name == 'NoCoin':     self._render_machine_parent_list(list_name)
                elif list_name == 'Mechanical': self._render_machine_parent_list(list_name)

        elif 'clist' in args:
            clist_name = args['clist'][0]
            if clist_name == 'Manufacturer':
                kodi_dialog_OK('Advanced MAME Launcher', 'Not implemented yet. Sorry.')
                return
                if 'manufacturer' in args:
                    manufacturer_name = args['manufacturer'][0]
                    if 'parent' in args: self._render_machine_indexed_clone_list(clist_name, manufacturer_name, args['parent'][0])
                    else:                self._render_machine_indexed_parent_list(clist_name, manufacturer_name)
                else:                    self._render_machine_indexed_list(clist_name)

            elif clist_name == 'SL':
                if 'SL' in args:
                    SL_name = args['SL'][0]
                    self._render_SL_machine_ROM_list(SL_name)
                else:
                    self._render_SL_machine_list()

        elif 'command' in args:
            command = args['command'][0]
            if command == 'LAUNCH':
                mame_args = args['mame_args'][0]
                log_info('Launching mame with mame_args "{0}"'.format(mame_args))
            elif command == 'VIEW_MACHINE':
                self._command_view_machine(args['machine_name'][0])
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
        self._render_root_list_row('Machines (with coin slot)',  self._misc_url_1_arg('list', 'Machines'))
        self._render_root_list_row('Machines (no coin slot)',    self._misc_url_1_arg('list', 'NoCoin'))
        self._render_root_list_row('Machines (mechanical)',      self._misc_url_1_arg('list', 'Mechanical'))
        self._render_root_list_row('Machines by Manufacturer',   self._misc_url_1_arg('clist', 'Manufacturer'))
        # self._render_root_list_row('Machines by Year',           self._misc_url_root('Year'))
        # self._render_root_list_row('Machines by Driver',         self._misc_url_root('Driver'))
        # self._render_root_list_row('Machines by Control',        self._misc_url_root('Controls'))
        # self._render_root_list_row('Machines by Orientation',    self._misc_url_root('Orientation'))
        self._render_root_list_row('Software Lists',             self._misc_url_1_arg('clist', 'SL'))
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
    def _render_machine_parent_list(self, list_name):
        # >> Load main MAME info DB and PClone index
        MAME_info_dic = fs_load_JSON_file(Main_DB_filename)
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(Machines_DB_filename)
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(Machines_NoCoin_DB_filename)
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(Machines_Mechanical_DB_filename)

        # >> Render parent main list
        self._set_Kodi_content()
        for parent_name in Machines_PClone_dic:
            machine = MAME_info_dic[parent_name]
            self._render_machine_row(parent_name, machine, True, list_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Also render parent together with clones
    # If user clicks in this list then ROM is launched.
    #
    def _render_machine_clone_list(self, list_name, parent_name):
        # >> Load main MAME info DB and PClone index
        MAME_info_dic = fs_load_JSON_file(Main_DB_filename)
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(Machines_DB_filename)
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(Machines_NoCoin_DB_filename)
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(Machines_Mechanical_DB_filename)

        # >> Render parent first
        self._set_Kodi_content()
        machine = MAME_info_dic[parent_name]
        self._render_machine_row(parent_name, machine, False)
        # >> Render clones
        for clone_name in Machines_PClone_dic[parent_name]:
            machine = MAME_info_dic[clone_name]
            self._render_machine_row(clone_name, machine, False)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Render parent or clone machines.
    # Information and artwork/assets are the same for all machines.
    # URL is different: parent URL leads to clones, clone URL launchs machine.
    #
    def _render_machine_row(self, machine_name, machine, is_parent_list, list_name = u''):
        # --- Mark devices ---
        display_name = machine['description']
        if machine['isdevice']: display_name += ' [COLOR violet][Device][/COLOR]'
        if machine['isbios']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
        if machine['cloneof']:  display_name += ' [COLOR orange][Clone][/COLOR]'
        # Do not mark machines working OK
        if   machine['driver_status'] == u'imperfect':   display_name += ' [COLOR yellow][Imperfect][/COLOR]'
        elif machine['driver_status'] == u'preliminary': display_name += ' [COLOR red][Preliminary][/COLOR]'

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : display_name,        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_2_arg_RunPlugin('command', 'VIEW_MACHINE', 'machine_name', machine_name)
        commands.append(('View Machine data',  URL_view, ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        if is_parent_list:
            URL = self._misc_url_2_arg('list', list_name, 'parent', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
        else:
            URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine_name', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

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
        # >> Load Software List catalog
        SL_catalog_dic = fs_load_JSON_file(SL_cat_filename)

        self._set_Kodi_content()
        for SL_name in SL_catalog_dic:
            SL = SL_catalog_dic[SL_name]
            self._render_SL_machine_row(SL_name, SL)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_machine_ROM_list(self, SL_name):
        # >> Load Software List catalog
        SL_catalog_dic = fs_load_JSON_file(SL_cat_filename)

        # >> Load Software List ROMs
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + u'.json'
        SL_DB_filename = os.path.join(AML_ADDON_DIR, u'db_SoftwareLists', file_name).decode('utf-8')
        log_info(u'_render_SL_machine_ROM_list() ROMs JSON "{0}"'.format(SL_DB_filename))
        SL_roms = fs_load_JSON_file(SL_DB_filename)

        self._set_Kodi_content()
        for rom_name in SL_roms:
            ROM = SL_roms[rom_name]
            self._render_SL_ROM_row(SL_name, rom_name, ROM)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_machine_row(self, SL_name, SL):
        if SL['rom_count'] == 1:
            display_name = u'{0} ({1} ROM)'.format(SL['display_name'], SL['rom_count'])
        else:
            display_name = u'{0} ({1} ROMs)'.format(SL['display_name'], SL['rom_count'])

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : display_name,        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_2_arg('clist', 'SL', 'SL', SL_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    def _render_SL_ROM_row(self, SL_name, rom_name, ROM):
        display_name = ROM['description']

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : display_name,        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_3_arg('clist', 'SL', 'SL', SL_name, 'ROM', rom_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    #----------------------------------------------------------------------------------------------
    # Render rows (ListItems) 
    #----------------------------------------------------------------------------------------------


    # ---------------------------------------------------------------------------------------------
    # Information display
    # ---------------------------------------------------------------------------------------------
    def _command_view_machine(self, machine_name):
        # >> Read MAME machine information
        MAME_info_dic = fs_load_JSON_file(Main_DB_filename)
        machine = MAME_info_dic[machine_name]

        # --- Make information string ---
        info_text  = u'[COLOR orange]Machine {0}[/COLOR]\n'.format(machine_name)
        info_text += u"[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(machine['cloneof'])
        info_text += u"[COLOR skyblue]coins[/COLOR]: '{0}'\n".format(machine['coins'])
        info_text += u"[COLOR violet]description[/COLOR]: '{0}'\n".format(machine['description'])
        info_text += u"[COLOR skyblue]haveCoin[/COLOR]: '{0}'\n".format(machine['haveCoin'])
        info_text += u"[COLOR skyblue]isbios[/COLOR]: '{0}'\n".format(machine['isbios'])
        info_text += u"[COLOR skyblue]isdevice[/COLOR]: '{0}'\n".format(machine['isdevice'])
        info_text += u"[COLOR skyblue]ismechanical[/COLOR]: '{0}'\n".format(machine['ismechanical'])
        info_text += u"[COLOR violet]manufacturer[/COLOR]: '{0}'\n".format(machine['manufacturer'])
        info_text += u"[COLOR violet]romof[/COLOR]: '{0}'\n".format(machine['romof'])
        info_text += u"[COLOR skyblue]runnable[/COLOR]: '{0}'\n".format(machine['runnable'])
        info_text += u"[COLOR violet]sampleof[/COLOR]: '{0}'\n".format(machine['sampleof'])
        info_text += u"[COLOR violet]sourcefile[/COLOR]: '{0}'\n".format(machine['sourcefile'])
        info_text += u"[COLOR violet]year[/COLOR]: '{0}'\n".format(machine['year'])

        # --- Show information window ---
        window_title = u'Machine Information'
        try:
            xbmc.executebuiltin('ActivateWindow(10147)')
            window = xbmcgui.Window(10147)
            xbmc.sleep(100)
            window.getControl(1).setLabel(window_title)
            window.getControl(5).setText(info_text)
        except:
            log_error('_command_view_machine() Exception rendering INFO window')

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------
    def _set_Kodi_content(self):
        # --- Set content type and sorting methods ---
        # NOTE This code should be move to _gui_* functions which generate
        #      list. Do not place it here because not all commands of the module
        #      need it!
        # Experiment to try to increase the number of views the addon supports. I do not know why
        # programs does not support all views movies do.
        # xbmcplugin.setContent(handle=self.addon_handle, content = 'movies')

        # Adds a sorting method for the media list.
        if self.addon_handle > 0:
            xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
            xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
            xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
            xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

    def _misc_url_1_arg(self, arg_name, arg_value):
        return u'{0}?{1}={2}'.format(self.base_url, arg_name, arg_value)

    def _misc_url_2_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return u'{0}?{1}={2}&{3}={4}'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)

    def _misc_url_3_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, arg_name_3, arg_value_3):
        return u'{0}?{1}={2}&{3}={4}&{5}={6}'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2, arg_name_3, arg_value_3)

    def _misc_url_2_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return u'XBMC.RunPlugin({0}?{1}={2}&{3}={4})'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)
