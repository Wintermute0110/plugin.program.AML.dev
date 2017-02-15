# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher main script file
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
import os
import urlparse
import subprocess

# --- Kodi stuff ---
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# --- Modules/packages in this plugin ---
from utils import *
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
# _PATH is a filename | _DIR is a directory
ADDONS_DATA_DIR = FileName('special://profile/addon_data')
PLUGIN_DATA_DIR = ADDONS_DATA_DIR.pjoin(__addon_id__)
BASE_DIR        = FileName('special://profile')
HOME_DIR        = FileName('special://home')
KODI_FAV_PATH   = FileName('special://profile/favourites.xml')
ADDONS_DIR      = HOME_DIR.pjoin('addons')
AML_ADDON_DIR   = ADDONS_DIR.pjoin(__addon_id__)
ICON_IMG_PATH   = AML_ADDON_DIR.pjoin('icon.png')
FANART_IMG_PATH = AML_ADDON_DIR.pjoin('fanart.jpg')

# --- Plugin database indices ---
class AML_Paths:
    def __init__(self):
        # >> MAME XML, main database and main PClone list
        self.MAME_XML_PATH               = PLUGIN_DATA_DIR.pjoin('MAME.xml')
        self.MAME_STDOUT_PATH            = PLUGIN_DATA_DIR.pjoin('MAME_stdout.log')
        self.MAME_STDERR_PATH            = PLUGIN_DATA_DIR.pjoin('MAME_stderr.log')
        self.MAIN_DB_PATH                = PLUGIN_DATA_DIR.pjoin('MAME_main_db.json')
        self.MAIN_PCLONE_DIC_PATH        = PLUGIN_DATA_DIR.pjoin('MAME_PClone_dic.json')
        self.MAIN_CONTROL_PATH           = PLUGIN_DATA_DIR.pjoin('MAME_control_dic.json')
        self.MAIN_ASSETS_DB_PATH         = PLUGIN_DATA_DIR.pjoin('MAME_assets_db.json')

        # >> Indices
        self.MACHINES_IDX_PATH           = PLUGIN_DATA_DIR.pjoin('idx_Machines.json')
        self.MACHINES_IDX_NOCOIN_PATH    = PLUGIN_DATA_DIR.pjoin('idx_Machines_NoCoin.json')
        self.MACHINES_IDX_MECHA_PATH     = PLUGIN_DATA_DIR.pjoin('idx_Machines_Mechanical.json')
        self.MACHINES_IDX_DEAD_PATH      = PLUGIN_DATA_DIR.pjoin('idx_Machines_Dead.json')
        self.MACHINES_IDX_NOROMS_PATH    = PLUGIN_DATA_DIR.pjoin('idx_Machines_NoROM.json')
        self.MACHINES_IDX_CHD_PATH       = PLUGIN_DATA_DIR.pjoin('idx_Machines_CHD.json')
        self.MACHINES_IDX_SAMPLES_PATH   = PLUGIN_DATA_DIR.pjoin('idx_Machines_Samples.json')
        self.MACHINES_IDX_BIOS_PATH      = PLUGIN_DATA_DIR.pjoin('idx_Machines_BIOS.json')
        self.MACHINES_IDX_DEVICES_PATH   = PLUGIN_DATA_DIR.pjoin('idx_Machines_Devices.json')

        # >> Catalogs
        self.CATALOG_CATVER_PATH         = PLUGIN_DATA_DIR.pjoin('catalog_catver.json')
        self.CATALOG_CATLIST_PATH        = PLUGIN_DATA_DIR.pjoin('catalog_catlist.json')
        self.CATALOG_GENRE_PATH          = PLUGIN_DATA_DIR.pjoin('catalog_genre.json')
        self.CATALOG_NPLAYERS_PATH       = PLUGIN_DATA_DIR.pjoin('catalog_nplayers.json')
        self.CATALOG_MANUFACTURER_PATH   = PLUGIN_DATA_DIR.pjoin('catalog_manufacturer.json')
        self.CATALOG_YEAR_PATH           = PLUGIN_DATA_DIR.pjoin('catalog_year.json')
        self.CATALOG_DRIVER_PATH         = PLUGIN_DATA_DIR.pjoin('catalog_driver.json')
        self.CATALOG_CONTROL_PATH        = PLUGIN_DATA_DIR.pjoin('catalog_control.json')
        self.CATALOG_DISPLAY_TAG_PATH    = PLUGIN_DATA_DIR.pjoin('catalog_display_tag.json')
        self.CATALOG_DISPLAY_TYPE_PATH   = PLUGIN_DATA_DIR.pjoin('catalog_display_type.json')
        self.CATALOG_DISPLAY_ROTATE_PATH = PLUGIN_DATA_DIR.pjoin('catalog_display_rotate.json')
        self.CATALOG_DEVICE_LIST_PATH    = PLUGIN_DATA_DIR.pjoin('catalog_device_list.json')
        self.CATALOG_SL_PATH             = PLUGIN_DATA_DIR.pjoin('catalog_SL.json')

        # >> Software Lists
        self.SL_DB_DIR                   = PLUGIN_DATA_DIR.pjoin('db_SoftwareLists')
        self.SL_INDEX_PATH               = PLUGIN_DATA_DIR.pjoin('SoftwareLists_index.json')
        self.SL_MACHINES_PATH            = PLUGIN_DATA_DIR.pjoin('SoftwareLists_machines.json')
        
        # >> Favourites
        self.FAV_MACHINES_PATH           = PLUGIN_DATA_DIR.pjoin('Favourite_Machines.json')
        self.FAV_SL_ROMS_PATH            = PLUGIN_DATA_DIR.pjoin('Favourite_SL_ROMs.json')
PATHS = AML_Paths()

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
        log_debug('---------- Called AML Main::run_plugin() constructor ----------')
        log_debug('sys.platform   {0}'.format(sys.platform))
        log_debug('Python version ' + sys.version.replace('\n', ''))
        log_debug('__addon_version__ {0}'.format(__addon_version__))
        for i in range(len(sys.argv)): log_debug('sys.argv[{0}] = "{1}"'.format(i, sys.argv[i]))

        # --- Addon data paths creation ---
        if not PLUGIN_DATA_DIR.exists(): PLUGIN_DATA_DIR.makedirs()
        if not PATHS.SL_DB_DIR.exists(): PATHS.SL_DB_DIR.makedirs()

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
        args_size = len(args)
        if args_size == 0:
            self._render_root_list()
            log_debug('Advanced MAME Launcher exit (addon root)')
            return

        # ~~~ Routing step 2 ~~~
        if 'list' in args and not 'command' in args:
            list_name = args['list'][0]
            if 'parent' in args:
                parent_name = args['parent'][0]
                self._render_machine_clone_list(list_name, parent_name)
            else:
                self._render_machine_parent_list(list_name)

        elif 'clist' in args and not 'command' in args:
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
            elif clist_name == 'NPlayers':
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
            elif clist_name == 'Devices':
                if 'device' in args:
                    if 'parent' in args: self._render_indexed_clone_list(clist_name, args['device'][0], args['parent'][0])
                    else:                self._render_indexed_parent_list(clist_name, args['device'][0])
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
                machine  = args['machine'][0]
                location = args['location'][0] if 'location' in args else ''
                log_info('Launching MAME machine "{0}"'.format(machine, location))
                self._run_machine(machine, location)
            elif command == 'LAUNCH_SL':
                SL_name  = args['SL'][0]
                ROM_name = args['ROM'][0]
                log_info('Launching SL machine "{0}" (ROM "{1}")'.format(SL_name, ROM_name))
                self._run_SL_machine(SL_name, ROM_name)
            elif command == 'SETUP_PLUGIN':
                self._command_setup_plugin()
            elif command == 'VIEW':
                machine = args['machine'][0] if 'machine' in args else ''
                SL      = args['SL'][0]      if 'SL' in args else ''
                ROM     = args['ROM'][0]     if 'ROM' in args else ''
                self._command_view(machine, SL, ROM)
            elif command == 'DISPLAY_SETTINGS':
                clist   = args['clist'][0]   if 'clist' in args else ''
                catalog = args['catalog'][0] if 'catalog' in args else ''
                machine = args['machine'][0] if 'machine' in args else ''
                self._command_display_settings(clist, catalog, machine)
            elif command == 'ADD_MAME_FAV':
                self._command_add_mame_fav(args['machine'][0])
            elif command == 'DELETE_MAME_FAV':
                self._command_delete_mame_fav(args['machine'][0])
            elif command == 'SHOW_MAME_FAVS':
                self._command_show_mame_fav()
            elif command == 'ADD_SL_FAV':
                self._command_add_sl_fav(args['SL'][0], args['ROM'][0])
            elif command == 'DELETE_SL_FAV':
                self._command_delete_sl_fav(args['SL'][0], args['ROM'][0])
            elif command == 'SHOW_SL_FAVS':
                self._command_show_sl_fav()
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
        self.settings['mame_prog']               = __addon_obj__.getSetting('mame_prog').decode('utf-8')
        self.settings['rom_path']                = __addon_obj__.getSetting('rom_path').decode('utf-8')

        self.settings['assets_path']             = __addon_obj__.getSetting('assets_path').decode('utf-8')
        self.settings['SL_hash_path']            = __addon_obj__.getSetting('SL_hash_path').decode('utf-8')
        self.settings['SL_rom_path']             = __addon_obj__.getSetting('SL_rom_path').decode('utf-8')
        self.settings['chd_path']                = __addon_obj__.getSetting('chd_path').decode('utf-8')
        self.settings['samples_path']            = __addon_obj__.getSetting('samples_path').decode('utf-8')
        self.settings['catver_path']             = __addon_obj__.getSetting('catver_path').decode('utf-8')
        self.settings['catlist_path']            = __addon_obj__.getSetting('catlist_path').decode('utf-8')
        self.settings['genre_path']              = __addon_obj__.getSetting('genre_path').decode('utf-8')
        self.settings['nplayers_path']           = __addon_obj__.getSetting('nplayers_path').decode('utf-8')

        # --- Display ---
        self.settings['display_hide_nonworking'] = True if __addon_obj__.getSetting('display_hide_nonworking') == 'true' else False
        self.settings['display_hide_imperfect']  = True if __addon_obj__.getSetting('display_hide_imperfect') == 'true' else False
        self.settings['display_available_only']  = True if __addon_obj__.getSetting('display_available_only') == 'true' else False

        # --- Advanced ---
        self.settings['log_level']               = int(__addon_obj__.getSetting('log_level'))

        # --- Dump settings for DEBUG ---
        # log_debug('Settings dump BEGIN')
        # for key in sorted(self.settings):
        #     log_debug('{0} --> {1:10s} {2}'.format(key.rjust(21), str(self.settings[key]), type(self.settings[key])))
        # log_debug('Settings dump END')

    # ---------------------------------------------------------------------------------------------
    # Root menu rendering
    # ---------------------------------------------------------------------------------------------
    # NOTE Devices are excluded from main PClone list.
    def _render_root_list(self):
        # >> Code Machines/Manufacturer/SF first. Rest are variations of those three.
        self._render_root_list_row('Machines (with coin slot)',       self._misc_url_1_arg('list',  'Machines'))
        self._render_root_list_row('Machines (no coin slot)',         self._misc_url_1_arg('list',  'NoCoin'))
        self._render_root_list_row('Machines (mechanical)',           self._misc_url_1_arg('list',  'Mechanical'))
        self._render_root_list_row('Machines (dead)',                 self._misc_url_1_arg('list',  'Dead'))
        self._render_root_list_row('Machines [with no ROMs]',         self._misc_url_1_arg('list',  'NoROM'))
        self._render_root_list_row('Machines [with CHDs]',            self._misc_url_1_arg('list',  'CHD'))
        self._render_root_list_row('Machines [with Samples]',         self._misc_url_1_arg('list',  'Samples'))
        self._render_root_list_row('Machines [BIOS]',                 self._misc_url_1_arg('list',  'BIOS'))
        # self._render_root_list_row('Machines [Devices]',              self._misc_url_1_arg('list',  'Devices'))
        self._render_root_list_row('Machines by Category (Catver)',   self._misc_url_1_arg('clist', 'Catver'))
        self._render_root_list_row('Machines by Category (Catlist)',  self._misc_url_1_arg('clist', 'Catlist'))
        self._render_root_list_row('Machines by Category (Genre)',    self._misc_url_1_arg('clist', 'Genre'))
        self._render_root_list_row('Machines by Number of players',   self._misc_url_1_arg('clist', 'NPlayers'))
        self._render_root_list_row('Machines by Manufacturer',        self._misc_url_1_arg('clist', 'Manufacturer'))
        self._render_root_list_row('Machines by Year',                self._misc_url_1_arg('clist', 'Year'))
        self._render_root_list_row('Machines by Driver',              self._misc_url_1_arg('clist', 'Driver'))
        self._render_root_list_row('Machines by Control Type',        self._misc_url_1_arg('clist', 'Controls'))
        self._render_root_list_row('Machines by Display Tag',         self._misc_url_1_arg('clist', 'Display_Tag'))
        self._render_root_list_row('Machines by Display Type',        self._misc_url_1_arg('clist', 'Display_Type'))
        self._render_root_list_row('Machines by Display Rotation',    self._misc_url_1_arg('clist', 'Display_Rotate'))
        self._render_root_list_row('Machines by Device',              self._misc_url_1_arg('clist', 'Devices'))
        self._render_root_list_row('Machines by Software List',       self._misc_url_1_arg('clist', 'BySL'))
        self._render_root_list_row('Software Lists',                  self._misc_url_1_arg('clist', 'SL'))
        self._render_root_list_row('<Favourite MAME machines>',       self._misc_url_1_arg('command', 'SHOW_MAME_FAVS'))
        self._render_root_list_row('<Favourite Software Lists ROMs>', self._misc_url_1_arg('command', 'SHOW_SL_FAVS'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_root_list_row(self, root_name, root_URL):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(root_name, iconImage = icon)

        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : root_name, 'Overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        commands.append(('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW'), ))
        commands.append(('Setup plugin', self._misc_url_1_arg_RunPlugin('command', 'SETUP_PLUGIN'), ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)', ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__), ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = root_URL, listitem = listitem, isFolder = True)

    #----------------------------------------------------------------------------------------------
    # Indexed machines
    #----------------------------------------------------------------------------------------------
    #
    # Render a list of parent machines that have been indexed.
    # A) If a machine has no clones it may be launched from this list.
    # B) If a machine has clones then print the number of clones.
    #
    def _render_machine_parent_list(self, list_name):
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load main MAME info DB and PClone index
        loading_ticks_start = time.time()
        MAME_db_dic         = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic     = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        Machines_index_dic  = self._load_indexed_pclone_dic(list_name)
        loading_ticks_end = time.time()

        # >> Render parent main list
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        for parent_name, idx_dic in Machines_index_dic.iteritems():
            num_clones = idx_dic['num_clones']
            clone_list = idx_dic['machines']
            machine = MAME_db_dic[parent_name]
            assets  = MAME_assets_dic[parent_name]
            # >> Skip non-working/imperfect machines (Python 'and' and 'or' are short-circuit)
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_machine_row(parent_name, machine, assets, True, list_name, num_clones)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading seconds   {0}'.format(loading_ticks_end - loading_ticks_start))
        log_debug('Rendering seconds {0}'.format(rendering_ticks_end - rendering_ticks_start))

    #
    # Render a Parent/Clone list of machines.
    # If user clicks in this list then ROM is launched.
    #
    def _render_machine_clone_list(self, list_name, parent_name):
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load main MAME info DB and PClone index
        loading_ticks_start = time.time()
        MAME_db_dic        = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic    = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        Machines_index_dic = self._load_indexed_pclone_dic(list_name)
        loading_ticks_end = time.time()

        # >> Render parent first
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        num_clones = Machines_index_dic[parent_name]['num_clones']
        clone_list = Machines_index_dic[parent_name]['machines']
        machine = MAME_db_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_machine_row(parent_name, machine, assets, False)
        # >> Render clones
        for clone_name in clone_list:
            machine = MAME_db_dic[clone_name]
            assets  = MAME_assets_dic[clone_name]
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_machine_row(clone_name, machine, assets, False)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading seconds   {0}'.format(loading_ticks_end - loading_ticks_start))
        log_debug('Rendering seconds {0}'.format(rendering_ticks_end - rendering_ticks_start))

    #
    # Render parent or clone machines.
    # Information and artwork/assets are the same for all machines.
    # URL is different: parent URL leads to clones, clone URL launchs machine.
    #
    def _render_machine_row(self, machine_name, machine, machine_assets, flag_parent_list, list_name = '', num_clones = 0):
        display_name = machine['description']

        # --- Render a Parent only list ---
        if flag_parent_list and num_clones > 0:
            # >> Machine has clones
            display_name += '  [COLOR orange]({0} clones)[/COLOR]'.format(num_clones)
        else:
            # >> Machine has no clones
            # --- Mark Status ---
            status = '{0}{1}{2}{3}{4}'.format(machine['status_ROM'], machine['status_CHD'],
                                              machine['status_SAM'], machine['status_SL'],
                                              machine['status_Device'])
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)

            # --- Mark Devices, BIOS and clones ---
            if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
            if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
            if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

            # --- Mark driver status: Good (no mark), Imperfect, Preliminar ---
            if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
            elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

        # --- Assets/artwork ---
        thumb_path      = machine_assets['title']
        thumb_fanart    = machine_assets['snap']
        thumb_banner    = machine_assets['marquee']
        thumb_clearlogo = machine_assets['clearlogo']
        thumb_poster    = machine_assets['flyer']

        # --- Create listitem row ---
        default_icon = 'DefaultFolder.png'
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)

        # --- Metadata ---
        # >> Make all the infotables compatible with Advanced Emulator Launcher
        listitem.setInfo('video', {'title'   : display_name,            'year'    : machine['year'],
                                   'genre'   : '',                      'plot'    : '',
                                   'studio'  : machine['manufacturer'], 'rating'  : '',
                                   'trailer' : '',                      'overlay' : ICON_OVERLAY })
        listitem.setProperty('platform', 'MAME')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title'     : machine_assets['title'],   'snap'    : machine_assets['snap'],
                         'boxfront'  : machine_assets['cabinet'], 'boxback' : machine_assets['cpanel'], 
                         'cartridge' : machine_assets['PCB'],     'flyer'   : machine_assets['flyer'] })

        # >> Kodi official artwork fields
        listitem.setArt({'icon'   : thumb_path,   'fanart'    : thumb_fanart,
                         'banner' : thumb_banner, 'clearlogo' : thumb_clearlogo, 'poster' : thumb_poster })

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_2_arg_RunPlugin('command', 'VIEW', 'machine', machine_name)
        URL_display = self._misc_url_3_arg_RunPlugin('command', 'DISPLAY_SETTINGS', 'clist', list_name, 'machine', machine_name)
        URL_fav = self._misc_url_2_arg_RunPlugin('command', 'ADD_MAME_FAV', 'machine', machine_name)
        commands.append(('View', URL_view ))
        commands.append(('Display settings', URL_display ))
        commands.append(('Add machine to MAME Favourites', URL_fav ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        if flag_parent_list:
            # >> If machine has no clones then machine can be launched
            if num_clones > 0:
                URL = self._misc_url_2_arg('list', list_name, 'parent', machine_name)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
            # >> If not PClone list can be browsed in
            else:
                URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine', machine_name)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)
        else:
            URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    def _load_indexed_pclone_dic(self, list_name):
        if   list_name == 'Machines':   Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_PATH.getPath())
        elif list_name == 'NoCoin':     Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_NOCOIN_PATH.getPath())
        elif list_name == 'Mechanical': Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_MECHA_PATH.getPath())
        elif list_name == 'Dead':       Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEAD_PATH.getPath())
        elif list_name == 'NoROM':      Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_NOROMS_PATH.getPath())
        elif list_name == 'CHD':        Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_CHD_PATH.getPath())
        elif list_name == 'Samples':    Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_SAMPLES_PATH.getPath())
        elif list_name == 'BIOS':       Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_BIOS_PATH.getPath())
        elif list_name == 'Devices':    Machines_index_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEVICES_PATH.getPath())

        return Machines_index_dic

    #----------------------------------------------------------------------------------------------
    # Cataloged machines
    #----------------------------------------------------------------------------------------------
    def _render_indexed_list(self, clist_name):
        log_error('_render_indexed_list() Starting ...')
        # >> Load catalog index
        catalog_name = self._get_catalog_name(clist_name)
        catalog_dic = self._get_cataloged_dic(clist_name)

        # >> Render categories in catalog index
        self._set_Kodi_all_sorting_methods_and_size()
        for catalog_key, catalog_value in catalog_dic.iteritems():
            self._render_indexed_list_row(clist_name, catalog_name, catalog_key, catalog_value['num_machines'])
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Renders a Parent list knowing the generalised category (cataloged filter)
    #
    def _render_indexed_parent_list(self, clist_name, catalog_item_name):
        log_error('_render_indexed_parent_list() Starting ...')
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load main MAME info DB
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())

        # >> Load catalog index
        catalog_name = self._get_catalog_name(clist_name)
        catalog_dic = self._get_cataloged_dic(clist_name)

        # >> Get parents for this category
        parent_machines_list = catalog_dic[catalog_item_name]['machines']

        # >> Render parent main list
        self._set_Kodi_all_sorting_methods()
        for parent_name in parent_machines_list:
            num_clones = len(main_pclone_dic[parent_name])
            machine = MAME_db_dic[parent_name]
            assets  = MAME_assets_dic[parent_name]
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_indexed_machine_row(parent_name, machine, assets, True, 
                                             clist_name, catalog_name, catalog_item_name, num_clones)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_indexed_clone_list(self, clist_name, catalog_item_name, parent_name):
        log_error('_render_indexed_clone_list() Starting ...')
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load main MAME info DB
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())

        # >> Get catalog name
        catalog_name = self._get_catalog_name(clist_name)

        # >> Render parent first
        self._set_Kodi_all_sorting_methods()
        machine = MAME_db_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_indexed_machine_row(parent_name, machine, assets, False, clist_name, catalog_name, catalog_item_name)

        # >> Render clones belonging to parent in this category
        for p_name in main_pclone_dic[parent_name]:
            machine = MAME_db_dic[p_name]
            assets  = MAME_assets_dic[p_name]
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_indexed_machine_row(p_name, machine, assets, False, clist_name, catalog_name, catalog_item_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_indexed_list_row(self, clist_name, catalog_name, catalog_key, num_machines):
        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        ICON_OVERLAY = 6
        title_str = '{0} [COLOR orange]({1} machines)[/COLOR]'.format(catalog_key, num_machines)

        listitem = xbmcgui.ListItem(title_str, iconImage = icon)
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : title_str, 'Overlay' : ICON_OVERLAY, 'size' : num_machines})

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_1_arg_RunPlugin('command', 'VIEW')
        commands.append(('View', URL_view ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_2_arg('clist', clist_name, catalog_name, catalog_key)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    def _render_indexed_machine_row(self, machine_name, machine, machine_assets, flag_parent_list,
                                    clist_name, catalog_name, catalog_item_name, num_clones = 0):
        display_name = machine['description']

        # --- Render a Parent only list ---
        if flag_parent_list and num_clones > 0:
            # >> Machine has clones
            display_name += ' [COLOR orange] ({0} clones)[/COLOR]'.format(num_clones)
        else:
            # >> Machine has no clones
            # --- Mark Status ---
            status = '{0}{1}{2}{3}{4}'.format(machine['status_ROM'], machine['status_CHD'],
                                              machine['status_SAM'], machine['status_SL'],
                                              machine['status_Device'])
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)

            # --- Mark Devices, BIOS and clones ---
            if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
            if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
            if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

            # --- Mark driver status: Good (no mark), Imperfect, Preliminar ---
            if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
            elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

        # --- Assets/artwork ---
        thumb_path      = machine_assets['title']
        thumb_fanart    = machine_assets['snap']
        thumb_banner    = machine_assets['marquee']
        thumb_clearlogo = machine_assets['clearlogo']
        thumb_poster    = machine_assets['flyer']

        # --- Create listitem row ---
        default_icon = 'DefaultFolder.png'
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)

        # --- Metadata ---
        # >> Make all the infotables compatible with Advanced Emulator Launcher
        listitem.setInfo('video', {'title'   : display_name,            'year'    : machine['year'],
                                   'genre'   : '',                      'plot'    : '',
                                   'studio'  : machine['manufacturer'], 'rating'  : '',
                                   'trailer' : '',                      'overlay' : ICON_OVERLAY})
        listitem.setProperty('platform', 'MAME')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title'     : machine_assets['title'],   'snap'    : machine_assets['snap'],
                         'boxfront'  : machine_assets['cabinet'], 'boxback' : machine_assets['cpanel'],
                         'cartridge' : machine_assets['PCB'],     'flyer'   : machine_assets['flyer'] })

        # >> Kodi official artwork fields
        listitem.setArt({'icon'   : thumb_path,   'fanart'    : thumb_fanart,
                         'banner' : thumb_banner, 'clearlogo' : thumb_clearlogo, 'poster' : thumb_poster })

        # --- Create context menu ---
        commands = []
        URL_view    = self._misc_url_2_arg_RunPlugin('command', 'VIEW', 'machine', machine_name)
        URL_display = self._misc_url_4_arg_RunPlugin('command', 'DISPLAY_SETTINGS', 
                                                     'clist', clist_name, 'catalog', catalog_name, 'machine', machine_name)
        URL_fav = self._misc_url_2_arg_RunPlugin('command', 'ADD_MAME_FAV', 'machine', machine_name)
        commands.append(('View',  URL_view ))
        commands.append(('Display settings', URL_display ))
        commands.append(('Add machine to MAME Favourites', URL_fav ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        if flag_parent_list:
            # >> If machine has no clones then machine can be launched
            if num_clones > 0:
                URL = self._misc_url_3_arg('clist', clist_name, catalog_name, catalog_item_name, 'parent', machine_name)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
            # >> If not PClone list can be browsed in
            else:
                URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine', machine_name)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)
        else:
            URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine', machine_name)
            xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    def _get_catalog_name(self, clist_name):
        if   clist_name == 'Catver':         catalog_name = 'category'
        elif clist_name == 'Catlist':        catalog_name = 'category'
        elif clist_name == 'Genre':          catalog_name = 'category'
        elif clist_name == 'NPlayers':       catalog_name = 'category'
        elif clist_name == 'Manufacturer':   catalog_name = 'manufacturer'
        elif clist_name == 'Year':           catalog_name = 'year'
        elif clist_name == 'Driver':         catalog_name = 'driver'
        elif clist_name == 'Controls':       catalog_name = 'control'
        elif clist_name == 'Display_Tag':    catalog_name = 'tag'
        elif clist_name == 'Display_Type':   catalog_name = 'type'
        elif clist_name == 'Display_Rotate': catalog_name = 'rotate'
        elif clist_name == 'Devices':        catalog_name = 'device'
        elif clist_name == 'BySL':           catalog_name = 'SL'

        return catalog_name

    def _get_cataloged_dic(self, clist_name):
        if   clist_name == 'Catver':         catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATVER_PATH.getPath())
        elif clist_name == 'Catlist':        catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATLIST_PATH.getPath())
        elif clist_name == 'Genre':          catalog_dic = fs_load_JSON_file(PATHS.CATALOG_GENRE_PATH.getPath())
        elif clist_name == 'NPlayers':       catalog_dic = fs_load_JSON_file(PATHS.CATALOG_NPLAYERS_PATH.getPath())
        elif clist_name == 'Manufacturer':   catalog_dic = fs_load_JSON_file(PATHS.CATALOG_MANUFACTURER_PATH.getPath())
        elif clist_name == 'Year':           catalog_dic = fs_load_JSON_file(PATHS.CATALOG_YEAR_PATH.getPath())
        elif clist_name == 'Driver':         catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DRIVER_PATH.getPath())
        elif clist_name == 'Controls':       catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CONTROL_PATH.getPath())
        elif clist_name == 'Display_Tag':    catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TAG_PATH.getPath())
        elif clist_name == 'Display_Type':   catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TYPE_PATH.getPath())
        elif clist_name == 'Display_Rotate': catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_ROTATE_PATH.getPath())
        elif clist_name == 'Devices':        catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DEVICE_LIST_PATH.getPath())
        elif clist_name == 'BySL':           catalog_dic = fs_load_JSON_file(PATHS.CATALOG_SL_PATH.getPath())

        return catalog_dic

    #----------------------------------------------------------------------------------------------
    # Software Lists
    #----------------------------------------------------------------------------------------------
    def _render_SL_machine_list(self):
        # >> Load Software List catalog
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())

        self._set_Kodi_all_sorting_methods()
        for SL_name in SL_catalog_dic:
            SL = SL_catalog_dic[SL_name]
            self._render_SL_machine_row(SL_name, SL)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_machine_ROM_list(self, SL_name):
        # >> Load Software List catalog
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())

        # >> Load Software List ROMs
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        log_info('_render_SL_machine_ROM_list() ROMs JSON "{0}"'.format(SL_DB_FN.getPath()))
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())

        self._set_Kodi_all_sorting_methods()
        for rom_name in SL_roms:
            ROM = SL_roms[rom_name]
            self._render_SL_ROM_row(SL_name, rom_name, ROM)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_machine_row(self, SL_name, SL):
        if SL['chd_count'] == 0:
            if SL['rom_count'] == 1: display_name = '{0}  [COLOR orange]({1} ROM)[/COLOR]'.format(SL['display_name'], SL['rom_count'])
            else:                    display_name = '{0}  [COLOR orange]({1} ROMs)[/COLOR]'.format(SL['display_name'], SL['rom_count'])
        elif SL['rom_count'] == 0:
            if SL['chd_count'] == 1: display_name = '{0}  [COLOR orange]({1} CHD)[/COLOR]'.format(SL['display_name'], SL['chd_count'])
            else:                    display_name = '{0}  [COLOR orange]({1} CHDs)[/COLOR]'.format(SL['display_name'], SL['chd_count'])
        else:
            display_name = '{0}  [COLOR orange]({1} ROMs and {2} CHDs)[/COLOR]'.format(SL['display_name'], SL['rom_count'], SL['chd_count'])

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'title' : display_name, 'overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_1_arg_RunPlugin('command', 'VIEW')
        commands.append(('View', URL_view ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_2_arg('clist', 'SL', 'SL', SL_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    def _render_SL_ROM_row(self, SL_name, rom_name, ROM):
        display_name = ROM['description']

        # --- Mark Status and Clones ---
        display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(ROM['status'])
        if ROM['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'title'   : display_name,     'year'    : ROM['year'],
                                   'studio'  : ROM['publisher'], 'overlay' : ICON_OVERLAY })

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_3_arg_RunPlugin('command', 'VIEW', 'SL', SL_name, 'ROM', rom_name)
        URL_fav = self._misc_url_3_arg_RunPlugin('command', 'ADD_SL_FAV', 'SL', SL_name, 'ROM', rom_name)
        commands.append(('View', URL_view ))
        commands.append(('Add ROM to SL Favourites', URL_fav ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_3_arg('command', 'LAUNCH_SL', 'SL', SL_name, 'ROM', rom_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    # ---------------------------------------------------------------------------------------------
    # Information display
    # ---------------------------------------------------------------------------------------------
    def _command_view(self, mname, SLname, SLROM):
        MENU_SIMPLE    = 100
        MENU_MAME_DATA = 200
        MENU_SL_DATA   = 300
        menu_kind = 0
        size_stdout = 0
        if PATHS.MAME_STDOUT_PATH.exists():
            stat_stdout = PATHS.MAME_STDOUT_PATH.stat()
            size_stdout = stat_stdout.st_size
        size_stderr = 0
        if PATHS.MAME_STDERR_PATH.exists():
            stat_stderr = PATHS.MAME_STDERR_PATH.stat()
            size_stderr = stat_stderr.st_size
        dialog = xbmcgui.Dialog()
        if not mname and not SLname:
            menu_kind = MENU_SIMPLE
            type = dialog.select('View ...',
                                 ['View database information',
                                  'MAME last execution stdout ({0} bytes)'.format(size_stdout),
                                  'MAME last execution stderr ({0} bytes)'.format(size_stderr)])
        elif mname:
            menu_kind = MENU_MAME_DATA
            type = dialog.select('View ...',
                                 ['View MAME machine data',
                                  'View database information',
                                  'MAME last execution stdout ({0} bytes)'.format(size_stdout),
                                  'MAME last execution stderr ({0} bytes)'.format(size_stderr)])
        elif SLname:
            menu_kind = MENU_SL_DATA
            type = dialog.select('View ...',
                                 ['View Software List machine data',
                                  'View database information',
                                  'MAME last execution stdout ({0} bytes)'.format(size_stdout),
                                  'MAME last execution stderr ({0} bytes)'.format(size_stderr)])
        else:
            kodi_dialog_OK('_command_view() runtime error. Report this bug')
            return
        if type < 0: return

        # --- View MAME Machine ---
        if menu_kind == MENU_MAME_DATA:
            type_nb = 0
            if type == 0:
                # >> Read MAME machine information
                kodi_busydialog_ON()
                MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                kodi_busydialog_OFF()
                machine = MAME_db_dic[mname]
                assets  = MAME_assets_dic[mname]

                # --- Make information string ---
                info_text  = '[COLOR orange]Machine {0}[/COLOR]\n'.format(mname)
                info_text += "[COLOR skyblue]CHDs[/COLOR]: {0}\n".format(machine['CHDs'])                
                info_text += "[COLOR skyblue]bios_desc[/COLOR]: {0}\n".format(machine['bios_desc'])
                info_text += "[COLOR skyblue]bios_name[/COLOR]: {0}\n".format(machine['bios_name'])
                info_text += "[COLOR violet]catlist[/COLOR]: '{0}'\n".format(machine['catlist'])
                info_text += "[COLOR violet]catver[/COLOR]: '{0}'\n".format(machine['catver'])
                info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(machine['cloneof'])
                info_text += "[COLOR skyblue]coins[/COLOR]: {0}\n".format(machine['coins'])
                info_text += "[COLOR skyblue]control_type[/COLOR]: {0}\n".format(machine['control_type'])
                info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(machine['description'])
                info_text += "[COLOR skyblue]device_list[/COLOR]: {0}\n".format(machine['device_list'])
                # info_text += "[COLOR skyblue]device_tags[/COLOR]: {0}\n".format(machine['device_tags'])
                info_text += "[COLOR skyblue]display_rotate[/COLOR]: {0}\n".format(machine['display_rotate'])
                info_text += "[COLOR skyblue]display_tag[/COLOR]: {0}\n".format(machine['display_tag'])
                info_text += "[COLOR skyblue]display_type[/COLOR]: {0}\n".format(machine['display_type'])
                info_text += "[COLOR violet]driver_status[/COLOR]: '{0}'\n".format(machine['driver_status'])
                info_text += "[COLOR violet]genre[/COLOR]: '{0}'\n".format(machine['genre'])
                info_text += "[COLOR skyblue]hasCoin[/COLOR]: {0}\n".format(machine['hasCoin'])
                info_text += "[COLOR skyblue]hasROM[/COLOR]: {0}\n".format(machine['hasROM'])
                info_text += "[COLOR skyblue]isBIOS[/COLOR]: {0}\n".format(machine['isBIOS'])
                info_text += "[COLOR skyblue]isDead[/COLOR]: {0}\n".format(machine['isDead'])
                info_text += "[COLOR skyblue]isDevice[/COLOR]: {0}\n".format(machine['isDevice'])
                info_text += "[COLOR skyblue]isMechanical[/COLOR]: {0}\n".format(machine['isMechanical'])
                info_text += "[COLOR violet]manufacturer[/COLOR]: '{0}'\n".format(machine['manufacturer'])
                info_text += "[COLOR violet]nplayers[/COLOR]: '{0}'\n".format(machine['nplayers'])
                info_text += "[COLOR violet]romof[/COLOR]: '{0}'\n".format(machine['romof'])
                info_text += "[COLOR violet]sampleof[/COLOR]: '{0}'\n".format(machine['sampleof'])
                info_text += "[COLOR skyblue]softwarelists[/COLOR]: {0}\n".format(machine['softwarelists'])
                info_text += "[COLOR violet]sourcefile[/COLOR]: '{0}'\n".format(machine['sourcefile'])
                info_text += "[COLOR violet]status_CHD[/COLOR]: '{0}'\n".format(machine['status_CHD'])
                info_text += "[COLOR violet]status_ROM[/COLOR]: '{0}'\n".format(machine['status_ROM'])
                info_text += "[COLOR violet]status_SAM[/COLOR]: '{0}'\n".format(machine['status_SAM'])
                info_text += "[COLOR violet]status_SL[/COLOR]: '{0}'\n".format(machine['status_SL'])
                info_text += "[COLOR violet]year[/COLOR]: '{0}'\n".format(machine['year'])

                info_text += '\n[COLOR orange]Asset/artwork information[/COLOR]\n'
                info_text += "[COLOR violet]cabinet[/COLOR]: '{0}'\n".format(assets['cabinet'])
                info_text += "[COLOR violet]cpanel[/COLOR]: '{0}'\n".format(assets['cpanel'])
                info_text += "[COLOR violet]flyer[/COLOR]: '{0}'\n".format(assets['flyer'])
                info_text += "[COLOR violet]marquee[/COLOR]: '{0}'\n".format(assets['marquee'])
                info_text += "[COLOR violet]PCB[/COLOR]: '{0}'\n".format(assets['PCB'])
                info_text += "[COLOR violet]snap[/COLOR]: '{0}'\n".format(assets['snap'])
                info_text += "[COLOR violet]title[/COLOR]: '{0}'\n".format(assets['title'])
                info_text += "[COLOR violet]clearlogo[/COLOR]: '{0}'\n".format(assets['clearlogo'])

                # --- Show information window ---
                window_title = 'Machine Information'
                try:
                    xbmc.executebuiltin('ActivateWindow(10147)')
                    window = xbmcgui.Window(10147)
                    xbmc.sleep(100)
                    window.getControl(1).setLabel(window_title)
                    window.getControl(5).setText(info_text)
                except:
                    log_error('_command_view_machine() Exception rendering INFO window')

        # --- View Software List Machine ---
        elif menu_kind == MENU_SL_DATA:
            type_nb = 0
            if type == type_nb:
                # >> Read Software List information
                SL_DB_FN = PATHS.SL_DB_DIR.pjoin(SLname + '.json')
                kodi_busydialog_ON()
                SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
                roms = fs_load_JSON_file(SL_DB_FN.getPath())
                kodi_busydialog_OFF()

                # >> SL + ROM data
                SL_dic = SL_catalog_dic[SLname]
                SL_machine_list = SL_machines_dic[SLname]
                rom = roms[SLROM]

                # >> Build information string
                info_text  = '[COLOR orange]ROM {0}[/COLOR]\n'.format(SLROM)
                info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(rom['cloneof'])
                info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(rom['description'])                
                info_text += "[COLOR skyblue]part_interface[/COLOR]: {0}\n".format(rom['part_interface'])
                info_text += "[COLOR skyblue]part_name[/COLOR]: {0}\n".format(rom['part_name'])
                info_text += "[COLOR violet]publisher[/COLOR]: '{0}'\n".format(rom['publisher'])
                info_text += "[COLOR violet]status[/COLOR]: '{0}'\n".format(rom['status'])
                info_text += "[COLOR violet]year[/COLOR]: '{0}'\n".format(rom['year'])

                info_text += '\n[COLOR orange]Software List {0}[/COLOR]\n'.format(SLname)
                info_text += "[COLOR violet]display_name[/COLOR]: '{0}'\n".format(SL_dic['display_name'])
                info_text += "[COLOR skyblue]part_type[/COLOR]: {0}\n".format(SL_dic['part_type'])
                info_text += "[COLOR violet]rom_DB_noext[/COLOR]: '{0}'\n".format(SL_dic['rom_DB_noext'])
                info_text += "[COLOR violet]rom_count[/COLOR]: '{0}'\n".format(SL_dic['rom_count'])
                info_text += "[COLOR violet]chd_count[/COLOR]: '{0}'\n".format(SL_dic['chd_count'])

                info_text += '\n[COLOR orange]Runnable by[/COLOR]\n'
                for machine_dic in SL_machine_list:
                    info_text += "[COLOR violet]machine[/COLOR]: '{0}'   ({1})\n".format(machine_dic['description'], machine_dic['machine'])

                # --- Show information window ---
                window_title = 'Software List ROM Information'
                try:
                    xbmc.executebuiltin('ActivateWindow(10147)')
                    window = xbmcgui.Window(10147)
                    xbmc.sleep(100)
                    window.getControl(1).setLabel(window_title)
                    window.getControl(5).setText(info_text)
                except:
                    log_error('_command_view_machine() Exception rendering INFO window')
        else:
            type_nb = -1

        # --- View database information and statistics ---
        type_nb += 1
        if type == type_nb:
            # --- Load control dic ---
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            
            # --- Main stuff ---
            info_text  = '[COLOR orange]Main information[/COLOR]\n'
            info_text += "AML version: {0}\n".format(__addon_version__)
            info_text += "MAME version: {0}\n".format(control_dic['mame_version'])
            info_text += "Catver.ini version: {0}\n".format(control_dic['catver_version'])
            info_text += "Catlist.ini version: {0}\n".format(control_dic['catlist_version'])
            info_text += "Genre.ini version: {0}\n".format(control_dic['genre_version'])
            info_text += "nplayers.ini version: {0}\n".format(control_dic['nplayers_version'])

            info_text += '\n[COLOR orange]MAME machine count[/COLOR]\n'
            info_text += "Machines: {0} ({1} Parents / {2} Clones)\n".format(control_dic['processed_machines'], 
                                                                             control_dic['parent_machines'], control_dic['clone_machines'])
            info_text += "Devices: {0}\n".format(control_dic['devices_machines'])
            info_text += "BIOS: {0}\n".format(control_dic['BIOS_machines'])
            info_text += "Coin: {0}\n".format(control_dic['coin_machines'])
            info_text += "Nocoin: {0}\n".format(control_dic['nocoin_machines'])
            info_text += "Mechanical: {0}\n".format(control_dic['mechanical_machines'])
            info_text += "Dead: {0}\n".format(control_dic['dead_machines'])
            info_text += "ROMs: {0} ({1} ROMless)\n".format(control_dic['ROM_machines'], control_dic['ROMless_machines'])
            info_text += "CHDs: {0}\n".format(control_dic['CHD_machines'])
            info_text += "Samples: {0}\n".format(control_dic['samples_machines'])

            info_text += '\n[COLOR orange]Software Lists ROM count[/COLOR]\n'
            info_text += "Number of SL files: {0}\n".format(control_dic['num_SL_files'])
            info_text += "Total ROMs in all SLs: {0}\n".format(control_dic['num_SL_ROMs'])
            info_text += "Total CHDs in all SLs: {0}\n".format(control_dic['num_SL_CHDs'])

            info_text += '\n[COLOR orange]ROM audit information[/COLOR]\n'
            info_text += "You have {0} ROMs out of {1} ({2} missing)\n".format(control_dic['ROMs_have'], 
                                                                               control_dic['ROMs_total'], control_dic['ROMs_missing'])
            info_text += "You have {0} CHDs out of {1} ({2} missing)\n".format(control_dic['CHDs_have'], 
                                                                               control_dic['CHDs_total'], control_dic['CHDs_missing'])
            info_text += "You have {0} Samples out of {1} ({2} missing)\n".format(control_dic['Samples_have'], 
                                                                                  control_dic['Samples_total'], control_dic['Samples_missing'])
            info_text += "You have {0} SL ROMs out of {1} ({2} missing)\n".format(control_dic['SL_ROMs_have'], 
                                                                                  control_dic['SL_ROMs_total'], control_dic['SL_ROMs_missing'])
            info_text += "You have {0} SL CHDs out of {1} ({2} missing)\n".format(control_dic['SL_CHDs_have'], 
                                                                                  control_dic['SL_CHDs_total'], control_dic['SL_CHDs_missing'])

            # --- Show information window ---
            window_title = 'Database information and statistics'
            try:
                xbmc.executebuiltin('ActivateWindow(10147)')
                window = xbmcgui.Window(10147)
                xbmc.sleep(100)
                window.getControl(1).setLabel(window_title)
                window.getControl(5).setText(info_text)
            except:
                log_error('_command_view_machine() Exception rendering INFO window')

        # --- View MAME stdout ---
        type_nb += 1
        if type == type_nb:
            # --- Read stdout and put into a string ---
            info_text = ''
            with open(PATHS.MAME_STDOUT_PATH.getPath(), "r") as myfile:
                info_text = myfile.read()

            # --- Show information window ---
            window_title = 'MAME last execution stdout'
            try:
                xbmc.executebuiltin('ActivateWindow(10147)')
                window = xbmcgui.Window(10147)
                xbmc.sleep(100)
                window.getControl(1).setLabel(window_title)
                window.getControl(5).setText(info_text)
            except:
                log_error('_command_view_machine() Exception rendering INFO window')

        # --- View MAME stderr ---
        type_nb += 1
        if type == type_nb:
            # --- Read stdout and put into a string ---
            info_text = ''
            with open(PATHS.MAME_STDERR_PATH.getPath(), "r") as myfile:
                info_text = myfile.read()

            # --- Show information window ---
            window_title = 'MAME last execution stderr'
            try:
                xbmc.executebuiltin('ActivateWindow(10147)')
                window = xbmcgui.Window(10147)
                xbmc.sleep(100)
                window.getControl(1).setLabel(window_title)
                window.getControl(5).setText(info_text)
            except:
                log_error('_command_view_machine() Exception rendering INFO window')

    def _command_display_settings(self, clist, catalog, mname):
        log_debug('_command_display_settings() clist   "{0}"'.format(clist))
        log_debug('_command_display_settings() catalog "{0}"'.format(catalog))
        log_debug('_command_display_settings() mname   "{0}"'.format(mname))

        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Display settings',
                                 ['Display mode',
                                  'Default Icon',   'Default Fanart',
                                  'Default Banner', 'Default Poster',
                                  'Default Clearlogo'])
        if menu_item < 0: return

    def _command_add_mame_fav(self, machine_name):
        log_debug('_command_add_mame_fav() Machine_name "{0}"'.format(machine_name))

        # >> Get Machine database entry
        kodi_busydialog_ON()
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        kodi_busydialog_OFF()
        machine = MAME_db_dic[machine_name]
        assets  = MAME_assets_dic[machine_name]
        
        # >> Open Favourite Machines dictionary
        fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
        machine['assets'] = assets
        fav_machines[machine_name] = machine

        # >> Save Favourites
        fs_write_JSON_file(PATHS.FAV_MACHINES_PATH.getPath(), fav_machines)
        kodi_notify('Machine {0} added to MAME Favourites'.format(machine_name))

    def _command_delete_mame_fav(self, machine_name):
        kodi_dialog_OK('_command_delete_mame_fav() not coded yet. Sorry')

    def _command_show_mame_fav(self):
        log_debug('_command_show_mame_fav() Starting ...')

        # >> Open Favourite Machines dictionary
        fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())

        # >> Render Favourites
        for m_name in fav_machines:
            machine = fav_machines[m_name]
            assets  = machine['assets']
            self._render_fav_machine_row(m_name, machine, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_fav_machine_row(self, m_name, machine, machine_assets):
        display_name = machine['description']

        # --- Mark Status ---
        status = '{0}{1}{2}{3}{4}'.format(machine['status_ROM'], machine['status_CHD'],
                                          machine['status_SAM'], machine['status_SL'],
                                          machine['status_Device'])
        display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)

        # --- Mark Devices, BIOS and clones ---
        if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
        if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
        if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

        # --- Mark driver status: Good (no mark), Imperfect, Preliminar ---
        if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
        elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

        # --- Assets/artwork ---
        thumb_path      = machine_assets['title']
        thumb_fanart    = machine_assets['snap']
        thumb_banner    = machine_assets['marquee']
        thumb_clearlogo = machine_assets['clearlogo']
        thumb_poster    = machine_assets['flyer']

        # --- Create listitem row ---
        default_icon = 'DefaultFolder.png'
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)

        # --- Metadata ---
        # >> Make all the infotables compatible with Advanced Emulator Launcher
        listitem.setInfo('video', {'title'   : display_name,            'year'    : machine['year'],
                                   'genre'   : '',                      'plot'    : '',
                                   'studio'  : machine['manufacturer'], 'rating'  : '',
                                   'trailer' : '',                      'overlay' : ICON_OVERLAY})
        listitem.setProperty('platform', 'MAME')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title'     : machine_assets['title'],   'snap'    : machine_assets['snap'],
                         'boxfront'  : machine_assets['cabinet'], 'boxback' : machine_assets['cpanel'],
                         'cartridge' : machine_assets['PCB'],     'flyer'   : machine_assets['flyer'] })

        # >> Kodi official artwork fields
        listitem.setArt({'icon'   : thumb_path,   'fanart'    : thumb_fanart,
                         'banner' : thumb_banner, 'clearlogo' : thumb_clearlogo, 'poster' : thumb_poster })

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_2_arg_RunPlugin('command', 'VIEW', 'machine', m_name)
        URL_display = self._misc_url_2_arg_RunPlugin('command', 'DELETE_MAME_FAV', 'machine', m_name)
        commands.append(('View',  URL_view ))
        commands.append(('Delete machine from Favourites', URL_display ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_3_arg('command', 'LAUNCH', 'machine', m_name, 'location', 'MAME_FAV')
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    def _command_add_sl_fav(self, SL_name, ROM_name):
        log_debug('_command_add_sl_fav() SL_name  "{0}"'.format(SL_name))
        log_debug('_command_add_sl_fav() ROM_name "{0}"'.format(ROM_name))

        # >> Get Machine database entry
        kodi_busydialog_ON()
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())
        kodi_busydialog_OFF()
        ROM = SL_roms[ROM_name]
        
        # >> Open Favourite Machines dictionary
        fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
        SL_fav_key = SL_name + '-' + ROM_name
        log_debug('_command_add_sl_fav() SL_fav_key "{0}"'.format(SL_fav_key))
        ROM['ROM_name'] = ROM_name
        ROM['SL_name']  = SL_name
        fav_SL_roms[SL_fav_key] = ROM

        # >> Save Favourites
        fs_write_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath(), fav_SL_roms)
        kodi_notify('ROM {0} added to SL Favourite ROMs'.format(ROM_name))

    def _command_delete_sl_fav(self, SL_name, ROM_name):
        kodi_dialog_OK('_command_delete_sl_fav() not coded yet. Sorry')

    def _command_show_sl_fav(self):
        log_debug('_command_show_sl_fav() Starting ...')

        # >> Open Favourite Machines dictionary
        fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())

        # >> Render Favourites
        for SL_fav_key in fav_SL_roms:
            SL_fav_ROM = fav_SL_roms[SL_fav_key]
            self._render_sl_fav_machine_row(SL_fav_key, SL_fav_ROM)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_sl_fav_machine_row(self, SL_fav_key, ROM):
        SL_name  = ROM['SL_name']
        ROM_name = ROM['ROM_name']
        display_name = ROM['description']

        # --- Mark Status and Clones ---
        display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(ROM['status'])
        if ROM['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

        # --- Create listitem row ---
        icon = 'DefaultFolder.png'
        listitem = xbmcgui.ListItem(display_name, iconImage = icon)
        ICON_OVERLAY = 6
        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'title'   : display_name,     'year'    : ROM['year'],
                                   'studio'  : ROM['publisher'], 'overlay' : ICON_OVERLAY })

        # --- Create context menu ---
        commands = []
        URL_view = self._misc_url_3_arg_RunPlugin('command', 'VIEW', 'SL', SL_name, 'ROM', ROM_name)
        URL_fav = self._misc_url_3_arg_RunPlugin('command', 'DELETE_SL_FAV', 'SL', SL_name, 'ROM', ROM_name)
        commands.append(('View', URL_view ))
        commands.append(('Delete ROM from SL Favourites', URL_fav ))
        commands.append(('Kodi File Manager', 'ActivateWindow(filemanager)' ))
        commands.append(('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__) ))
        listitem.addContextMenuItems(commands, replaceItems = True)

        # --- Add row ---
        URL = self._misc_url_3_arg('command', 'LAUNCH_SL', 'SL', SL_name, 'ROM', ROM_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    # ---------------------------------------------------------------------------------------------
    # Setup plugin databases
    # ---------------------------------------------------------------------------------------------
    def _command_setup_plugin(self):
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Setup plugin',
                                 ['Extract MAME.xml ...',
                                  'Build MAME database ...',
                                  'Build MAME indices and catalogs ...',
                                  'Build Software Lists indices and catalogs ...',
                                  'Scan MAME ROMs/CHDs/Samples ...',
                                  'Scan MAME assets/artwork ...',
                                  'Scan Software Lists ROMs ...',
                                  'Scan Software Lists assets/artwork ...' ])
        if menu_item < 0: return

        # --- Extract MAME.xml ---
        if menu_item == 0:
            if not self.settings['mame_prog']:
                kodi_dialog_OK('MAME executable is not set.')
                return
            mame_prog_FN = FileName(self.settings['mame_prog'])

            # --- Extract MAME XML ---
            (filesize, total_machines) = fs_extract_MAME_XML(PATHS, mame_prog_FN)
            kodi_dialog_OK('Extracted MAME XML database. '
                           'Size is {0} MB and there are {1} machines.'.format(filesize / 1000000, total_machines))

        # --- Build main MAME database and PClone list ---
        elif menu_item == 1:
            # --- Error checks ---
            # >> Check that MAME_XML_PATH exists

            # --- Parse MAME XML and generate main database and PClone list ---
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            log_info('_command_setup_plugin() Generating MAME main database and PClone list...')
            fs_build_MAME_main_database(PATHS, self.settings, control_dic)
            kodi_notify('Main MAME database built')

        # --- Build MAME indices/catalogs ---
        elif menu_item == 2:
            # --- Error checks ---
            # >> Check that main MAME database exists

            # --- Read main database and control dic ---
            kodi_busydialog_ON()
            machines        = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
            kodi_busydialog_OFF()

            # --- Generate indices ---
            fs_build_MAME_indices_and_catalogs(PATHS, machines, main_pclone_dic)
            kodi_notify('Indices and catalogs built')

        # --- Build Software Lists indices/catalogs ---
        elif menu_item == 3:
            # --- Error checks ---
            if not self.settings['SL_hash_path']:
                kodi_dialog_OK('Software Lists hash path not set.')
                return

            # --- Read main database and control dic ---
            kodi_busydialog_ON()
            machines        = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
            control_dic     = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            kodi_busydialog_OFF()

            # --- Build Software List indices ---
            fs_build_SoftwareLists_index(PATHS, self.settings, machines, main_pclone_dic, control_dic)
            kodi_notify('Software Lists indices and catalogs built')

        # --- Scan ROMs/CHDs/Samples and updates ROM status ---
        elif menu_item == 4:
            log_info('_command_setup_plugin() Scanning MAME ROMs/CHDs/Samples ...')

            # >> Get paths and check they exist
            if not self.settings['rom_path']:
                kodi_dialog_OK('ROM directory not configured. Aborting.')
                return
            ROM_path_FN = FileName(self.settings['rom_path'])
            if not ROM_path_FN.isdir():
                kodi_dialog_OK('ROM directory does not exist. Aborting.')
                return

            scan_CHDs = False
            if self.settings['chd_path']:
                CHD_path_FN = FileName(self.settings['chd_path'])
                if not CHD_path_FN.isdir():
                    kodi_dialog_OK('CHD directory does not exist. CHD scanning disabled.')
                else:
                    scan_CHDs = True
            else:
                kodi_dialog_OK('CHD directory not configured. CHD scanning disabled.')

            scan_Samples = False
            if self.settings['samples_path']:
                Samples_path_FN = FileName(self.settings['samples_path'])
                if not Samples_path_FN.isdir():
                    kodi_dialog_OK('Samples directory does not exist. Samples scanning disabled.')
                else:
                    scan_Samples = True
            else:
                kodi_dialog_OK('Samples directory not configured. Samples scanning disabled.')

            # >> Load machine database and control_dic
            kodi_busydialog_ON()
            machines    = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            kodi_busydialog_OFF()

            # >> Iterate machines, check if ROMs exits. Update status field
            pDialog = xbmcgui.DialogProgress()
            pDialog_canceled = False
            pDialog.create('Advanced MAME Launcher', 'Scanning MAME ROMs...')
            total_machines = len(machines)
            processed_machines = 0
            ROMs_have    = ROMs_missing    = ROMs_total    = 0
            CHDs_have    = CHDs_missing    = CHDs_total    = 0
            Samples_have = Samples_missing = Samples_total = 0
            for key, machine in machines.iteritems():
                machine = machines[key]
                # log_info('_command_setup_plugin() Checking machine {0}'.format(key))

                # >> Scan ROMs
                if machine['hasROM']:
                    ROMs_total += 1
                    # >> Machine has ROM. Get ROM filename and check if file exist
                    ROM_FN = ROM_path_FN.pjoin(key + '.zip')
                    if ROM_FN.exists():
                        machine['status_ROM'] = 'R'
                        ROMs_have += 1
                    else:
                        machine['status_ROM'] = 'r'
                        ROMs_missing += 1
                else:
                    machine['status_ROM'] = '-'
                    
                # >> Scan CHDs
                if machine['CHDs']:
                    CHDs_total += 1
                    if scan_CHDs:
                        hasCHD_list = [False] * len(machine['CHDs'])
                        for idx, CHD_name in enumerate(machine['CHDs']):
                            CHD_this_path_FN = CHD_path_FN.pjoin(key)
                            CHD_FN = CHD_this_path_FN.pjoin(CHD_name + '.chd')
                            # log_debug('Testing CHD OP "{0}"'.format(CHD_FN.getOriginalPath()))
                            if CHD_FN.exists(): hasCHD_list[idx] = True
                        if all(hasCHD_list):
                            machine['status_CHD'] = 'C'
                            CHDs_have += 1
                        else:
                            machine['status_CHD'] = 'c'
                            CHDs_missing += 1
                    else:
                        machine['status_CHD'] = 'c'
                        CHDs_missing += 1
                else:
                    machine['status_CHD'] = '-'

                # >> Scan Samples
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
                    else:
                        machine['status_SAM'] = 's'
                        Samples_missing += 1
                else:
                    machine['status_SAM'] = '-'

                # >> Progress dialog
                processed_machines = processed_machines + 1
                pDialog.update(100 * processed_machines / total_machines)
            pDialog.close()

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

            # >> Save database
            kodi_busydialog_ON()
            fs_write_JSON_file(PATHS.MAIN_DB_PATH.getPath(), machines)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_busydialog_OFF()
            kodi_notify('Scanning of ROMs, CHDs and Samples finished')

        # --- Scans assets/artwork ---
        elif menu_item == 5:
            log_info('_command_setup_plugin() Scanning MAME assets/artwork ...')

            # >> Get assets directory. Abort if not configured/found.
            if not self.settings['assets_path']:
                kodi_dialog_OK('Asset directory not configured. Aborting.')
                return
            Asset_path_FN = FileName(self.settings['assets_path'])
            if not Asset_path_FN.isdir():
                kodi_dialog_OK('Asset directory does not exist. Aborting.')
                return

            # >> Load machine database
            kodi_busydialog_ON()
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            kodi_busydialog_OFF()

            # >> Iterate machines, check if assets/artwork exist.
            pDialog = xbmcgui.DialogProgress()
            pDialog_canceled = False
            pDialog.create('Advanced MAME Launcher', 'Scanning MAME assets/artwork...')
            total_machines = len(machines)
            processed_machines = 0
            assets_dic = {}
            for key, machine in machines.iteritems():
                machine = machines[key]

                # >> Scan assets
                machine_assets = fs_new_asset()
                for idx, asset_key in enumerate(ASSET_KEY_LIST):
                    full_asset_dir_FN = Asset_path_FN.pjoin(ASSET_PATH_LIST[idx])
                    asset_FN = full_asset_dir_FN.pjoin(key + '.png')
                    if asset_FN.exists(): machine_assets[asset_key] = asset_FN.getOriginalPath()
                    else:                 machine_assets[asset_key] = ''
                assets_dic[key] = machine_assets

                # >> Progress dialog
                processed_machines = processed_machines + 1
                pDialog.update(100 * processed_machines / total_machines)
            pDialog.close()

            # >> Save asset database
            kodi_busydialog_ON()
            fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
            kodi_busydialog_OFF()
            kodi_notify('Scanning of assets/artwork finished')

        # --- Scan SL ROMs ---
        elif menu_item == 6:
            log_info('_command_setup_plugin() Scanning SL ROMs ...')

            # >> Abort if SL hash path not configured.
            if not self.settings['SL_hash_path']:
                kodi_dialog_OK('Software Lists hash path not set. Scanning aborted.')
                return
            SL_hash_dir_FN = PATHS.SL_DB_DIR
            log_info('_command_setup_plugin() SL hash dir OP {0}'.format(SL_hash_dir_FN.getOriginalPath()))
            log_info('_command_setup_plugin() SL hash dir  P {0}'.format(SL_hash_dir_FN.getPath()))

            # >> Abort if SL ROM dir not configured.
            if not self.settings['SL_rom_path']:
                kodi_dialog_OK('Software Lists ROM path not set. Scanning aborted.')
                return
            SL_ROM_dir_FN = FileName(self.settings['SL_rom_path'])
            log_info('_command_setup_plugin() SL ROM dir OP {0}'.format(SL_ROM_dir_FN.getOriginalPath()))
            log_info('_command_setup_plugin() SL ROM dir  P {0}'.format(SL_ROM_dir_FN.getPath()))

            # >> Load SL catalog
            SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())            
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())

            # >> Traverse Software List, check if ROM exists, update and save database
            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Scanning Sofware Lists ROMs ...'
            pDialog.create('Advanced MAME Launcher', pdialog_line1)
            pDialog.update(0)
            total_files = len(SL_catalog_dic)
            processed_files = 0
            SL_ROMs_have = SL_ROMs_missing = SL_ROMs_total = 0
            SL_CHDs_have = SL_CHDs_missing = SL_CHDs_total = 0
            for SL_name in SL_catalog_dic:
                log_debug('Processing "{0}" ({1})'.format(SL_name, SL_catalog_dic[SL_name]['display_name']))
                SL_DB_FN = SL_hash_dir_FN.pjoin(SL_name + '.json')
                
                # >> Open database
                # log_debug('File "{0}"'.format(SL_DB_FN.getPath()))
                roms = fs_load_JSON_file(SL_DB_FN.getPath())

                # >> Scan for ROMs
                for rom_key, rom in roms.iteritems():
                    SL_ROMs_total += 1
                    this_SL_ROM_dir_FN = SL_ROM_dir_FN.pjoin(SL_name)
                    SL_ROM_FN = this_SL_ROM_dir_FN.pjoin(rom_key + '.zip')
                    # log_debug('Scanning "{0}"'.format(SL_ROM_FN.getPath()))
                    if SL_ROM_FN.exists():
                        rom['status'] = 'R'
                        SL_ROMs_have += 1
                    else:
                        rom['status'] = 'r'
                        SL_ROMs_missing += 1

                # >> Update database
                fs_write_JSON_file(SL_DB_FN.getPath(), roms)
                
                # >> Update progress
                processed_files += 1
                update_number = 100 * processed_files / total_files
                pDialog.update(update_number, pdialog_line1, 'Software List {0} ...'.format(SL_name))
            pDialog.close()

            # >> Update statistics
            control_dic['SL_ROMs_have']    = SL_ROMs_have
            control_dic['SL_ROMs_missing'] = SL_ROMs_missing
            control_dic['SL_ROMs_total']   = SL_ROMs_total
            control_dic['SL_CHDs_have']    = SL_CHDs_have
            control_dic['SL_CHDs_missing'] = SL_CHDs_missing
            control_dic['SL_CHDs_total']   = SL_CHDs_total
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('Scanning of SL ROMs finished')

        # --- Scan SL assets/artwork ---
        elif menu_item == 7:
            log_info('_command_setup_plugin() Scanning SL assets/artwork ...')
            kodi_dialog_OK('Not coded yet. Sorry.')

    #
    # Launch MAME machine.
    # Example: $ mame dino
    #
    def _run_machine(self, machine_name, location):
        log_info('_run_machine() Launching MAME machine  "{0}"'.format(machine_name))
        log_info('_run_machine() Launching MAME location "{0}"'.format(location))

        # >> If launching from Favourites read ROM from Fav database
        if location and location == 'MAME_FAV':
            fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
            machine = fav_machines[machine_name]
            assets  = machine['assets']

        # >> Get paths
        mame_prog_FN = FileName(self.settings['mame_prog'])

        # >> Check if ROM exist
        if not self.settings['rom_path']:
            kodi_dialog_OK('ROM directory not configured.')
            return
        ROM_path_FN = FileName(self.settings['rom_path'])
        if not ROM_path_FN.isdir():
            kodi_dialog_OK('ROM directory does not exist.')
            return
        ROM_FN = ROM_path_FN.pjoin(machine_name + '.zip')
        # if not ROM_FN.exists():
        #     kodi_dialog_OK('ROM "{0}" not found.'.format(ROM_FN.getBase()))
        #     return

        # >> Choose BIOS (only available for Favourite Machines)
        if location and location == 'MAME_FAV' and len(machine['bios_name']) > 1:
            dialog = xbmcgui.Dialog()
            m_index = dialog.select('Select BIOS', machine['bios_desc'])
            if m_index < 0: return
            BIOS_name = machine['bios_name'][m_index]
        else:
            BIOS_name = ''

        # >> Launch machine using subprocess module
        (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
        log_info('_run_machine() mame_prog_FN "{0}"'.format(mame_prog_FN.getPath()))    
        log_info('_run_machine() mame_dir     "{0}"'.format(mame_dir))
        log_info('_run_machine() mame_exec    "{0}"'.format(mame_exec))
        log_info('_run_machine() machine_name "{0}"'.format(machine_name))
        log_info('_run_machine() BIOS_name    "{0}"'.format(BIOS_name))

        # >> Prevent a console window to be shown in Windows. Not working yet!
        if sys.platform == 'win32':
            log_info('_run_machine() Platform is win32. Creating _info structure')
            _info = subprocess.STARTUPINFO()
            _info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            # See https://msdn.microsoft.com/en-us/library/ms633548(v=vs.85).aspx
            # See https://docs.python.org/2/library/subprocess.html#subprocess.STARTUPINFO
            # >> SW_HIDE = 0
            # >> Does not work: MAME console window is not shown, graphical window not shonw either,
            # >> process run in background.
            # _info.wShowWindow = subprocess.SW_HIDE
            # >> SW_SHOWMINIMIZED = 2
            # >> Both MAME console and graphical window minimized.
            # _info.wShowWindow = 2
            # >> SW_SHOWNORMAL = 1
            # >> MAME console window is shown, MAME graphical window on top, Kodi on bottom.
            _info.wShowWindow = 1
        else:
            log_info('_run_machine() _info is None')
            _info = None

        # >> Launch MAME
        # arg_list = [mame_prog_FN.getPath(), '-window', machine_name]
        if BIOS_name: arg_list = [mame_prog_FN.getPath(), machine_name, '-bios', BIOS_name]
        else:         arg_list = [mame_prog_FN.getPath(), machine_name]
        log_info('arg_list = {0}'.format(arg_list))
        log_info('_run_machine() Calling subprocess.Popen()...')
        with open(PATHS.MAME_STDOUT_PATH.getPath(), 'wb') as _stdout, \
             open(PATHS.MAME_STDERR_PATH.getPath(), 'wb') as _stderr:
            p = subprocess.Popen(arg_list, stdout = _stdout, stderr = _stderr, cwd = mame_dir, startupinfo = _info)
        p.wait()
        log_info('_run_machine() Exiting function')

    #
    # Launch SL machine. See http://docs.mamedev.org/usingmame/usingmame.html
    # Syntax: $ mame <system> <software>
    # Example: $ mame smspal sonic
    # Requirements:
    #   A) machine_name
    #   B) media_name
    #
    # Software list <part> tag has an interface attribute that tells how to virtually plug the
    # cartridge/cassete/disk/etc. There is not need to media type in MAME commandline.
    #
    def _run_SL_machine(self, SL_name, ROM_name):
        log_info('_run_SL_machine() Launching SL machine ...')

        # >> Get paths
        mame_prog_FN = FileName(self.settings['mame_prog'])

        # >> Get a list of machines that can launch this SL ROM. User chooses.
        SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
        SL_machine_list = SL_machines_dic[SL_name]
        SL_machine_names_list = []
        SL_machine_desc_list = []
        # SL_machine_device_props_list = []
        for SL_machine in SL_machine_list: 
            SL_machine_names_list.append(SL_machine['machine'])
            SL_machine_desc_list.append(SL_machine['description'])
            # SL_machine_device_props_list.append(SL_machine['device_props'])
        dialog = xbmcgui.Dialog()
        m_index = dialog.select('Select machine', SL_machine_desc_list)
        if m_index < 0: return
        machine_name = SL_machine_names_list[m_index]
        machine_desc = SL_machine_desc_list[m_index]

        # >> Select media if more than one device instance
        # >> Not necessary. MAME knows what media to plug the SL ROM into.
        # if len(SL_machine_device_props_list[m_index]) > 1:
        #     device_names_list = []
        #     for device in SL_machine_device_props_list[m_index]: device_names_list.append(device['name'])
        #     dialog = xbmcgui.Dialog()
        #     d_index = dialog.select('Select device', device_names_list)
        #     if d_index < 0: return
        #     media_name = SL_machine_device_props_list[m_index][d_index]['name']
        # else:
        #     media_name = SL_machine_device_props_list[m_index][0]['name']

        # >> Launch machine using subprocess module
        (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
        log_info('_run_SL_machine() mame_prog_FN "{0}"'.format(mame_prog_FN.getPath()))    
        log_info('_run_SL_machine() mame_dir     "{0}"'.format(mame_dir))
        log_info('_run_SL_machine() mame_exec    "{0}"'.format(mame_exec))
        log_info('_run_SL_machine() machine_name "{0}"'.format(machine_name))
        log_info('_run_SL_machine() machine_desc "{0}"'.format(machine_desc))
        # log_info('_run_SL_machine() media_name   "{0}"'.format(media_name))
        log_info('_run_SL_machine() SL_name      "{0}"'.format(SL_name))
        log_info('_run_SL_machine() ROM_name     "{0}"'.format(ROM_name))

        # >> Prevent a console window to be shown in Windows. Not working yet!
        if sys.platform == 'win32':
            log_info('_run_SL_machine() Platform is win32. Creating _info structure')
            _info = subprocess.STARTUPINFO()
            _info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            _info.wShowWindow = 1
        else:
            log_info('_run_SL_machine() _info is None')
            _info = None

        # >> Launch MAME
        # arg_list = [mame_prog_FN.getPath(), machine_name, '-{0}'.format(media_name), ROM_name]
        arg_list = [mame_prog_FN.getPath(), machine_name, ROM_name]
        log_info('arg_list = {0}'.format(arg_list))
        log_info('_run_SL_machine() Calling subprocess.Popen()...')
        with open(PATHS.MAME_STDOUT_PATH.getPath(), 'wb') as _stdout, \
             open(PATHS.MAME_STDERR_PATH.getPath(), 'wb') as _stderr:
            p = subprocess.Popen(arg_list, stdout = _stdout, stderr = _stderr, cwd = mame_dir, startupinfo = _info)
        p.wait()
        log_info('_run_SL_machine() Exiting function')

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------
    # List of sorting methods here http://mirrors.xbmc.org/docs/python-docs/16.x-jarvis/xbmcplugin.html#-setSetting
    def _set_Kodi_all_sorting_methods(self):
        if self.addon_handle < 0: return
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

    def _set_Kodi_all_sorting_methods_and_size(self):
        if self.addon_handle < 0: return
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_FOLDERS)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_STUDIO)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_SIZE)
        xbmcplugin.addSortMethod(handle=self.addon_handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

    # ---------------------------------------------------------------------------------------------
    # Misc URL building functions
    # ---------------------------------------------------------------------------------------------
    #
    # Used in xbmcplugin.addDirectoryItem()
    #
    def _misc_url_1_arg(self, arg_name, arg_value):
        arg_value_escaped = arg_value.replace('&', '%26')

        return '{0}?{1}={2}'.format(self.base_url, arg_name, arg_value_escaped)

    def _misc_url_2_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        # >> Escape '&' in URLs
        arg_value_1_escaped = arg_value_1.replace('&', '%26')
        arg_value_2_escaped = arg_value_2.replace('&', '%26')

        return '{0}?{1}={2}&{3}={4}'.format(self.base_url, 
                                            arg_name_1, arg_value_1_escaped,
                                            arg_name_2, arg_value_2_escaped)

    def _misc_url_3_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, arg_name_3, arg_value_3):
        arg_value_1_escaped = arg_value_1.replace('&', '%26')
        arg_value_2_escaped = arg_value_2.replace('&', '%26')
        arg_value_3_escaped = arg_value_3.replace('&', '%26')

        return '{0}?{1}={2}&{3}={4}&{5}={6}'.format(self.base_url,
                                                    arg_name_1, arg_value_1_escaped,
                                                    arg_name_2, arg_value_2_escaped,
                                                    arg_name_3, arg_value_3_escaped)

    #
    # Used in context menus
    #
    def _misc_url_1_arg_RunPlugin(self, arg_name_1, arg_value_1):
        return 'XBMC.RunPlugin({0}?{1}={2})'.format(self.base_url, 
                                                    arg_name_1, arg_value_1)

    def _misc_url_2_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4})'.format(self.base_url,
                                                            arg_name_1, arg_value_1,
                                                            arg_name_2, arg_value_2)

    def _misc_url_3_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                                  arg_name_3, arg_value_3):
        return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4}&{5}={6})'.format(self.base_url,
                                                                    arg_name_1, arg_value_1,
                                                                    arg_name_2, arg_value_2,
                                                                    arg_name_3, arg_value_3)

    def _misc_url_4_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                                  arg_name_3, arg_value_3, arg_name_4, arg_value_4):
        return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4}&{5}={6}&{7}={8})'.format(self.base_url,
                                                                            arg_name_1, arg_value_1,
                                                                            arg_name_2, arg_value_2,
                                                                            arg_name_3, arg_value_3, 
                                                                            arg_name_4, arg_value_4)
