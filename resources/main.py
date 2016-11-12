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

# --- Python standard library ---
from __future__ import unicode_literals
import os
import urlparse

# --- Kodi stuff ---
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# --- Modules/packages in this plugin ---
from utils_kodi import *
from disk_IO import *

# --- Addon object (used to access settings) ---
__addon_obj__     = xbmcaddon.Addon()
__addon_id__      = __addon_obj__.getAddonInfo('id').decode('utf-8')
__addon_name__    = __addon_obj__.getAddonInfo('name').decode('utf-8')
__addon_version__ = __addon_obj__.getAddonInfo('version').decode('utf-8')
__addon_author__  = __addon_obj__.getAddonInfo('author').decode('utf-8')
__addon_profile__ = __addon_obj__.getAddonInfo('profile').decode('utf-8')
__addon_type__    = __addon_obj__.getAddonInfo('type').decode('utf-8')


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
MAIN_DB_FILE_PATH                = os.path.join(AML_ADDON_DIR, 'MAME_info.json').decode('utf-8')
MAIN_PCLONE_DIC_FILE_PATH        = os.path.join(AML_ADDON_DIR, 'MAME_PClone_dic.json').decode('utf-8')

MACHINES_IDX_FILE_PATH           = os.path.join(AML_ADDON_DIR, 'idx_Machines.json').decode('utf-8')
MACHINES_IDX_NOCOIN_FILE_PATH    = os.path.join(AML_ADDON_DIR, 'idx_Machines_NoCoin.json').decode('utf-8')
MACHINES_IDX_MECHA_FILE_PATH     = os.path.join(AML_ADDON_DIR, 'idx_Machines_Mechanical.json').decode('utf-8')
MACHINES_IDX_DEAD_FILE_PATH      = os.path.join(AML_ADDON_DIR, 'idx_Machines_Dead.json').decode('utf-8')
MACHINES_IDX_CHD_FILE_PATH       = os.path.join(AML_ADDON_DIR, 'idx_Machines_CHD.json').decode('utf-8')

CATALOG_CATVER_FILE_PATH         = os.path.join(AML_ADDON_DIR, 'catalog_catver.json').decode('utf-8')
CATALOG_CATLIST_FILE_PATH        = os.path.join(AML_ADDON_DIR, 'catalog_catlist.json').decode('utf-8')
CATALOG_GENRE_FILE_PATH          = os.path.join(AML_ADDON_DIR, 'catalog_genre.json').decode('utf-8')
CATALOG_MANUFACTURER_FILE_PATH   = os.path.join(AML_ADDON_DIR, 'catalog_manufacturer.json').decode('utf-8')
CATALOG_YEAR_FILE_PATH           = os.path.join(AML_ADDON_DIR, 'catalog_year.json').decode('utf-8')
CATALOG_DRIVER_FILE_PATH         = os.path.join(AML_ADDON_DIR, 'catalog_driver.json').decode('utf-8')
CATALOG_CONTROL_FILE_PATH        = os.path.join(AML_ADDON_DIR, 'catalog_control.json').decode('utf-8')
CATALOG_DISPLAY_TAG_FILE_PATH    = os.path.join(AML_ADDON_DIR, 'catalog_display_tag.json').decode('utf-8')
CATALOG_DISPLAY_TYPE_FILE_PATH   = os.path.join(AML_ADDON_DIR, 'catalog_display_type.json').decode('utf-8')
CATALOG_DISPLAY_ROTATE_FILE_PATH = os.path.join(AML_ADDON_DIR, 'catalog_display_rotate.json').decode('utf-8')
CATALOG_SL_FILE_PATH             = os.path.join(AML_ADDON_DIR, 'catalog_SL.json').decode('utf-8')

SL_cat_filename                  = os.path.join(AML_ADDON_DIR, 'cat_SoftwareLists.json').decode('utf-8')

class Main:
    # --- Object variables ---
    settings = {}

    # ---------------------------------------------------------------------------------------------
    # This is the plugin entry point.
    # ---------------------------------------------------------------------------------------------
    def run_plugin(self):
        # --- Initialise log system ---
        # >> Force DEBUG log level for development.
        # >> Place it before setting loading so settings can be dumped during debugging.
        set_log_level(LOG_DEBUG)

        # --- Fill in settings dictionary using addon_obj.getSetting() ---
        self._get_settings()
        # set_log_level(self.settings['log_level'])

        # --- Some debug stuff for development ---
        log_debug('---------- Called AML Main::run_plugin() ----------')
        log_debug('sys.platform   {0}'.format(sys.platform))
        log_debug('Python version ' + sys.version.replace('\n', ''))
        log_debug('__addon_version__ {0}'.format(__addon_version__))
        for i in range(len(sys.argv)):
            log_debug('sys.argv[{0}] = "{1}"'.format(i, sys.argv[i]))

        # --- Addon data paths creation ---

        # --- Process URL ---
        self.base_url     = sys.argv[0]
        self.addon_handle = int(sys.argv[1])
        args              = urlparse.parse_qs(sys.argv[2][1:])
        log_debug('args = {0}'.format(args))
        # Interestingly, if plugin is called as type executable then args is empty.
        # However, if plugin is called as type video then Kodi adds the following
        # even for the first call: 'content_type': ['video']
        self.content_type = args['content_type'] if 'content_type' in args else None
        log_debug('content_type = {0}'.format(self.content_type))

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
                elif list_name == 'Dead':       self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'CHD':        self._render_machine_clone_list(list_name, parent_name)
            else:
                if list_name == 'Machines':     self._render_machine_parent_list(list_name)
                elif list_name == 'NoCoin':     self._render_machine_parent_list(list_name)
                elif list_name == 'Mechanical': self._render_machine_parent_list(list_name)
                elif list_name == 'Dead':       self._render_machine_parent_list(list_name)
                elif list_name == 'CHD':        self._render_machine_parent_list(list_name)                

        elif 'clist' in args:
            clist_name = args['clist'][0]

            if clist_name == 'Catver':
                if 'category' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['category'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['category'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Catlist':
                if 'category' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['category'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['category'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Genre':
                if 'category' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['category'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['category'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Manufacturer':
                if 'manufacturer' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['manufacturer'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['manufacturer'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Year':
                if 'year' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['year'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['year'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Driver':
                if 'driver' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['driver'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['driver'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Controls':
                if 'control' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['control'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['control'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Display_Tag':
                if 'tag' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['tag'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['tag'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Display_Type':
                if 'type' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['type'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['type'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'Display_Rotate':
                if 'rotate' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['rotate'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['rotate'][0])
                else:                    self._render_indexed_list(clist_name)
            elif clist_name == 'BySL':
                if 'SL' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['SL'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['SL'][0])
                else:                    self._render_indexed_list(clist_name)
            # --- Software Lists are a special case ---
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
            elif command == 'SETUP_PLUGIN':
                self._command_setup_plugin()
            elif command == 'VIEW_MACHINE':
                self._command_view_machine(args['machine_name'][0])
            else:
                log_error('Unknown command "{0}"'.format(command))

        else:
            log_error('Error in URL routing')
            
        # --- So Long, and Thanks for All the Fish ---
        log_debug('Advanced MAME Launcher exit')

    #
    # Get Addon Settings
    #
    def _get_settings(self):
        # --- Paths ---
        self.settings['mame_prog']    = __addon_obj__.getSetting('mame_prog').decode('utf-8')
        self.settings['SL_hash_path'] = __addon_obj__.getSetting('SL_hash_path').decode('utf-8')
        self.settings['rom_path']     = __addon_obj__.getSetting('rom_path').decode('utf-8')
        self.settings['chd_path']     = __addon_obj__.getSetting('chd_path').decode('utf-8')
        self.settings['SL_rom_path']  = __addon_obj__.getSetting('SL_rom_path').decode('utf-8')
        self.settings['assets_path']  = __addon_obj__.getSetting('assets_path').decode('utf-8')

        # --- Advanced ---
        self.settings['log_level']    = int(__addon_obj__.getSetting('log_level'))

        # --- Dump settings for DEBUG ---
        # log_debug('Settings dump BEGIN')
        # for key in sorted(self.settings):
        #     log_debug('{0} --> {1:10s} {2}'.format(key.rjust(21), str(self.settings[key]), type(self.settings[key])))
        # log_debug('Settings dump END')

    # ---------------------------------------------------------------------------------------------
    # Root menu rendering
    # ---------------------------------------------------------------------------------------------
    def _render_root_list(self):
        # >> Code Machines/Manufacturer/SF first. Rest are variations of those three.
        self._render_root_list_row('Machines (with coin slot)',      self._misc_url_1_arg('list',  'Machines'))
        self._render_root_list_row('Machines (no coin slot)',        self._misc_url_1_arg('list',  'NoCoin'))
        self._render_root_list_row('Machines (mechanical)',          self._misc_url_1_arg('list',  'Mechanical'))
        self._render_root_list_row('Machines (dead)',                self._misc_url_1_arg('list',  'Dead'))
        self._render_root_list_row('Machines (with CHDs)',           self._misc_url_1_arg('list',  'CHD'))
        self._render_root_list_row('Machines by Category (Catver)',  self._misc_url_1_arg('clist', 'Catver'))
        self._render_root_list_row('Machines by Category (Catlist)', self._misc_url_1_arg('clist', 'Catlist'))
        self._render_root_list_row('Machines by Category (Genre)',   self._misc_url_1_arg('clist', 'Genre'))
        self._render_root_list_row('Machines by Manufacturer',       self._misc_url_1_arg('clist', 'Manufacturer'))
        self._render_root_list_row('Machines by Year',               self._misc_url_1_arg('clist', 'Year'))
        self._render_root_list_row('Machines by Driver',             self._misc_url_1_arg('clist', 'Driver'))
        self._render_root_list_row('Machines by Control Type',       self._misc_url_1_arg('clist', 'Controls'))
        self._render_root_list_row('Machines by Display Tag',        self._misc_url_1_arg('clist', 'Display_Tag'))
        self._render_root_list_row('Machines by Display Type',       self._misc_url_1_arg('clist', 'Display_Type'))
        self._render_root_list_row('Machines by Display Rotation',   self._misc_url_1_arg('clist', 'Display_Rotate'))
        self._render_root_list_row('Machines by Software List',      self._misc_url_1_arg('clist', 'BySL'))
        self._render_root_list_row('Software Lists',                 self._misc_url_1_arg('clist', 'SL'))
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
        commands.append(('Setup plugin', self._misc_url_1_arg_RunPlugin('command', 'SETUP_PLUGIN'), ))
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
        MAME_info_dic = fs_load_JSON_file(MAIN_DB_FILE_PATH)
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_FILE_PATH)
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_NOCOIN_FILE_PATH)
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_MECHA_FILE_PATH)
        elif list_name == 'Dead':       Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_DEAD_FILE_PATH)
        elif list_name == 'CHD':        Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_CHD_FILE_PATH)

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
        MAME_info_dic = fs_load_JSON_file(MAIN_DB_FILE_PATH)
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_FILE_PATH)
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_NOCOIN_FILE_PATH)
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_MECHA_FILE_PATH)
        elif list_name == 'Dead':       Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_DEAD_FILE_PATH)
        elif list_name == 'CHD':        Machines_PClone_dic = fs_load_JSON_file(MACHINES_IDX_CHD_FILE_PATH)

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
        # --- Mark devices, BIOS and clones ---
        display_name = machine['description']
        if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
        if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
        if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'
        # Do not mark machines working OK
        if   machine['driver_status'] == u'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
        elif machine['driver_status'] == u'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

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
    # Cataloged lists
    #----------------------------------------------------------------------------------------------
    def _render_indexed_list(self, clist_name):
        # >> Load catalog index
        if clist_name == 'Catver':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_CATVER_FILE_PATH)
        elif clist_name == 'Catlist':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_CATLIST_FILE_PATH)
        elif clist_name == 'Genre':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_GENRE_FILE_PATH)
        elif clist_name == 'Manufacturer':
            catalog_name = 'manufacturer'
            catalog_dic = fs_load_JSON_file(CATALOG_MANUFACTURER_FILE_PATH)
        elif clist_name == 'Year':
            catalog_name = 'year'
            catalog_dic = fs_load_JSON_file(CATALOG_YEAR_FILE_PATH)
        elif clist_name == 'Driver':
            catalog_name = 'driver'
            catalog_dic = fs_load_JSON_file(CATALOG_DRIVER_FILE_PATH)
        elif clist_name == 'Controls':
            catalog_name = 'control'
            catalog_dic = fs_load_JSON_file(CATALOG_CONTROL_FILE_PATH)            
        elif clist_name == 'Display_Tag':
            catalog_name = 'tag'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_TAG_FILE_PATH)
        elif clist_name == 'Display_Type':
            catalog_name = 'type'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_TYPE_FILE_PATH)
        elif clist_name == 'Display_Rotate':
            catalog_name = 'rotate'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_ROTATE_FILE_PATH)            
        elif clist_name == 'BySL':
            catalog_name = 'SL'
            catalog_dic = fs_load_JSON_file(CATALOG_SL_FILE_PATH)

        # >> Render categories in catalog index
        self._set_Kodi_content()
        for catalog_key in catalog_dic:
            self._render_indexed_list_row(clist_name, catalog_name, catalog_key)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Renders a Parent list knowing the index (category)
    #
    def _render_indexed_parent_list(self, clist_name, catalog_item_name):
        # >> Load main MAME info DB
        MAME_info_dic = fs_load_JSON_file(MAIN_DB_FILE_PATH)

        # >> Load catalog index
        if clist_name == 'Catver':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_CATVER_FILE_PATH)
        elif clist_name == 'Catlist':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_CATLIST_FILE_PATH)
        elif clist_name == 'Genre':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(CATALOG_GENRE_FILE_PATH)
        elif clist_name == 'Manufacturer':
            catalog_name = 'manufacturer'
            catalog_dic = fs_load_JSON_file(CATALOG_MANUFACTURER_FILE_PATH)
        elif clist_name == 'Year':
            catalog_name = 'year'
            catalog_dic = fs_load_JSON_file(CATALOG_YEAR_FILE_PATH)
        elif clist_name == 'Driver':
            catalog_name = 'driver'
            catalog_dic = fs_load_JSON_file(CATALOG_DRIVER_FILE_PATH)
        elif clist_name == 'Controls':
            catalog_name = 'control'
            catalog_dic = fs_load_JSON_file(CATALOG_CONTROL_FILE_PATH)            
        elif clist_name == 'Display_Tag':
            catalog_name = 'tag'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_TAG_FILE_PATH)
        elif clist_name == 'Display_Type':
            catalog_name = 'type'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_TYPE_FILE_PATH)
        elif clist_name == 'Display_Rotate':
            catalog_name = 'rotate'
            catalog_dic = fs_load_JSON_file(CATALOG_DISPLAY_ROTATE_FILE_PATH)            
        elif clist_name == 'BySL':
            catalog_name = 'SL'
            catalog_dic = fs_load_JSON_file(CATALOG_SL_FILE_PATH)

        # >> Get parents for this category
        Machines_PClone_dic = catalog_dic[catalog_item_name]

        # >> Render parent main list
        self._set_Kodi_content()
        for parent_name in Machines_PClone_dic:
            machine = MAME_info_dic[parent_name]
            self._render_indexed_machine_row(parent_name, machine, True, clist_name, catalog_name, catalog_item_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_indexed_clone_list(self, clist_name, catalog_item_name, parent_name):
        # >> Load main MAME info DB
        MAME_info_dic = fs_load_JSON_file(MAIN_DB_FILE_PATH)

        # >> Load main PClone dictionary
        main_pclone_dic = fs_load_JSON_file(MAIN_PCLONE_DIC_FILE_PATH)

        # >> Get catalog name
        if   clist_name == 'Catver':         catalog_name = 'category'
        elif clist_name == 'Catlist':        catalog_name = 'category'
        elif clist_name == 'Genre':          catalog_name = 'category'
        elif clist_name == 'Manufacturer':   catalog_name = 'manufacturer'
        elif clist_name == 'Year':           catalog_name = 'year'
        elif clist_name == 'Driver':         catalog_name = 'driver'
        elif clist_name == 'Controls':       catalog_name = 'control'
        elif clist_name == 'Display_Tag':    catalog_name = 'tag'
        elif clist_name == 'Display_Type':   catalog_name = 'type'
        elif clist_name == 'Display_Rotate': catalog_name = 'rotate'
        elif clist_name == 'BySL':           catalog_name = 'SL'

        # >> Render parent first
        self._set_Kodi_content()
        machine = MAME_info_dic[parent_name]
        self._render_indexed_machine_row(parent_name, machine, False, clist_name, catalog_name, catalog_item_name)

        # >> Render clones belonging to parent in this category
        for p_name in main_pclone_dic[parent_name]:
            machine = MAME_info_dic[p_name]
            self._render_indexed_machine_row(p_name, machine, False, clist_name, catalog_name, catalog_item_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    #
    #
    def _render_indexed_list_row(self, clist_name, catalog_name, catalog_key):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(catalog_key, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : catalog_key,        
                                   'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_2_arg('clist', clist_name, catalog_name, catalog_key)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    #
    #
    #
    def _render_indexed_machine_row(self, machine_name, machine, is_parent_list, clist_name, catalog_name, catalog_item_name):
        # --- Mark devices, BIOS and clones ---
        display_name = machine['description']
        if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
        if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
        if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'
        # Do not mark machines working OK
        if   machine['driver_status'] == u'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
        elif machine['driver_status'] == u'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

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
            URL = self._misc_url_3_arg('clist', clist_name, catalog_name, catalog_item_name, 'parent', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
        else:
            URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine_name', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    #----------------------------------------------------------------------------------------------
    # Software Lists
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

    # ---------------------------------------------------------------------------------------------
    # Information display
    # ---------------------------------------------------------------------------------------------
    def _command_view_machine(self, machine_name):
        # >> Read MAME machine information
        MAME_info_dic = fs_load_JSON_file(MAIN_DB_FILE_PATH)
        machine = MAME_info_dic[machine_name]

        # --- Make information string ---
        info_text  = u'[COLOR orange]Machine {0}[/COLOR]\n'.format(machine_name)
        info_text += u"[COLOR violet]catlist[/COLOR]: '{0}'\n".format(machine['catlist'])
        info_text += u"[COLOR violet]catver[/COLOR]: '{0}'\n".format(machine['catver'])        
        info_text += u"[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(machine['cloneof'])
        info_text += u"[COLOR skyblue]coins[/COLOR]: {0}\n".format(machine['coins'])
        info_text += u"[COLOR skyblue]control_type[/COLOR]: {0}\n".format(machine['control_type'])
        info_text += u"[COLOR violet]description[/COLOR]: '{0}'\n".format(machine['description'])
        info_text += u"[COLOR skyblue]display_rotate[/COLOR]: {0}\n".format(machine['display_rotate'])
        info_text += u"[COLOR skyblue]display_tag[/COLOR]: {0}\n".format(machine['display_tag'])
        info_text += u"[COLOR skyblue]display_type[/COLOR]: {0}\n".format(machine['display_type'])
        info_text += u"[COLOR violet]driver_status[/COLOR]: '{0}'\n".format(machine['driver_status'])
        info_text += u"[COLOR violet]genre[/COLOR]: '{0}'\n".format(machine['genre'])
        info_text += u"[COLOR skyblue]hasCHD[/COLOR]: {0}\n".format(machine['hasCHD'])
        info_text += u"[COLOR skyblue]hasCoin[/COLOR]: {0}\n".format(machine['hasCoin'])
        info_text += u"[COLOR skyblue]hasROM[/COLOR]: {0}\n".format(machine['hasROM'])
        info_text += u"[COLOR skyblue]isBIOS[/COLOR]: {0}\n".format(machine['isBIOS'])
        info_text += u"[COLOR skyblue]isDead[/COLOR]: {0}\n".format(machine['isDead'])
        info_text += u"[COLOR skyblue]isDevice[/COLOR]: {0}\n".format(machine['isDevice'])
        info_text += u"[COLOR skyblue]isMechanical[/COLOR]: {0}\n".format(machine['isMechanical'])
        info_text += u"[COLOR violet]manufacturer[/COLOR]: '{0}'\n".format(machine['manufacturer'])
        info_text += u"[COLOR violet]romof[/COLOR]: '{0}'\n".format(machine['romof'])
        info_text += u"[COLOR violet]sampleof[/COLOR]: '{0}'\n".format(machine['sampleof'])
        info_text += u"[COLOR skyblue]softwarelists[/COLOR]: {0}\n".format(machine['softwarelists'])
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
    # Setup plugin databases
    # ---------------------------------------------------------------------------------------------
    def _command_setup_plugin(self):
        kodi_dialog_OK('Setting up plugin')

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------
    def _set_Kodi_all_sorting_methods(self):
        if self.addon_handle < 0: return
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

    # ---------------------------------------------------------------------------------------------
    # Misc URL building functions
    # ---------------------------------------------------------------------------------------------
    def _misc_url_1_arg(self, arg_name, arg_value):
        return u'{0}?{1}={2}'.format(self.base_url, arg_name, arg_value)

    def _misc_url_2_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return u'{0}?{1}={2}&{3}={4}'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)

    def _misc_url_3_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, arg_name_3, arg_value_3):
        return u'{0}?{1}={2}&{3}={4}&{5}={6}'.format(self.base_url, arg_name_1, arg_value_1, 
                                                                    arg_name_2, arg_value_2, arg_name_3, arg_value_3)

    def _misc_url_1_arg_RunPlugin(self, arg_name_1, arg_value_1):
        return u'XBMC.RunPlugin({0}?{1}={2})'.format(self.base_url, arg_name_1, arg_value_1)

    def _misc_url_2_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return u'XBMC.RunPlugin({0}?{1}={2}&{3}={4})'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)
