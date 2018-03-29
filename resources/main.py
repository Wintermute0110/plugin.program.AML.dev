# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher main script file
#

# Copyright (c) 2016-2018 Wintermute0110 <wintermute0110@gmail.com>
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
# Division operator: https://www.python.org/dev/peps/pep-0238/
from __future__ import unicode_literals
from __future__ import division
import os
import urlparse
import subprocess
import copy

# --- Kodi stuff ---
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# --- Modules/packages in this plugin ---
# Addon module dependencies:
#   main <-- mame <-- disk_IO <-- assets, utils, utils_kodi, constants
#   ReaderPDF <-- utils, utils_kodi
#   filters <- utils, utils_kodi
from constants import *
from assets import *
from utils import *
from utils_kodi import *
from disk_IO import *
from mame import *
from ReaderPDF import *
from filters import *

# --- Addon object (used to access settings) ---
__addon__         = xbmcaddon.Addon()
__addon_id__      = __addon__.getAddonInfo('id').decode('utf-8')
__addon_name__    = __addon__.getAddonInfo('name').decode('utf-8')
__addon_version__ = __addon__.getAddonInfo('version').decode('utf-8')
__addon_author__  = __addon__.getAddonInfo('author').decode('utf-8')
__addon_profile__ = __addon__.getAddonInfo('profile').decode('utf-8')
__addon_type__    = __addon__.getAddonInfo('type').decode('utf-8')

# --- Addon paths and constant definition ---
# _PATH is a filename | _DIR is a directory
ADDONS_DATA_DIR      = FileName('special://profile/addon_data')
PLUGIN_DATA_DIR      = ADDONS_DATA_DIR.pjoin(__addon_id__)
BASE_DIR             = FileName('special://profile')
HOME_DIR             = FileName('special://home')
KODI_FAV_PATH        = FileName('special://profile/favourites.xml')
ADDONS_DIR           = HOME_DIR.pjoin('addons')
AML_ADDON_DIR        = ADDONS_DIR.pjoin(__addon_id__)
AML_ICON_FILE_PATH   = AML_ADDON_DIR.pjoin('media/icon.png')
AML_FANART_FILE_PATH = AML_ADDON_DIR.pjoin('media/fanart.jpg')

# --- Plugin database indices ---
class AML_Paths:
    def __init__(self):
        # >> MAME stdout/strderr files
        self.MAME_STDOUT_PATH     = PLUGIN_DATA_DIR.pjoin('log_stdout.log')
        self.MAME_STDERR_PATH     = PLUGIN_DATA_DIR.pjoin('log_stderr.log')
        self.MAME_STDOUT_VER_PATH = PLUGIN_DATA_DIR.pjoin('log_version_stdout.log')
        self.MAME_STDERR_VER_PATH = PLUGIN_DATA_DIR.pjoin('log_version_stderr.log')
        self.MAME_OUTPUT_PATH     = PLUGIN_DATA_DIR.pjoin('log_output.log')
        self.MONO_FONT_PATH       = AML_ADDON_DIR.pjoin('fonts/Inconsolata.otf')

        # >> MAME XML, main database and main PClone list.
        self.MAME_XML_PATH        = PLUGIN_DATA_DIR.pjoin('MAME.xml')
        self.MAIN_ASSETS_DB_PATH  = PLUGIN_DATA_DIR.pjoin('MAME_assets.json')
        self.MAIN_CONTROL_PATH    = PLUGIN_DATA_DIR.pjoin('MAME_control_dic.json')
        self.DEVICES_DB_PATH      = PLUGIN_DATA_DIR.pjoin('MAME_DB_devices.json')
        self.MAIN_DB_PATH         = PLUGIN_DATA_DIR.pjoin('MAME_DB_main.json')
        self.RENDER_DB_PATH       = PLUGIN_DATA_DIR.pjoin('MAME_DB_render.json')
        self.ROMS_DB_PATH         = PLUGIN_DATA_DIR.pjoin('MAME_DB_roms.json')
        self.MAIN_PCLONE_DIC_PATH = PLUGIN_DATA_DIR.pjoin('MAME_DB_pclone_dic.json')

        # >> ROM set databases
        self.ROM_AUDIT_DB_PATH                = PLUGIN_DATA_DIR.pjoin('ROM_Audit_DB.json')
        self.ROM_SET_MACHINE_ARCHIVES_DB_PATH = PLUGIN_DATA_DIR.pjoin('ROM_Set_machine_archives.json')
        self.ROM_SET_ROM_ARCHIVES_DB_PATH     = PLUGIN_DATA_DIR.pjoin('ROM_Set_ROM_archives.json')
        self.ROM_SET_CHD_ARCHIVES_DB_PATH     = PLUGIN_DATA_DIR.pjoin('ROM_Set_CHD_archives.json')

        # >> DAT indices and databases.
        self.HISTORY_IDX_PATH  = PLUGIN_DATA_DIR.pjoin('DAT_History_index.json')
        self.HISTORY_DB_PATH   = PLUGIN_DATA_DIR.pjoin('DAT_History_DB.json')
        self.MAMEINFO_IDX_PATH = PLUGIN_DATA_DIR.pjoin('DAT_MAMEInfo_index.json')
        self.MAMEINFO_DB_PATH  = PLUGIN_DATA_DIR.pjoin('DAT_MAMEInfo_DB.json')
        self.GAMEINIT_IDX_PATH = PLUGIN_DATA_DIR.pjoin('DAT_GameInit_index.json')
        self.GAMEINIT_DB_PATH  = PLUGIN_DATA_DIR.pjoin('DAT_GameInit_DB.json')
        self.COMMAND_IDX_PATH  = PLUGIN_DATA_DIR.pjoin('DAT_Command_index.json')
        self.COMMAND_DB_PATH   = PLUGIN_DATA_DIR.pjoin('DAT_Command_DB.json')

        # >> Disabled. Now there are global properties for this.
        # self.MAIN_PROPERTIES_PATH = PLUGIN_DATA_DIR.pjoin('MAME_properties.json')

        # >> ROM cache
        self.CACHE_DIR        = PLUGIN_DATA_DIR.pjoin('cache')
        self.CACHE_INDEX_PATH = PLUGIN_DATA_DIR.pjoin('MAME_cache_index.json')

        # >> Catalogs
        self.CATALOG_DIR                        = PLUGIN_DATA_DIR.pjoin('catalogs')
        self.CATALOG_MAIN_PARENT_PATH           = self.CATALOG_DIR.pjoin('catalog_main_parents.json')
        self.CATALOG_MAIN_ALL_PATH              = self.CATALOG_DIR.pjoin('catalog_main_all.json')
        self.CATALOG_BINARY_PARENT_PATH         = self.CATALOG_DIR.pjoin('catalog_binary_parents.json')
        self.CATALOG_BINARY_ALL_PATH            = self.CATALOG_DIR.pjoin('catalog_binary_all.json')
        self.CATALOG_CATVER_PARENT_PATH         = self.CATALOG_DIR.pjoin('catalog_catver_parents.json')
        self.CATALOG_CATVER_ALL_PATH            = self.CATALOG_DIR.pjoin('catalog_catver_all.json')
        self.CATALOG_CATLIST_PARENT_PATH        = self.CATALOG_DIR.pjoin('catalog_catlist_parents.json')
        self.CATALOG_CATLIST_ALL_PATH           = self.CATALOG_DIR.pjoin('catalog_catlist_all.json')
        self.CATALOG_GENRE_PARENT_PATH          = self.CATALOG_DIR.pjoin('catalog_genre_parents.json')
        self.CATALOG_GENRE_ALL_PATH             = self.CATALOG_DIR.pjoin('catalog_genre_all.json')
        self.CATALOG_NPLAYERS_PARENT_PATH       = self.CATALOG_DIR.pjoin('catalog_nplayers_parents.json')
        self.CATALOG_NPLAYERS_ALL_PATH          = self.CATALOG_DIR.pjoin('catalog_nplayers_all.json')
        self.CATALOG_BESTGAMES_PARENT_PATH      = self.CATALOG_DIR.pjoin('catalog_bestgames_parents.json')
        self.CATALOG_BESTGAMES_ALL_PATH         = self.CATALOG_DIR.pjoin('catalog_bestgames_all.json')
        self.CATALOG_SERIES_PARENT_PATH         = self.CATALOG_DIR.pjoin('catalog_series_parents.json')
        self.CATALOG_SERIES_ALL_PATH            = self.CATALOG_DIR.pjoin('catalog_series_all.json')
        self.CATALOG_MANUFACTURER_PARENT_PATH   = self.CATALOG_DIR.pjoin('catalog_manufacturer_parents.json')
        self.CATALOG_MANUFACTURER_ALL_PATH      = self.CATALOG_DIR.pjoin('catalog_manufacturer_all.json')
        self.CATALOG_YEAR_PARENT_PATH           = self.CATALOG_DIR.pjoin('catalog_year_parents.json')
        self.CATALOG_YEAR_ALL_PATH              = self.CATALOG_DIR.pjoin('catalog_year_all.json')
        self.CATALOG_DRIVER_PARENT_PATH         = self.CATALOG_DIR.pjoin('catalog_driver_parents.json')
        self.CATALOG_DRIVER_ALL_PATH            = self.CATALOG_DIR.pjoin('catalog_driver_all.json')
        self.CATALOG_CONTROL_PARENT_PATH        = self.CATALOG_DIR.pjoin('catalog_control_parents.json')
        self.CATALOG_CONTROL_ALL_PATH           = self.CATALOG_DIR.pjoin('catalog_control_all.json')
        self.CATALOG_DISPLAY_TAG_PARENT_PATH    = self.CATALOG_DIR.pjoin('catalog_display_tag_parents.json')
        self.CATALOG_DISPLAY_TAG_ALL_PATH       = self.CATALOG_DIR.pjoin('catalog_display_tag_all.json')
        self.CATALOG_DISPLAY_TYPE_PARENT_PATH   = self.CATALOG_DIR.pjoin('catalog_display_type_parents.json')
        self.CATALOG_DISPLAY_TYPE_ALL_PATH      = self.CATALOG_DIR.pjoin('catalog_display_type_all.json')
        self.CATALOG_DISPLAY_ROTATE_PARENT_PATH = self.CATALOG_DIR.pjoin('catalog_display_rotate_parents.json')
        self.CATALOG_DISPLAY_ROTATE_ALL_PATH    = self.CATALOG_DIR.pjoin('catalog_display_rotate_all.json')
        self.CATALOG_DEVICE_LIST_PARENT_PATH    = self.CATALOG_DIR.pjoin('catalog_device_list_parents.json')
        self.CATALOG_DEVICE_LIST_ALL_PATH       = self.CATALOG_DIR.pjoin('catalog_device_list_all.json')
        self.CATALOG_SL_PARENT_PATH             = self.CATALOG_DIR.pjoin('catalog_SL_parents.json')
        self.CATALOG_SL_ALL_PATH                = self.CATALOG_DIR.pjoin('catalog_SL_all.json')
        self.CATALOG_SHORTNAME_PARENT_PATH      = self.CATALOG_DIR.pjoin('catalog_shortname_parents.json')
        self.CATALOG_SHORTNAME_ALL_PATH         = self.CATALOG_DIR.pjoin('catalog_shortname_all.json')
        self.CATALOG_LONGNAME_PARENT_PATH       = self.CATALOG_DIR.pjoin('catalog_longname_parents.json')
        self.CATALOG_LONGNAME_ALL_PATH          = self.CATALOG_DIR.pjoin('catalog_longname_all.json')

        # >> Distributed hashed database
        self.MAIN_DB_HASH_DIR      = PLUGIN_DATA_DIR.pjoin('hash')
        self.ROMS_DB_HASH_DIR      = PLUGIN_DATA_DIR.pjoin('hash_ROM')
        self.ROM_AUDIT_DB_HASH_DIR = PLUGIN_DATA_DIR.pjoin('hash_ROM_Audit')

        # >> MAME custom filters
        self.FILTERS_DB_DIR     = PLUGIN_DATA_DIR.pjoin('filters')
        self.FILTERS_INDEX_PATH = PLUGIN_DATA_DIR.pjoin('Filter_index.json')

        # >> Software Lists
        self.SL_DB_DIR             = PLUGIN_DATA_DIR.pjoin('SoftwareLists')
        self.SL_NAMES_PATH         = PLUGIN_DATA_DIR.pjoin('SoftwareLists_names.json')
        self.SL_INDEX_PATH         = PLUGIN_DATA_DIR.pjoin('SoftwareLists_index.json')
        self.SL_MACHINES_PATH      = PLUGIN_DATA_DIR.pjoin('SoftwareLists_machines.json')
        self.SL_PCLONE_DIC_PATH    = PLUGIN_DATA_DIR.pjoin('SoftwareLists_pclone_dic.json')
        # >> Disabled. There are global properties
        # self.SL_MACHINES_PROP_PATH = PLUGIN_DATA_DIR.pjoin('SoftwareLists_properties.json')

        # >> Favourites
        self.FAV_MACHINES_PATH = PLUGIN_DATA_DIR.pjoin('Favourite_Machines.json')
        self.FAV_SL_ROMS_PATH  = PLUGIN_DATA_DIR.pjoin('Favourite_SL_ROMs.json')

        # >> ROM/CHD scanner reports. These reports show missing ROM/CHDs only.
        self.REPORTS_DIR                             = PLUGIN_DATA_DIR.pjoin('reports')
        self.REPORT_MAME_SCAN_MACHINE_ARCH_HAVE_PATH = self.REPORTS_DIR.pjoin('Scanner_MAME_machine_archives_have.txt')
        self.REPORT_MAME_SCAN_MACHINE_ARCH_MISS_PATH = self.REPORTS_DIR.pjoin('Scanner_MAME_machine_archives_miss.txt')
        self.REPORT_MAME_SCAN_ROM_LIST_MISS_PATH     = self.REPORTS_DIR.pjoin('Scanner_MAME_ROM_list_miss.txt')
        self.REPORT_MAME_SCAN_CHD_LIST_MISS_PATH     = self.REPORTS_DIR.pjoin('Scanner_MAME_CHD_list_miss.txt')
        self.REPORT_MAME_SCAN_SAMP_HAVE_PATH         = self.REPORTS_DIR.pjoin('Scanner_Samples_have.txt')
        self.REPORT_MAME_SCAN_SAMP_MISS_PATH         = self.REPORTS_DIR.pjoin('Scanner_Samples_miss.txt')
        self.REPORT_SL_SCAN_MACHINE_ARCH_HAVE_PATH   = self.REPORTS_DIR.pjoin('Scanner_SL_item_archives_have.txt')
        self.REPORT_SL_SCAN_MACHINE_ARCH_MISS_PATH   = self.REPORTS_DIR.pjoin('Scanner_SL_item_archives_miss.txt')
        self.REPORT_SL_SCAN_ROM_LIST_PATH            = self.REPORTS_DIR.pjoin('Scanner_SL_ROM_list.txt')
        self.REPORT_SL_SCAN_CHD_LIST_PATH            = self.REPORTS_DIR.pjoin('Scanner_SL_CHD_list.txt')

        # >> Asset scanner reports. These reports show have and missing assets.
        self.REPORT_MAME_ASSETS_PATH = self.REPORTS_DIR.pjoin('Assets_MAME.txt')
        self.REPORT_SL_ASSETS_PATH   = self.REPORTS_DIR.pjoin('Assets_SL.txt')

        # >> Audit report
        self.REPORT_MAME_AUDIT_GOOD_PATH       = self.REPORTS_DIR.pjoin('Audit_MAME_good.txt')
        self.REPORT_MAME_AUDIT_ERRORS_PATH     = self.REPORTS_DIR.pjoin('Audit_MAME_errors.txt')
        self.REPORT_MAME_AUDIT_ROM_GOOD_PATH   = self.REPORTS_DIR.pjoin('Audit_MAME_ROMs_good.txt')
        self.REPORT_MAME_AUDIT_ROM_ERRORS_PATH = self.REPORTS_DIR.pjoin('Audit_MAME_ROMs_errors.txt')
        self.REPORT_MAME_AUDIT_CHD_GOOD_PATH   = self.REPORTS_DIR.pjoin('Audit_MAME_CHDs_good.txt')
        self.REPORT_MAME_AUDIT_CHD_ERRORS_PATH = self.REPORTS_DIR.pjoin('Audit_MAME_CHDs_errors.txt')

        self.REPORT_SL_AUDIT_GOOD_PATH         = self.REPORTS_DIR.pjoin('Audit_SL_good.txt')
        self.REPORT_SL_AUDIT_ERRORS_PATH       = self.REPORTS_DIR.pjoin('Audit_SL_errors.txt')
        self.REPORT_SL_AUDIT_ROMS_GOOD_PATH    = self.REPORTS_DIR.pjoin('Audit_SL_ROMs_good.txt')
        self.REPORT_SL_AUDIT_ROMS_ERRORS_PATH  = self.REPORTS_DIR.pjoin('Audit_SL_ROMs_errors.txt')
        self.REPORT_SL_AUDIT_CHDS_GOOD_PATH    = self.REPORTS_DIR.pjoin('Audit_SL_CHDs_good.txt')
        self.REPORT_SL_AUDIT_CHDS_ERRORS_PATH  = self.REPORTS_DIR.pjoin('Audit_SL_CHDs_errors.txt')
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
        # set_log_level(LOG_DEBUG)

        # --- Fill in settings dictionary using addon_obj.getSetting() ---
        self._get_settings()
        set_log_level(self.settings['log_level'])

        # --- Some debug stuff for development ---
        log_debug('---------- Called AML Main::run_plugin() constructor ----------')
        log_debug('sys.platform {0}'.format(sys.platform))
        log_debug('Python version ' + sys.version.replace('\n', ''))
        log_debug('__addon_version__ {0}'.format(__addon_version__))
        for i in range(len(sys.argv)): log_debug('sys.argv[{0}] = "{1}"'.format(i, sys.argv[i]))

        # --- Addon data paths creation ---
        if not PLUGIN_DATA_DIR.exists(): PLUGIN_DATA_DIR.makedirs()
        if not PATHS.CACHE_DIR.exists(): PATHS.CACHE_DIR.makedirs()
        if not PATHS.CATALOG_DIR.exists(): PATHS.CATALOG_DIR.makedirs()
        if not PATHS.MAIN_DB_HASH_DIR.exists(): PATHS.MAIN_DB_HASH_DIR.makedirs()
        if not PATHS.FILTERS_DB_DIR.exists(): PATHS.FILTERS_DB_DIR.makedirs()
        if not PATHS.SL_DB_DIR.exists(): PATHS.SL_DB_DIR.makedirs()
        if not PATHS.REPORTS_DIR.exists(): PATHS.REPORTS_DIR.makedirs()

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

        elif 'catalog' in args and not 'command' in args:
            catalog_name = args['catalog'][0]
            # --- Software list is a special case ---
            if catalog_name == 'SL' or catalog_name == 'SL_ROM' or \
               catalog_name == 'SL_CHD' or catalog_name == 'SL_ROM_CHD':
                SL_name     = args['category'][0] if 'category' in args else ''
                parent_name = args['parent'][0] if 'parent' in args else ''
                if SL_name and parent_name:
                    self._render_SL_pclone_set(SL_name, parent_name)
                elif SL_name and not parent_name:
                    self._render_SL_ROMs(SL_name)
                else:
                    self._render_SL_list(catalog_name)
            # --- Custom filter ---
            elif catalog_name == 'Custom':
                filter_name = args['category'][0] if 'category' in args else ''
                parent_name = args['parent'][0] if 'parent' in args else ''
                if filter_name and parent_name:
                    self._render_custom_filter_clones(filter_name, parent_name)
                else:
                    self._render_custom_filter_ROMs(filter_name)
            # --- DAT browsing ---
            elif catalog_name == 'History' or catalog_name == 'MAMEINFO' or \
                 catalog_name == 'Gameinit' or catalog_name == 'Command':
                category_name = args['category'][0] if 'category' in args else ''
                machine_name = args['machine'][0] if 'machine' in args else ''
                if category_name and machine_name:
                    self._render_DAT_machine_info(catalog_name, category_name, machine_name)
                elif category_name and not machine_name:
                    self._render_DAT_category(catalog_name, category_name)
                else:
                    self._render_DAT_list(catalog_name)
            else:
                category_name = args['category'][0] if 'category' in args else ''
                parent_name   = args['parent'][0] if 'parent' in args else ''
                if category_name and parent_name:
                    self._render_catalog_clone_list(catalog_name, category_name, parent_name)
                elif category_name and not parent_name:
                    self._render_catalog_parent_list(catalog_name, category_name)
                else:
                    self._render_catalog_list(catalog_name)

        elif 'command' in args:
            command = args['command'][0]

            # >> Commands used by skins to render items of the addon root menu.
            if   command == 'SKIN_SHOW_FAV_SLOTS':       self._render_skin_fav_slots()
            elif command == 'SKIN_SHOW_MAIN_FILTERS':    self._render_skin_main_filters()
            elif command == 'SKIN_SHOW_BINARY_FILTERS':  self._render_skin_binary_filters()
            elif command == 'SKIN_SHOW_CATALOG_FILTERS': self._render_skin_catalog_filters()
            elif command == 'SKIN_SHOW_DAT_SLOTS':       self._render_skin_dat_slots()
            elif command == 'SKIN_SHOW_SL_FILTERS':      self._render_skin_SL_filters()

            # >> Auxiliar commands from parent machine context menu
            # >> Not sure if this will cause problems with the concurrent protected code once it's
            #    implemented.
            elif command == 'EXEC_SHOW_MAME_CLONES':
                catalog_name  = args['catalog'][0] if 'catalog' in args else ''
                category_name = args['category'][0] if 'category' in args else ''
                machine_name  = args['parent'][0] if 'parent' in args else ''
                url = self._misc_url_3_arg('catalog', catalog_name, 'category', category_name, 'parent', machine_name)
                xbmc.executebuiltin('Container.Update({0})'.format(url))

            elif command == 'EXEC_SHOW_SL_CLONES':
                catalog_name  = args['catalog'][0] if 'catalog' in args else ''
                category_name = args['category'][0] if 'category' in args else ''
                machine_name  = args['parent'][0] if 'parent' in args else ''
                url = self._misc_url_3_arg('catalog', 'SL', 'category', category_name, 'parent', machine_name)
                xbmc.executebuiltin('Container.Update({0})'.format(url))

            elif command == 'LAUNCH':
                machine  = args['machine'][0]
                location = args['location'][0] if 'location' in args else ''
                log_info('Launching MAME machine "{0}"'.format(machine, location))
                self._run_machine(machine, location)
            elif command == 'LAUNCH_SL':
                SL_name  = args['SL'][0]
                ROM_name = args['ROM'][0]
                location = args['location'][0] if 'location' in args else LOCATION_STANDARD
                log_info('Launching SL machine "{0}" (ROM "{1}")'.format(SL_name, ROM_name))
                self._run_SL_machine(SL_name, ROM_name, location)

            elif command == 'SETUP_PLUGIN':
                self._command_context_setup_plugin()

            #
            # Not used at the moment.
            # Instead of per-catalog, per-category display mode there are global settings.
            #
            elif command == 'DISPLAY_SETTINGS_MAME':
                catalog_name = args['catalog'][0]
                category_name = args['category'][0] if 'category' in args else ''
                self._command_context_display_settings(catalog_name, category_name)
            elif command == 'DISPLAY_SETTINGS_SL':
                self._command_context_display_settings_SL(args['category'][0])
            elif command == 'VIEW_DAT':
                machine  = args['machine'][0]  if 'machine'  in args else ''
                SL       = args['SL'][0]       if 'SL'       in args else ''
                ROM      = args['ROM'][0]      if 'ROM'      in args else ''
                location = args['location'][0] if 'location' in args else LOCATION_STANDARD
                self._command_context_view_DAT(machine, SL, ROM, location)
            elif command == 'VIEW':
                machine  = args['machine'][0]  if 'machine'  in args else ''
                SL       = args['SL'][0]       if 'SL'       in args else ''
                ROM      = args['ROM'][0]      if 'ROM'      in args else ''
                location = args['location'][0] if 'location' in args else LOCATION_STANDARD
                self._command_context_view(machine, SL, ROM, location)
            elif command == 'UTILITIES':
                catalog_name  = args['catalog'][0] if 'catalog' in args else ''
                category_name = args['category'][0] if 'category' in args else ''
                self._command_context_utilities(catalog_name, category_name)

            # >> MAME Favourites
            elif command == 'ADD_MAME_FAV':
                self._command_context_add_mame_fav(args['machine'][0])
            elif command == 'MANAGE_MAME_FAV':
                self._command_context_manage_mame_fav(args['machine'][0])
            elif command == 'SHOW_MAME_FAVS':
                self._command_show_mame_fav()

            # >> SL Favourites
            elif command == 'ADD_SL_FAV':
                self._command_context_add_sl_fav(args['SL'][0], args['ROM'][0])
            elif command == 'MANAGE_SL_FAV':
                self._command_context_manage_sl_fav(args['SL'][0], args['ROM'][0])
            elif command == 'SHOW_SL_FAVS':
                self._command_show_sl_fav()

            # >> Custom filters
            elif command == 'SHOW_CUSTOM_FILTERS':
                self._command_show_custom_filters()
            elif command == 'SETUP_CUSTOM_FILTERS':
                self._command_context_setup_custom_filters()

            else:
                u = 'Unknown command "{0}"'.format(command)
                log_error(u)
                kodi_dialog_OK(u)
                xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        else:
            u = 'Error in URL routing'
            log_error(u)
            kodi_dialog_OK(u)
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

        # --- So Long, and Thanks for All the Fish ---
        log_debug('Advanced MAME Launcher exit')

    #
    # Get Addon Settings
    #
    def _get_settings(self):
        # --- Paths ---
        self.settings['mame_prog']    = __addon__.getSetting('mame_prog').decode('utf-8')
        self.settings['rom_path']     = __addon__.getSetting('rom_path').decode('utf-8')

        self.settings['assets_path']  = __addon__.getSetting('assets_path').decode('utf-8')
        self.settings['chd_path']     = __addon__.getSetting('chd_path').decode('utf-8')        
        self.settings['SL_hash_path'] = __addon__.getSetting('SL_hash_path').decode('utf-8')
        self.settings['SL_rom_path']  = __addon__.getSetting('SL_rom_path').decode('utf-8')
        self.settings['SL_chd_path']  = __addon__.getSetting('SL_chd_path').decode('utf-8')
        self.settings['samples_path'] = __addon__.getSetting('samples_path').decode('utf-8')

        # --- DAT Paths ---
        self.settings['catver_path']    = __addon__.getSetting('catver_path').decode('utf-8')
        self.settings['catlist_path']   = __addon__.getSetting('catlist_path').decode('utf-8')
        self.settings['genre_path']     = __addon__.getSetting('genre_path').decode('utf-8')
        self.settings['nplayers_path']  = __addon__.getSetting('nplayers_path').decode('utf-8')
        self.settings['bestgames_path'] = __addon__.getSetting('bestgames_path').decode('utf-8')
        self.settings['series_path']    = __addon__.getSetting('series_path').decode('utf-8')
        self.settings['history_path']   = __addon__.getSetting('history_path').decode('utf-8')
        self.settings['mameinfo_path']  = __addon__.getSetting('mameinfo_path').decode('utf-8')
        self.settings['gameinit_path']  = __addon__.getSetting('gameinit_path').decode('utf-8')
        self.settings['command_path']   = __addon__.getSetting('command_path').decode('utf-8')

        # --- ROM sets ---
        self.settings['mame_rom_set'] = int(__addon__.getSetting('mame_rom_set'))
        self.settings['mame_chd_set'] = int(__addon__.getSetting('mame_chd_set'))
        self.settings['SL_rom_set']   = int(__addon__.getSetting('SL_rom_set'))
        self.settings['SL_chd_set']   = int(__addon__.getSetting('SL_chd_set'))
        self.settings['filter_XML']   = __addon__.getSetting('filter_XML').decode('utf-8')

        # --- Display ---
        self.settings['display_launcher_notify'] = True if __addon__.getSetting('display_launcher_notify') == 'true' else False
        self.settings['mame_view_mode']          = int(__addon__.getSetting('mame_view_mode'))
        self.settings['sl_view_mode']            = int(__addon__.getSetting('sl_view_mode'))
        self.settings['display_hide_BIOS']       = True if __addon__.getSetting('display_hide_BIOS') == 'true' else False
        self.settings['display_hide_nonworking'] = True if __addon__.getSetting('display_hide_nonworking') == 'true' else False
        self.settings['display_hide_imperfect']  = True if __addon__.getSetting('display_hide_imperfect') == 'true' else False
        self.settings['display_rom_available']   = True if __addon__.getSetting('display_rom_available') == 'true' else False
        self.settings['display_chd_available']   = True if __addon__.getSetting('display_chd_available') == 'true' else False

        self.settings['display_main_filters']    = True if __addon__.getSetting('display_main_filters') == 'true' else False
        self.settings['display_binary_filters']  = True if __addon__.getSetting('display_binary_filters') == 'true' else False
        self.settings['display_catalog_filters'] = True if __addon__.getSetting('display_catalog_filters') == 'true' else False
        self.settings['display_DAT_browser']     = True if __addon__.getSetting('display_DAT_browser') == 'true' else False
        self.settings['display_SL_browser']      = True if __addon__.getSetting('display_SL_browser') == 'true' else False
        self.settings['display_MAME_favs']       = True if __addon__.getSetting('display_MAME_favs') == 'true' else False
        self.settings['display_SL_favs']         = True if __addon__.getSetting('display_SL_favs') == 'true' else False
        self.settings['display_custom_filters']  = True if __addon__.getSetting('display_custom_filters') == 'true' else False

        # --- Display ---
        self.settings['artwork_mame_icon']     = int(__addon__.getSetting('artwork_mame_icon'))
        self.settings['artwork_mame_fanart']   = int(__addon__.getSetting('artwork_mame_fanart'))
        self.settings['artwork_SL_icon']       = int(__addon__.getSetting('artwork_SL_icon'))
        self.settings['artwork_SL_fanart']     = int(__addon__.getSetting('artwork_SL_fanart'))
        self.settings['display_hide_trailers'] = True if __addon__.getSetting('display_hide_trailers') == 'true' else False

        # --- Advanced ---
        self.settings['log_level'] = int(__addon__.getSetting('log_level'))

        # --- Transform settings data ---
        self.mame_icon   = assets_get_asset_key_MAME_icon(self.settings['artwork_mame_icon'])
        self.mame_fanart = assets_get_asset_key_MAME_fanart(self.settings['artwork_mame_fanart'])
        self.SL_icon     = assets_get_asset_key_SL_icon(self.settings['artwork_SL_icon'])
        self.SL_fanart   = assets_get_asset_key_SL_fanart(self.settings['artwork_SL_fanart'])

        # --- Dump settings for DEBUG ---
        # log_debug('Settings dump BEGIN')
        # for key in sorted(self.settings):
        #     log_debug('{0} --> {1:10s} {2}'.format(key.rjust(21), str(self.settings[key]), type(self.settings[key])))
        # log_debug('Settings dump END')

    # ---------------------------------------------------------------------------------------------
    # Root menu rendering
    # ---------------------------------------------------------------------------------------------
    def _render_root_list(self):
        mame_view_mode = self.settings['mame_view_mode']

        # ----- Machine count -----
        cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())

        # >> Main filter
        machines_n_str = 'Machines with coin slot (Normal)'
        machines_u_str = 'Machines with coin slot (Unusual)'
        nocoin_str     = 'Machines with no coin slot'
        mecha_str      = 'Mechanical machines'
        dead_str       = 'Dead machines'
        devices_str    = 'Device machines'

        # >> Binary filters
        bios_str       = 'Machines [BIOS]'
        norom_str      = 'Machines [ROMless]'
        chd_str        = 'Machines [with CHDs]'
        samples_str    = 'Machines [with Samples]'
        softlists_str  = 'Machines [with Software Lists]'

        # >> Cataloged filters (optional)
        catver_str       = 'Machines by Category (Catver)'
        catlist_str      = 'Machines by Category (Catlist)'
        genre_str        = 'Machines by Category (Genre)'
        NPLayers_str     = 'Machines by Number of players'
        score_str        = 'Machines by Score'
        series_str       = 'Machines by Series'
        # >> Cataloged filters (always there)
        # NOTE: use the same names as MAME executable
        # -listdevices         list available devices
        # -listslots           list available slots and slot devices
        # -listmedia           list available media for the system
        ctype_str        = 'Machines by Control Type'
        drotation_str    = 'Machines by Display Rotation'
        dtype_str        = 'Machines by Display Type'
        device_str       = 'Machines by Device'
        driver_str       = 'Machines by Driver'
        shortname_str    = 'Machines by MAME short name'
        longname_str     = 'Machines by MAME long name'
        manufacturer_str = 'Machines by Manufacturer'
        SL_str           = 'Machines by Software List'
        year_str         = 'Machines by Year'

        if cache_index_dic and mame_view_mode == VIEW_MODE_FLAT:
            machines_n_str += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['Normal']['num_machines'])
            machines_u_str += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['Unusual']['num_machines'])
            nocoin_str     += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['NoCoin']['num_machines'])
            mecha_str      += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['Mechanical']['num_machines'])
            dead_str       += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['Dead']['num_machines'])
            devices_str    += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Main']['Devices']['num_machines'])
            norom_str      += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Binary']['NoROM']['num_machines'])
            chd_str        += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Binary']['CHD']['num_machines'])
            samples_str    += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Binary']['Samples']['num_machines'])
            bios_str       += ' [COLOR orange]({0} machines)[/COLOR]'.format(cache_index_dic['Binary']['BIOS']['num_machines'])

        elif cache_index_dic and mame_view_mode == VIEW_MODE_PCLONE:
            machines_n_str += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['Normal']['num_parents'])
            machines_u_str += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['Unusual']['num_parents'])
            nocoin_str     += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['NoCoin']['num_parents'])
            mecha_str      += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['Mechanical']['num_parents'])
            dead_str       += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['Dead']['num_parents'])
            devices_str    += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Main']['Devices']['num_parents'])
            norom_str      += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Binary']['NoROM']['num_parents'])
            chd_str        += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Binary']['CHD']['num_parents'])
            samples_str    += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Binary']['Samples']['num_parents'])
            bios_str       += ' [COLOR orange]({0} parents)[/COLOR]'.format(cache_index_dic['Binary']['BIOS']['num_parents'])

        if cache_index_dic:
            # >> Optional
            catver_str       += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Catver']))
            catlist_str      += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Catlist']))
            genre_str        += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Genre']))
            NPLayers_str     += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['NPlayers']))
            score_str        += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Bestgames']))
            series_str       += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Series']))
            # >> Always there
            ctype_str        += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Controls']))
            drotation_str    += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Display_Rotate']))
            dtype_str        += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Display_Type']))
            device_str       += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Devices']))
            driver_str       += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Driver']))
            manufacturer_str += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Manufacturer']))
            shortname_str    += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['ShortName']))
            longname_str     += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['LongName']))
            SL_str           += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['BySL']))
            year_str         += ' [COLOR gold]({0} items)[/COLOR]'.format(len(cache_index_dic['Year']))

        # >> If everything deactivated render the main filters so user has access to the context menu.
        big_OR = self.settings['display_main_filters'] or self.settings['display_binary_filters'] or \
                 self.settings['display_catalog_filters'] or self.settings['display_DAT_browser'] or \
                 self.settings['display_SL_browser'] or self.settings['display_MAME_favs'] or \
                 self.settings['display_SL_favs'] or self.settings['display_custom_filters']
        if not big_OR:
            self.settings['display_main_filters'] = True

        # >> Main filters (Virtual catalog 'Main')
        if self.settings['display_main_filters']:
            self._render_root_list_row_catalog(machines_n_str, 'Main', 'Normal')
            self._render_root_list_row_catalog(machines_u_str, 'Main', 'Unusual')
            self._render_root_list_row_catalog(nocoin_str, 'Main', 'NoCoin')
            self._render_root_list_row_catalog(mecha_str, 'Main', 'Mechanical')
            self._render_root_list_row_catalog(dead_str, 'Main', 'Dead')
            self._render_root_list_row_catalog(devices_str, 'Main', 'Devices')

        # >> Binary filters (Virtual catalog 'Binary')
        if self.settings['display_binary_filters']:
            self._render_root_list_row_catalog(norom_str, 'Binary', 'NoROM')
            self._render_root_list_row_catalog(chd_str, 'Binary', 'CHD')
            self._render_root_list_row_catalog(samples_str, 'Binary', 'Samples')
            self._render_root_list_row_catalog(bios_str, 'Binary', 'BIOS')

        if self.settings['display_catalog_filters']:
            # >> Optional cataloged filters (depend on a INI file)
            self._render_root_list_row_standard(catver_str, self._misc_url_1_arg('catalog', 'Catver'))
            self._render_root_list_row_standard(catlist_str, self._misc_url_1_arg('catalog', 'Catlist'))
            self._render_root_list_row_standard(genre_str, self._misc_url_1_arg('catalog', 'Genre'))
            self._render_root_list_row_standard(NPLayers_str, self._misc_url_1_arg('catalog', 'NPlayers'))
            self._render_root_list_row_standard(score_str, self._misc_url_1_arg('catalog', 'Bestgames'))
            self._render_root_list_row_standard(series_str, self._misc_url_1_arg('catalog', 'Series'))
            # >> Cataloged filters (always there)
            self._render_root_list_row_standard(ctype_str, self._misc_url_1_arg('catalog', 'Controls'))
            self._render_root_list_row_standard(drotation_str, self._misc_url_1_arg('catalog', 'Display_Rotate'))
            self._render_root_list_row_standard(dtype_str, self._misc_url_1_arg('catalog', 'Display_Type'))
            self._render_root_list_row_standard(device_str, self._misc_url_1_arg('catalog', 'Devices'))
            self._render_root_list_row_standard(driver_str, self._misc_url_1_arg('catalog', 'Driver'))
            self._render_root_list_row_standard(manufacturer_str, self._misc_url_1_arg('catalog', 'Manufacturer'))
            self._render_root_list_row_standard(shortname_str, self._misc_url_1_arg('catalog', 'ShortName'))
            self._render_root_list_row_standard(longname_str, self._misc_url_1_arg('catalog', 'LongName'))
            self._render_root_list_row_standard(SL_str, self._misc_url_1_arg('catalog', 'BySL'))
            self._render_root_list_row_standard(year_str, self._misc_url_1_arg('catalog', 'Year'))

        # >> history.dat, mameinfo.dat, gameinit.dat, command.dat
        if self.settings['display_DAT_browser']:
            self._render_root_list_row_standard('History DAT',  self._misc_url_1_arg('catalog', 'History'))
            self._render_root_list_row_standard('MAMEINFO DAT', self._misc_url_1_arg('catalog', 'MAMEINFO'))
            self._render_root_list_row_standard('Gameinit DAT', self._misc_url_1_arg('catalog', 'Gameinit'))
            self._render_root_list_row_standard('Command DAT',  self._misc_url_1_arg('catalog', 'Command'))

        # >> Software lists
        if self.settings['display_SL_browser']:
            self._render_root_list_row_standard('Software Lists (with ROMs)', self._misc_url_1_arg('catalog', 'SL_ROM'))
            self._render_root_list_row_standard('Software Lists (with CHDs)', self._misc_url_1_arg('catalog', 'SL_CHD'))
            self._render_root_list_row_standard('Software Lists (with ROMs and CHDs)', self._misc_url_1_arg('catalog', 'SL_ROM_CHD'))

        # >> Special launchers
        if self.settings['display_MAME_favs']:
            self._render_root_list_row_standard('<Favourite MAME machines>', self._misc_url_1_arg('command', 'SHOW_MAME_FAVS'))
        if self.settings['display_SL_favs']:
            self._render_root_list_row_standard('<Favourite Software Lists ROMs>', self._misc_url_1_arg('command', 'SHOW_SL_FAVS'))
        if self.settings['display_custom_filters']:
            self._render_custom_filter_row('[Custom MAME filters]', self._misc_url_1_arg('command', 'SHOW_CUSTOM_FILTERS'))
        # self._render_root_list_row_standard('{Most played MAME machines}', self._misc_url_1_arg('command', 'SHOW_CUSTOM_FILTERS'))
        # self._render_root_list_row_standard('{Recently played MAME machines}', self._misc_url_1_arg('command', 'SHOW_CUSTOM_FILTERS'))
        # self._render_root_list_row_standard('{Most played SL ROMs}', self._misc_url_1_arg('command', 'SHOW_CUSTOM_FILTERS'))
        # self._render_root_list_row_standard('{Recently played SL ROMs}', self._misc_url_1_arg('command', 'SHOW_CUSTOM_FILTERS'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # These _render_skin_* functions used by skins to display widgets.
    #
    def _render_skin_fav_slots(self):
        self._render_root_list_row_standard('Favourite MAME machines', self._misc_url_1_arg('command', 'SHOW_MAME_FAVS'))
        self._render_root_list_row_standard('Favourite Software Lists ROMs', self._misc_url_1_arg('command', 'SHOW_SL_FAVS'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_skin_main_filters(self):
        machines_n_str = 'Machines with coin slot (Normal)'
        machines_u_str = 'Machines with coin slot (Unusual)'
        nocoin_str = 'Machines with no coin slot'
        mecha_str = 'Mechanical machines'
        dead_str = 'Dead machines'
        devices_str = 'Device machines'

        self._render_root_list_row_standard(machines_n_str, self._misc_url_2_arg('catalog', 'Main', 'category', 'Normal'))
        self._render_root_list_row_standard(machines_u_str, self._misc_url_2_arg('catalog', 'Main', 'category', 'Unusual'))
        self._render_root_list_row_standard(nocoin_str,     self._misc_url_2_arg('catalog', 'Main', 'category', 'NoCoin'))
        self._render_root_list_row_standard(mecha_str,      self._misc_url_2_arg('catalog', 'Main', 'category', 'Mechanical'))
        self._render_root_list_row_standard(dead_str,       self._misc_url_2_arg('catalog', 'Main', 'category', 'Dead'))
        self._render_root_list_row_standard(devices_str,    self._misc_url_2_arg('catalog', 'Main', 'category', 'Devices'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_skin_binary_filters(self):
        norom_str = 'Machines [with no ROMs]'
        chd_str = 'Machines [with CHDs]'
        samples_str = 'Machines [with Samples]'
        bios_str = 'Machines [BIOS]'

        self._render_root_list_row_standard(norom_str,      self._misc_url_2_arg('catalog', 'Binary', 'category', 'NoROM'))
        self._render_root_list_row_standard(chd_str,        self._misc_url_2_arg('catalog', 'Binary', 'category', 'CHD'))
        self._render_root_list_row_standard(samples_str,    self._misc_url_2_arg('catalog', 'Binary', 'category', 'Samples'))
        self._render_root_list_row_standard(bios_str,       self._misc_url_2_arg('catalog', 'Binary', 'category', 'BIOS'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_skin_catalog_filters(self):
        if self.settings['catver_path']:
            self._render_root_list_row_standard('Machines by Category (Catver)',  self._misc_url_1_arg('catalog', 'Catver'))
        if self.settings['catlist_path']:
            self._render_root_list_row_standard('Machines by Category (Catlist)', self._misc_url_1_arg('catalog', 'Catlist'))
        if self.settings['genre_path']:
            self._render_root_list_row_standard('Machines by Category (Genre)',   self._misc_url_1_arg('catalog', 'Genre'))
        if self.settings['nplayers_path']:
            self._render_root_list_row_standard('Machines by Number of players',  self._misc_url_1_arg('catalog', 'NPlayers'))
        if self.settings['bestgames_path']:
            self._render_root_list_row_standard('Machines by Score',              self._misc_url_1_arg('catalog', 'Bestgames'))
        if self.settings['series_path']:
            self._render_root_list_row_standard('Machines by Series',             self._misc_url_1_arg('catalog', 'Series'))

        self._render_root_list_row_standard('Machines by Manufacturer',        self._misc_url_1_arg('catalog', 'Manufacturer'))
        self._render_root_list_row_standard('Machines by Year',                self._misc_url_1_arg('catalog', 'Year'))
        self._render_root_list_row_standard('Machines by Driver',              self._misc_url_1_arg('catalog', 'Driver'))
        self._render_root_list_row_standard('Machines by Control Type',        self._misc_url_1_arg('catalog', 'Controls'))
        self._render_root_list_row_standard('Machines by Display Type',        self._misc_url_1_arg('catalog', 'Display_Type'))
        self._render_root_list_row_standard('Machines by Display Rotation',    self._misc_url_1_arg('catalog', 'Display_Rotate'))
        self._render_root_list_row_standard('Machines by Device',              self._misc_url_1_arg('catalog', 'Devices'))
        self._render_root_list_row_standard('Machines by Software List',       self._misc_url_1_arg('catalog', 'BySL'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_skin_dat_slots(self):
        self._render_root_list_row_standard('History DAT',  self._misc_url_1_arg('catalog', 'History'))
        self._render_root_list_row_standard('MAMEINFO DAT', self._misc_url_1_arg('catalog', 'MAMEINFO'))
        self._render_root_list_row_standard('Gameinit DAT', self._misc_url_1_arg('catalog', 'Gameinit'))
        self._render_root_list_row_standard('Command DAT',  self._misc_url_1_arg('catalog', 'Command'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_skin_SL_filters(self):
        if self.settings['SL_hash_path']:
            self._render_root_list_row_standard('Software Lists (with ROMs)', self._misc_url_1_arg('catalog', 'SL_ROM'))
            self._render_root_list_row_standard('Software Lists (with CHDs)', self._misc_url_1_arg('catalog', 'SL_CHD'))
            self._render_root_list_row_standard('Software Lists (with ROMs and CHDs)', self._misc_url_1_arg('catalog', 'SL_ROM_CHD'))
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_root_list_row_catalog(self, display_name, catalog_name, catalog_key):
        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        listitem.setInfo('video', {'title' : display_name, 'overlay' : ICON_OVERLAY})

        # --- Artwork ---
        icon_path   = AML_ICON_FILE_PATH.getPath()
        fanart_path = AML_FANART_FILE_PATH.getPath()
        listitem.setArt({'icon' : icon_path, 'fanart' : fanart_path})

        # --- Create context menu ---
        URL_utils = self._misc_url_3_arg_RunPlugin('command', 'UTILITIES',
                                                   'catalog', catalog_name, 'category', catalog_key)
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Setup plugin', self._misc_url_1_arg_RunPlugin('command', 'SETUP_PLUGIN')),
            ('Utilities', URL_utils),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_2_arg('catalog', catalog_name, 'category', catalog_key)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    def _render_root_list_row_standard(self, root_name, root_URL):
        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(root_name)
        listitem.setInfo('video', {'title' : root_name, 'overlay' : ICON_OVERLAY})

        # --- Artwork ---
        icon_path   = AML_ICON_FILE_PATH.getPath()
        fanart_path = AML_FANART_FILE_PATH.getPath()
        listitem.setArt({'icon' : icon_path, 'fanart' : fanart_path})

        # --- Create context menu ---
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Setup plugin', self._misc_url_1_arg_RunPlugin('command', 'SETUP_PLUGIN')),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = root_URL, listitem = listitem, isFolder = True)

    def _render_custom_filter_row(self, root_name, root_URL):
        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(root_name)
        listitem.setInfo('video', {'title' : root_name, 'overlay' : ICON_OVERLAY})

        # --- Artwork ---
        icon_path   = AML_ICON_FILE_PATH.getPath()
        fanart_path = AML_FANART_FILE_PATH.getPath()
        listitem.setArt({'icon' : icon_path, 'fanart' : fanart_path})

        # --- Create context menu ---
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Setup custom filters', self._misc_url_1_arg_RunPlugin('command', 'SETUP_CUSTOM_FILTERS')),
            ('Setup plugin', self._misc_url_1_arg_RunPlugin('command', 'SETUP_PLUGIN')),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = root_URL, listitem = listitem, isFolder = True)

    #----------------------------------------------------------------------------------------------
    # Cataloged machines
    #----------------------------------------------------------------------------------------------
    # Renders the category names in a catalog.
    def _render_catalog_list(self, catalog_name):
        log_debug('_render_catalog_list() Starting ...')
        log_debug('_render_catalog_list() catalog_name = "{0}"'.format(catalog_name))

        # >> Render categories in catalog index
        self._set_Kodi_all_sorting_methods_and_size()
        mame_view_mode = self.settings['mame_view_mode']
        loading_ticks_start = time.time()
        cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
        if mame_view_mode == VIEW_MODE_FLAT:
            catalog_dic = fs_get_cataloged_dic_all(PATHS, catalog_name)
        elif mame_view_mode == VIEW_MODE_PCLONE:
            catalog_dic = fs_get_cataloged_dic_parents(PATHS, catalog_name)
        if not catalog_dic:
            kodi_dialog_OK('Catalog is empty. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        loading_ticks_end = time.time()
        rendering_ticks_start = time.time()
        for catalog_key in sorted(catalog_dic):
            if mame_view_mode == VIEW_MODE_FLAT:
                num_machines = cache_index_dic[catalog_name][catalog_key]['num_machines']
                if num_machines == 1: machine_str = 'machine'
                else:                 machine_str = 'machines'
            elif mame_view_mode == VIEW_MODE_PCLONE:
                num_machines = cache_index_dic[catalog_name][catalog_key]['num_parents']
                if num_machines == 1: machine_str = 'parent'
                else:                 machine_str = 'parents'
            self._render_catalog_list_row(catalog_name, catalog_key, num_machines, machine_str)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading seconds   {0}'.format(loading_ticks_end - loading_ticks_start))
        log_debug('Rendering seconds {0}'.format(rendering_ticks_end - rendering_ticks_start))

    def _render_catalog_list_row(self, catalog_name, catalog_key, num_machines, machine_str):
        # --- Create listitem row ---
        ICON_OVERLAY = 6
        title_str = '{0} [COLOR orange]({1} {2})[/COLOR]'.format(catalog_key, num_machines, machine_str)
        plot_str = 'Catalog {0}\nCategory {1}'.format(catalog_name, catalog_key)
        listitem = xbmcgui.ListItem(title_str)
        listitem.setInfo('video', {'title' : title_str,      'plot' : plot_str,
                                   'overlay' : ICON_OVERLAY, 'size' : num_machines})

        # --- Artwork ---
        icon_path   = AML_ICON_FILE_PATH.getPath()
        fanart_path = AML_FANART_FILE_PATH.getPath()
        listitem.setArt({'icon' : icon_path, 'fanart' : fanart_path})

        # --- Create context menu ---
        URL_utils = self._misc_url_3_arg_RunPlugin('command', 'UTILITIES',
                                                   'catalog', catalog_name, 'category', catalog_key)
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Utilities', URL_utils),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_2_arg('catalog', catalog_name, 'category', catalog_key)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    #
    # Renders a list of parent MAME machines knowing the catalog name and the category.
    # Display mode: a) parents only b) all machines (flat)
    #
    def _render_catalog_parent_list(self, catalog_name, category_name):
        # When using threads the performance gain is small: from 0.76 to 0.71, just 20 ms.
        # It's not worth it.
        log_debug('_render_catalog_parent_list() catalog_name  = {0}'.format(catalog_name))
        log_debug('_render_catalog_parent_list() category_name = {0}'.format(category_name))
        display_hide_BIOS = self.settings['display_hide_BIOS']
        if catalog_name == 'None' and category_name == 'BIOS': display_hide_BIOS = False
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load ListItem properties (Not used at the moment)
        # prop_key = '{0} - {1}'.format(catalog_name, category_name)
        # log_debug('_render_catalog_parent_list() Loading props with key "{0}"'.format(prop_key))
        # mame_properties_dic = fs_load_JSON_file(PATHS.MAIN_PROPERTIES_PATH.getPath())
        # prop_dic = mame_properties_dic[prop_key]
        # view_mode_property = prop_dic['vm']
        # >> Global properties
        view_mode_property = self.settings['mame_view_mode']
        log_debug('_render_catalog_parent_list() view_mode_property = {0}'.format(view_mode_property))

        # >> Check id main DB exists
        if not PATHS.RENDER_DB_PATH.exists():
            kodi_dialog_OK('MAME database not found. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Load main MAME info DB and catalog
        l_cataloged_dic_start = time.time()
        if view_mode_property == VIEW_MODE_PCLONE:
            catalog_dic = fs_get_cataloged_dic_parents(PATHS, catalog_name)
        elif view_mode_property == VIEW_MODE_FLAT:
            catalog_dic = fs_get_cataloged_dic_all(PATHS, catalog_name)
        else:
            kodi_dialog_OK('Wrong view_mode_property = "{0}". '.format(view_mode_property) +
                           'This is a bug, please report it.')
            return
        l_cataloged_dic_end = time.time()
        if USE_ROM_CACHE:
            l_render_db_start = time.time()
            cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
            MAME_render_db_dic = fs_load_roms_all(PATHS, cache_index_dic, catalog_name, category_name)
            l_render_db_end = time.time()
            l_assets_db_start = time.time()
            MAME_assets_dic = fs_load_assets_all(PATHS, cache_index_dic, catalog_name, category_name)
            l_assets_db_end = time.time()
        else:
            l_render_db_start = time.time()
            MAME_render_db_dic = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            l_render_db_end = time.time()
            l_assets_db_start = time.time()
            MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
            l_assets_db_end = time.time()
        l_pclone_dic_start = time.time()
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
        l_pclone_dic_end = time.time()
        # >> Compute loading times.
        catalog_t = l_cataloged_dic_end - l_cataloged_dic_start
        render_t = l_render_db_end - l_render_db_start
        assets_t = l_assets_db_end - l_assets_db_start
        pclone_t = l_pclone_dic_end - l_pclone_dic_start
        loading_time = catalog_t + render_t + assets_t + pclone_t

        # >> Check if catalog is empty
        if not catalog_dic:
            kodi_dialog_OK('Catalog is empty. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render parent main list
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        machine_dic = catalog_dic[category_name]
        if view_mode_property == VIEW_MODE_PCLONE:
            # >> Parent/Clone mode render parents only
            for machine_name, render_name in machine_dic.iteritems():
                machine = MAME_render_db_dic[machine_name]
                if display_hide_BIOS and machine['isBIOS']: continue
                if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
                if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
                self._render_catalog_machine_row(machine_name, render_name, machine,
                                                 MAME_assets_dic[machine_name],
                                                 True, len(main_pclone_dic[machine_name]),
                                                 catalog_name, category_name)
        else:
            # >> Flat mode renders all machines
            for machine_name, render_name in machine_dic.iteritems():
                machine = MAME_render_db_dic[machine_name]
                if display_hide_BIOS and machine['isBIOS']: continue
                if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
                if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
                self._render_catalog_machine_row(machine_name, render_name, machine,
                                                 MAME_assets_dic[machine_name])
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()
        rendering_time = rendering_ticks_end - rendering_ticks_start
        total_time = loading_time + rendering_time

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading catalog dic {0:.4f} s'.format(catalog_t))
        log_debug('Loading render db   {0:.4f} s'.format(render_t))
        log_debug('Loading assets db   {0:.4f} s'.format(assets_t))
        log_debug('Loading pclone dic  {0:.4f} s'.format(pclone_t))
        log_debug('Loading             {0:.4f} s'.format(loading_time))
        log_debug('Rendering           {0:.4f} s'.format(rendering_time))
        log_debug('Total               {0:.4f} s'.format(total_time))

    #
    # Renders a list of MAME Clone machines (including parent).
    # No need to check for DB existance here. If this function is called is because parents and
    # hence all ROMs databases exist.
    #
    def _render_catalog_clone_list(self, catalog_name, category_name, parent_name):
        log_debug('_render_catalog_clone_list() catalog_name  = {0}'.format(catalog_name))
        log_debug('_render_catalog_clone_list() category_name = {0}'.format(category_name))
        log_debug('_render_catalog_clone_list() parent_name   = {0}'.format(parent_name))
        display_hide_BIOS = self.settings['display_hide_BIOS']
        if catalog_name == 'None' and category_name == 'BIOS': display_hide_BIOS = False
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']
        view_mode_property = self.settings['mame_view_mode']
        log_debug('_render_catalog_clone_list() view_mode_property = {0}'.format(view_mode_property))

        # >> Load main MAME info DB
        loading_ticks_start = time.time()
        catalog_dic = fs_get_cataloged_dic_all(PATHS, catalog_name)
        if USE_ROM_CACHE:
            cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
            MAME_render_db_dic = fs_load_roms_all(PATHS, cache_index_dic, catalog_name, category_name)
            MAME_assets_dic = fs_load_assets_all(PATHS, cache_index_dic, catalog_name, category_name)
        else:
            MAME_render_db_dic = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
        machine_dic = catalog_dic[category_name]
        loading_ticks_end = time.time()

        # >> Render parent first
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        render_name = machine_dic[parent_name]
        machine = MAME_render_db_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_catalog_machine_row(parent_name, render_name, machine, assets)

        # >> Render clones belonging to parent in this category
        for p_name in main_pclone_dic[parent_name]:
            render_name = machine_dic[p_name]
            machine = MAME_render_db_dic[p_name]
            assets  = MAME_assets_dic[p_name]
            if display_hide_BIOS and machine['isBIOS']: continue
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_catalog_machine_row(p_name, render_name, machine, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading seconds   {0}'.format(loading_ticks_end - loading_ticks_start))
        log_debug('Rendering seconds {0}'.format(rendering_ticks_end - rendering_ticks_start))

    def _render_catalog_machine_row(self, m_name, display_name, machine, m_assets,
                                    flag_parent_list = False, num_clones = 0,
                                    catalog_name = '', category_name = ''):
        # --- Default values for flags ---
        AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_NONE

        # --- Render a Parent only list ---
        if flag_parent_list and num_clones > 0:
            # NOTE all machines here are parents
            # --- Mark number of clones ---
            display_name += ' [COLOR orange] ({0} clones)[/COLOR]'.format(num_clones)

            # --- Mark Flags, BIOS, Devices, BIOS, Parent/Clone and Driver status ---
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(m_assets['flags'])
            if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
            if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
            if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
            elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

            # --- Skin flags ---
            AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_PARENT
        else:
            # --- Mark Flags, BIOS, Devices, BIOS, Parent/Clone and Driver status ---
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(m_assets['flags'])
            if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
            if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
            if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'
            if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
            elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

            # --- Skin flags ---
            if machine['cloneof']: AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_CLONE
            else:                  AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_PARENT

        # --- Assets/artwork ---
        icon_path      = m_assets[self.mame_icon] if m_assets[self.mame_icon] else 'DefaultProgram.png'
        fanart_path    = m_assets[self.mame_fanart]
        banner_path    = m_assets['marquee']
        clearlogo_path = m_assets['clearlogo']
        poster_path    = m_assets['flyer']

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        # >> Make all the infolabels compatible with Advanced Emulator Launcher
        if self.settings['display_hide_trailers']:
            listitem.setInfo('video', {'title'   : display_name,     'year'    : machine['year'],
                                       'genre'   : machine['genre'], 'studio'  : machine['manufacturer'],
                                       'plot'    : m_assets['plot'],
                                       'overlay' : ICON_OVERLAY})
        else:
            listitem.setInfo('video', {'title'   : display_name,     'year'    : machine['year'],
                                       'genre'   : machine['genre'], 'studio'  : machine['manufacturer'],
                                       'plot'    : m_assets['plot'], 'trailer' : m_assets['trailer'],
                                       'overlay' : ICON_OVERLAY})
        listitem.setProperty('nplayers', machine['nplayers'])
        listitem.setProperty('platform', 'MAME')

        # --- Assets ---
        # >> AEL/AML custom artwork fields
        listitem.setArt({
            'title'     : m_assets['title'],   'snap'      : m_assets['snap'],
            'boxfront'  : m_assets['cabinet'], 'boxback'   : m_assets['cpanel'],
            'cartridge' : m_assets['PCB'],     'flyer'     : m_assets['flyer'],
            'icon'      : icon_path,           'fanart'    : fanart_path,
            'banner'    : banner_path,         'clearlogo' : clearlogo_path, 'poster' : poster_path
        })

        # --- ROM flags (Skins will use these flags to render icons) ---
        listitem.setProperty(AEL_PCLONE_STAT_LABEL, AEL_PClone_stat_value)

        # --- Create context menu ---
        URL_view_DAT = self._misc_url_2_arg_RunPlugin('command', 'VIEW_DAT', 'machine', m_name)
        URL_view = self._misc_url_2_arg_RunPlugin('command', 'VIEW', 'machine', m_name)
        URL_fav = self._misc_url_2_arg_RunPlugin('command', 'ADD_MAME_FAV', 'machine', m_name)
        if flag_parent_list and num_clones > 0:
            URL_clones = self._misc_url_4_arg_RunPlugin('command', 'EXEC_SHOW_MAME_CLONES', 
                                                        'catalog', catalog_name,
                                                        'category', category_name, 'parent', m_name)
            commands = [
                ('Info / Utils', URL_view_DAT),
                ('View / Audit', URL_view),
                ('Show clones', URL_clones),
                ('Add to MAME Favourites', URL_fav),
                ('Kodi File Manager', 'ActivateWindow(filemanager)'),
                ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
            ]
        else:
            commands = [
                ('Info / Utils', URL_view_DAT),
                ('View / Audit', URL_view),
                ('Add to MAME Favourites', URL_fav),
                ('Kodi File Manager', 'ActivateWindow(filemanager)'),
                ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
            ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_2_arg('command', 'LAUNCH', 'machine', m_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    #
    # Not used at the moment -> There are global display settings.
    #
    def _command_context_display_settings(self, catalog_name, category_name):
        # >> Load ListItem properties
        log_debug('_command_display_settings() catalog_name  "{0}"'.format(catalog_name))
        log_debug('_command_display_settings() category_name "{0}"'.format(category_name))
        prop_key = '{0} - {1}'.format(catalog_name, category_name)
        log_debug('_command_display_settings() Loading props with key "{0}"'.format(prop_key))
        mame_properties_dic = fs_load_JSON_file(PATHS.MAIN_PROPERTIES_PATH.getPath())
        prop_dic = mame_properties_dic[prop_key]
        if prop_dic['vm'] == VIEW_MODE_NORMAL: dmode_str = 'Parents only'
        else:                                  dmode_str = 'Parents and clones'

        # --- Select menu ---
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Display settings',
                                 ['Display mode (currently {0})'.format(dmode_str),
                                  'Default Icon',   'Default Fanart',
                                  'Default Banner', 'Default Poster',
                                  'Default Clearlogo'])
        if menu_item < 0: return
        
        # --- Display settings ---
        if menu_item == 0:
            # >> Krypton feature: preselect the current item.
            # >> NOTE Preselect must be called with named parameter, otherwise it does not work well.
            # See http://forum.kodi.tv/showthread.php?tid=250936&pid=2327011#pid2327011
            if prop_dic['vm'] == VIEW_MODE_NORMAL: p_idx = 0
            else:                                  p_idx = 1
            log_debug('_command_display_settings() p_idx = "{0}"'.format(p_idx))
            idx = dialog.select('Display mode', ['Parents only', 'Parents and clones'], preselect = p_idx)
            log_debug('_command_display_settings() idx = "{0}"'.format(idx))
            if idx < 0: return
            if idx == 0:   prop_dic['vm'] = VIEW_MODE_NORMAL
            elif idx == 1: prop_dic['vm'] = VIEW_MODE_ALL

        # --- Change default icon ---
        elif menu_item == 1:
            kodi_dialog_OK('Not coded yet. Sorry')

        # >> Changes made. Refreash container
        fs_write_JSON_file(PATHS.MAIN_PROPERTIES_PATH.getPath(), mame_properties_dic)
        kodi_refresh_container()

    #----------------------------------------------------------------------------------------------
    # Software Lists
    #----------------------------------------------------------------------------------------------
    def _render_SL_list(self, catalog_name):
        log_debug('_render_SL_list() catalog_name = {0}\n'.format(catalog_name))
        # >> Load Software List catalog
        SL_main_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
        if not SL_main_catalog_dic:
            kodi_dialog_OK('Software Lists database not found. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Build SL
        SL_catalog_dic = {}
        if catalog_name == 'SL_ROM':
            for SL_name, SL_dic in SL_main_catalog_dic.iteritems():
                if SL_dic['num_with_ROMs'] > 0 and SL_dic['num_with_CHDs'] == 0:
                    SL_catalog_dic[SL_name] = SL_dic
        elif catalog_name == 'SL_CHD':
            for SL_name, SL_dic in SL_main_catalog_dic.iteritems():
                if SL_dic['num_with_CHDs'] > 0 and SL_dic['num_with_ROMs'] == 0:
                    SL_catalog_dic[SL_name] = SL_dic
        elif catalog_name == 'SL_ROM_CHD':
            for SL_name, SL_dic in SL_main_catalog_dic.iteritems():
                if SL_dic['num_with_ROMs'] > 0 and SL_dic['num_with_CHDs'] > 0:
                    SL_catalog_dic[SL_name] = SL_dic
        else:
            kodi_dialog_OK('Wrong catalog_name {0}'.format(catalog_name))
            return
        log_debug('_render_SL_list() len(catalog_name) = {0}\n'.format(len(SL_catalog_dic)))

        self._set_Kodi_all_sorting_methods()
        for SL_name in SL_catalog_dic:
            SL = SL_catalog_dic[SL_name]
            self._render_SL_list_row(SL_name, SL)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_ROMs(self, SL_name):
        log_debug('_render_SL_ROMs() SL_name "{0}"'.format(SL_name))

        # >> Load ListItem properties (Not used at the moment)
        # SL_properties_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PROP_PATH.getPath()) 
        # prop_dic = SL_properties_dic[SL_name]
        # >> Global properties
        view_mode_property = self.settings['sl_view_mode']
        log_debug('_render_SL_ROMs() view_mode_property = {0}'.format(view_mode_property))

        # >> Load Software List ROMs
        SL_PClone_dic = fs_load_JSON_file(PATHS.SL_PCLONE_DIC_PATH.getPath())
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        # log_debug('_render_SL_ROMs() SL ROMs JSON "{0}"'.format(SL_DB_FN.getPath()))
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())

        assets_file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
        SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
        SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())

        self._set_Kodi_all_sorting_methods()
        SL_proper_name = SL_catalog_dic[SL_name]['display_name']
        if view_mode_property == VIEW_MODE_PCLONE:
            log_debug('_render_SL_ROMs() Rendering Parent/Clone launcher')
            # >> Get list of parents
            parent_list = []
            for parent_name in sorted(SL_PClone_dic[SL_name]): parent_list.append(parent_name)
            for parent_name in parent_list:
                ROM        = SL_roms[parent_name]
                assets     = SL_asset_dic[parent_name] if parent_name in SL_asset_dic else fs_new_SL_asset()
                num_clones = len(SL_PClone_dic[SL_name][parent_name])
                ROM['genre'] = SL_proper_name # >> Add the SL name as 'genre'
                self._render_SL_ROM_row(SL_name, parent_name, ROM, assets, True, num_clones)
        elif view_mode_property == VIEW_MODE_FLAT:
            log_debug('_render_SL_ROMs() Rendering Flat launcher')
            for rom_name in SL_roms:
                ROM    = SL_roms[rom_name]
                assets = SL_asset_dic[rom_name] if rom_name in SL_asset_dic else fs_new_SL_asset()
                ROM['genre'] = SL_proper_name # >> Add the SL name as 'genre'
                self._render_SL_ROM_row(SL_name, rom_name, ROM, assets)
        else:
            kodi_dialog_OK('Wrong vm = "{0}". This is a bug, please report it.'.format(prop_dic['vm']))
            return
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_pclone_set(self, SL_name, parent_name):
        log_debug('_render_SL_pclone_set() SL_name     "{0}"'.format(SL_name))
        log_debug('_render_SL_pclone_set() parent_name "{0}"'.format(parent_name))
        view_mode_property = self.settings['sl_view_mode']
        log_debug('_render_SL_pclone_set() view_mode_property = {0}'.format(view_mode_property))

        # >> Load Software List ROMs
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
        SL_PClone_dic = fs_load_JSON_file(PATHS.SL_PCLONE_DIC_PATH.getPath())
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        log_debug('_render_SL_pclone_set() ROMs JSON "{0}"'.format(SL_DB_FN.getPath()))
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())

        assets_file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
        SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
        SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())

        # >> Render parent first
        SL_proper_name = SL_catalog_dic[SL_name]['display_name']
        self._set_Kodi_all_sorting_methods()
        ROM = SL_roms[parent_name]
        assets = SL_asset_dic[parent_name] if parent_name in SL_asset_dic else fs_new_SL_asset()
        ROM['genre'] = SL_proper_name # >> Add the SL name as 'genre'
        self._render_SL_ROM_row(SL_name, parent_name, ROM, assets, False, view_mode_property)

        # >> Render clones belonging to parent in this category
        for clone_name in sorted(SL_PClone_dic[SL_name][parent_name]):
            ROM = SL_roms[clone_name]
            assets = SL_asset_dic[clone_name] if clone_name in SL_asset_dic else fs_new_SL_asset()
            ROM['genre'] = SL_proper_name # >> Add the SL name as 'genre'
            log_debug(unicode(ROM))
            self._render_SL_ROM_row(SL_name, clone_name, ROM, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_SL_list_row(self, SL_name, SL):
        if SL['num_with_CHDs'] == 0:
            if SL['num_with_ROMs'] == 1:
                display_name = '{0}  [COLOR orange]({1} ROM)[/COLOR]'.format(SL['display_name'], SL['num_with_ROMs'])
            else:
                display_name = '{0}  [COLOR orange]({1} ROMs)[/COLOR]'.format(SL['display_name'], SL['num_with_ROMs'])
        elif SL['num_with_ROMs'] == 0:
            if SL['num_with_CHDs'] == 1:
                display_name = '{0}  [COLOR orange]({1} CHD)[/COLOR]'.format(SL['display_name'], SL['num_with_CHDs'])
            else:
                display_name = '{0}  [COLOR orange]({1} CHDs)[/COLOR]'.format(SL['display_name'], SL['num_with_CHDs'])
        else:
            display_name = '{0}  [COLOR orange]({1} ROMs and {2} CHDs)[/COLOR]'.format(SL['display_name'], SL['num_with_ROMs'], SL['num_with_CHDs'])

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        listitem.setInfo('video', {'title' : display_name, 'overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Kodi File Manager', 'ActivateWindow(filemanager)' ),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_2_arg('catalog', 'SL', 'category', SL_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    def _render_SL_ROM_row(self, SL_name, rom_name, ROM, assets, flag_parent_list = False, num_clones = 0):
        display_name = ROM['description']
        if flag_parent_list and num_clones > 0:
            display_name += ' [COLOR orange] ({0} clones)[/COLOR]'.format(num_clones)
            status = '{0}{1}'.format(ROM['status_ROM'], ROM['status_CHD'])
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)
        else:
            # --- Mark flags and status ---
            status = '{0}{1}'.format(ROM['status_ROM'], ROM['status_CHD'])
            display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)
            if ROM['cloneof']: display_name += ' [COLOR orange][Clo][/COLOR]'

        # --- Assets/artwork ---
        icon_path   = assets[self.SL_icon] if assets[self.SL_icon] else 'DefaultProgram.png'
        fanart_path = assets[self.SL_fanart]
        poster_path = assets['boxfront']

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        # >> Make all the infolabels compatible with Advanced Emulator Launcher
        if self.settings['display_hide_trailers']:
            listitem.setInfo('video', {'title'   : display_name,      'year'    : ROM['year'],
                                       'genre'   : ROM['genre'],      'studio'  : ROM['publisher'],
                                       'plot'    : ROM['plot'],       'overlay' : ICON_OVERLAY })
        else:
            listitem.setInfo('video', {'title'   : display_name,      'year'    : ROM['year'],
                                       'genre'   : ROM['genre'],      'studio'  : ROM['publisher'],
                                       'plot'    : ROM['plot'],       'overlay' : ICON_OVERLAY,
                                       'trailer' : assets['trailer'] })
        listitem.setProperty('platform', 'MAME Software List')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title' : assets['title'], 'snap' : assets['snap'], 'boxfront' : assets['boxfront'],
                         'icon' : icon_path, 'fanart' : fanart_path, 'poster' : poster_path})

        # --- Create context menu ---
        URL_view_DAT = self._misc_url_3_arg_RunPlugin('command', 'VIEW_DAT', 'SL', SL_name, 'ROM', rom_name)
        URL_view = self._misc_url_3_arg_RunPlugin('command', 'VIEW', 'SL', SL_name, 'ROM', rom_name)
        URL_fav = self._misc_url_3_arg_RunPlugin('command', 'ADD_SL_FAV', 'SL', SL_name, 'ROM', rom_name)
        if flag_parent_list and num_clones > 0:
            URL_show_c = self._misc_url_4_arg_RunPlugin('command', 'EXEC_SHOW_SL_CLONES', 
                                                        'catalog', 'SL', 'category', SL_name, 'parent', rom_name)
            commands = [
                ('Info / Utils', URL_view_DAT),
                ('View / Audit', URL_view),
                ('Show clones', URL_show_c),
                ('Add ROM to SL Favourites', URL_fav),
                ('Kodi File Manager', 'ActivateWindow(filemanager)'),
                ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
            ]
        else:
            commands = [
                ('Info / Utils', URL_view_DAT),
                ('View / Audit', URL_view),
                ('Add ROM to SL Favourites', URL_fav),
                ('Kodi File Manager', 'ActivateWindow(filemanager)'),
                ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
            ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_3_arg('command', 'LAUNCH_SL', 'SL', SL_name, 'ROM', rom_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    #----------------------------------------------------------------------------------------------
    # DATs
    #
    # catalog = 'History'  / category = '32x' / machine = 'sonic'
    # catalog = 'MAMEINFO' / category = '32x' / machine = 'sonic'
    # catalog = 'Gameinit' / category = 'None' / machine = 'sonic'
    # catalog = 'Command'  / category = 'None' / machine = 'sonic'
    #----------------------------------------------------------------------------------------------
    def _render_DAT_list(self, catalog_name):
        # --- Create context menu ---
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        # --- Unrolled variables ---
        ICON_OVERLAY = 6

        # >> Load Software List catalog
        if catalog_name == 'History':
            DAT_idx_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
            if not DAT_idx_dic:
                kodi_dialog_OK('DAT database file "{0}" empty.'.format(catalog_name))
                xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
                return
            self._set_Kodi_all_sorting_methods()
            for key in DAT_idx_dic:
                category_name = '{0} [COLOR lightgray]({1})[/COLOR]'.format(DAT_idx_dic[key]['name'], key)
                listitem = xbmcgui.ListItem(category_name)
                listitem.setInfo('video', {'title' : category_name, 'overlay' : ICON_OVERLAY } )
                listitem.addContextMenuItems(commands)
                URL = self._misc_url_2_arg('catalog', catalog_name, 'category', key)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
        elif catalog_name == 'MAMEINFO':
            DAT_idx_dic = fs_load_JSON_file(PATHS.MAMEINFO_IDX_PATH.getPath())
            if not DAT_idx_dic:
                kodi_dialog_OK('DAT database file "{0}" empty.'.format(catalog_name))
                xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
                return
            self._set_Kodi_all_sorting_methods()
            for key in DAT_idx_dic:
                category_name = '{0}'.format(key)
                listitem = xbmcgui.ListItem(category_name)
                listitem.setInfo('video', {'title' : category_name, 'overlay' : ICON_OVERLAY } )
                listitem.addContextMenuItems(commands)
                URL = self._misc_url_2_arg('catalog', catalog_name, 'category', key)
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)
        elif catalog_name == 'Gameinit':
            DAT_idx_list = fs_load_JSON_file(PATHS.GAMEINIT_IDX_PATH.getPath())
            if not DAT_idx_list:
                kodi_dialog_OK('DAT database file "{0}" empty.'.format(catalog_name))
                xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
                return
            self._set_Kodi_all_sorting_methods()
            for machine_name_list in DAT_idx_list:
                machine_name = '{0} [COLOR lightgray]({1})[/COLOR]'.format(machine_name_list[1], machine_name_list[0])
                listitem = xbmcgui.ListItem(machine_name)
                listitem.setInfo('video', {'title' : machine_name, 'overlay' : ICON_OVERLAY } )
                listitem.addContextMenuItems(commands)
                URL = self._misc_url_3_arg('catalog', catalog_name, 'category', 'None', 'machine', machine_name_list[0])
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)
        elif catalog_name == 'Command':
            DAT_idx_list = fs_load_JSON_file(PATHS.COMMAND_IDX_PATH.getPath())
            if not DAT_idx_list:
                kodi_dialog_OK('DAT database file "{0}" empty.'.format(catalog_name))
                xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
                return
            self._set_Kodi_all_sorting_methods()
            for machine_name_list in DAT_idx_list:
                machine_name = '{0} [COLOR lightgray]({1})[/COLOR]'.format(machine_name_list[1], machine_name_list[0])
                listitem = xbmcgui.ListItem(machine_name)
                listitem.setInfo('video', {'title' : machine_name, 'overlay' : ICON_OVERLAY } )
                listitem.addContextMenuItems(commands)
                URL = self._misc_url_3_arg('catalog', catalog_name, 'category', 'None', 'machine', machine_name_list[0])
                xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)
        else:
            kodi_dialog_OK('DAT database file "{0}" not found. Check out "Setup plugin" context menu.'.format(catalog_name))
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_DAT_category(self, catalog_name, category_name):
        # >> Load Software List catalog
        if catalog_name == 'History':
            DAT_catalog_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
        elif catalog_name == 'MAMEINFO':
            DAT_catalog_dic = fs_load_JSON_file(PATHS.MAMEINFO_IDX_PATH.getPath())
        else:
            kodi_dialog_OK('DAT database file "{0}" not found. Check out "Setup plugin" context menu.'.format(catalog_name))
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return
        if not DAT_catalog_dic:
            kodi_dialog_OK('DAT database file "{0}" empty.'.format(catalog_name))
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return
        self._set_Kodi_all_sorting_methods()
        if catalog_name == 'History':
            category_machine_list = DAT_catalog_dic[category_name]['machines']
            for machine_tuple in category_machine_list:
                self._render_DAT_category_row(catalog_name, category_name, machine_tuple)
        elif catalog_name == 'MAMEINFO':
            category_machine_list = DAT_catalog_dic[category_name]
            for machine_tuple in category_machine_list:
                self._render_DAT_category_row(catalog_name, category_name, machine_tuple)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_DAT_category_row(self, catalog_name, category_name, machine_tuple):
        display_name = '{0} [COLOR lightgray]({1})[/COLOR]'.format(machine_tuple[1], machine_tuple[0])

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        listitem.setInfo('video', {'title' : display_name, 'overlay' : ICON_OVERLAY } )

        # --- Create context menu ---
        commands = [
            ('View', self._misc_url_1_arg_RunPlugin('command', 'VIEW')),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('Add-on Settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_3_arg('catalog', catalog_name, 'category', category_name, 'machine', machine_tuple[0])
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    def _render_DAT_machine_info(self, catalog_name, category_name, machine_name):
        log_debug('_render_DAT_machine_info() catalog_name "{0}"'.format(catalog_name))
        log_debug('_render_DAT_machine_info() category_name "{0}"'.format(category_name))
        log_debug('_render_DAT_machine_info() machine_name "{0}"'.format(machine_name))

        # >> Load Software List catalog
        if catalog_name == 'History':
            DAT_dic = fs_load_JSON_file(PATHS.HISTORY_DB_PATH.getPath())
            info_str = DAT_dic[category_name][machine_name]
            info_text = info_str
        elif catalog_name == 'MAMEINFO':
            DAT_dic = fs_load_JSON_file(PATHS.MAMEINFO_DB_PATH.getPath())
            info_str = DAT_dic[category_name][machine_name]
            info_text = info_str
        elif catalog_name == 'Gameinit':
            DAT_dic = fs_load_JSON_file(PATHS.GAMEINIT_DB_PATH.getPath())
            info_str = DAT_dic[machine_name]
            info_text = info_str
        elif catalog_name == 'Command':
            DAT_dic = fs_load_JSON_file(PATHS.COMMAND_DB_PATH.getPath())
            info_str = DAT_dic[machine_name]
            info_text = info_str
        else:
            kodi_dialog_OK('Wrong catalog_name "{0}". '.format(catalog_name) +
                           'This is a bug, please report it.')
            return

        # --- Show information window ---
        window_title = '{0} information'.format(catalog_name)
        self._display_text_window(window_title, info_text)

    #
    # Not used at the moment -> There are global display settings.
    #
    def _command_context_display_settings_SL(self, SL_name):
        log_debug('_command_display_settings_SL() SL_name "{0}"'.format(SL_name))

        # --- Load properties DB ---
        SL_properties_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PROP_PATH.getPath())
        prop_dic = SL_properties_dic[SL_name]

        # --- Show menu ---
        if prop_dic['vm'] == VIEW_MODE_NORMAL: dmode_str = 'Parents only'
        else:                                  dmode_str = 'Parents and clones'
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Display settings',
                                 ['Display mode (currently {0})'.format(dmode_str),
                                  'Default Icon', 'Default Fanart', 
                                  'Default Banner', 'Default Poster', 'Default Clearlogo'])
        if menu_item < 0: return

        # --- Change display mode ---
        if menu_item == 0:
            if prop_dic['vm'] == VIEW_MODE_NORMAL: p_idx = 0
            else:                                  p_idx = 1
            log_debug('_command_display_settings() p_idx = "{0}"'.format(p_idx))
            idx = dialog.select('Display mode', ['Parents only', 'Parents and clones'], preselect = p_idx)
            log_debug('_command_display_settings() idx = "{0}"'.format(idx))
            if idx < 0: return
            if idx == 0:   prop_dic['vm'] = VIEW_MODE_NORMAL
            elif idx == 1: prop_dic['vm'] = VIEW_MODE_ALL

        # --- Change default icon ---
        elif menu_item == 1:
            kodi_dialog_OK('Not coded yet. Sorry')

        # --- Save display settings ---
        fs_write_JSON_file(PATHS.SL_MACHINES_PROP_PATH.getPath(), SL_properties_dic)
        kodi_refresh_container()

    # ---------------------------------------------------------------------------------------------
    # Information display / Utilities
    # ---------------------------------------------------------------------------------------------
    def _command_context_view_DAT(self, machine_name, SL_name, SL_ROM, location):
        VIEW_MAME_MACHINE = 100
        VIEW_SL_ROM       = 200

        ACTION_VIEW_HISTORY           = 100
        ACTION_VIEW_MAMEINFO          = 200
        ACTION_VIEW_GAMEINIT          = 300
        ACTION_VIEW_COMMAND           = 400
        ACTION_VIEW_FANART            = 500
        ACTION_VIEW_MANUAL            = 600
        ACTION_VIEW_BROTHERS          = 700
        ACTION_VIEW_SAME_GENRE        = 800
        ACTION_VIEW_SAME_MANUFACTURER = 900

        # --- Determine if we are in a category, launcher or ROM ---
        log_debug('_command_context_view_DAT() machine_name "{0}"'.format(machine_name))
        log_debug('_command_context_view_DAT() SL_name      "{0}"'.format(SL_name))
        log_debug('_command_context_view_DAT() SL_ROM       "{0}"'.format(SL_ROM))
        log_debug('_command_context_view_DAT() location     "{0}"'.format(location))
        if machine_name:
            view_type = VIEW_MAME_MACHINE
        elif SL_name:
            view_type = VIEW_SL_ROM
        log_debug('_command_context_view_DAT() view_type = {0}'.format(view_type))

        if view_type == VIEW_MAME_MACHINE:
            # >> Load DAT indices
            History_idx_dic   = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
            Mameinfo_idx_dic  = fs_load_JSON_file(PATHS.MAMEINFO_IDX_PATH.getPath())
            Gameinit_idx_list = fs_load_JSON_file(PATHS.GAMEINIT_IDX_PATH.getPath())
            Command_idx_list  = fs_load_JSON_file(PATHS.COMMAND_IDX_PATH.getPath())

            # >> Check if DAT information is available for this machine
            if History_idx_dic:
                # >> Python Set Comprehension
                History_MAME_set = { machine[0] for machine in History_idx_dic['mame']['machines'] }
                if machine_name in History_MAME_set: History_str = 'Found'
                else:                                History_str = 'Not found'
            else:
                History_str = 'Not configured'
            if Mameinfo_idx_dic:
                Mameinfo_MAME_set = { machine[0] for machine in Mameinfo_idx_dic['mame'] }
                if machine_name in Mameinfo_MAME_set: Mameinfo_str = 'Found'
                else:                                 Mameinfo_str = 'Not found'
            else:
                Mameinfo_str = 'Not configured'
            if Gameinit_idx_list:
                Gameinit_MAME_set = { machine[0] for machine in Gameinit_idx_list }
                if machine_name in Gameinit_MAME_set: Gameinit_str = 'Found'
                else:                                 Gameinit_str = 'Not found'
            else:
                Gameinit_str = 'Not configured'
            if Command_idx_list:
                Command_MAME_set = { machine[0] for machine in Command_idx_list }
                if machine_name in Command_MAME_set: Command_str = 'Found'
                else:                                Command_str = 'Not found'
            else:
                Command_str = 'Not configured'
        elif view_type == VIEW_SL_ROM:
            History_idx_dic   = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
            if History_idx_dic:
                if SL_name in History_idx_dic:
                    History_MAME_set = { machine[0] for machine in History_idx_dic[SL_name]['machines'] }
                    if SL_ROM in History_MAME_set: History_str = 'Found'
                    else:                          History_str = 'Not found'
                else:
                    History_str = 'SL not found'
            else:
                History_str = 'Not configured'

        # --- Build menu base on view_type ---
        if view_type == VIEW_MAME_MACHINE:
            d_list = [
              'View History DAT ({0})'.format(History_str),
              'View MAMEinfo DAT ({0})'.format(Mameinfo_str),
              'View Gameinit DAT ({0})'.format(Gameinit_str),
              'View Command DAT ({0})'.format(Command_str),
              'View Fanart',
              'View Manual',
              'Display brother machines',
              'Display machines with same Genre',
              'Display machines by same Manufacturer',
            ]
        elif view_type == VIEW_SL_ROM:
            d_list = [
              'View History DAT ({0})'.format(History_str),
              'View Fanart',
              'View Manual',
            ]
        else:
            kodi_dialog_OK('Wrong view_type = {0}. This is a bug, please report it.'.format(view_type))
            return
        selected_value = xbmcgui.Dialog().select('View', d_list)
        if selected_value < 0: return

        # --- Polymorphic menu. Determine action to do. ---
        if view_type == VIEW_MAME_MACHINE:
            if   selected_value == 0: action = ACTION_VIEW_HISTORY
            elif selected_value == 1: action = ACTION_VIEW_MAMEINFO
            elif selected_value == 2: action = ACTION_VIEW_GAMEINIT
            elif selected_value == 3: action = ACTION_VIEW_COMMAND
            elif selected_value == 4: action = ACTION_VIEW_FANART
            elif selected_value == 5: action = ACTION_VIEW_MANUAL
            elif selected_value == 6: action = ACTION_VIEW_BROTHERS
            elif selected_value == 7: action = ACTION_VIEW_SAME_GENRE
            elif selected_value == 8: action = ACTION_VIEW_SAME_MANUFACTURER
            else:
                kodi_dialog_OK('view_type == VIEW_MAME_MACHINE and selected_value = {0}. '.format(selected_value) +
                               'This is a bug, please report it.')
                return
        elif view_type == VIEW_SL_ROM:
            if   selected_value == 0: action = ACTION_VIEW_HISTORY
            elif selected_value == 1: action = ACTION_VIEW_FANART
            elif selected_value == 2: action = ACTION_VIEW_MANUAL
            else:
                kodi_dialog_OK('view_type == VIEW_SL_ROM and selected_value = {0}. '.format(selected_value) +
                               'This is a bug, please report it.')
                return

        # --- Execute action ---
        if action == ACTION_VIEW_HISTORY:
            if view_type == VIEW_MAME_MACHINE:
                if machine_name not in History_MAME_set:
                    kodi_dialog_OK('MAME machine {0} not in History DAT'.format(machine_name))
                    return
                DAT_dic = fs_load_JSON_file(PATHS.HISTORY_DB_PATH.getPath())
                window_title = 'History DAT for MAME machine {0}'.format(machine_name)
                info_text = DAT_dic['mame'][machine_name]
            elif view_type == VIEW_SL_ROM:
                if SL_ROM not in History_MAME_set:
                    kodi_dialog_OK('SL item {0} not in History DAT'.format(SL_ROM))
                    return
                DAT_dic = fs_load_JSON_file(PATHS.HISTORY_DB_PATH.getPath())
                window_title = 'History DAT for SL item {0}'.format(SL_ROM)
                info_text = DAT_dic[SL_name][SL_ROM]
            self._display_text_window(window_title, info_text)

        elif action == ACTION_VIEW_MAMEINFO:
            if machine_name not in Mameinfo_MAME_set:
                kodi_dialog_OK('Machine {0} not in Mameinfo DAT'.format(machine_name))
                return
            DAT_dic = fs_load_JSON_file(PATHS.MAMEINFO_DB_PATH.getPath())
            info_text = DAT_dic['mame'][machine_name]

            window_title = 'MAMEinfo DAT for machine {0}'.format(machine_name)
            self._display_text_window(window_title, info_text)

        elif action == ACTION_VIEW_GAMEINIT:
            if machine_name not in Gameinit_MAME_set:
                kodi_dialog_OK('Machine {0} not in Gameinit DAT'.format(machine_name))
                return
            DAT_dic = fs_load_JSON_file(PATHS.GAMEINIT_DB_PATH.getPath())
            window_title = 'Gameinit DAT for machine {0}'.format(machine_name)
            info_text = DAT_dic[machine_name]
            self._display_text_window(window_title, info_text)

        elif action == ACTION_VIEW_COMMAND:
            if machine_name not in Command_MAME_set:
                kodi_dialog_OK('Machine {0} not in Command DAT'.format(machine_name))
                return
            DAT_dic = fs_load_JSON_file(PATHS.COMMAND_DB_PATH.getPath())
            window_title = 'Command DAT for machine {0}'.format(machine_name)
            info_text = DAT_dic[machine_name]
            self._display_text_window(window_title, info_text)

        # --- View Fanart ---
        elif action == ACTION_VIEW_FANART:
            # >> Open ROM in assets database
            if view_type == VIEW_MAME_MACHINE:
                if location == 'STANDARD':
                    assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                    m_assets = assets_dic[machine_name]
                else:
                    mame_favs_dic = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
                    m_assets = mame_favs_dic[machine_name]['assets']
                if not m_assets['fanart']:
                    kodi_dialog_OK('Fanart for machine {0} not found.'.format(machine_name))
                    return
            elif view_type == VIEW_SL_ROM:
                SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                assets_file_name = SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
                SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
                SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())
                m_assets = SL_asset_dic[SL_ROM]
                if not m_assets['fanart']:
                    kodi_dialog_OK('Fanart for SL item {0} not found.'.format(SL_ROM))
                    return

            # >> If manual found then display it.
            log_debug('Rendering FS fanart "{0}"'.format(m_assets['fanart']))
            xbmc.executebuiltin('ShowPicture("{0}")'.format(m_assets['fanart']))

        # --- View Manual ---
        # For the PDF viewer implementation look at https://github.com/i96751414/plugin.image.pdfreader
        #
        # When Pictures menu is clicked on Home, the window pictures (MyPics.xml) opens.
        # Pictures are browsed with the pictures window. When an image is clicked with ENTER the
        # window changes to slideshow (SlideShow.xml) and the pictures are displayed in full 
        # screen with not pan/zoom effects. Pictures can be changed with the arrow keys (they
        # do not change automatically). The slideshow can also be started from the side menu 
        # "View slideshow". Initiated this way, the slideshow has a pan/zooming effects and all 
        # pictures in the list are changed every few seconds.
        #
        # Use the builtin function SlideShow("{0}",pause) to show a set of pictures in full screen.
        # See https://forum.kodi.tv/showthread.php?tid=329349
        #
        elif action == ACTION_VIEW_MANUAL:
            # --- Slideshow DEBUG snippet ---
            # >> https://kodi.wiki/view/List_of_built-in_functions is outdated!
            # >> See https://github.com/xbmc/xbmc/blob/master/xbmc/interfaces/builtins/PictureBuiltins.cpp
            # >> '\' in path strings must be escaped like '\\'
            # >> Builtin function arguments can be in any order (at least for this function).
            # xbmc.executebuiltin('SlideShow("{0}",pause)'.format(r'E:\\AML-stuff\\AML-assets\\fanarts\\'))

            # >> If manual found then display it.
            # >> First, extract images from the PDF/CBZ.
            # >> Put the extracted images in a directory named MANUALS_DIR/manual_name.pages/
            # >> Check the modification times of the PDF manual file witht the timestamp of
            # >> the first file to regenerate the images if PDF is newer than first extracted img.
            # NOTE CBZ/CBR files are supported by Kodi. It can be extracted with the builtin
            #      function extract. In addition to PDF extension, CBR and CBZ extensions must
            #      also be searched for manuals.
            if view_type == VIEW_MAME_MACHINE:
                log_debug('Displaying Manual for MAME machine {0} ...'.format(machine_name))
                # machine = fs_get_machine_main_db_hash(PATHS, machine_name)
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                if not assets_dic[machine_name]['manual']:
                    kodi_dialog_OK('Manual not found in database.')
                    return
                PDF_file_FN = FileName(assets_dic[machine_name]['manual'])
                img_dir_FN = FileName(self.settings['assets_path']).pjoin('manuals').pjoin(machine_name + '.pages')
            elif view_type == VIEW_SL_ROM:
                log_debug('Displaying Manual for SL {0} item {1} ...'.format(SL_name, SL_ROM))
                SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                assets_file_name = SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
                SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
                SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())
                if not SL_asset_dic[SL_ROM]['manual']:
                    kodi_dialog_OK('Manual not found in database.')
                    return
                PDF_file_FN = FileName(SL_asset_dic[SL_ROM]['manual'])
                img_dir_FN = FileName(self.settings['assets_path']).pjoin('manuals_SL').pjoin(SL_name).pjoin(SL_ROM + '.pages')
            log_debug('PDF_file_FN P "{0}"'.format(PDF_file_FN.getPath()))
            log_debug('img_dir_FN P  "{0}"'.format(img_dir_FN.getPath()))
            if not PDF_file_FN.exists():
                kodi_dialog_OK('PDF file {0} not found.'.format(PDF_file_FN.getPath()))
                return

            # >> Progress dialog
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('Advanced MAME Launcher', 'Extracting images from PDF file ...')
            pDialog.update(0)

            # >> Extract images from PDF
            reader = PDFReader(PDF_file_FN.getPath(), img_dir_FN.getPath())
            log_debug('reader.info() = {0}'.format(unicode(reader.info())))
            images = reader.convert_to_images()
            # log_debug(unicode(images))
            pDialog.update(100)
            pDialog.close()

            # >> Show images
            if not images:
                kodi_dialog_OK('Cannot find images inside the PDF file.')
                return
            # kodi_dialog_OK('PDF contains {0} images. Showing them ...'.format(len(images)))
            log_debug('Rendering images in "{0}"'.format(img_dir_FN.getPath()))
            xbmc.executebuiltin('SlideShow("{0}",pause)'.format(img_dir_FN.getPath()))

        # --- Display brother machines (same driver) ---
        elif action == ACTION_VIEW_BROTHERS:
            # >> Load ROM Render data from hashed database
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            # >> Some (important) drivers have a different name
            sourcefile_str = machine['sourcefile']
            log_debug('Original driver "{0}"'.format(sourcefile_str))
            if sourcefile_str in mame_driver_name_dic:
                sourcefile_str = mame_driver_name_dic[sourcefile_str]
            log_debug('Final driver    "{0}"'.format(sourcefile_str))

            # --- Replace current window by search window ---
            # When user press Back in search window it returns to the original window (either showing
            # launcher in a cateogory or displaying ROMs in a launcher/virtual launcher).
            #
            # NOTE ActivateWindow() / RunPlugin() / RunAddon() seem not to work here
            url = self._misc_url_2_arg('catalog', 'Driver', 'category', sourcefile_str)
            log_debug('Container.Update URL "{0}"'.format(url))
            xbmc.executebuiltin('Container.Update({0})'.format(url))

        # --- Display machines with same Genre ---
        elif action == ACTION_VIEW_SAME_GENRE:
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            genre_str = machine['genre']
            url = self._misc_url_2_arg('catalog', 'Genre', 'category', genre_str)
            log_debug('Container.Update URL {0}'.format(url))
            xbmc.executebuiltin('Container.Update({0})'.format(url))

        # --- Display machines by same Manufacturer ---
        elif action == ACTION_VIEW_SAME_MANUFACTURER:
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            manufacturer_str = machine['manufacturer']
            url = self._misc_url_2_arg('catalog', 'Manufacturer', 'category', manufacturer_str)
            log_debug('Container.Update URL {0}'.format(url))
            xbmc.executebuiltin('Container.Update({0})'.format(url))

        else:
            kodi_dialog_OK('Unknown action == {0}. '.format(action) +
                           'This is a bug, please report it.')

    # ---------------------------------------------------------------------------------------------
    # Information display
    # ---------------------------------------------------------------------------------------------
    def _command_context_view(self, machine_name, SL_name, SL_ROM, location):
        VIEW_SIMPLE       = 100
        VIEW_MAME_MACHINE = 200
        VIEW_SL_ROM       = 300

        ACTION_VIEW_MACHINE_DATA       = 100
        ACTION_VIEW_MACHINE_ROMS       = 200
        ACTION_VIEW_MACHINE_AUDIT_ROMS = 300
        ACTION_VIEW_SL_ROM_DATA        = 400
        ACTION_VIEW_SL_ROM_ROMS        = 500
        ACTION_VIEW_SL_ROM_AUDIT_ROMS  = 600
        ACTION_VIEW_DB_STATS           = 700
        ACTION_VIEW_EXEC_OUTPUT        = 800
        ACTION_VIEW_REPORT_SCANNER     = 900
        ACTION_VIEW_REPORT_AUDIT       = 1000
        ACTION_AUDIT_MAME_MACHINE      = 1100
        ACTION_AUDIT_SL_MACHINE        = 1200

        # --- Determine if we are in a category, launcher or ROM ---
        log_debug('_command_context_view() machine_name "{0}"'.format(machine_name))
        log_debug('_command_context_view() SL_name      "{0}"'.format(SL_name))
        log_debug('_command_context_view() SL_ROM       "{0}"'.format(SL_ROM))
        log_debug('_command_context_view() location     "{0}"'.format(location))
        if not machine_name and not SL_name:
            view_type = VIEW_SIMPLE
        elif machine_name:
            view_type = VIEW_MAME_MACHINE
        elif SL_name:
            view_type = VIEW_SL_ROM
        log_debug('_command_context_view() view_type = {0}'.format(view_type))

        # --- Build menu base on view_type ---
        if PATHS.MAME_OUTPUT_PATH.exists():
            filesize = PATHS.MAME_OUTPUT_PATH.fileSize()
            STD_status = '{0} bytes'.format(filesize)
        else:
            STD_status = 'not found'

        if view_type == VIEW_SIMPLE:
            d_list = [
              'View database statistics ...',
              'View scanner reports ...',
              'View audit reports ...',
              'View MAME last execution output ({0})'.format(STD_status),
            ]
        elif view_type == VIEW_MAME_MACHINE:
            d_list = [
              'View MAME machine data',
              'View MAME machine ROMs (ROMs DB)',
              'View MAME machine ROMs (Audit DB)',
              'Audit MAME machine ROMs',
              'View database statistics ...',
              'View asset/artwork reports ...',
              'View audit reports ...',
              'View MAME last execution output ({0})'.format(STD_status),
            ]
        elif view_type == VIEW_SL_ROM:
            d_list = [
              'View Software List item data',
              'View Software List ROMs (ROMs DB)',
              'View Software List ROMs (Audit DB)',
              'Audit Software List ROMs',
              'View database statistics ...',
              'View asset/artwork reports ...',
              'View audit reports ...',
              'View MAME last execution output ({0})'.format(STD_status),
            ]
        else:
            kodi_dialog_OK('Wrong view_type = {0}. This is a bug, please report it.'.format(view_type))
            return
        selected_value = xbmcgui.Dialog().select('View', d_list)
        if selected_value < 0: return

        # --- Polymorphic menu. Determine action to do. ---
        if view_type == VIEW_SIMPLE:
            if   selected_value == 0: action = ACTION_VIEW_DB_STATS
            elif selected_value == 1: action = ACTION_VIEW_REPORT_SCANNER
            elif selected_value == 2: action = ACTION_VIEW_REPORT_AUDIT
            elif selected_value == 3: action = ACTION_VIEW_EXEC_OUTPUT
            else:
                kodi_dialog_OK('view_type == VIEW_SIMPLE and selected_value = {0}. '.format(selected_value) +
                               'This is a bug, please report it.')
                return
        elif view_type == VIEW_MAME_MACHINE:
            if   selected_value == 0: action = ACTION_VIEW_MACHINE_DATA
            elif selected_value == 1: action = ACTION_VIEW_MACHINE_ROMS
            elif selected_value == 2: action = ACTION_VIEW_MACHINE_AUDIT_ROMS
            elif selected_value == 3: action = ACTION_AUDIT_MAME_MACHINE
            elif selected_value == 4: action = ACTION_VIEW_DB_STATS
            elif selected_value == 5: action = ACTION_VIEW_REPORT_SCANNER
            elif selected_value == 6: action = ACTION_VIEW_REPORT_AUDIT
            elif selected_value == 7: action = ACTION_VIEW_EXEC_OUTPUT
            else:
                kodi_dialog_OK('view_type == VIEW_MAME_MACHINE and selected_value = {0}. '.format(selected_value) +
                               'This is a bug, please report it.')
                return
        elif view_type == VIEW_SL_ROM:
            if   selected_value == 0: action = ACTION_VIEW_SL_ROM_DATA
            elif selected_value == 1: action = ACTION_VIEW_SL_ROM_ROMS
            elif selected_value == 2: action = ACTION_VIEW_SL_ROM_AUDIT_ROMS
            elif selected_value == 3: action = ACTION_AUDIT_SL_MACHINE
            elif selected_value == 4: action = ACTION_VIEW_DB_STATS
            elif selected_value == 5: action = ACTION_VIEW_REPORT_SCANNER
            elif selected_value == 6: action = ACTION_VIEW_REPORT_AUDIT
            elif selected_value == 7: action = ACTION_VIEW_EXEC_OUTPUT
            else:
                kodi_dialog_OK('view_type == VIEW_SL_ROM and selected_value = {0}. '.format(selected_value) +
                               'This is a bug, please report it.')
                return
        else:
            kodi_dialog_OK('Wrong view_type = {0}. '.format(view_type) +
                           'This is a bug, please report it.')
            return
        log_debug('_command_context_view() action = {0}'.format(action))

        # --- Execute action ---
        if action == ACTION_VIEW_MACHINE_DATA:
            pDialog = xbmcgui.DialogProgress()
            if location == LOCATION_STANDARD:
                pdialog_line1 = 'Loading databases ...'
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(0, pdialog_line1, 'ROM hashed database')
                machine = fs_get_machine_main_db_hash(PATHS, machine_name)
                pDialog.update(50, pdialog_line1, 'Assets database')
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(100, pdialog_line1)
                pDialog.close()
                assets  = assets_dic[machine_name]
                window_title = 'MAME Machine Information'
            elif location == LOCATION_MAME_FAVS:
                pdialog_line1 = 'Loading databases ...'
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(0, pdialog_line1, 'MAME Favourites database')
                machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
                pDialog.update(100, pdialog_line1)
                pDialog.close()
                machine = machines[machine_name]
                assets = machine['assets']
                window_title = 'Favourite MAME Machine Information'

            # --- Make information string ---
            info_text  = '[COLOR orange]Machine {0} / Render data[/COLOR]\n'.format(machine_name)
            # >> Print MAME Favourites special fields
            if location == LOCATION_MAME_FAVS:
                if 'ver_mame' in machine:
                    info_text += "[COLOR slateblue]ver_mame[/COLOR]: {0}\n".format(machine['ver_mame'])
                else:
                    info_text += "[COLOR slateblue]ver_mame[/COLOR]: not available\n"
                if 'ver_mame_str' in machine:
                    info_text += "[COLOR slateblue]ver_mame_str[/COLOR]: {0}\n".format(machine['ver_mame_str'])
                else:
                    info_text += "[COLOR slateblue]ver_mame_str[/COLOR]: not available\n"
            info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(machine['cloneof'])
            info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(machine['description'])
            info_text += "[COLOR violet]driver_status[/COLOR]: '{0}'\n".format(machine['driver_status'])
            info_text += "[COLOR violet]genre[/COLOR]: '{0}'\n".format(machine['genre'])
            info_text += "[COLOR skyblue]isBIOS[/COLOR]: {0}\n".format(machine['isBIOS'])
            info_text += "[COLOR skyblue]isDevice[/COLOR]: {0}\n".format(machine['isDevice'])
            info_text += "[COLOR violet]manufacturer[/COLOR]: '{0}'\n".format(machine['manufacturer'])
            info_text += "[COLOR violet]nplayers[/COLOR]: '{0}'\n".format(machine['nplayers'])
            info_text += "[COLOR violet]year[/COLOR]: '{0}'\n".format(machine['year'])

            info_text += '\n[COLOR orange]Machine data[/COLOR]\n'.format(machine_name)
            info_text += "[COLOR violet]bestgames[/COLOR]: '{0}'\n".format(machine['bestgames'])
            info_text += "[COLOR violet]catlist[/COLOR]: '{0}'\n".format(machine['catlist'])
            info_text += "[COLOR violet]catver[/COLOR]: '{0}'\n".format(machine['catver'])
            info_text += "[COLOR skyblue]coins[/COLOR]: {0}\n".format(machine['coins'])
            info_text += "[COLOR skyblue]control_type[/COLOR]: {0}\n".format(unicode(machine['control_type']))
            # Devices list is a special case.
            if machine['devices']:
                for i, device in enumerate(machine['devices']):
                    info_text += "[COLOR lime]devices[/COLOR][{0}]:\n".format(i)
                    info_text += "  [COLOR violet]att_type[/COLOR]: {0}\n".format(device['att_type'])
                    info_text += "  [COLOR violet]att_tag[/COLOR]: {0}\n".format(device['att_tag'])
                    info_text += "  [COLOR skyblue]att_mandatory[/COLOR]: {0}\n".format(unicode(device['att_mandatory']))
                    info_text += "  [COLOR violet]att_interface[/COLOR]: {0}\n".format(device['att_interface'])
                    info_text += "  [COLOR skyblue]instance[/COLOR]: {0}\n".format(unicode(device['instance']))
                    info_text += "  [COLOR skyblue]ext_names[/COLOR]: {0}\n".format(unicode(device['ext_names']))
            else:
                info_text += "[COLOR lime]devices[/COLOR]: []\n"
            info_text += "[COLOR skyblue]display_rotate[/COLOR]: {0}\n".format(unicode(machine['display_rotate']))
            info_text += "[COLOR skyblue]display_type[/COLOR]: {0}\n".format(unicode(machine['display_type']))
            info_text += "[COLOR violet]genre[/COLOR]: '{0}'\n".format(machine['genre'])
            info_text += "[COLOR skyblue]isDead[/COLOR]: {0}\n".format(unicode(machine['isDead']))
            info_text += "[COLOR skyblue]isMechanical[/COLOR]: {0}\n".format(unicode(machine['isMechanical']))
            info_text += "[COLOR violet]romof[/COLOR]: '{0}'\n".format(machine['romof'])
            info_text += "[COLOR violet]sampleof[/COLOR]: '{0}'\n".format(machine['sampleof'])
            info_text += "[COLOR violet]series[/COLOR]: '{0}'\n".format(machine['series'])
            info_text += "[COLOR skyblue]softwarelists[/COLOR]: {0}\n".format(unicode(machine['softwarelists']))
            info_text += "[COLOR violet]sourcefile[/COLOR]: '{0}'\n".format(machine['sourcefile'])

            info_text += '\n[COLOR orange]Asset/artwork data[/COLOR]\n'
            info_text += "[COLOR violet]PCB[/COLOR]: '{0}'\n".format(assets['PCB'])
            info_text += "[COLOR violet]artpreview[/COLOR]: '{0}'\n".format(assets['artpreview'])
            info_text += "[COLOR violet]artwork[/COLOR]: '{0}'\n".format(assets['artwork'])
            info_text += "[COLOR violet]cabinet[/COLOR]: '{0}'\n".format(assets['cabinet'])
            info_text += "[COLOR violet]clearlogo[/COLOR]: '{0}'\n".format(assets['clearlogo'])
            info_text += "[COLOR violet]cpanel[/COLOR]: '{0}'\n".format(assets['cpanel'])
            info_text += "[COLOR violet]fanart[/COLOR]: '{0}'\n".format(assets['fanart'])
            info_text += "[COLOR violet]flags[/COLOR]: '{0}'\n".format(assets['flags'])
            info_text += "[COLOR violet]flyer[/COLOR]: '{0}'\n".format(assets['flyer'])
            info_text += "[COLOR violet]manual[/COLOR]: '{0}'\n".format(assets['manual'])
            info_text += "[COLOR violet]marquee[/COLOR]: '{0}'\n".format(assets['marquee'])
            info_text += "[COLOR violet]plot[/COLOR]: '{0}'\n".format(assets['plot'])
            info_text += "[COLOR violet]snap[/COLOR]: '{0}'\n".format(assets['snap'])
            info_text += "[COLOR violet]title[/COLOR]: '{0}'\n".format(assets['title'])
            info_text += "[COLOR violet]trailer[/COLOR]: '{0}'\n".format(assets['trailer'])

            # --- Show information window ---
            self._display_text_window(window_title, info_text)

        # --- View Software List ROM Machine data ---
        elif action == ACTION_VIEW_SL_ROM_DATA:
            if location == LOCATION_STANDARD:
                kodi_busydialog_ON()
                SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
                SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                assets_file_name = SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
                SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
                SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())
                SL_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '.json')
                roms = fs_load_JSON_file(SL_DB_FN.getPath())
                kodi_busydialog_OFF()
                SL_machine_list = SL_machines_dic[SL_name]
                SL_dic = SL_catalog_dic[SL_name]
                rom = roms[SL_ROM]
                assets = SL_asset_dic[SL_ROM]
                window_title = 'Software List ROM Information'

                # >> Build information string
                info_text  = '[COLOR orange]ROM {0}[/COLOR]\n'.format(SL_ROM)
                info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(rom['cloneof'])
                info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(rom['description'])
                info_text += "[COLOR skyblue]hasCHDs[/COLOR]: {0}\n".format(unicode(rom['hasCHDs']))
                info_text += "[COLOR skyblue]hasROMs[/COLOR]: {0}\n".format(unicode(rom['hasROMs']))
                if rom['parts']:
                    for i, part in enumerate(rom['parts']):
                        info_text += "[COLOR lime]parts[/COLOR][{0}]:\n".format(i)
                        info_text += "  [COLOR violet]interface[/COLOR]: '{0}'\n".format(part['interface'])
                        info_text += "  [COLOR violet]name[/COLOR]: '{0}'\n".format(part['name'])
                else:
                    info_text += '[COLOR lime]parts[/COLOR]: []\n'
                info_text += "[COLOR violet]plot[/COLOR]: '{0}'\n".format(rom['plot'])
                info_text += "[COLOR violet]publisher[/COLOR]: '{0}'\n".format(rom['publisher'])
                info_text += "[COLOR violet]status_CHD[/COLOR]: '{0}'\n".format(rom['status_CHD'])
                info_text += "[COLOR violet]status_ROM[/COLOR]: '{0}'\n".format(rom['status_ROM'])
                info_text += "[COLOR violet]year[/COLOR]: '{0}'\n".format(rom['year'])

                info_text += '\n[COLOR orange]Software List assets[/COLOR]\n'
                info_text += "[COLOR violet]title[/COLOR]: '{0}'\n".format(assets['title'])
                info_text += "[COLOR violet]snap[/COLOR]: '{0}'\n".format(assets['snap'])
                info_text += "[COLOR violet]boxfront[/COLOR]: '{0}'\n".format(assets['boxfront'])
                info_text += "[COLOR violet]fanart[/COLOR]: '{0}'\n".format(assets['fanart'])
                info_text += "[COLOR violet]trailer[/COLOR]: '{0}'\n".format(assets['trailer'])
                info_text += "[COLOR violet]manual[/COLOR]: '{0}'\n".format(assets['manual'])

                info_text += '\n[COLOR orange]Software List {0}[/COLOR]\n'.format(SL_name)
                info_text += "[COLOR violet]display_name[/COLOR]: '{0}'\n".format(SL_dic['display_name'])
                info_text += "[COLOR skyblue]num_with_CHDs[/COLOR]: {0}\n".format(unicode(SL_dic['num_with_CHDs']))
                info_text += "[COLOR skyblue]num_with_ROMs[/COLOR]: {0}\n".format(unicode(SL_dic['num_with_ROMs']))
                info_text += "[COLOR violet]rom_DB_noext[/COLOR]: '{0}'\n".format(SL_dic['rom_DB_noext'])

                info_text += '\n[COLOR orange]Runnable by[/COLOR]\n'
                for machine_dic in sorted(SL_machine_list):
                    t = "[COLOR violet]machine[/COLOR]: '{0}' [COLOR slateblue]({1})[/COLOR]\n"
                    info_text += t.format(machine_dic['description'], machine_dic['machine'])

            elif location == LOCATION_SL_FAVS:
                fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
                fav_key = SL_name + '-' + SL_ROM
                rom = fav_SL_roms[fav_key]
                window_title = 'Favourite Software List ROM Information'

                # >> Build information string
                info_text = '[COLOR orange]ROM {0}[/COLOR]\n'.format(fav_key)
                if 'ver_mame' in rom:
                    info_text += "[COLOR slateblue]ver_mame[/COLOR]: {0}\n".format(rom['ver_mame'])
                else:
                    info_text += "[COLOR slateblue]ver_mame[/COLOR]: not available\n"
                if 'ver_mame_str' in rom:
                    info_text += "[COLOR slateblue]ver_mame_str[/COLOR]: {0}\n".format(rom['ver_mame_str'])
                else:
                    info_text += "[COLOR slateblue]ver_mame_str[/COLOR]: not available\n"
                info_text += "[COLOR violet]ROM_name[/COLOR]: '{0}'\n".format(rom['ROM_name'])
                info_text += "[COLOR violet]SL_name[/COLOR]: '{0}'\n".format(rom['SL_name'])
                info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(rom['cloneof'])
                info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(rom['description'])
                info_text += "[COLOR skyblue]hasCHDs[/COLOR]: {0}\n".format(unicode(rom['hasCHDs']))
                info_text += "[COLOR skyblue]hasROMs[/COLOR]: {0}\n".format(unicode(rom['hasROMs']))
                info_text += "[COLOR violet]launch_machine[/COLOR]: '{0}'\n".format(rom['launch_machine'])
                if rom['parts']:
                    for i, part in enumerate(rom['parts']):
                        info_text += "[COLOR lime]parts[/COLOR][{0}]:\n".format(i)
                        info_text += "  [COLOR violet]interface[/COLOR]: '{0}'\n".format(part['interface'])
                        info_text += "  [COLOR violet]name[/COLOR]: '{0}'\n".format(part['name'])
                else:
                    info_text += '[COLOR lime]parts[/COLOR]: []\n'
                info_text += "[COLOR violet]plot[/COLOR]: '{0}'\n".format(rom['plot'])
                info_text += "[COLOR violet]publisher[/COLOR]: '{0}'\n".format(rom['publisher'])
                info_text += "[COLOR violet]status_CHD[/COLOR]: '{0}'\n".format(rom['status_CHD'])
                info_text += "[COLOR violet]status_ROM[/COLOR]: '{0}'\n".format(rom['status_ROM'])
                info_text += "[COLOR violet]year[/COLOR]: '{0}'\n".format(rom['year'])

                info_text += '\n[COLOR orange]Software List assets[/COLOR]\n'
                info_text += "[COLOR violet]title[/COLOR]: '{0}'\n".format(rom['assets']['title'])
                info_text += "[COLOR violet]snap[/COLOR]: '{0}'\n".format(rom['assets']['snap'])
                info_text += "[COLOR violet]boxfront[/COLOR]: '{0}'\n".format(rom['assets']['boxfront'])
                info_text += "[COLOR violet]fanart[/COLOR]: '{0}'\n".format(rom['assets']['fanart'])
                info_text += "[COLOR violet]trailer[/COLOR]: '{0}'\n".format(rom['assets']['trailer'])
                info_text += "[COLOR violet]manual[/COLOR]: '{0}'\n".format(rom['assets']['manual'])
            self._display_text_window(window_title, info_text)

        # --- View database information and statistics stored in control dictionary ---
        elif action == ACTION_VIEW_DB_STATS:
            d = xbmcgui.Dialog()
            type_sub = d.select('View scanner reports',
                                ['View main statistics',
                                 'View scanner statistics'])
            if type_sub < 0: return

            # --- Main stats ---
            if type_sub == 0:
                # --- Warn user if error ---
                if not PATHS.MAIN_CONTROL_PATH.exists():
                    kodi_dialog_OK('MAME database not found. Please setup the addon first.')
                    return
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                window_title = 'Database information and statistics'

                # --- Main stuff ---
                info_text  = '[COLOR orange]Main information[/COLOR]\n'
                info_text += "AML version            {0}\n".format(__addon_version__)
                info_text += "MAME version string    {0}\n".format(control_dic['ver_mame_str'])
                info_text += "MAME version numerical {0}\n".format(control_dic['ver_mame'])
                info_text += "catver.ini version     {0}\n".format(control_dic['ver_catver'])
                info_text += "catlist.ini version    {0}\n".format(control_dic['ver_catlist'])
                info_text += "genre.ini version      {0}\n".format(control_dic['ver_genre'])
                info_text += "nplayers.ini version   {0}\n".format(control_dic['ver_nplayers'])
                info_text += "bestgames.ini version  {0}\n".format(control_dic['ver_bestgames'])
                info_text += "series.ini version     {0}\n".format(control_dic['ver_series'])
                info_text += "History.dat version    {0}\n".format(control_dic['ver_history'])
                info_text += "MAMEinfo.dat version   {0}\n".format(control_dic['ver_mameinfo'])
                info_text += "Gameinit.dat version   {0}\n".format(control_dic['ver_gameinit'])
                info_text += "Command.dat version    {0}\n".format(control_dic['ver_command'])

                info_text += '\n[COLOR orange]Timestamps[/COLOR]\n'
                if control_dic['t_XML_extraction']:
                    info_text += "MAME XML extracted on   {0}\n".format(time.ctime(control_dic['t_XML_extraction']))
                else:
                    info_text += "MAME XML never extracted\n"
                if control_dic['t_MAME_DB_build']:
                    info_text += "MAME DB built on        {0}\n".format(time.ctime(control_dic['t_MAME_DB_build']))
                else:
                    info_text += "MAME DB never built\n"
                if control_dic['t_MAME_Audit_DB_build']:
                    info_text += "MAME Audit DB built on  {0}\n".format(time.ctime(control_dic['t_MAME_Audit_DB_build']))
                else:
                    info_text += "MAME Audit DB never built\n"
                if control_dic['t_MAME_Catalog_build']:
                    info_text += "MAME Catalog built on   {0}\n".format(time.ctime(control_dic['t_MAME_Catalog_build']))
                else:
                    info_text += "MAME Catalog never built\n"
                if control_dic['t_SL_DB_build']:
                    info_text += "SL DB built on          {0}\n".format(time.ctime(control_dic['t_SL_DB_build']))
                else:
                    info_text += "SL DB never built\n"
                if control_dic['t_MAME_ROMs_scan']:
                    info_text += "MAME ROMs scaned on     {0}\n".format(time.ctime(control_dic['t_MAME_ROMs_scan']))
                else:
                    info_text += "MAME ROMs never scaned\n"
                if control_dic['t_MAME_assets_scan']:
                    info_text += "MAME assets scaned on   {0}\n".format(time.ctime(control_dic['t_MAME_assets_scan']))
                else:
                    info_text += "MAME assets never scaned\n"
                if control_dic['t_SL_ROMs_scan']:
                    info_text += "SL ROMs scaned on       {0}\n".format(time.ctime(control_dic['t_SL_ROMs_scan']))
                else:
                    info_text += "SL ROMs never scaned\n"
                if control_dic['t_SL_assets_scan']:
                    info_text += "SL assets scaned on     {0}\n".format(time.ctime(control_dic['t_SL_assets_scan']))
                else:
                    info_text += "SL assets never scaned\n"
                if control_dic['t_Custom_Filter_build']:
                    info_text += "Custom filters built on {0}\n".format(time.ctime(control_dic['t_Custom_Filter_build']))
                else:
                    info_text += "Custom filters never built\n"

                info_text += '\n[COLOR orange]MAME machine count[/COLOR]\n'
                t = "Machines   {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_processed_machines'],
                                      control_dic['stats_parents'], 
                                      control_dic['stats_clones'])
                t = "Runnable   {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_runnable'],
                                      control_dic['stats_runnable_parents'], 
                                      control_dic['stats_runnable_clones'])
                t = "Coin       {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_coin'],
                                      control_dic['stats_coin_parents'], 
                                      control_dic['stats_coin_clones'])
                t = "Nocoin     {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_nocoin'],
                                      control_dic['stats_nocoin_parents'],
                                      control_dic['stats_nocoin_clones'])
                t = "Mechanical {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_mechanical'],
                                      control_dic['stats_mechanical_parents'],
                                      control_dic['stats_mechanical_clones'])
                t = "Dead       {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_dead'],
                                      control_dic['stats_dead_parents'], 
                                      control_dic['stats_dead_clones'])
                t = "Devices    {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_devices'],
                                      control_dic['stats_devices_parents'], 
                                      control_dic['stats_devices_clones'])
                # >> Binary filters
                t = "BIOS       {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_BIOS'],
                                      control_dic['stats_BIOS_parents'], 
                                      control_dic['stats_BIOS_clones'])
                t = "Samples    {0:5d}  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['stats_samples'],
                                      control_dic['stats_samples_parents'], 
                                      control_dic['stats_samples_clones'])

                info_text += '\n[COLOR orange]Software Lists item count[/COLOR]\n'
                info_text += "SL files           {0:5d}\n".format(control_dic['stats_SL_XML_files'])
                info_text += "SL software items  {0:5d}\n".format(control_dic['stats_SL_software_items'])
                info_text += "SL items with ROMs {0:5d}\n".format(control_dic['stats_SL_machine_archives_ROM'])
                info_text += "SL items with CHDs {0:5d}\n".format(control_dic['stats_SL_machine_archives_CHD'])

                info_text += '\n[COLOR orange]ROM audit statistics[/COLOR]\n'
                rom_set = ['Merged', 'Split', 'Non-merged'][self.settings['mame_rom_set']]
                chd_set = ['Merged', 'Split', 'Non-merged'][self.settings['mame_chd_set']]
                info_text += "There are {0:5d} ROM ZIP archives in the {1} set\n".format(control_dic['audit_MAME_ZIP_files'], rom_set)
                info_text += "There are {0:5d}     CHD archives in the {1} set\n".format(control_dic['audit_MAME_CHD_files'], chd_set)
                t = "{0:5d} machines require ROM ZIPs ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['audit_machine_archives_ROM'],
                                      control_dic['audit_machine_archives_ROM_parents'],
                                      control_dic['audit_machine_archives_ROM_clones'])
                t = "{0:5d} machines require CHDs     ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['audit_machine_archives_CHD'],
                                      control_dic['audit_machine_archives_CHD_parents'],
                                      control_dic['audit_machine_archives_CHD_clones'])
                t = "{0:5d} machines require nothing  ({1:5d} Parents / {2:5d} Clones)\n"
                info_text += t.format(control_dic['audit_archive_less'],
                                      control_dic['audit_archive_less_parents'],
                                      control_dic['audit_archive_less_clones'])

                # >> Not coded yet.
                # info_text += '\n[COLOR orange]ROM audit information[/COLOR]\n'

                self._display_text_window(window_title, info_text)

            # --- Main stats ---
            elif type_sub == 1:
                # --- Warn user if error ---
                if not PATHS.MAIN_CONTROL_PATH.exists():
                    kodi_dialog_OK('MAME database not found. Please setup the addon first.')
                    return
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                window_title = 'Scanner statistics'

                info_text = '[COLOR orange]ROM scanner information[/COLOR]\n'
                t = "You have {0:5d} ROM ZIP files out of {1:5d} ({2:5d} missing)\n"
                info_text += t.format(control_dic['scan_ROM_ZIP_files_have'],
                                      control_dic['scan_ROM_ZIP_files_total'],
                                      control_dic['scan_ROM_ZIP_files_missing'])
                t = "You have {0:5d} CHDs out of          {1:5d} ({2:5d} missing)\n"
                info_text += t.format(control_dic['scan_CHD_files_have'],
                                      control_dic['scan_CHD_files_total'],
                                      control_dic['scan_CHD_files_missing'])
                t = "Can run  {0:5d} ROM machines out of  {1:5d} ({2:5d} unrunnable machines)\n"
                info_text += t.format(control_dic['scan_machine_archives_ROM_have'],
                                      control_dic['scan_machine_archives_ROM_total'],
                                      control_dic['scan_machine_archives_ROM_missing'])
                t = "Can run  {0:5d} CHD machines out of  {1:5d} ({2:5d} unrunnable machines)\n"
                info_text += t.format(control_dic['scan_machine_archives_CHD_have'],
                                      control_dic['scan_machine_archives_CHD_total'],
                                      control_dic['scan_machine_archives_CHD_missing'])
                # >> Samples
                t = "You have {0:5d} Samples out of       {1:5d} ({2:5d} missing)\n"
                info_text += t.format(control_dic['scan_Samples_have'],
                                      control_dic['scan_Samples_total'],
                                      control_dic['scan_Samples_missing'])
                # >> SL scanner
                t = "You have {0:5d} SL ROMs out of       {1:5d} ({2:5d} missing)\n"
                info_text += t.format(control_dic['scan_software_archives_ROM_have'],
                                      control_dic['scan_software_archives_ROM_total'],
                                      control_dic['scan_software_archives_ROM_missing'])
                t = "You have {0:5d} SL CHDs out of       {1:5d} ({2:5d} missing)\n"
                info_text += t.format(control_dic['scan_software_archives_CHD_have'],
                                      control_dic['scan_software_archives_CHD_total'],
                                      control_dic['scan_software_archives_CHD_missing'])

                # >> MAME assets.
                info_text += '\n[COLOR orange]Asset scanner information[/COLOR]\n'
                t = "You have {0:6d} MAME PCBs        out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_PCBs_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_PCBs_missing'],
                                      control_dic['assets_PCBs_alternate'])
                t = "You have {0:6d} MAME Artpreviews out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_artpreview_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_artpreview_missing'],
                                      control_dic['assets_artpreview_alternate'])
                t = "You have {0:6d} MAME Artwork     out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_artwork_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_artwork_missing'],
                                      control_dic['assets_artwork_alternate'])
                t = "You have {0:6d} MAME Cabinets    out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_cabinets_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_cabinets_missing'],
                                      control_dic['assets_cabinets_alternate'])
                t = "You have {0:6d} MAME Clearlogos  out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_clearlogos_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_clearlogos_missing'],
                                      control_dic['assets_clearlogos_alternate'])
                t = "You have {0:6d} MAME CPanels     out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_cpanels_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_cpanels_missing'],
                                      control_dic['assets_cpanels_alternate'])
                t = "You have {0:6d} MAME Fanart      out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_fanarts_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_fanarts_missing'],
                                      control_dic['assets_fanarts_alternate'])
                t = "You have {0:6d} MAME Flyers      out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_flyers_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_flyers_missing'],
                                      control_dic['assets_flyers_alternate'])
                t = "You have {0:6d} MAME Manuals     out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_manuals_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_manuals_missing'],
                                      control_dic['assets_manuals_alternate'])
                t = "You have {0:6d} MAME Marquees    out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_marquees_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_marquees_missing'],
                                      control_dic['assets_marquees_alternate'])
                t = "You have {0:6d} MAME Snaps       out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_snaps_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_snaps_missing'],
                                      control_dic['assets_snaps_alternate'])
                t = "You have {0:6d} MAME Titles      out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_titles_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_titles_missing'],
                                      control_dic['assets_titles_alternate'])
                t = "You have {0:6d} MAME Trailers    out of {1:6d} ({2:6d} missing, {3:6d} alternate)\n"
                info_text += t.format(control_dic['assets_trailers_have'],
                                      control_dic['assets_num_MAME_machines'],
                                      control_dic['assets_trailers_missing'],
                                      control_dic['assets_trailers_alternate'])

                # >> Software Lists
                t = "You have {0:6d} SL Titles        out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_titles_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_titles_missing'])
                t = "You have {0:6d} SL Snaps         out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_snaps_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_snaps_missing'])
                t = "You have {0:6d} SL Boxfronts     out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_boxfronts_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_boxfronts_missing'])
                t = "You have {0:6d} SL Fanarts       out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_fanarts_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_fanarts_missing'])
                t = "You have {0:6d} SL Trailers      out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_trailers_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_trailers_missing'])
                t = "You have {0:6d} SL Manuals       out of {1:6d} ({2:6d} missing)\n"
                info_text += t.format(control_dic['assets_SL_manuals_have'],
                                      control_dic['assets_SL_num_items'],
                                      control_dic['assets_SL_manuals_missing'])

                self._display_text_window(window_title, info_text)

        # --- View MAME machine ROMs (ROMs database) ---
        elif action == ACTION_VIEW_MACHINE_ROMS:
            # >> Load machine dictionary, ROM database and Devices database.
            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 3
            pDialog.create('Advanced MAME Launcher', pdialog_line1)
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'MAME machines Main')
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machine ROMs')
            roms_db_dic = fs_load_JSON_file(PATHS.ROMS_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), pdialog_line1, 'MAME machine Devices')
            devices_db_dic = fs_load_JSON_file(PATHS.DEVICES_DB_PATH.getPath())
            pDialog.update(int((3*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Make a dictionary with device ROMs ---
            device_roms_list = []
            for device in devices_db_dic[machine_name]:
                device_roms_dic = roms_db_dic[device]
                for rom in device_roms_dic['roms']:
                    rom['device_name'] = device
                    device_roms_list.append(copy.deepcopy(rom))

            # --- ROM info ---
            info_text = []
            if machine['cloneof'] and machine['romof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0} / '.format(machine['cloneof']) +
                                 '[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            elif machine['cloneof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0}'.format(machine['cloneof']))
            elif machine['romof']:
                info_text.append('[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            info_text.append('[COLOR skyblue]isBIOS[/COLOR] {0} / '.format(unicode(machine['isBIOS'])) +
                             '[COLOR skyblue]isDevice[/COLOR] {0}'.format(unicode(machine['isDevice'])))
            info_text.append('')

            # --- Table header ---
            # Table cell padding: left, right
            # Table columns: Type - ROM name - Size - CRC/SHA1 - Merge - BIOS - Location
            table_str = []
            table_str.append(['right', 'left',     'right', 'left',     'left',  'left'])
            table_str.append(['Type',  'ROM name', 'Size',  'CRC/SHA1', 'Merge', 'BIOS/Device'])

            # --- Table: Machine ROMs ---
            roms_dic = roms_db_dic[machine_name]
            if roms_dic['roms']:
                for rom in roms_dic['roms']:
                    if       rom['bios'] and     rom['merge']: r_type = 'BROM'
                    elif     rom['bios'] and not rom['merge']: r_type = 'XROM'
                    elif not rom['bios'] and     rom['merge']: r_type = 'MROM'
                    elif not rom['bios'] and not rom['merge']: r_type = 'ROM'
                    else:                                      r_type = 'ERROR'
                    table_row = [r_type, str(rom['name']), str(rom['size']),
                                 str(rom['crc']), str(rom['merge']), str(rom['bios'])]
                    table_str.append(table_row)

            # --- Table: device ROMs ---
            if device_roms_list:
                for rom in device_roms_list:
                    table_row = ['DROM', str(rom['name']), str(rom['size']),
                                 str(rom['crc']), str(rom['merge']), str(rom['device_name'])]
                    table_str.append(table_row)

            # --- Table: machine CHDs ---
            if roms_dic['disks']:
                for disk in roms_dic['disks']:
                    table_row = ['DISK', str(disk['name']), '',
                                 str(disk['sha1'])[0:8], str(disk['merge']), '']
                    table_str.append(table_row)

            # --- Table: BIOSes ---
            if roms_dic['bios']:
                bios_table_str = []
                bios_table_str.append(['right',     'left'])
                bios_table_str.append(['BIOS name', 'Description'])
                for bios in roms_dic['bios']:
                    table_row = [str(bios['name']), str(bios['description'])]
                    bios_table_str.append(table_row)

            # --- Render text information window ---
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            if roms_dic['bios']:
                bios_table_str_list = text_render_table_str(bios_table_str)
                info_text.append('')
                info_text.extend(bios_table_str_list)
            window_title = 'Machine {0} ROMs'.format(machine_name)
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- View MAME machine ROMs (Audit ROM database) ---
        elif action == ACTION_VIEW_MACHINE_AUDIT_ROMS:
            # --- Load machine dictionary and ROM database ---
            rom_set = ['MERGED', 'SPLIT', 'NONMERGED'][self.settings['mame_rom_set']]
            log_debug('_command_context_view() View Machine ROMs (Audit database)\n')
            log_debug('_command_context_view() rom_set {0}\n'.format(rom_set))

            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 2
            pDialog.create('Advanced MAME Launcher', pdialog_line1)
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'MAME machine hash')
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME ROM Audit')
            audit_roms_dic = fs_load_JSON_file(PATHS.ROM_AUDIT_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Grab data and settings ---
            rom_list = audit_roms_dic[machine_name]
            cloneof = machine['cloneof']
            romof = machine['romof']
            log_debug('_command_context_view() machine {0}\n'.format(machine_name))
            log_debug('_command_context_view() cloneof {0}\n'.format(cloneof))
            log_debug('_command_context_view() romof   {0}\n'.format(romof))

            # --- Generate report ---
            info_text = []
            if machine['cloneof'] and machine['romof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0} / '.format(machine['cloneof']) +
                                 '[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            elif machine['cloneof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0}'.format(machine['cloneof']))
            elif machine['romof']:
                info_text.append('[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            info_text.append('[COLOR skyblue]isBIOS[/COLOR] {0} / '.format(unicode(machine['isBIOS'])) +
                             '[COLOR skyblue]isDevice[/COLOR] {0}'.format(unicode(machine['isDevice'])))
            info_text.append('')

            # --- Table header ---
            # Table cell padding: left, right
            # Table columns: Type - ROM name - Size - CRC/SHA1 - Merge - BIOS - Location
            table_str = []
            table_str.append(['right', 'left',     'right', 'left',     'left'])
            table_str.append(['Type',  'ROM name', 'Size',  'CRC/SHA1', 'Location'])

            # --- Table rows ---
            for m_rom in rom_list:
                if m_rom['type'] == 'DISK':
                    sha1_str = str(m_rom['sha1'])[0:8]
                    table_row = [str(m_rom['type']), str(m_rom['name']), '',
                                 sha1_str, m_rom['location']]
                else:
                    table_row = [str(m_rom['type']), str(m_rom['name']), str(m_rom['size']),
                                 str(m_rom['crc']), str(m_rom['location'])]
                table_str.append(table_row)
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            window_title = 'Machine {0} ROM audit'.format(machine_name)
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- View SL ROMs ---
        elif action == ACTION_VIEW_SL_ROM_ROMS:
            SL_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '.json')
            SL_ROMS_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '_ROMs.json')
            # kodi_busydialog_ON()
            # SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
            # SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
            # assets_file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
            # SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
            # SL_asset_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())
            # kodi_busydialog_OFF()
            # SL_dic = SL_catalog_dic[SL_name]
            # SL_machine_list = SL_machines_dic[SL_name]
            # assets = SL_asset_dic[SL_ROM] if SL_ROM in SL_asset_dic else fs_new_SL_asset()
            roms = fs_load_JSON_file(SL_DB_FN.getPath())
            roms_db = fs_load_JSON_file(SL_ROMS_DB_FN.getPath())
            rom = roms[SL_ROM]
            rom_db_list = roms_db[SL_ROM]

            info_text = []
            info_text.append('[COLOR violet]SL_name[/COLOR] {0}'.format(SL_name))
            info_text.append('[COLOR violet]SL_ROM[/COLOR] {0}'.format(SL_ROM))
            info_text.append('[COLOR violet]description[/COLOR] {0}'.format(rom['description']))
            if rom['cloneof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0}'.format(rom['cloneof']))
            info_text.append('')

            table_str = []
            table_str.append(['left',      'left',       'left',      'left',      'left', 'left', 'left'])
            table_str.append(['Part name', 'Part iface', 'Area type', 'A name', 'ROM/CHD name', 'Size', 'CRC/SHA1'])
            # >> Iterate Parts
            for part_dic in rom_db_list:
                part_name = part_dic['part_name']
                part_interface = part_dic['part_interface']
                if 'dataarea' in part_dic:
                    # >> Iterate Dataareas
                    for dataarea_dic in part_dic['dataarea']:
                        dataarea_name = dataarea_dic['name']
                        # >> Interate ROMs in dataarea
                        for rom_dic in dataarea_dic['roms']:
                            table_row = [part_name, part_interface,
                                         'dataarea', dataarea_name,
                                         rom_dic['name'], rom_dic['size'], rom_dic['crc']]
                            table_str.append(table_row)
                if 'diskarea' in part_dic:
                    # >> Iterate Diskareas
                    for diskarea_dic in part_dic['diskarea']:
                        diskarea_name = diskarea_dic['name']
                        # >> Iterate DISKs in diskarea
                        for rom_dic in diskarea_dic['disks']:
                            table_row = [part_name, part_interface,
                                         'diskarea', diskarea_name,
                                         rom_dic['name'], '', rom_dic['sha1'][0:8]]
                            table_str.append(table_row)
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            window_title = 'Software List ROM List (ROMs DB)'
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- View SL ROM Audit ROMs ---
        elif action == ACTION_VIEW_SL_ROM_AUDIT_ROMS:
            SL_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '.json')
            # SL_ROMs_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '_roms.json')
            SL_ROM_Audit_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '_ROM_audit.json')

            roms = fs_load_JSON_file(SL_DB_FN.getPath())
            rom_audit_db = fs_load_JSON_file(SL_ROM_Audit_DB_FN.getPath())
            rom = roms[SL_ROM]
            rom_db_list = rom_audit_db[SL_ROM]

            info_text = []
            info_text.append('[COLOR violet]SL_name[/COLOR] {0}'.format(SL_name))
            info_text.append('[COLOR violet]SL_ROM[/COLOR] {0}'.format(SL_ROM))
            info_text.append('[COLOR violet]description[/COLOR] {0}'.format(rom['description']))
            if rom['cloneof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0}'.format(rom['cloneof']))
            info_text.append('')

            # table_str = [    ['left', 'left',         'left', 'left',     'left'] ]
            # table_str.append(['Type', 'ROM/CHD name', 'Size', 'CRC/SHA1', 'Location'])
            table_str = [    ['left', 'left', 'left',     'left'] ]
            table_str.append(['Type', 'Size', 'CRC/SHA1', 'Location'])
            for rom_dic in rom_db_list:
                if rom_dic['type'] == ROM_TYPE_DISK:
                    table_row = [rom_dic['type'], # rom_dic['name'],
                                 '', rom_dic['sha1'][0:8], rom_dic['location']]
                    table_str.append(table_row)
                else:
                    table_row = [rom_dic['type'], # rom_dic['name'],
                                 rom_dic['size'], rom_dic['crc'], rom_dic['location']]
                    table_str.append(table_row)
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            window_title = 'Software List ROM List (Audit DB)'
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- View MAME stdout/stderr ---
        elif action == ACTION_VIEW_EXEC_OUTPUT:
            if not PATHS.MAME_OUTPUT_PATH.exists():
                kodi_dialog_OK('MAME output file not found. Execute MAME and try again.')
                return

            # --- Read stdout and put into a string ---
            window_title = 'MAME last execution output'
            info_text = ''
            with open(PATHS.MAME_OUTPUT_PATH.getPath(), 'r') as myfile:
                info_text = myfile.read()
            self._display_text_window(window_title, info_text)

        # --- Audit ROMs of a single machine ---
        elif action == ACTION_AUDIT_MAME_MACHINE:
            # --- Load machine dictionary and ROM database ---
            rom_set = ['MERGED', 'SPLIT', 'NONMERGED'][self.settings['mame_rom_set']]
            log_debug('_command_context_view() Auditing Machine ROMs\n')
            log_debug('_command_context_view() rom_set {0}\n'.format(rom_set))

            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 2
            pDialog.create('Advanced MAME Launcher', pdialog_line1)
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'MAME machine hash')
            machine = fs_get_machine_main_db_hash(PATHS, machine_name)
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME ROM Audit')
            audit_roms_dic = fs_load_JSON_file(PATHS.ROM_AUDIT_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Grab data and settings ---
            rom_list = audit_roms_dic[machine_name]
            cloneof = machine['cloneof']
            romof = machine['romof']
            log_debug('_command_context_view() machine {0}\n'.format(machine_name))
            log_debug('_command_context_view() cloneof {0}\n'.format(cloneof))
            log_debug('_command_context_view() romof   {0}\n'.format(romof))

            # --- Open ZIP file, check CRC32 and also CHDs ---
            mame_audit_machine(self.settings, rom_list)

            # --- Generate report ---
            info_text = []
            if machine['cloneof'] and machine['romof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0} / '.format(machine['cloneof']) +
                                 '[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            elif machine['cloneof']:
                info_text.append('[COLOR violet]cloneof[/COLOR] {0}'.format(machine['cloneof']))
            elif machine['romof']:
                info_text.append('[COLOR violet]romof[/COLOR] {0}'.format(machine['romof']))
            info_text.append('[COLOR skyblue]isBIOS[/COLOR] {0} / '.format(unicode(machine['isBIOS'])) +
                             '[COLOR skyblue]isDevice[/COLOR] {0}'.format(unicode(machine['isDevice'])))
            info_text.append('')

            # --- Table header ---
            # Table cell padding: left, right
            # Table columns: Type - ROM name - Size - CRC/SHA1 - Merge - BIOS - Location
            table_str = []
            table_str.append(['right', 'left',     'right', 'left',     'left',     'left'])
            table_str.append(['Type',  'ROM name', 'Size',  'CRC/SHA1', 'Location', 'Status'])

            # --- Table rows ---
            for m_rom in rom_list:
                if m_rom['type'] == 'DISK':
                    sha1_srt = m_rom['sha1'][0:8]
                    table_row = [m_rom['type'], m_rom['name'],
                                 '', sha1_srt,
                                 m_rom['location'], m_rom['status_colour']]
                else:
                    table_row = [str(m_rom['type']), str(m_rom['name']),
                                 str(m_rom['size']), str(m_rom['crc']),
                                 m_rom['location'], m_rom['status_colour']]
                table_str.append(table_row)
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            window_title = 'Machine {0} ROM audit'.format(machine_name)
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- Audit ROMs of SL item ---
        elif action == ACTION_AUDIT_SL_MACHINE:
            # --- Load machine dictionary and ROM database ---
            log_debug('_command_context_view() Auditing SL Software ROMs\n')
            log_debug('_command_context_view() SL_name {0}\n'.format(SL_name))
            log_debug('_command_context_view() SL_ROM {0}\n'.format(SL_ROM))

            SL_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '.json')
            SL_ROM_Audit_DB_FN = PATHS.SL_DB_DIR.pjoin(SL_name + '_ROM_audit.json')

            roms = fs_load_JSON_file(SL_DB_FN.getPath())
            roms_audit_db = fs_load_JSON_file(SL_ROM_Audit_DB_FN.getPath())
            rom = roms[SL_ROM]
            rom_db_list = roms_audit_db[SL_ROM]

            # --- Open ZIP file and check CRC32 ---
            mame_SL_audit_machine(self.settings, rom_db_list)

            info_text = []
            info_text.append('[COLOR violet]SL_name[/COLOR] {0}'.format(SL_name))
            info_text.append('[COLOR violet]SL_ROM[/COLOR] {0}'.format(SL_ROM))
            info_text.append('[COLOR violet]description[/COLOR] {0}'.format(rom['description']))
            info_text.append('')

            # --- Table header and rows ---
            # >> Do not render ROM name in SLs, cos they are really long.
            # table_str = [    ['right', 'left',     'right', 'left',     'left',     'left'] ]
            # table_str.append(['Type',  'ROM name', 'Size',  'CRC/SHA1', 'Location', 'Status'])
            table_str = [    ['right', 'right', 'left',     'left',     'left'] ]
            table_str.append(['Type',  'Size',  'CRC/SHA1', 'Location', 'Status'])
            for m_rom in rom_db_list:
                if m_rom['type'] == ROM_TYPE_DISK:
                    table_row = [m_rom['type'], # m_rom['name'],
                                 '', m_rom['sha1'][0:8], m_rom['location'],
                                 m_rom['status_colour']]
                    table_str.append(table_row)
                else:
                    table_row = [m_rom['type'], # m_rom['name'],
                                 m_rom['size'], m_rom['crc'], m_rom['location'],
                                 m_rom['status_colour']]
                    table_str.append(table_row)
            table_str_list = text_render_table_str(table_str)
            info_text.extend(table_str_list)
            window_title = 'SL {0} Software {1} ROM audit'.format(SL_name, SL_ROM)
            self._display_text_window(window_title, '\n'.join(info_text))

        # --- View ROM scanner reports ---
        elif action == ACTION_VIEW_REPORT_SCANNER:
            d = xbmcgui.Dialog()
            type_sub = d.select('View scanner reports',
                                ['View Have MAME machines archives',
                                 'View Missing MAME machines archives',
                                 'View MAME missing ROM list',
                                 'View MAME missing CHD list',
                                 'View Have MAME Samples',
                                 'View Missing MAME Samples',
                                 'View Have Software Lists item archives',
                                 'View Missing Software Lists item archives',
                                 'View Software Lists missing ROM list',
                                 'View Software Lists missing CHD list',
                                 'View MAME asset report',
                                 'View Software Lists asset report'])
            if type_sub < 0: return

            # --- View MAME machines have archives ---
            if type_sub == 0:
                if not PATHS.REPORT_MAME_SCAN_MACHINE_ARCH_HAVE_PATH.exists():
                    kodi_dialog_OK('MAME machines have archives scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_SCAN_MACHINE_ARCH_HAVE_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME machines have archives scanner report', info_text)

            # --- View MAME machines missing archives ---
            elif type_sub == 1:
                if not PATHS.REPORT_MAME_SCAN_MACHINE_ARCH_MISS_PATH.exists():
                    kodi_dialog_OK('MAME machines missing archives scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_SCAN_MACHINE_ARCH_MISS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME machines missing archives scanner report', info_text)

            # --- View MAME ROM archive scanner report ---
            elif type_sub == 2:
                if not PATHS.REPORT_MAME_SCAN_ROM_LIST_PATH.exists():
                    kodi_dialog_OK('MAME missing ROM list scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_SCAN_ROM_LIST_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME missing ROM list scanner report', info_text)

            # --- View MAME machine CHD scanner report ---
            elif type_sub == 3:
                if not PATHS.REPORT_MAME_SCAN_CHD_LIST_PATH.exists():
                    kodi_dialog_OK('MAME missing CHD list scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_SCAN_CHD_LIST_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME missing CHD list scanner report', info_text)

            # --- View MAME Samples have report ---
            elif type_sub == 4:
                if not PATHS.REPORT_MAME_SCAN_SAMP_HAVE_PATH.exists():
                    kodi_dialog_OK('MAME Have Samples scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_SCAN_SAMP_HAVE_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME Have Samples scanner report', info_text)

            # --- View MAME Samples missing report ---
            elif type_sub == 5:
                if not PATHS.REPORT_SL_SCAN_MACHINE_ARCH_MISS_PATH.exists():
                    kodi_dialog_OK('MAME Missing Samples scanner report not found. '
                                   'Please scan MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_SCAN_MACHINE_ARCH_MISS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME Missing Samples scanner report', info_text)

            # --- View Software Lists have archives ---
            elif type_sub == 6:
                if not PATHS.REPORT_SL_SCAN_MACHINE_ARCH_HAVE_PATH.exists():
                    kodi_dialog_OK('Software Lists have archives scanner report not found. '
                                   'Please scan SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_SCAN_MACHINE_ARCH_HAVE_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    # >> Kodi BUG: if size of file is 0 then previous text in window is rendered.
                    # log_debug('len(info_text) = {0}'.format(len(info_text)))
                    if len(info_text) == 0:
                        kodi_notify('Report is empty')
                        return
                    self._display_text_window('Software Lists have archives scanner report', info_text)

            # --- View Software Lists miss archives ---
            elif type_sub == 7:
                if not PATHS.REPORT_SL_SCAN_MACHINE_ARCH_MISS_PATH.exists():
                    kodi_dialog_OK('Software Lists missing archives scanner report not found. '
                                   'Please scan SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_SCAN_MACHINE_ARCH_MISS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('Software Lists missing archives scanner report', info_text)

            # --- View Software Lists ROM scanner report ---
            elif type_sub == 8:
                if not PATHS.REPORT_SL_SCAN_ROM_LIST_PATH.exists():
                    kodi_dialog_OK('Software Lists missing ROM list scanner report not found. '
                                   'Please scan SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_SCAN_ROM_LIST_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('Software Lists missing ROM list scanner report', info_text)

            # --- View Software Lists CHD scanner report ---
            elif type_sub == 9:
                if not PATHS.REPORT_SL_SCAN_CHD_LIST_PATH.exists():
                    kodi_dialog_OK('Software Lists missing CHD list scanner report not found. '
                                   'Please scan SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_SCAN_CHD_LIST_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('Software Lists missing CHD list scanner report', info_text)

            # --- View MAME asset report ---
            elif type_sub == 10:
                if not PATHS.REPORT_MAME_ASSETS_PATH.exists():
                    kodi_dialog_OK('MAME asset report report not found. '
                                   'Please scan MAME assets and try again.')
                    return
                with open(PATHS.REPORT_MAME_ASSETS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME asset report', info_text)

            # --- View Software Lists asset report ---
            elif type_sub == 11:
                if not PATHS.REPORT_SL_ASSETS_PATH.exists():
                    kodi_dialog_OK('Software Lists asset report not found. '
                                   'Please scan Software List assets and try again.')
                    return
                with open(PATHS.REPORT_SL_ASSETS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('Software Lists asset report', info_text)

        # --- View audit reports ---
        elif action == ACTION_VIEW_REPORT_AUDIT:
            d = xbmcgui.Dialog()
            type_sub = d.select('View audit reports',
                                ['View MAME audit report (Good)',
                                 'View MAME audit report (Errors)',
                                 'View MAME audit report (ROM Good)',
                                 'View MAME audit report (ROM Errors)',
                                 'View MAME audit report (CHD Good)',
                                 'View MAME audit report (CHD Errors)',
                                 'View SL audit report (Good)',
                                 'View SL audit report (Errors)',
                                 'View SL audit report (ROM Good)',
                                 'View SL audit report (ROM Errors)',
                                 'View SL audit report (CHD Good)',
                                 'View SL audit report (CHD Errors)'
                                 ])
            if type_sub < 0: return

            # >> MAME audit reports
            if type_sub == 0:
                if not PATHS.REPORT_MAME_AUDIT_GOOD_PATH.exists():
                    kodi_dialog_OK('MAME audit report (Good) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (Good)', info_text)

            elif type_sub == 1:
                if not PATHS.REPORT_MAME_AUDIT_ERRORS_PATH.exists():
                    kodi_dialog_OK('MAME audit report (Errors) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (Errors)', info_text)

            elif type_sub == 2:
                if not PATHS.REPORT_MAME_AUDIT_ROM_GOOD_PATH.exists():
                    kodi_dialog_OK('MAME audit report (ROM Good) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_ROM_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (ROM Good)', info_text)

            elif type_sub == 3:
                if not PATHS.REPORT_MAME_AUDIT_ROM_ERRORS_PATH.exists():
                    kodi_dialog_OK('MAME audit report (ROM Errors) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_ROM_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (ROM Errors)', info_text)

            elif type_sub == 4:
                if not PATHS.REPORT_MAME_AUDIT_CHD_GOOD_PATH.exists():
                    kodi_dialog_OK('MAME audit report (CHD Good) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_CHD_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (CHD Good)', info_text)

            elif type_sub == 5:
                if not PATHS.REPORT_MAME_AUDIT_CHD_ERRORS_PATH.exists():
                    kodi_dialog_OK('MAME audit report (CHD Errors) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_MAME_AUDIT_CHD_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (CHD Errors)', info_text)

            # >> SL audit reports
            elif type_sub == 6:
                if not PATHS.REPORT_SL_AUDIT_GOOD_PATH.exists():
                    kodi_dialog_OK('SL audit report (Good) not found. '
                                   'Please audit your SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('SL audit report (Good)', info_text)

            elif type_sub == 7:
                if not PATHS.REPORT_SL_AUDIT_ERRORS_PATH.exists():
                    kodi_dialog_OK('SL audit report (Errors) not found. '
                                   'Please audit your SL ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('SL audit report (Errors)', info_text)

            elif type_sub == 8:
                if not PATHS.REPORT_SL_AUDIT_ROMS_GOOD_PATH.exists():
                    kodi_dialog_OK('MAME audit report (ROM Good) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_ROMS_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (ROM Good)', info_text)

            elif type_sub == 9:
                if not PATHS.REPORT_SL_AUDIT_ROMS_ERRORS_PATH.exists():
                    kodi_dialog_OK('MAME audit report (ROM Errors) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_ROMS_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (ROM Errors)', info_text)

            elif type_sub == 10:
                if not PATHS.REPORT_SL_AUDIT_CHDS_GOOD_PATH.exists():
                    kodi_dialog_OK('MAME audit report (CHD Good) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_CHDS_GOOD_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (CHD Good)', info_text)

            elif type_sub == 11:
                if not PATHS.REPORT_SL_AUDIT_CHDS_ERRORS_PATH.exists():
                    kodi_dialog_OK('MAME audit report (CHD Errors) not found. '
                                   'Please audit your MAME ROMs and try again.')
                    return
                with open(PATHS.REPORT_SL_AUDIT_CHDS_ERRORS_PATH.getPath(), 'r') as myfile:
                    info_text = myfile.read()
                    self._display_text_window('MAME audit report (CHD Errors)', info_text)

        else:
            kodi_dialog_OK('Wrong action == {0}. This is a bug, please report it.'.format(action))

    def _command_context_utilities(self, catalog_name, category_name):
        log_debug('_command_context_utilities() catalog_name  "{0}"'.format(catalog_name))
        log_debug('_command_context_utilities() category_name "{0}"'.format(category_name))

        d_list = [
          'Export AEL Virtual Launcher',
        ]
        selected_value = xbmcgui.Dialog().select('View', d_list)
        if selected_value < 0: return

        # --- Export AEL Virtual Launcher ---
        if selected_value == 0:
            log_debug('_command_context_utilities() Export AEL Virtual Launcher')

            # >> Ask user for a path to export the launcher configuration
            vlauncher_str_name = 'AML_VLauncher_' + catalog_name + '_' + category_name + '.xml'
            dir_path = xbmcgui.Dialog().browse(0, 'Select XML export directory', 'files', 
                                               '', False, False).decode('utf-8')
            if not dir_path: return
            export_FN = FileName(dir_path).pjoin(vlauncher_str_name)
            if export_FN.exists():
                ret = kodi_dialog_yesno('Overwrite file {0}?'.format(export_FN.getPath()))
                if not ret:
                    kodi_notify_warn('Export of Launcher XML cancelled')
                    return

            # --- Open databases and get list of machines of this filter ---
            # >> This can be optimised: load stuff from the cache instead of the main databases.
            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 4
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'Catalog dictionary')
            catalog_dic = fs_get_cataloged_dic_parents(PATHS, catalog_name)
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machines Main')
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), pdialog_line1, 'MAME machines Render')
            machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            pDialog.update(int((3*100) / num_items), pdialog_line1, 'MAME machine Assets')
            assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
            pDialog.update(int((4*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Print error message is something goes wrong writing file ---
            try:
                fs_export_Virtual_Launcher(export_FN, catalog_dic[category_name],
                                           machines, machines_render, assets_dic)
            except Addon_Error as ex:
                kodi_notify_warn('{0}'.format(ex))
            else:
                kodi_notify('Exported Virtual Launcher "{0}"'.format(vlauncher_str_name))

    # ---------------------------------------------------------------------------------------------
    # Favourites
    # ---------------------------------------------------------------------------------------------
    # >> Favourites use the main hashed database, not the main and render databases.
    def _command_context_add_mame_fav(self, machine_name):
        log_debug('_command_add_mame_fav() Machine_name "{0}"'.format(machine_name))

        # >> Get Machine database entry
        kodi_busydialog_ON()
        control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
        machine = fs_get_machine_main_db_hash(PATHS, machine_name)
        assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        kodi_busydialog_OFF()

        # >> Open Favourite Machines dictionary
        fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
        
        # >> If machine already in Favourites ask user if overwrite.
        if machine_name in fav_machines:
            ret = kodi_dialog_yesno('Machine {0} ({1}) '.format(machine['description'], machine_name) +
                                    'already in MAME Favourites. Overwrite?')
            if ret < 1: return

        # >> Add machine. Add database version to Favourite.
        assets = assets_dic[machine_name]
        machine['assets'] = assets
        machine['ver_mame'] = control_dic['ver_mame']
        machine['ver_mame_str'] = control_dic['ver_mame_str']
        fav_machines[machine_name] = machine
        log_info('_command_add_mame_fav() Added machine "{0}"'.format(machine_name))

        # >> Save Favourites
        fs_write_JSON_file(PATHS.FAV_MACHINES_PATH.getPath(), fav_machines)
        kodi_notify('Machine {0} added to MAME Favourites'.format(machine_name))


    #
    # Context menu "Manage Favourite machines"
    #   * UNIMPLEMENTED. IS IT USEFUL?
    #     'Scan all ROMs/CHDs/Samples'
    #     Scan Favourite machines ROM ZIPs and CHDs and update flags of the Favourites 
    #     database JSON.
    #
    #   * UNIMPLEMENTED. IS IT USEFUL?
    #     'Scan all assets/artwork'
    #     Scan Favourite machines assets/artwork and update MAME Favourites database JSON.
    #
    #   * 'Check/Update all MAME Favourites'
    #     Checks that all MAME Favourite machines exist in current database. If the ROM exists,
    #     then update information from current MAME database. If the machine doesn't exist, then
    #     delete it from MAME Favourites (prompt the user about this).
    #
    #   * 'Delete machine from MAME Favourites'
    #
    def _command_context_manage_mame_fav(self, machine_name):
        dialog = xbmcgui.Dialog()
        idx = dialog.select('Manage MAME Favourites', 
                           ['Check/Update all MAME Favourites',
                            'Delete machine from MAME Favourites'])
        if idx < 0: return

        # --- Check/Update all MAME Favourites ---
        # >> Check if Favourites can be found in current MAME main database. It may happen that
        # >> a machine is renamed between MAME version although I think this is very unlikely.
        # >> MAME Favs can not be relinked. If the machine is not found in current database it must
        # >> be deleted by the user and a new Favourite created.
        # >> If the machine is found in the main database, then update the Favourite database
        # >> with data from the main database.
        if idx == 0:
            # >> Load databases.
            pDialog = xbmcgui.DialogProgress()
            line1_str = 'Loading databases ...'
            num_items = 5
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            pDialog.update(int((1*100) / num_items), line1_str, 'MAME Favourites')
            fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
            pDialog.update(int((2*100) / num_items), line1_str, 'MAME machines Main')
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            pDialog.update(int((3*100) / num_items), line1_str, 'MAME machines Render')
            machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            pDialog.update(int((4*100) / num_items), line1_str, 'MAME machine Assets')
            assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
            pDialog.update(int((5*100) / num_items), ' ', ' ')
            pDialog.close()

            # >> Check/Update MAME Favourite machines.
            for fav_key in sorted(fav_machines):
                log_debug('Checking Favourite "{0}"'.format(fav_key))
                if fav_key in machines:
                    # >> Update Favourite database (info + assets)
                    new_fav = machines[fav_key].copy()
                    new_fav.update(machines_render[fav_key])
                    new_fav['assets'] = assets_dic[fav_key]
                    new_fav['ver_mame'] = control_dic['ver_mame']
                    new_fav['ver_mame_str'] = control_dic['ver_mame_str']
                    fav_machines[fav_key] = new_fav
                    log_debug('Updated machine "{0}"'.format(fav_key))
                else:
                    log_debug('Machine "{0}" not found in MAME main DB'.format(fav_key))
                    t = 'Favourite machine "{0}" not found in database'.format(fav_key)
                    kodi_dialog_OK(t)

            # >> Save MAME Favourites DB
            fs_write_JSON_file(PATHS.FAV_MACHINES_PATH.getPath(), fav_machines)
            kodi_refresh_container()
            kodi_notify('MAME Favourite checked and updated')

        # --- Delete machine from MAME Favourites ---
        elif idx == 1:
            log_debug('_command_context_manage_mame_fav() Delete MAME Favourite machine')
            log_debug('_command_context_manage_mame_fav() Machine_name "{0}"'.format(machine_name))

            # >> Open Favourite Machines dictionary
            fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
            
            # >> Ask user for confirmation.
            ret = kodi_dialog_yesno('Delete Machine {0} ({1})?'.format(fav_machines[machine_name]['description'], machine_name))
            if ret < 1: return
            
            # >> Delete machine
            del fav_machines[machine_name]
            log_info('_command_context_manage_mame_fav() Deleted machine "{0}"'.format(machine_name))

            # >> Save Favourites
            fs_write_JSON_file(PATHS.FAV_MACHINES_PATH.getPath(), fav_machines)
            kodi_refresh_container()
            kodi_notify('Machine {0} deleted from MAME Favourites'.format(machine_name))

    def _command_show_mame_fav(self):
        log_debug('_command_show_mame_fav() Starting ...')

        # >> Open Favourite Machines dictionary
        fav_machines = fs_load_JSON_file(PATHS.FAV_MACHINES_PATH.getPath())
        if not fav_machines:
            kodi_dialog_OK('No Favourite MAME machines. Add some machines to MAME Favourites first.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render Favourites
        self._set_Kodi_all_sorting_methods()
        for m_name in fav_machines:
            machine = fav_machines[m_name]
            assets  = machine['assets']
            self._render_fav_machine_row(m_name, machine, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_fav_machine_row(self, m_name, machine, m_assets):
        # --- Default values for flags ---
        AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_NONE

        # --- Mark Flags, BIOS, Devices, BIOS, Parent/Clone and Driver status ---
        display_name = machine['description']
        display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(m_assets['flags'])            
        if machine['isBIOS']:   display_name += ' [COLOR cyan][BIOS][/COLOR]'
        if machine['isDevice']: display_name += ' [COLOR violet][Dev][/COLOR]'
        if machine['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'
        if   machine['driver_status'] == 'imperfect':   display_name += ' [COLOR yellow][Imp][/COLOR]'
        elif machine['driver_status'] == 'preliminary': display_name += ' [COLOR red][Pre][/COLOR]'

        # --- Skin flags ---
        if machine['cloneof']: AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_CLONE
        else:                  AEL_PClone_stat_value = AEL_PCLONE_STAT_VALUE_PARENT

        # --- Assets/artwork ---
        icon_path      = m_assets[self.mame_icon] if m_assets[self.mame_icon] else 'DefaultProgram.png'
        fanart_path    = m_assets[self.mame_fanart]
        banner_path    = m_assets['marquee']
        clearlogo_path = m_assets['clearlogo']
        poster_path    = m_assets['flyer']

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)

        # --- Metadata ---
        # >> Make all the infotables compatible with Advanced Emulator Launcher
        if self.settings['display_hide_trailers']:
            listitem.setInfo('video', {'title'   : display_name,     'year'    : machine['year'],
                                       'genre'   : machine['genre'], 'studio'  : machine['manufacturer'],
                                       'plot'    : m_assets['plot'],
                                       'overlay' : ICON_OVERLAY})
        else:
            listitem.setInfo('video', {'title'   : display_name,     'year'    : machine['year'],
                                       'genre'   : machine['genre'], 'studio'  : machine['manufacturer'],
                                       'plot'    : m_assets['plot'], 'trailer' : m_assets['trailer'],
                                       'overlay' : ICON_OVERLAY})
        listitem.setProperty('nplayers', machine['nplayers'])
        listitem.setProperty('platform', 'MAME')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title'     : m_assets['title'],   'snap'    : m_assets['snap'],
                         'boxfront'  : m_assets['cabinet'], 'boxback' : m_assets['cpanel'],
                         'cartridge' : m_assets['PCB'],     'flyer'   : m_assets['flyer'],
                         'icon'      : icon_path,           'fanart'    : fanart_path,
                         'banner'    : banner_path,         'clearlogo' : clearlogo_path,
                         'poster'    : poster_path})

        # --- ROM flags (Skins will use these flags to render icons) ---
        listitem.setProperty(AEL_PCLONE_STAT_LABEL, AEL_PClone_stat_value)

        # --- Create context menu ---
        URL_view_DAT = self._misc_url_2_arg_RunPlugin('command', 'VIEW_DAT', 'machine', m_name)
        URL_view = self._misc_url_3_arg_RunPlugin('command', 'VIEW', 'machine', m_name, 'location', LOCATION_MAME_FAVS)
        URL_manage = self._misc_url_2_arg_RunPlugin('command', 'MANAGE_MAME_FAV', 'machine', m_name)
        commands = [
            ('Info / Utils',  URL_view_DAT),
            ('View / Audit',  URL_view),
            ('Manage Favourite machines', URL_manage),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_3_arg('command', 'LAUNCH', 'machine', m_name, 'location', 'MAME_FAV')
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    def _command_context_add_sl_fav(self, SL_name, ROM_name):
        log_debug('_command_add_sl_fav() SL_name  "{0}"'.format(SL_name))
        log_debug('_command_add_sl_fav() ROM_name "{0}"'.format(ROM_name))

        # >> Get Machine database entry
        kodi_busydialog_ON()
        control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
        # >> Load SL ROMs
        file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
        SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
        SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())
        # >> Load SL assets
        assets_file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '_assets.json'
        SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
        SL_assets_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())
        kodi_busydialog_OFF()

        # >> Open Favourite Machines dictionary
        fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
        SL_fav_key = SL_name + '-' + ROM_name
        log_debug('_command_add_sl_fav() SL_fav_key "{0}"'.format(SL_fav_key))
        
        # >> If machine already in Favourites ask user if overwrite.
        if SL_fav_key in fav_SL_roms:
            ret = kodi_dialog_yesno('Machine {0} ({1}) '.format(ROM_name, SL_name) +
                                    'already in SL Favourites. Overwrite?')
            if ret < 1: return

        # >> Add machine to SL Favourites
        ROM = SL_roms[ROM_name]
        assets = SL_assets_dic[ROM_name] if ROM_name in SL_assets_dic else fs_new_SL_asset()
        ROM['ROM_name']       = ROM_name
        ROM['SL_name']        = SL_name
        ROM['ver_mame']       = control_dic['ver_mame']
        ROM['ver_mame_str']   = control_dic['ver_mame_str']
        ROM['launch_machine'] = ''
        ROM['assets']         = assets
        fav_SL_roms[SL_fav_key] = ROM
        log_info('_command_add_sl_fav() Added machine "{0}" ("{1}")'.format(ROM_name, SL_name))

        # >> Save Favourites
        fs_write_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath(), fav_SL_roms)
        kodi_notify('ROM {0} added to SL Favourite ROMs'.format(ROM_name))

    #
    # Context menu "Manage SL Favourite ROMs"
    #   * 'Choose default machine for SL ROM'
    #      Allows to set the default machine to launch each SL ROM.
    #
    #   * (UNIMPLEMENTED, IS IT USEFUL?)
    #     'Scan all SL Favourite ROMs/CHDs'
    #      Scan SL ROM ZIPs and CHDs and update flags of the SL Favourites database JSON.
    #
    #   * (UNIMPLEMENTED, IS IT USEFUL?)
    #     'Scan all SL Favourite assets/artwork'
    #      Scan SL ROMs assets/artwork and update SL Favourites database JSON.
    #
    #   * 'Check/Update all SL Favourites ROMs'
    #      Checks that all SL Favourite ROMs exist in current database. If the ROM exists,
    #      then update information from current SL database. If the ROM doesn't exist, then
    #      delete it from SL Favourites (prompt the user about this).
    #
    #   * 'Delete ROM from SL Favourites'
    #
    def _command_context_manage_sl_fav(self, SL_name, ROM_name):
        dialog = xbmcgui.Dialog()
        idx = dialog.select('Manage Software Lists Favourites', 
                           ['Choose default machine for SL ROM',
                            'Check/Update all SL Favourites ROMs',
                            'Delete ROM from SL Favourites'])
        if idx < 0: return

        # --- Choose default machine for SL ROM ---
        if idx == 0:
            # >> Load Favs
            fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
            SL_fav_key = SL_name + '-' + ROM_name

            # >> Get a list of machines that can launch this SL ROM. User chooses.
            SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
            SL_machine_list = SL_machines_dic[SL_name]
            SL_machine_names_list = []
            SL_machine_desc_list = []
            SL_machine_names_list.append('')
            SL_machine_desc_list.append('[ Not set ]')
            for SL_machine in SL_machine_list: 
                SL_machine_names_list.append(SL_machine['machine'])
                SL_machine_desc_list.append(SL_machine['description'])
            # >> Krypton feature: preselect current machine
            pre_idx = SL_machine_names_list.index(fav_SL_roms[SL_fav_key]['launch_machine'])
            if pre_idx < 0: pre_idx = 0
            dialog = xbmcgui.Dialog()
            m_index = dialog.select('Select machine', SL_machine_desc_list, preselect = pre_idx)
            if m_index < 0 or m_index == pre_idx: return
            machine_name = SL_machine_names_list[m_index]
            machine_desc = SL_machine_desc_list[m_index]

            # >> Edit and save
            fav_SL_roms[SL_fav_key]['launch_machine'] = machine_name
            fs_write_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath(), fav_SL_roms)
            kodi_notify('Deafult machine set to {0} ({1})'.format(machine_name, machine_desc))

        # --- Check/Update SL Favourites ---
        elif idx == 1:
            # --- Load databases ---
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
            fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())

            # --- Check/Update SL Favourite ROMs ---
            num_SL_favs = len(fav_SL_roms)
            num_iteration = 0
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('Advanced MAME Launcher')
            for fav_SL_key in sorted(fav_SL_roms):
                fav_ROM_name = fav_SL_roms[fav_SL_key]['ROM_name']
                fav_SL_name = fav_SL_roms[fav_SL_key]['SL_name']
                log_debug('Checking Favourite "{0}" / "{1}"'.format(fav_ROM_name, fav_SL_name))

                # >> Update progress dialog (BEGIN)
                update_number = (num_iteration * 100) // num_SL_favs
                pDialog.update(update_number, 'Checking SL Favourites (ROM "{0}") ...'.format(fav_ROM_name))

                # >> Load SL ROMs DB and assets
                file_name =  SL_catalog_dic[fav_SL_name]['rom_DB_noext'] + '.json'
                SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
                SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())
                assets_file_name =  SL_catalog_dic[fav_SL_name]['rom_DB_noext'] + '_assets.json'
                SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
                SL_assets_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())

                if fav_ROM_name in SL_roms:
                    # >> Update Favourite DB
                    new_Fav_ROM = SL_roms[fav_ROM_name]
                    new_assets = SL_assets_dic[fav_ROM_name]
                    new_Fav_ROM['ROM_name']       = fav_ROM_name
                    new_Fav_ROM['SL_name']        = fav_SL_name
                    new_Fav_ROM['ver_mame']       = control_dic['ver_mame']
                    new_Fav_ROM['ver_mame_str']   = control_dic['ver_mame_str']
                    new_Fav_ROM['launch_machine'] = ''
                    new_Fav_ROM['assets']         = new_assets
                    fav_SL_roms[fav_SL_key] = new_Fav_ROM
                    log_debug('Updated SL Fav ROM "{0}" / "{1}"'.format(fav_ROM_name, fav_SL_name))

                else:
                    # >> Delete Favourite ROM from Favourite DB
                    log_debug('Machine "{0}" / "{1}" not found in MAME main DB'.format(fav_ROM_name, fav_SL_name))
                    t = 'Favourite machine "{0}" in SL "{1}" not found in database'.format(fav_ROM_name, fav_SL_name)
                    kodi_dialog_OK(t)

                # >> Update progress dialog (END)
                num_iteration += 1
            pDialog.update(100)
            pDialog.close()

            # --- Save SL Favourite ROMs DB ---
            fs_write_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath(), fav_SL_roms)
            kodi_refresh_container()
            kodi_notify('SL Favourite ROMs checked and updated')

        # --- Delete ROM from SL Favourites ---
        elif idx == 2:
            log_debug('_command_context_manage_sl_fav() Delete SL Favourite ROM')
            log_debug('_command_context_manage_sl_fav() SL_name  "{0}"'.format(SL_name))
            log_debug('_command_context_manage_sl_fav() ROM_name "{0}"'.format(ROM_name))

            # >> Get Machine database row
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
            log_debug('_command_delete_sl_fav() SL_fav_key "{0}"'.format(SL_fav_key))
            
            # >> Ask user for confirmation.
            ret = kodi_dialog_yesno('Delete Machine {0} ({1})?'.format(ROM_name, SL_name))
            if ret < 1: return

            # >> Delete machine
            del fav_SL_roms[SL_fav_key]
            log_info('_command_delete_sl_fav() Deleted machine {0} ({1})'.format(ROM_name, SL_name))

            # >> Save Favourites
            fs_write_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath(), fav_SL_roms)
            kodi_refresh_container()
            kodi_notify('ROM {0} deleted from SL Favourites'.format(ROM_name))


    def _command_show_sl_fav(self):
        log_debug('_command_show_sl_fav() Starting ...')

        # >> Load Software List ROMs
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())

        # >> Open Favourite Machines dictionary
        fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
        if not fav_SL_roms:
            kodi_dialog_OK('No Favourite Software Lists ROMs. Add some ROMs to SL Favourites first.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render Favourites
        self._set_Kodi_all_sorting_methods()
        for SL_fav_key in fav_SL_roms:
            SL_fav_ROM = fav_SL_roms[SL_fav_key]
            assets = SL_fav_ROM['assets']
            # >> Add the SL name as 'genre'
            SL_name = SL_fav_ROM['SL_name']
            SL_fav_ROM['genre'] = SL_catalog_dic[SL_name]['display_name']
            self._render_sl_fav_machine_row(SL_fav_key, SL_fav_ROM, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_sl_fav_machine_row(self, SL_fav_key, ROM, assets):
        SL_name  = ROM['SL_name']
        ROM_name = ROM['ROM_name']
        display_name = ROM['description']

        # --- Mark Status and Clones ---
        status = '{0}{1}'.format(ROM['status_ROM'], ROM['status_CHD'])
        display_name += ' [COLOR skyblue]{0}[/COLOR]'.format(status)
        if ROM['cloneof']:  display_name += ' [COLOR orange][Clo][/COLOR]'

        # --- Assets/artwork ---
        icon_path   = assets[self.SL_icon] if assets[self.SL_icon] else 'DefaultProgram.png'
        fanart_path = assets[self.SL_fanart]
        poster_path = assets['boxfront']

        # --- Create listitem row ---
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(display_name)
        # >> Make all the infolabels compatible with Advanced Emulator Launcher
        if self.settings['display_hide_trailers']:
            listitem.setInfo('video', {'title'   : display_name,      'year'    : ROM['year'],
                                       'genre'   : ROM['genre'],      'studio'  : ROM['publisher'],
                                       'plot'    : ROM['plot'],       'overlay' : ICON_OVERLAY })
        else:
            listitem.setInfo('video', {'title'   : display_name,      'year'    : ROM['year'],
                                       'genre'   : ROM['genre'],      'studio'  : ROM['publisher'],
                                       'plot'    : ROM['plot'],       'overlay' : ICON_OVERLAY,
                                       'trailer' : assets['trailer'] })
        listitem.setProperty('platform', 'MAME Software List')

        # --- Assets ---
        # >> AEL custom artwork fields
        listitem.setArt({'title' : assets['title'], 'snap' : assets['snap'], 'boxfront' : assets['boxfront'],
                         'icon' : icon_path, 'fanart' : fanart_path, 'poster' : poster_path})

        # --- Create context menu ---
        URL_view_DAT = self._misc_url_4_arg_RunPlugin('command', 'VIEW_DAT', 'SL', SL_name, 'ROM', ROM_name, 'location', LOCATION_SL_FAVS)
        URL_view = self._misc_url_4_arg_RunPlugin('command', 'VIEW', 'SL', SL_name, 'ROM', ROM_name, 'location', LOCATION_SL_FAVS)
        URL_manage = self._misc_url_3_arg_RunPlugin('command', 'MANAGE_SL_FAV', 'SL', SL_name, 'ROM', ROM_name)
        commands = [
            ('Info / Utils', URL_view_DAT),
            ('View / Audit', URL_view),
            ('Manage SL Favourite ROMs', URL_manage),
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__)),
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_4_arg('command', 'LAUNCH_SL', 'SL', SL_name, 'ROM', ROM_name, 'location', LOCATION_SL_FAVS)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = False)

    # ---------------------------------------------------------------------------------------------
    # Custom MAME filters
    # Custom filters behave like standard catalogs.
    # Custom filters are defined in a XML file, the XML file is processed and the custom catalogs
    # created from the main database.
    # ---------------------------------------------------------------------------------------------
    def _command_show_custom_filters(self):
        log_debug('_command_show_custom_filters() Starting ...')

        # >> Open Custom filter count database and index
        filter_index_dic = fs_load_JSON_file(PATHS.FILTERS_INDEX_PATH.getPath())
        if not filter_index_dic:
            kodi_dialog_OK('MAME filter index is empty. Please rebuild your filters.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render Custom Filters
        mame_view_mode = self.settings['mame_view_mode']
        self._set_Kodi_all_sorting_methods()
        for f_name in filter_index_dic:
            if mame_view_mode == VIEW_MODE_FLAT:
                num_machines = filter_index_dic[f_name]['num_machines']
                if num_machines == 1: machine_str = 'machine'
                else:                 machine_str = 'machines'
            elif mame_view_mode == VIEW_MODE_PCLONE:
                num_machines = filter_index_dic[f_name]['num_parents']
                if num_machines == 1: machine_str = 'parent'
                else:                 machine_str = 'parents'
            self._render_custom_filter_item_row(f_name, num_machines, machine_str)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_custom_filter_item_row(self, f_name, num_machines, machine_str):
        # --- Create listitem row ---
        ICON_OVERLAY = 6
        title_str = '{0} [COLOR orange]({1} {2})[/COLOR]'.format(f_name, num_machines, machine_str)
        listitem = xbmcgui.ListItem(title_str)
        listitem.setInfo('video', {'title' : title_str, 'overlay' : ICON_OVERLAY})

        # --- Artwork ---
        icon_path   = AML_ICON_FILE_PATH.getPath()
        fanart_path = AML_FANART_FILE_PATH.getPath()
        listitem.setArt({'icon' : icon_path, 'fanart' : fanart_path})

        # --- Create context menu ---
        # >> Make a list of tuples
        commands = [
            ('Kodi File Manager', 'ActivateWindow(filemanager)'),
            ('AML addon settings', 'Addon.OpenSettings({0})'.format(__addon_id__))
        ]
        listitem.addContextMenuItems(commands)

        # --- Add row ---
        URL = self._misc_url_2_arg('catalog', 'Custom', 'category', f_name)
        xbmcplugin.addDirectoryItem(handle = self.addon_handle, url = URL, listitem = listitem, isFolder = True)

    #
    # Renders a Parent or Flat machine list
    #
    def _render_custom_filter_ROMs(self, filter_name):
        log_debug('_render_custom_filter_ROMs() filter_name  = {0}'.format(filter_name))
        display_hide_BIOS = self.settings['display_hide_BIOS']
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Global properties
        view_mode_property = self.settings['mame_view_mode']
        log_debug('_render_custom_filter_ROMs() view_mode_property = {0}'.format(view_mode_property))

        # >> Check id main DB exists
        if not PATHS.RENDER_DB_PATH.exists():
            kodi_dialog_OK('MAME database not found. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Load main MAME info DB and catalog
        l_cataloged_dic_start = time.time()
        Filters_index_dic = fs_load_JSON_file(PATHS.FILTERS_INDEX_PATH.getPath())
        rom_DB_noext = Filters_index_dic[filter_name]['rom_DB_noext']
        if view_mode_property == VIEW_MODE_PCLONE:
            DB_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_parents.json')
            machine_list = fs_load_JSON_file(DB_FN.getPath())
        elif view_mode_property == VIEW_MODE_FLAT:
            DB_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_all.json')
            machine_list = fs_load_JSON_file(DB_FN.getPath())
        else:
            kodi_dialog_OK('Wrong view_mode_property = "{0}". '.format(view_mode_property) +
                           'This is a bug, please report it.')
            return
        l_cataloged_dic_end = time.time()
        l_render_db_start = time.time()
        # machine_render_dic = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
        machine_render_dic = fs_load_JSON_file(PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_ROMs.json').getPath())
        l_render_db_end = time.time()
        l_assets_db_start = time.time()
        # MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_assets.json').getPath())
        l_assets_db_end = time.time()
        l_pclone_dic_start = time.time()
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
        l_pclone_dic_end = time.time()

        catalog_t = l_cataloged_dic_end - l_cataloged_dic_start
        render_t = l_render_db_end - l_render_db_start
        assets_t = l_assets_db_end - l_assets_db_start
        pclone_t = l_pclone_dic_end - l_pclone_dic_start
        loading_time = catalog_t + render_t + assets_t + pclone_t

        # >> Check if catalog is empty
        if not machine_list:
            kodi_dialog_OK('Catalog is empty. Check out "Setup plugin" context menu.')
            xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
            return

        # >> Render parent main list
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        if view_mode_property == VIEW_MODE_PCLONE:
            # >> Parent/Clone mode render parents only
            for machine_name, render_name in machine_list.iteritems():
                machine = machine_render_dic[machine_name]
                if display_hide_BIOS and machine['isBIOS']: continue
                if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
                if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
                assets = MAME_assets_dic[machine_name]
                num_clones = len(main_pclone_dic[machine_name])
                self._render_catalog_machine_row(machine_name, render_name, machine, assets,
                                                 True, num_clones, 'Custom', filter_name)
        else:
            # >> Flat mode renders all machines
            for machine_name, render_name in machine_list.iteritems():
                machine = machine_render_dic[machine_name]
                if display_hide_BIOS and machine['isBIOS']: continue
                if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
                if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
                assets = MAME_assets_dic[machine_name]
                self._render_catalog_machine_row(machine_name, render_name, machine, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading render db     {0:.4f} s'.format(render_t))
        log_debug('Loading assets db     {0:.4f} s'.format(assets_t))
        log_debug('Loading pclone dic    {0:.4f} s'.format(pclone_t))
        log_debug('Loading cataloged dic {0:.4f} s'.format(catalog_t))
        log_debug('Loading               {0:.4f} s'.format(loading_time))
        log_debug('Rendering             {0:.4f} s'.format(rendering_ticks_end - rendering_ticks_start))

    #
    # No need to check for DB existance here. If this function is called is because parents and
    # hence all ROMs databases exist.
    #
    def _render_custom_filter_clones(self, filter_name, parent_name):
        log_debug('_render_custom_filter_clones() Starting ...')
        display_hide_nonworking = self.settings['display_hide_nonworking']
        display_hide_imperfect  = self.settings['display_hide_imperfect']

        # >> Load main MAME info DB
        loading_ticks_start = time.time()
        Filters_index_dic = fs_load_JSON_file(PATHS.FILTERS_INDEX_PATH.getPath())
        rom_DB_noext = Filters_index_dic[filter_name]['rom_DB_noext']
        # machine_render_dic = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
        machine_render_dic = fs_load_JSON_file(PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_ROMs.json').getPath())
        # MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_assets.json').getPath())
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
        view_mode_property = self.settings['mame_view_mode']
        log_debug('_render_custom_filter_clones() view_mode_property = {0}'.format(view_mode_property))
        loading_ticks_end = time.time()

        # >> Render parent first
        rendering_ticks_start = time.time()
        self._set_Kodi_all_sorting_methods()
        machine = machine_render_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_catalog_machine_row(parent_name, machine, assets)
        # >> and clones next.
        for p_name in main_pclone_dic[parent_name]:
            machine = machine_render_dic[p_name]
            assets  = MAME_assets_dic[p_name]
            if display_hide_nonworking and machine['driver_status'] == 'preliminary': continue
            if display_hide_imperfect and machine['driver_status'] == 'imperfect': continue
            self._render_catalog_machine_row(p_name, machine, assets)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)
        rendering_ticks_end = time.time()

        # --- DEBUG Data loading/rendering statistics ---
        log_debug('Loading seconds   {0}'.format(loading_ticks_end - loading_ticks_start))
        log_debug('Rendering seconds {0}'.format(rendering_ticks_end - rendering_ticks_start))

    def _command_context_setup_custom_filters(self):
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Setup AML custom filters',
                                 ['View custom filter XML',
                                  'Build custom filter databases'])
        if menu_item < 0: return

        # --- View custom filter XML ---
        if menu_item == 0:
            XML_FN = FileName(self.settings['filter_XML'])
            log_debug('_command_context_setup_custom_filters() Reading XML OP "{0}"'.format(XML_FN.getOriginalPath()))
            log_debug('_command_context_setup_custom_filters() Reading XML  P "{0}"'.format(XML_FN.getPath()))
            if not XML_FN.exists():
                kodi_dialog_OK('Custom filter XML file not found.')
                return
            with open(XML_FN.getPath(), 'r') as myfile:
                info_text = myfile.read().decode('utf-8')
                self._display_text_window('Custom filter XML', info_text)

        # --- Update custom filters ---
        # filter_index_dic = {
        #     'name' : {
        #         'display_name' : str,
        #         'num_machines' : int,
        #         'rom_DB_noext' : 
        #     }
        # }
        #
        # AML_DATA_DIR/filters/'rom_DB_noext'_all.json -> machine_list = {
        #     'machine1' : 'display_name1', 'machine2' : 'display_name2', ...
        # }
        #
        # AML_DATA_DIR/filters/'rom_DB_noext'_parents.json -> machine_list = {
        #     'machine1' : 'display_name1', 'machine2' : 'display_name2', ...
        # }
        #
        # AML_DATA_DIR/filters/'rom_DB_noext'_ROMs.json -> machine_render = {}
        #
        # AML_DATA_DIR/filters/'rom_DB_noext'_assets.json -> asset_dic = {}
        #
        elif menu_item == 1:
            __debug_xml_parser = False

            # >> Open custom filter XML and parse it
            # If XML has errors (invalid characters, etc.) this will rais exception 'err'
            XML_FN = FileName(self.settings['filter_XML'])
            if not XML_FN.exists():
                kodi_dialog_OK('Custom filter XML file not found.')
                return
            log_debug('_command_context_setup_custom_filters() Reading XML OP "{0}"'.format(XML_FN.getOriginalPath()))
            log_debug('_command_context_setup_custom_filters() Reading XML  P "{0}"'.format(XML_FN.getPath()))
            try:
                xml_tree = ET.parse(XML_FN.getPath())
            except:
                return SLData
            xml_root = xml_tree.getroot()
            define_dic = {}
            filters_dic = {}
            for root_element in xml_root:
                if __debug_xml_parser: log_debug('Root child {0}'.format(root_element.tag))

                if root_element.tag == 'DEFINE':
                    name_str = root_element.attrib['name']
                    define_str = root_element.text if root_element.text else ''
                    log_debug('DEFINE "{0}" := "{1}"'.format(name_str, define_str))
                    define_dic[name_str] = define_str
                elif root_element.tag == 'MAMEFilter':
                    this_filter_dic = {'name' : '', 'options' : '', 'driver' : ''}
                    for filter_element in root_element:
                        text_t = filter_element.text if filter_element.text else ''
                        if filter_element.tag == 'Name': this_filter_dic['name'] = text_t
                        elif filter_element.tag == 'Options': this_filter_dic['options'] = text_t
                        elif filter_element.tag == 'Driver': this_filter_dic['driver'] = text_t
                    log_debug('Adding filter "{0}"'.format(this_filter_dic['name']))
                    filters_dic[this_filter_dic['name']] = this_filter_dic

            # >> Resolve DEFINE tags (substitute by the defined value)
            for filter_key in filters_dic:
                f_definition = filters_dic[filter_key]
                for replace_initial_str, replace_final_str in define_dic.iteritems():
                    f_definition['driver'] = f_definition['driver'].replace(replace_initial_str, replace_final_str)

            # >> Open main ROM databases
            pDialog = xbmcgui.DialogProgress()
            pDialog_canceled = False
            pdialog_line1 = 'Loading databases ...'
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(0, pdialog_line1, 'Parent/Clone')
            main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
            pDialog.update(25, pdialog_line1, 'Machines Main')
            machine_main_dic = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            pDialog.update(50, pdialog_line1, 'Machines Render')
            machine_render_dic = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            pDialog.update(75, pdialog_line1, 'Machine assets')
            assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
            pDialog.update(100, pdialog_line1, ' ')
            pDialog.close()

            # >> Make a dictionary of objects to be filtered
            main_filter_dic = {}
            for m_name in main_pclone_dic:
                main_filter_dic[m_name] = {
                    'sourcefile' : machine_main_dic[m_name]['sourcefile']
                }

            # >> Traverse list of filters, build filter index and compute filter list.
            pdialog_line1 = 'Building custom MAME filters'
            pDialog.create('Advanced MAME Launcher', pdialog_line1)
            Filters_index_dic = {}
            total_items = len(filters_dic)
            processed_items = 0
            for filter_key in filters_dic:
                # >> Initialise
                f_definition = filters_dic[filter_key]
                f_name = f_definition['name']
                # log_debug('f_definition = {0}'.format(unicode(f_definition)))

                # >> Initial progress
                pDialog.update((processed_items*100) // total_items, pdialog_line1, 'Filter "{0}" ...'.format(f_name))

                # >> Driver filter
                filtered_machine_dic = mame_filter_Driver_tag(main_filter_dic, f_definition['driver'])

                # >> Make indexed catalog
                filtered_machine_parents_dic = {}
                filtered_machine_all_dic = {}
                filtered_render_ROMs = {}
                filtered_assets_dic = {}
                for p_name in sorted(filtered_machine_dic.keys()):
                    # >> Add parents
                    filtered_machine_parents_dic[p_name] = machine_render_dic[p_name]['description']
                    filtered_machine_all_dic[p_name] = machine_render_dic[p_name]['description']
                    filtered_render_ROMs[p_name] = machine_render_dic[p_name]
                    filtered_assets_dic[p_name] = assets_dic[p_name]
                    # >> Add clones
                    for c_name in main_pclone_dic[p_name]:
                        filtered_machine_all_dic[c_name] = machine_render_dic[c_name]['description']
                        filtered_render_ROMs[c_name] = machine_render_dic[c_name]
                        filtered_assets_dic[c_name] = assets_dic[c_name]
                rom_DB_noext = hashlib.md5(f_name).hexdigest()
                this_filter_idx_dic = {
                    'display_name' : f_definition['name'],
                    'num_parents'  : len(filtered_machine_parents_dic),
                    'num_machines' : len(filtered_machine_all_dic),
                    'rom_DB_noext' : rom_DB_noext
                }
                Filters_index_dic[f_name] = this_filter_idx_dic

                # >> Save filter database
                output_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_parents.json')
                fs_write_JSON_file(output_FN.getPath(), filtered_machine_parents_dic)
                output_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_all.json')
                fs_write_JSON_file(output_FN.getPath(), filtered_machine_all_dic)
                output_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_ROMs.json')
                fs_write_JSON_file(output_FN.getPath(), filtered_render_ROMs)
                output_FN = PATHS.FILTERS_DB_DIR.pjoin(rom_DB_noext + '_assets.json')
                fs_write_JSON_file(output_FN.getPath(), filtered_assets_dic)
                # >> Final progress
                processed_items += 1
            pDialog.update((processed_items*100) // total_items, pdialog_line1, ' ')
            pDialog.close()
            # >> Save custom filter index.
            fs_write_JSON_file(PATHS.FILTERS_INDEX_PATH.getPath(), Filters_index_dic)
            # >> Update timestamp
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            control_dic['t_Custom_Filter_build'] = time.time()
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('Custom filter database built')

    # ---------------------------------------------------------------------------------------------
    # Setup plugin databases
    # ---------------------------------------------------------------------------------------------
    def _command_context_setup_plugin(self):
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Setup plugin',
                                 ['Check MAME version',
                                  'Extract MAME.xml',
                                  'Build all databases',
                                  'Scan everything and build plots',
                                  'Build Fanarts ...',
                                  'Audit MAME machine ROMs/CHDs',
                                  'Audit SL ROMs/CHDs',
                                  'Step by step ...'])
        if menu_item < 0: return

        # --- Check MAME version ---
        # >> Run 'mame -?' and extract version from stdout
        if menu_item == 0:
            if not self.settings['mame_prog']:
                kodi_dialog_OK('MAME executable is not set.')
                return
            mame_prog_FN = FileName(self.settings['mame_prog'])
            mame_version_str = fs_extract_MAME_version(PATHS, mame_prog_FN)
            kodi_dialog_OK('MAME version is {0}'.format(mame_version_str))

        # --- Extract MAME.xml ---
        elif menu_item == 1:
            if not self.settings['mame_prog']:
                kodi_dialog_OK('MAME executable is not set.')
                return
            mame_prog_FN = FileName(self.settings['mame_prog'])

            # --- Extract MAME XML ---
            (filesize, total_machines) = fs_extract_MAME_XML(PATHS, mame_prog_FN)
            kodi_dialog_OK('Extracted MAME XML database. '
                           'Size is {0} MB and there are {1} machines.'.format(filesize / 1000000, total_machines))

        # --- Build everything ---
        elif menu_item == 2:
            if not PATHS.MAME_XML_PATH.exists():
                kodi_dialog_OK('MAME XML not found. Execute "Extract MAME.xml" first.')
                return

            pDialog = xbmcgui.DialogProgress()
            line1_str = 'Loading databases ...'
            num_items = 1
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            pDialog.update(int((1*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Build all databases ---
            # 1) Creates the ROM hashed database.
            # 2) Creates the (empty) Asset cache.
            # 3) Updates control_dic and t_MAME_DB_build timestamp.
            DB = mame_build_MAME_main_database(PATHS, self.settings, control_dic)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)

            # --- Build and save everything ---
            # 1) Updates control_dic and t_MAME_Audit_DB_build timestamp.
            mame_build_ROM_audit_databases(PATHS, self.settings, control_dic,
                                           DB.machines, DB.machines_render, DB.devices_db_dic, DB.machine_roms)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)

            # --- Build MAME catalog ---
            # >> At this time the asset database will be empty (scanner has not been run). However, 
            # >> the asset cache with an empty database is required to render the machines in the catalogs.
            # 1) Creates cache_index_dic and SAVES it.
            # 2) Requires rebuilding of the ROM cache.
            # 3) Requires rebuilding of the asset cache.
            # 4) Updates control_dic and t_MAME_Catalog_build timestamp.
            mame_build_MAME_catalogs(PATHS, self.settings, control_dic,
                                     DB.machines, DB.machines_render, DB.machine_roms,
                                     DB.main_pclone_dic, DB.assets_dic)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
            fs_build_ROM_cache(PATHS, DB.machines, DB.machines_render, cache_index_dic, pDialog)
            fs_build_asset_cache(PATHS, DB.assets_dic, cache_index_dic, pDialog)

            # 1) Updates control_dic and the t_SL_DB_build timestamp.
            mame_build_SoftwareLists_databases(PATHS, self.settings, control_dic,
                                               DB.machines, DB.machines_render)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('All databases built')

        # --- Scan everything ---
        elif menu_item == 3:
            log_info('_command_setup_plugin() Scanning everything ...')

            # --- MAME Machines -------------------------------------------------------------------
            # NOTE Here only check for abort conditions. Optinal conditions must be check
            #      inside the function.
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
                CHD_path_FN = FileName('')

            scan_Samples = False
            if self.settings['samples_path']:
                Samples_path_FN = FileName(self.settings['samples_path'])
                if not Samples_path_FN.isdir():
                    kodi_dialog_OK('Samples directory does not exist. Samples scanning disabled.')
                else:
                    scan_Samples = True
            else:
                kodi_dialog_OK('Samples directory not configured. Samples scanning disabled.')
                Samples_path_FN = FileName('')

            # >> Load machine database and control_dic
            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 12
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'Control dic')
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machines Main')
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), pdialog_line1, 'MAME machines Render')
            machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            pDialog.update(int((3*100) / num_items), pdialog_line1, 'MAME machine Assets')
            assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
            pDialog.update(int((4*100) / num_items), pdialog_line1, 'MAME Parent/Clone')
            main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
            pDialog.update(int((5*100) / num_items), pdialog_line1, 'MAME machine archives')
            machine_archives_dic = fs_load_JSON_file(PATHS.ROM_SET_MACHINE_ARCHIVES_DB_PATH.getPath())
            pDialog.update(int((6*100) / num_items), pdialog_line1, 'MAME ROM list')
            ROM_archive_list = fs_load_JSON_file(PATHS.ROM_SET_ROM_ARCHIVES_DB_PATH.getPath())
            pDialog.update(int((7*100) / num_items), pdialog_line1, 'MAME CHD list')
            CHD_archive_list = fs_load_JSON_file(PATHS.ROM_SET_CHD_ARCHIVES_DB_PATH.getPath())
            pDialog.update(int((8*100) / num_items), pdialog_line1, 'History DAT index')
            history_idx_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
            pDialog.update(int((9*100) / num_items), pdialog_line1, 'Mameinfo DAT index')
            mameinfo_idx_dic = fs_load_JSON_file(PATHS.MAMEINFO_IDX_PATH.getPath())
            pDialog.update(int((10*100) / num_items), pdialog_line1, 'Gameinit DAT index')
            gameinit_idx_list = fs_load_JSON_file(PATHS.GAMEINIT_IDX_PATH.getPath())
            pDialog.update(int((11*100) / num_items), pdialog_line1, 'Command DAT index')
            command_idx_list = fs_load_JSON_file(PATHS.COMMAND_IDX_PATH.getPath())
            pDialog.update(int((12*100) / num_items), ' ', ' ')
            pDialog.close()

            # 1) Updates 'flags' field in assets_dic
            # 2) Updates timestamp t_MAME_ROM_scan in control_dic
            mame_scan_MAME_ROMs(PATHS, self.settings, control_dic,
                                machines, machines_render, assets_dic,
                                machine_archives_dic, ROM_archive_list, CHD_archive_list,
                                ROM_path_FN, CHD_path_FN, Samples_path_FN,
                                scan_CHDs, scan_Samples)

            # >> Get assets directory. Abort if not configured/found.
            do_MAME_asset_scan = True
            if not self.settings['assets_path']:
                kodi_dialog_OK('Asset directory not configured. Aborting.')
                do_MAME_asset_scan = False
            Asset_path_FN = FileName(self.settings['assets_path'])
            if not Asset_path_FN.isdir():
                kodi_dialog_OK('Asset directory does not exist. Aborting.')
                do_MAME_asset_scan = False

            if do_MAME_asset_scan:
                # 1) Mutates assets_dic and control_dic
                mame_scan_MAME_assets(PATHS, assets_dic, control_dic, pDialog,
                                      machines_render, main_pclone_dic, Asset_path_FN)

            # >> Traverse MAME machines and build plot. Updates assets_dic
            mame_build_MAME_plots(machines, machines_render, assets_dic, pDialog,
                                  history_idx_dic, mameinfo_idx_dic, gameinit_idx_list, command_idx_list)

            pdialog_line1 = 'Saving databases ...'
            num_items = 2
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'Control dictionary')
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machine Assets')
            fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
            pDialog.update(int((2*100) / num_items))
            pDialog.close()

            # >> Regenerate asset cache.
            cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
            fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)

            # --- Software Lists ------------------------------------------------------------------
            # >> Abort if SL hash path not configured.
            do_SL_ROM_scan = True
            if not self.settings['SL_hash_path']:
                kodi_dialog_OK('Software Lists hash path not set. SL scanning disabled.')
                do_SL_ROM_scan = False
            SL_hash_dir_FN = PATHS.SL_DB_DIR
            log_info('_command_setup_plugin() SL hash dir OP {0}'.format(SL_hash_dir_FN.getOriginalPath()))
            log_info('_command_setup_plugin() SL hash dir  P {0}'.format(SL_hash_dir_FN.getPath()))

            # >> Abort if SL ROM dir not configured.
            if not self.settings['SL_rom_path']:
                kodi_dialog_OK('Software Lists ROM path not set. SL scanning disabled.')
                do_SL_ROM_scan = False
            SL_ROM_dir_FN = FileName(self.settings['SL_rom_path'])
            log_info('_command_setup_plugin() SL ROM dir OP {0}'.format(SL_ROM_dir_FN.getOriginalPath()))
            log_info('_command_setup_plugin() SL ROM dir  P {0}'.format(SL_ROM_dir_FN.getPath()))

            # >> SL CHDs scanning is optional
            scan_SL_CHDs = False
            if self.settings['SL_chd_path']:
                SL_CHD_path_FN = FileName(self.settings['SL_chd_path'])
                if not SL_CHD_path_FN.isdir():
                    kodi_dialog_OK('SL CHD directory does not exist. SL CHD scanning disabled.')
                else:
                    scan_SL_CHDs = True
            else:
                kodi_dialog_OK('SL CHD directory not configured. SL CHD scanning disabled.')
                SL_CHD_path_FN = FileName('')

            # >> Load SL catalog and PClone dictionary
            pdialog_line1 = 'Loading databases ...'
            num_items = 4
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'Software Lists index')
            SL_index_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'Software Lists machines')
            SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
            pDialog.update(int((2*100) / num_items), pdialog_line1, 'Software Lists Parent/Clone dictionary')
            SL_pclone_dic = fs_load_JSON_file(PATHS.SL_PCLONE_DIC_PATH.getPath())
            pDialog.update(int((3*100) / num_items), pdialog_line1, 'History DAT index')
            History_idx_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
            pDialog.update(int((4*100) / num_items), ' ', ' ')
            pDialog.close()

            if do_SL_ROM_scan:
                mame_scan_SL_ROMs(PATHS, control_dic, SL_index_dic, SL_hash_dir_FN,
                                  SL_ROM_dir_FN, scan_SL_CHDs, SL_CHD_path_FN)

            # >> Get assets directory. Abort if not configured/found.
            do_SL_asset_scan = True
            if not self.settings['assets_path']:
                kodi_dialog_OK('Asset directory not configured. Aborting.')
                do_SL_asset_scan = False
            Asset_path_FN = FileName(self.settings['assets_path'])
            if not Asset_path_FN.isdir():
                kodi_dialog_OK('Asset directory does not exist. Aborting.')
                do_SL_asset_scan = False

            if do_SL_asset_scan: 
                mame_scan_SL_assets(PATHS, control_dic, SL_index_dic, SL_pclone_dic, Asset_path_FN)

            # >> Build Software Lists plots
            mame_build_SL_plots(PATHS, SL_index_dic, SL_machines_dic, History_idx_dic, pDialog)

            # >> Save control_dic (has been updated in the SL scanner functions).
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('All ROM/asset scanning finished')

        # --- Build Fanarts ---
        elif menu_item == 4:
            submenu = dialog.select('Build Fanarts',
                                   ['Test MAME Fanart',
                                    'Test Software List item Fanart',
                                    'Build missing MAME Fanarts',
                                    'Rebuild all MAME Fanarts',
                                    'Build missing Software Lists Fanarts',
                                    'Rebuild all Software Lists Fanarts',
                                    ])
            if submenu < 0: return
            # >> Check if Pillow library is available. Abort if not.
            if not PILLOW_AVAILABLE:
                kodi_dialog_OK('Pillow Python library is not available. Aborting Fanart generation.')
                return

            # --- Test MAME Fanart ---
            if submenu == 0:
                Template_FN = AML_ADDON_DIR.pjoin('AML-MAME-Fanart-template.xml')
                Asset_path_FN = AML_ADDON_DIR.pjoin('media/MAME_assets')
                Fanart_FN = PLUGIN_DATA_DIR.pjoin('Fanart_MAME.png')
                log_debug('Testing MAME Fanart generation ...')
                log_debug('Template_FN   "{0}"'.format(Template_FN.getPath()))
                log_debug('Fanart_FN     "{0}"'.format(Fanart_FN.getPath()))
                log_debug('Asset_path_FN "{0}"'.format(Asset_path_FN.getPath()))

                # >> Load Fanart template from XML file
                layout = mame_load_MAME_Fanart_template(Template_FN)
                # log_debug(unicode(layout))
                if not layout:
                    kodi_dialog_OK('Error loading XML MAME Fanart layout.')
                    return
    
                # >> Use hard-coded assets
                m_name = 'dino'
                assets_dic = {
                    m_name : {
                        'title' :      Asset_path_FN.pjoin('dino_title.png').getPath(),
                        'snap' :       Asset_path_FN.pjoin('dino_snap.png').getPath(),
                        'flyer' :      Asset_path_FN.pjoin('dino_flyer.png').getPath(),
                        'cabinet' :    Asset_path_FN.pjoin('dino_cabinet.png').getPath(),
                        'artpreview' : Asset_path_FN.pjoin('dino_artpreview.png').getPath(),
                        'PCB' :        Asset_path_FN.pjoin('dino_PCB.png').getPath(),
                        'clearlogo' :  Asset_path_FN.pjoin('dino_clearlogo.png').getPath(),
                        'cpanel' :     Asset_path_FN.pjoin('dino_cpanel.png').getPath(),
                        'marquee' :    Asset_path_FN.pjoin('dino_marquee.png').getPath(),
                    }
                }
                mame_build_fanart(PATHS, layout, m_name, assets_dic, Fanart_FN, CANVAS_COLOR = (25, 25, 50))

                # >> Display Fanart
                log_debug('Rendering fanart "{0}"'.format(Fanart_FN.getPath()))
                xbmc.executebuiltin('ShowPicture("{0}")'.format(Fanart_FN.getPath()))

            # --- Test SL Fanart ---
            elif submenu == 1:
                Template_FN = AML_ADDON_DIR.pjoin('AML-SL-Fanart-template.xml')
                Fanart_FN = PLUGIN_DATA_DIR.pjoin('Fanart_SL.png')
                Asset_path_FN = AML_ADDON_DIR.pjoin('media/SL_assets')
                log_debug('Testing Software List Fanart generation ...')
                log_debug('Template_FN   "{0}"'.format(Template_FN.getPath()))
                log_debug('Fanart_FN     "{0}"'.format(Fanart_FN.getPath()))
                log_debug('Asset_path_FN "{0}"'.format(Asset_path_FN.getPath()))

                # >> Load Fanart template from XML file
                layout = mame_load_SL_Fanart_template(Template_FN)
                # log_debug(unicode(layout))
                if not layout:
                    kodi_dialog_OK('Error loading XML Software List Fanart layout.')
                    return
    
                # >> Use hard-coded assets
                SL_name = '32x'
                m_name = 'doom'
                assets_dic = {
                    m_name : {
                        'title' :    Asset_path_FN.pjoin('doom_title.png').getPath(),
                        'snap' :     Asset_path_FN.pjoin('doom_snap.png').getPath(),
                        'boxfront' : Asset_path_FN.pjoin('doom_boxfront.png').getPath(),
                    }
                }
                mame_build_SL_fanart(PATHS, layout, SL_name, m_name, assets_dic, Fanart_FN, CANVAS_COLOR = (50, 50, 75))

                # >> Display Fanart
                log_debug('Rendering fanart "{0}"'.format(Fanart_FN.getPath()))
                xbmc.executebuiltin('ShowPicture("{0}")'.format(Fanart_FN.getPath()))

            # --- 2 -> Build missing MAME Fanarts ---
            # --- 3 -> Rebuild all MAME Fanarts ---
            # >> For a complete MAME artwork collection rebuilding all Fanarts will take hours!
            elif submenu == 2 or submenu == 3:
                BUILD_MISSING = True if submenu == 2 else False
                if BUILD_MISSING: log_info('_command_setup_plugin() Building missing Fanarts ...')
                else:             log_info('_command_setup_plugin() Rebuilding all Fanarts ...')

                # >> If artwork directory not configured abort.
                if not self.settings['assets_path']:
                    kodi_dialog_OK('Asset directory not configured. Aborting Fanart generation.')
                    return

                # >> If fanart directory doesn't exist create it.
                Template_FN = AML_ADDON_DIR.pjoin('AML-MAME-Fanart-template.xml')
                Asset_path_FN = FileName(self.settings['assets_path'])
                Fanart_path_FN = Asset_path_FN.pjoin('fanarts')
                if not Fanart_path_FN.isdir():
                    log_info('Creating Fanart dir "{0}"'.format(Fanart_path_FN.getPath()))
                    Fanart_path_FN.makedirs()

                # >> Load Fanart template from XML file
                layout = mame_load_MAME_Fanart_template(Template_FN)
                # log_debug(unicode(layout))
                if not layout:
                    kodi_dialog_OK('Error loading XML MAME Fanart layout.')
                    return

                # >> Load Assets DB
                pDialog_canceled = False
                pDialog = xbmcgui.DialogProgress()
                pDialog.create('Advanced MAME Launcher', 'Loading assets database ... ')
                pDialog.update(0)
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(100)
                pDialog.close()

                # >> Traverse all machines and build fanart from other pieces of artwork
                total_machines = len(assets_dic)
                processed_machines = 0
                pDialog.create('Advanced MAME Launcher', 'Building MAME machine Fanarts ... ')
                for m_name in sorted(assets_dic):
                    pDialog.update((processed_machines * 100) // total_machines)
                    if pDialog.iscanceled():
                        pDialog_canceled = True
                        # kodi_dialog_OK('Fanart generation was cancelled by the user.')
                        break
                    # >> If build missing Fanarts was chosen only build fanart if file cannot
                    # >> be found.
                    Fanart_FN = Fanart_path_FN.pjoin('{0}.png'.format(m_name))
                    if BUILD_MISSING:
                        if Fanart_FN.exists():
                            assets_dic[m_name]['fanart'] = Fanart_FN.getPath()
                        else:
                            mame_build_fanart(PATHS, layout, m_name, assets_dic, Fanart_FN)
                    else:
                        mame_build_fanart(PATHS, layout, m_name, assets_dic, Fanart_FN)
                    processed_machines += 1
                pDialog.update(100)
                pDialog.close()

                # >> Save assets DB
                pDialog.create('Advanced MAME Launcher', 'Saving asset database ... ')
                pDialog.update(0)
                fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
                pDialog.update(100)
                pDialog.close()
                # >> Rebuild asset cache
                cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
                fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)
                if pDialog_canceled: kodi_notify('Fanart building stopped. Partial progress saved.')
                else:                kodi_notify('Fanart building finished')

            # --- 4 -> Missing SL Fanarts ---
            # --- 5 -> Rebuild all SL Fanarts ---
            elif submenu == 4 or submenu == 5:
                BUILD_MISSING = True if submenu == 4 else False
                if BUILD_MISSING: log_info('_command_setup_plugin() Building missing Software Lists Fanarts ...')
                else:             log_info('_command_setup_plugin() Rebuilding all Software Lists Fanarts ...')

                # >> If artwork directory not configured abort.
                if not self.settings['assets_path']:
                    kodi_dialog_OK('Asset directory not configured. Aborting Fanart generation.')
                    return

                # >> Load Fanart template from XML file
                Template_FN = AML_ADDON_DIR.pjoin('AML-SL-Fanart-template.xml')
                layout = mame_load_SL_Fanart_template(Template_FN)
                # log_debug(unicode(layout))
                if not layout:
                    kodi_dialog_OK('Error loading XML Software List Fanart layout.')
                    return

                # >> Load SL index
                SL_index_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())

                # >> Traverse all SL and on each SL every item
                pDialog_canceled = False
                pDialog = xbmcgui.DialogProgress()
                pDialog.create('Advanced MAME Launcher')
                SL_number = len(SL_index_dic)
                SL_count = 1
                for SL_name in sorted(SL_index_dic):
                    # >> Update progres dialog
                    pdialog_line1 = 'Processing SL {0} ({1} of {2})...'.format(SL_name, SL_count, SL_number)
                    pdialog_line2 = ' '
                    pDialog.update(0, pdialog_line1, pdialog_line2)

                    # >> If fanart directory doesn't exist create it.
                    Asset_path_FN = FileName(self.settings['assets_path'])
                    Fanart_path_FN = Asset_path_FN.pjoin('fanarts_SL/{0}'.format(SL_name))
                    if not Fanart_path_FN.isdir():
                        log_info('Creating SL Fanart dir "{0}"'.format(Fanart_path_FN.getPath()))
                        Fanart_path_FN.makedirs()

                    # >> Load Assets DB
                    pdialog_line2 = 'Loading SL asset database ... '
                    pDialog.update(0, pdialog_line1, pdialog_line2)
                    assets_file_name =  SL_index_dic[SL_name]['rom_DB_noext'] + '_assets.json'
                    SL_asset_DB_FN = PATHS.SL_DB_DIR.pjoin(assets_file_name)
                    SL_assets_dic = fs_load_JSON_file(SL_asset_DB_FN.getPath())

                    # >> Traverse all SL items and build fanart from other pieces of artwork
                    total_SL_items = len(SL_assets_dic)
                    processed_SL_items = 0
                    for m_name in sorted(SL_assets_dic):
                        pdialog_line2 = 'SL item {0}'.format(m_name)
                        update_number = (processed_SL_items * 100) // total_SL_items
                        pDialog.update(update_number, pdialog_line1, pdialog_line2)
                        if pDialog.iscanceled():
                            pDialog_canceled = True
                            # kodi_dialog_OK('SL Fanart generation was cancelled by the user.')
                            break
                        # >> If build missing Fanarts was chosen only build fanart if file cannot
                        # >> be found.
                        Fanart_FN = Fanart_path_FN.pjoin('{0}.png'.format(m_name))
                        if BUILD_MISSING:
                            if Fanart_FN.exists():
                                SL_assets_dic[m_name]['fanart'] = Fanart_FN.getPath()
                            else:
                                mame_build_SL_fanart(PATHS, layout, SL_name, m_name, SL_assets_dic, Fanart_FN)
                        else:
                            mame_build_SL_fanart(PATHS, layout, SL_name, m_name, SL_assets_dic, Fanart_FN)
                        processed_SL_items += 1

                    # >> Save assets DB
                    pdialog_line2 = 'Saving SL {0} asset database ... '.format(SL_name)
                    pDialog.update(100, pdialog_line1, pdialog_line2)
                    fs_write_JSON_file(SL_asset_DB_FN.getPath(), SL_assets_dic)

                    # >> Update progress
                    SL_count += 1
                    if pDialog_canceled: break
                pDialog.close()
                if pDialog_canceled: kodi_notify('SL Fanart building stopped. Partial progress saved.')
                else:                kodi_notify('SL Fanart building finished')

        # --- Audit MAME machine ROMs/CHDs ---
        # NOTE It is likekely that this function will take a looong time. It is important that the
        #      audit process can be canceled and a partial report is written.
        elif menu_item == 5:
            log_info('_command_setup_plugin() Audit MAME machines ROMs/CHDs ...')

            # --- Load machines, ROMs and CHDs databases ---
            pDialog = xbmcgui.DialogProgress()
            pdialog_line1 = 'Loading databases ...'
            num_items = 4
            pDialog.create('Advanced MAME Launcher')
            pDialog.update(int((0*100) / num_items), pdialog_line1, 'Control dic')
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machines Main')
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            pDialog.update(int((2*100) / num_items), pdialog_line1, 'MAME machines Render')
            machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
            pDialog.update(int((3*100) / num_items), pdialog_line1, 'MAME ROM Audit')
            audit_roms_dic = fs_load_JSON_file(PATHS.ROM_AUDIT_DB_PATH.getPath())
            pDialog.update(int((4*100) / num_items), ' ', ' ')
            pDialog.close()

            # --- Audit all MAME machines ---
            # 1) Updates control_dic statistics.
            mame_audit_MAME_all(PATHS, pDialog, self.settings, control_dic,
                                machines, machines_render, audit_roms_dic)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('ROM and CHD audit finished')

        # --- Audit SL ROMs/CHDs ---
        elif menu_item == 6:
            log_info('_command_setup_plugin() Audit SL ROMs/CHDs ...')

            # --- Load stuff ---
            control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())

            # --- Audit all Software List items ---
            # 1) Updates control_dic statistics.
            mame_audit_SL_all(PATHS, self.settings, control_dic)
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('Software Lists audit finished')

        # --- Build Step by Step ---
        elif menu_item == 7:
            submenu = dialog.select('Setup plugin (step by step)',
                                   ['Build MAME databases ...',
                                    'Build Audit/Scanner databases ...',
                                    'Build MAME catalogs ...',
                                    'Build Software Lists databases ...',
                                    'Scan MAME ROMs/CHDs/Samples ...',
                                    'Scan MAME assets/artwork ...',
                                    'Scan Software Lists ROMs/CHDs ...',
                                    'Scan Software Lists assets/artwork ...',
                                    'Build MAME machines plot',
                                    'Buils Software List items plot'])
            if submenu < 0: return

            # --- Build main MAME database, PClone list and hashed database ---
            if submenu == 0:
                # --- Error checks ---
                # >> Check that MAME_XML_PATH exists
                if not PATHS.MAME_XML_PATH.exists():
                    kodi_dialog_OK('MAME XML not found. Execute "Extract MAME.xml" first.')
                    return

                # --- Parse MAME XML and generate main database and PClone list ---
                log_info('_command_setup_plugin() Generating MAME main database and PClone list ...')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                # 1) Builds the ROM hashed database.
                # 2) Updates control_dic stats and timestamp.
                # try:
                #     DB = mame_build_MAME_main_database(PATHS, self.settings, control_dic)
                # except GeneralError as err:
                #     log_error(err.msg)
                #     raise SystemExit
                DB = mame_build_MAME_main_database(PATHS, self.settings, control_dic)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                kodi_notify('Main MAME databases built')

            # --- Build ROM audit/scanner databases ---
            elif submenu == 1:
                log_info('_command_setup_plugin() Generating ROM audit/scanner databases ...')
                # --- Error checks ---
                # >> Check that MAME_XML_PATH exists
                # if not PATHS.MAME_XML_PATH.exists():
                #     kodi_dialog_OK('MAME XML not found. Execute "Extract MAME.xml" first.')
                #     return

                # --- Load databases ---
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 5
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machines Main')
                machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), line1_str, 'MAME machine Devices')
                devices_db_dic = fs_load_JSON_file(PATHS.DEVICES_DB_PATH.getPath())
                pDialog.update(int((4*100) / num_items), line1_str, 'MAME machine ROMs')
                machine_roms = fs_load_JSON_file(PATHS.ROMS_DB_PATH.getPath())
                # >> Kodi BUG: when the progress dialog is closed and reopened again, the
                # >> second line of the previous dialog is not deleted (still printed).
                pDialog.update(int((5*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Generate ROM databases ---
                # 1) Updates control_dic and t_MAME_Audit_DB_build timestamp.
                mame_build_ROM_audit_databases(PATHS, self.settings, control_dic,
                                               machines, machines_render, devices_db_dic,
                                               machine_roms)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                kodi_notify('ROM audit/scanner databases built')

            # --- Build MAME catalogs ---
            elif submenu == 2:
                log_info('_command_setup_plugin() Building MAME catalogs ...')
                # --- Error checks ---
                # >> Check that main MAME database exists

                # --- Load databases ---
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 6
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machines Main')
                machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), line1_str, 'MAME machine ROMs')
                machine_roms = fs_load_JSON_file(PATHS.ROMS_DB_PATH.getPath())
                pDialog.update(int((4*100) / num_items), line1_str, 'MAME PClone dictionary')
                main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
                pDialog.update(int((5*100) / num_items), line1_str, 'MAME machine Assets')
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(int((6*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Build MAME catalog ---
                # >> At this time the asset database will be empty (scanner has not been run). However, 
                # >> the asset cache with an empty database is required to render the machines in the catalogs.
                # 1) Creates cache_index_dic and SAVES it.
                # 2) Requires rebuilding of the ROM cache.
                # 3) Requires rebuilding of the asset cache.
                # 4) Updates control_dic and t_MAME_Catalog_build timestamp.
                mame_build_MAME_catalogs(PATHS, self.settings, control_dic,
                                         machines, machines_render, machine_roms,
                                         main_pclone_dic, assets_dic)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
                fs_build_ROM_cache(PATHS, machines, machines_render, cache_index_dic, pDialog)
                fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)
                kodi_notify('MAME Catalogs built')

            # --- Build Software Lists ROM/CHD databases, SL indices and SL catalogs ---
            elif submenu == 3:
                # --- Error checks ---
                if not self.settings['SL_hash_path']:
                    kodi_dialog_OK('Software Lists hash path not set.')
                    return

                # --- Read main database and control dic ---
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 3
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machines Main')
                machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Build SL databases ---
                mame_build_SoftwareLists_databases(PATHS, self.settings, control_dic,
                                                   machines, machines_render)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                kodi_notify('Software Lists database built')

            # --- Scan ROMs/CHDs/Samples and updates ROM status ---
            elif submenu == 4:
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
                    CHD_path_FN = FileName('')

                scan_Samples = False
                if self.settings['samples_path']:
                    Samples_path_FN = FileName(self.settings['samples_path'])
                    if not Samples_path_FN.isdir():
                        kodi_dialog_OK('Samples directory does not exist. Samples scanning disabled.')
                    else:
                        scan_Samples = True
                else:
                    kodi_dialog_OK('Samples directory not configured. Samples scanning disabled.')
                    Samples_path_FN = FileName('')

                # >> Load machine database and control_dic and scan
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 7
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machines Main')
                machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), line1_str, 'MAME machine Assets')
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(int((4*100) / num_items), line1_str, 'Machine archives list')
                machine_archives_dic = fs_load_JSON_file(PATHS.ROM_SET_MACHINE_ARCHIVES_DB_PATH.getPath())
                pDialog.update(int((5*100) / num_items), line1_str, 'ROM List index')
                ROM_archive_list = fs_load_JSON_file(PATHS.ROM_SET_ROM_ARCHIVES_DB_PATH.getPath())
                pDialog.update(int((6*100) / num_items), line1_str, 'CHD list index')
                CHD_archive_list = fs_load_JSON_file(PATHS.ROM_SET_CHD_ARCHIVES_DB_PATH.getPath())
                pDialog.update(int((7*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Scan MAME ROMs/CHDs/Samples ---
                # 1) Updates 'flags' field in assets_dic
                # 2) Updates timestamp t_MAME_ROM_scan in control_dic
                # 3) Requires rebuilding of the asset cache.
                mame_scan_MAME_ROMs(PATHS, self.settings, control_dic,
                                    machines, machines_render, assets_dic,
                                    machine_archives_dic, ROM_archive_list, CHD_archive_list,
                                    ROM_path_FN, CHD_path_FN, Samples_path_FN,
                                    scan_CHDs, scan_Samples)

                # >> Save databases
                line1_str = 'Saving databases ...'
                num_items = 2
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machine Assets')
                fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
                pDialog.update(int((2*100) / num_items), ' ', ' ')
                pDialog.close()

                # >> assets_dic has changed. Update asset cache.
                cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
                fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)
                kodi_notify('Scanning of ROMs, CHDs and Samples finished')

            # --- Scans MAME assets/artwork ---
            elif submenu == 5:
                log_info('_command_setup_plugin() Scanning MAME assets/artwork ...')

                # >> Get assets directory. Abort if not configured/found.
                if not self.settings['assets_path']:
                    kodi_dialog_OK('Asset directory not configured. Aborting.')
                    return
                Asset_path_FN = FileName(self.settings['assets_path'])
                if not Asset_path_FN.isdir():
                    kodi_dialog_OK('Asset directory does not exist. Aborting.')
                    return

                # >> Load machine database and scan
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ... '
                num_items = 4
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'MAME machine Assets')
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), line1_str, 'MAME PClone dictionary')
                main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
                pDialog.update(int((4*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Scan MAME assets ---
                # 1) Mutates assets_dic and control_dic (timestamp and stats)
                # 2) Requires rebuilding of the asset cache.
                mame_scan_MAME_assets(PATHS, assets_dic, control_dic, pDialog,
                                      machines_render, main_pclone_dic, Asset_path_FN)

                # >> Save asset DB and control dic
                line1_str = 'Saving databases ...'
                num_items = 2
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                pDialog.update(int((1*100) / num_items), line1_str, 'MAME machine Assets')
                fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
                pDialog.update(int((2*100) / num_items), ' ', ' ')
                pDialog.close()

                # >> Asset cache must be regenerated.
                cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
                fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)
                kodi_notify('Scanning of assets/artwork finished')

            # --- Scan SL ROMs/CHDs ---
            elif submenu == 6:
                log_info('_command_setup_plugin() Scanning SL ROMs/CHDs ...')

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

                # >> SL CHDs scanning is optional
                scan_SL_CHDs = False
                if self.settings['SL_chd_path']:
                    SL_CHD_path_FN = FileName(self.settings['SL_chd_path'])
                    if not SL_CHD_path_FN.isdir():
                        kodi_dialog_OK('SL CHD directory does not exist. SL CHD scanning disabled.')
                    else:
                        scan_SL_CHDs = True
                else:
                    kodi_dialog_OK('SL CHD directory not configured. SL CHD scanning disabled.')
                    SL_CHD_path_FN = FileName('')

                # >> Load SL and scan ROMs/CHDs. fs_scan_SL_ROMs() updates each SL database.
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 2
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'Software Lists index')
                SL_index_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                pDialog.update(int((2*100) / num_items), ' ', ' ')
                pDialog.close()

                # 1) Mutates control_dic (timestamp and statistics)
                mame_scan_SL_ROMs(PATHS, control_dic, SL_index_dic, SL_hash_dir_FN,
                                  SL_ROM_dir_FN, scan_SL_CHDs, SL_CHD_path_FN)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                kodi_notify('Scanning of SL ROMs finished')

            # --- Scan SL assets/artwork ---
            # >> Database format: ADDON_DATA_DIR/db_SoftwareLists/32x_assets.json
            # >> { 'ROM_name' : {'asset1' : 'path', 'asset2' : 'path', ... }, ... }
            elif submenu == 7:
                log_info('_command_setup_plugin() Scanning SL assets/artwork ...')

                # >> Get assets directory. Abort if not configured/found.
                if not self.settings['assets_path']:
                    kodi_dialog_OK('Asset directory not configured. Aborting.')
                    return
                Asset_path_FN = FileName(self.settings['assets_path'])
                if not Asset_path_FN.isdir():
                    kodi_dialog_OK('Asset directory does not exist. Aborting.')
                    return

                # >> Load SL database and scan
                pDialog = xbmcgui.DialogProgress()
                line1_str = 'Loading databases ...'
                num_items = 3
                pDialog.create('Advanced MAME Launcher', line1_str)
                pDialog.update(int((0*100) / num_items), line1_str, 'Control dictionary')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), line1_str, 'Software Lists index')
                SL_index_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                pDialog.update(int((2*100) / num_items), line1_str, 'Software Lists Parent/Clone dictionary')
                SL_pclone_dic = fs_load_JSON_file(PATHS.SL_PCLONE_DIC_PATH.getPath())
                pDialog.update(int((3*100) / num_items), ' ', ' ')
                pDialog.close()

                # 1) Mutates control_dic (timestamp and statistics)
                mame_scan_SL_assets(PATHS, control_dic, SL_index_dic, SL_pclone_dic, Asset_path_FN)
                fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
                kodi_notify('Scanning of SL assets finished')

            # --- Build MAME machines plot ---
            elif submenu == 8:
                # >> Load machine database and control_dic
                pDialog = xbmcgui.DialogProgress()
                pdialog_line1 = 'Loading databases ...'
                num_items = 8
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), pdialog_line1, 'Control dic')
                control_dic = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
                pDialog.update(int((1*100) / num_items), pdialog_line1, 'MAME machines Main')
                machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
                pDialog.update(int((2*100) / num_items), pdialog_line1, 'MAME machines Render')
                machines_render = fs_load_JSON_file(PATHS.RENDER_DB_PATH.getPath())
                pDialog.update(int((3*100) / num_items), pdialog_line1, 'MAME machine Assets')
                assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
                pDialog.update(int((4*100) / num_items), pdialog_line1, 'History DAT')
                history_idx_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
                pDialog.update(int((5*100) / num_items), pdialog_line1, 'Mameinfo DAT')
                mameinfo_idx_dic = fs_load_JSON_file(PATHS.MAMEINFO_IDX_PATH.getPath())
                pDialog.update(int((6*100) / num_items), pdialog_line1, 'Gameinit DAT')
                gameinit_idx_list = fs_load_JSON_file(PATHS.GAMEINIT_IDX_PATH.getPath())
                pDialog.update(int((7*100) / num_items), pdialog_line1, 'Command DAT')
                command_idx_list = fs_load_JSON_file(PATHS.COMMAND_IDX_PATH.getPath())
                pDialog.update(int((8*100) / num_items), ' ', ' ')
                pDialog.close()

                # --- Traverse MAME machines and build plot ---
                # 1) Mutates assets_dic
                # 2) Requires rebuilding of the asset cache.
                mame_build_MAME_plots(machines, machines_render, assets_dic, pDialog,
                                      history_idx_dic, mameinfo_idx_dic,
                                      gameinit_idx_list, command_idx_list)

                # >> Update hashed DBs and save DBs
                # >> cache_index_dic built in fs_build_MAME_catalogs()
                pdialog_line1 = 'Saving databases ...'
                num_items = 1
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), pdialog_line1, 'MAME machine Assets')
                fs_write_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath(), assets_dic)
                pDialog.update(int((1*100) / num_items), ' ', ' ')
                pDialog.close()

                # >> Asset cache must be regenerated.
                cache_index_dic = fs_load_JSON_file(PATHS.CACHE_INDEX_PATH.getPath())
                fs_build_asset_cache(PATHS, assets_dic, cache_index_dic, pDialog)
                kodi_notify('MAME machines plot generation finished')

            # --- Buils Software List items plot ---
            elif submenu == 9:
                # >> Load SL index and SL machine index.
                pDialog = xbmcgui.DialogProgress()
                pdialog_line1 = 'Loading databases ...'
                num_items = 3
                pDialog.create('Advanced MAME Launcher')
                pDialog.update(int((0*100) / num_items), pdialog_line1, 'Software Lists index')
                SL_index_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
                pDialog.update(int((1*100) / num_items), pdialog_line1, 'Software Lists machines')
                SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
                pDialog.update(int((2*100) / num_items), pdialog_line1, 'History DAT index')
                History_idx_dic = fs_load_JSON_file(PATHS.HISTORY_IDX_PATH.getPath())
                pDialog.update(int((3*100) / num_items), ' ', ' ')
                pDialog.close()

                mame_build_SL_plots(PATHS, SL_index_dic, SL_machines_dic, History_idx_dic, pDialog)
                kodi_notify('SL item plot generation finished')

    #
    # Launch MAME machine. Syntax: $ mame <machine_name> [options]
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
        # Not implemented at the moment
        # if location and location == 'MAME_FAV' and len(machine['bios_name']) > 1:
        #     dialog = xbmcgui.Dialog()
        #     m_index = dialog.select('Select BIOS', machine['bios_desc'])
        #     if m_index < 0: return
        #     BIOS_name = machine['bios_name'][m_index]
        # else:
        #     BIOS_name = ''
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

        # --- User notification ---
        if self.settings['display_launcher_notify']:
            kodi_notify('Launching MAME machine "{0}"'.format(machine_name))

        # --- Launch MAME and run machine ---
        # arg_list = [mame_prog_FN.getPath(), '-window', machine_name]
        if BIOS_name: arg_list = [mame_prog_FN.getPath(), machine_name, '-bios', BIOS_name]
        else:         arg_list = [mame_prog_FN.getPath(), machine_name]
        log_info('arg_list = {0}'.format(arg_list))
        log_info('_run_machine() Calling subprocess.Popen()...')
        with open(PATHS.MAME_OUTPUT_PATH.getPath(), 'wb') as f:
            p = subprocess.Popen(arg_list, cwd = mame_dir, startupinfo = _info, stdout = f, stderr = subprocess.STDOUT)
        p.wait()
        log_info('_run_machine() Exiting function')

    #
    # Launch a SL machine. See http://docs.mamedev.org/usingmame/usingmame.html
    # Complex syntax: $ mame <system> <media> <software> [options]
    # Easy syntax: $ mame <system> <software> [options]
    # Valid example: $ mame smspal -cart sonic
    #
    # Software list <part> tag has an 'interface' attribute that tells how to virtually plug the
    # cartridge/cassete/disk/etc. into the MAME <device> with same 'interface' attribute. The
    # <media> argument in the command line is the <device> <instance> 'name' attribute.
    #
    # Launching cases:
    #   A) Machine has only one device (defined by a <device> tag) with a valid <instance> and
    #      SL ROM has only one part (defined by a <part> tag).
    #      Valid examples:$ mame smspal -cart sonic
    #      Launch as: $ mame machine_name -part_attrib_name SL_ROM_name
    #
    # <device type="cartridge" tag="slot" interface="sms_cart">
    #   <instance name="cartridge" briefname="cart"/>
    #   <extension name="bin"/>
    #   <extension name="sms"/>
    # </device>
    # <software name="sonic">
    #   <part name="cart" interface="sms_cart">
    #     <!-- PCB info based on SMS Power -->
    #     <feature name="pcb" value="171-5507" />
    #     <feature name="ic1" value="MPR-14271-F" />
    #     <dataarea name="rom" size="262144">
    #       <rom name="mpr-14271-f.ic1" size="262144" crc="b519e833" sha1="6b9..." offset="000000" />
    #     </dataarea>
    #   </part>
    # </software>
    #
    #   B) Machine has only one device with a valid <instance> and SL ROM has multiple parts.
    #      In this case, user should choose which part to plug.
    #      Currently not implemented and launch using easy syntax.
    #      Valid examples: 
    #      Launch as: $ mame machine_name -part_attrib_name SL_ROM_name
    #
    #   C) Machine has two or more devices with a valid <instance> and SL ROM has only one part.
    #      Traverse the machine devices until there is a match of the <part> interface attribute 
    #      with the <machine> interface attribute. After the match is found, check also that
    #      SL ROM <part> name attribute matches with machine <device> <intance> briefname attribute.
    #      Valid examples:
    #        MSX2 cartridge vampkill (in msx2_cart.xml) with MSX machine.
    #        vampkill is also in msx_flop SL.xml. MSX2 machines always have two or more interfaces.
    #        $ mame hbf700p -cart vampkill
    #      Launch as: $ mame machine_name -part_attrib_name SL_ROM_name
    #
    #   D) Machine has two or more devices with a valid <instance> and SL ROM has two or more parts.
    #      In this case it is not clear how to launch the machine.
    #      Not implemented and launch using easy syntax.
    #
    # Most common cases are A) and C).
    #
    def _run_SL_machine(self, SL_name, ROM_name, location):
        SL_LAUNCH_WITH_MEDIA = 100
        SL_LAUNCH_NO_MEDIA   = 200
        log_info('_run_SL_machine() Launching SL machine (location = {0}) ...'.format(location))
        log_info('_run_SL_machine() SL_name  "{0}"'.format(SL_name))
        log_info('_run_SL_machine() ROM_name "{0}"'.format(ROM_name))

        # --- Get paths ---
        mame_prog_FN = FileName(self.settings['mame_prog'])

        # --- Get a list of machine <devices> and SL ROM <parts>
        if location == LOCATION_SL_FAVS:
            log_info('_run_SL_machine() SL ROM is in Favourites')
            fav_SL_roms = fs_load_JSON_file(PATHS.FAV_SL_ROMS_PATH.getPath())
            SL_fav_key = SL_name + '-' + ROM_name
            machine_name = fav_SL_roms[SL_fav_key]['launch_machine']
            machine_desc = '[ Not available ]'
            log_info('_run_SL_machine() launch_machine = "{0}"'.format(machine_name))
        else:
            machine_name = ''
            machine_desc = ''

        # --- Load SL machines ---
        SL_machines_dic = fs_load_JSON_file(PATHS.SL_MACHINES_PATH.getPath())
        SL_machine_list = SL_machines_dic[SL_name]
        if not machine_name:
            # >> Get a list of machines that can launch this SL ROM. User chooses in a select dialog
            log_info('_run_SL_machine() User selecting SL run machine ...')
            SL_machine_names_list = []
            SL_machine_desc_list  = []
            SL_machine_devices    = []
            for SL_machine in sorted(SL_machine_list):
                SL_machine_names_list.append(SL_machine['machine'])
                SL_machine_desc_list.append(SL_machine['description'])
                SL_machine_devices.append(SL_machine['devices'])
            m_index = xbmcgui.Dialog().select('Select machine', SL_machine_desc_list)
            if m_index < 0: return
            machine_name    = SL_machine_names_list[m_index]
            machine_desc    = SL_machine_desc_list[m_index]
            machine_devices = SL_machine_devices[m_index]
            log_info('_run_SL_machine() User chose machine "{0}" ({1})'.format(machine_name, machine_desc))
        else:
            # >> User configured a machine to launch this SL item. Find the machine in the machine list.
            log_info('_run_SL_machine() Searching configured SL item running machine ...')
            machine_found = False
            for SL_machine in SL_machine_list:
                if SL_machine['machine'] == machine_name:
                    selected_SL_machine = SL_machine
                    machine_found = True
                    break
            if machine_found:
                log_info('_run_SL_machine() Found machine "{0}"'.format(machine_name))
                machine_desc    = SL_machine['description']
                machine_devices = SL_machine['devices']
            else:
                log_error('_run_SL_machine() Machine "{0}" not found'.format(machine_name))
                log_error('_run_SL_machine() Aborting launch')
                kodi_dialog_OK('Machine "{0}" not found. Aborting launch.'.format(machine_name))
                return

        # --- Get SL ROM list of <part> tags ---
        if location == LOCATION_SL_FAVS:
            part_list = fav_SL_roms[SL_fav_key]['parts']
        else:
            # >> Open SL ROM database and get information
            SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())
            file_name =  SL_catalog_dic[SL_name]['rom_DB_noext'] + '.json'
            SL_DB_FN = PATHS.SL_DB_DIR.pjoin(file_name)
            log_info('_run_SL_machine() SL ROMs JSON "{0}"'.format(SL_DB_FN.getPath()))
            SL_roms = fs_load_JSON_file(SL_DB_FN.getPath())
            SL_rom = SL_roms[ROM_name]
            part_list = SL_rom['parts']

        # --- DEBUG ---
        log_info('_run_SL_machine() Machine "{0}" has {1} interfaces'.format(machine_name, len(machine_devices)))
        log_info('_run_SL_machine() SL ROM  "{0}" has {1} parts'.format(ROM_name, len(part_list)))
        for device_dic in machine_devices:
            u = '<device type="{1}" interface="{0}">'.format(device_dic['att_type'], device_dic['att_interface'])
            log_info(u)
        for part_dic in part_list:
            u = '<part name="{1}" interface="{0}">'.format(part_dic['name'], part_dic['interface'])
            log_info(u)

        # --- Select media depending on SL launching case ---
        num_machine_interfaces = len(machine_devices)
        num_SL_ROM_parts = len(part_list)

        # >> Error
        if num_machine_interfaces == 0:
            kodi_dialog_OK('Machine has no inferfaces! Aborting launch.')
            return
        if num_SL_ROM_parts == 0:
            kodi_dialog_OK('SL ROM has no parts! Aborting launch.')
            return

        # >> Case A
        elif num_machine_interfaces == 1 and num_SL_ROM_parts == 1:
            log_info('_run_SL_machine() Launch case A)')
            launch_case = SL_LAUNCH_CASE_A
            media_name = machine_devices[0]['instance']['name']
            sl_launch_mode = SL_LAUNCH_WITH_MEDIA

        # >> Case B
        #    User chooses media to launch?
        elif num_machine_interfaces == 1 and num_SL_ROM_parts > 1:
            log_info('_run_SL_machine() Launch case B)')
            launch_case = SL_LAUNCH_CASE_B
            media_name = ''
            sl_launch_mode = SL_LAUNCH_NO_MEDIA

        # >> Case C
        elif num_machine_interfaces > 1 and num_SL_ROM_parts == 1:
            log_info('_run_SL_machine() Launch case C)')
            launch_case = SL_LAUNCH_CASE_C
            m_interface_found = False
            for device in machine_devices:
                if device['att_interface'] == part_list[0]['interface']:
                    media_name = device['instance']['name']
                    m_interface_found = True
                    break
            if not m_interface_found:
                kodi_dialog_OK('SL launch case C), not machine interface found! Aborting launch.')
                return
            log_info('_run_SL_machine() Matched machine device interface "{0}" '.format(device['att_interface']) +
                     'to SL ROM part "{0}"'.format(part_list[0]['interface']))
            sl_launch_mode = SL_LAUNCH_WITH_MEDIA

        # >> Case D.
        # >> User chooses media to launch?
        elif num_machine_interfaces > 1 and num_SL_ROM_parts > 1:
            log_info('_run_SL_machine() Launch case D)')
            launch_case = SL_LAUNCH_CASE_D
            media_name = ''
            sl_launch_mode = SL_LAUNCH_NO_MEDIA

        else:
            log_info(unicode(machine_interfaces))
            log_warning('_run_SL_machine() Logical error in SL launch case.')
            launch_case = SL_LAUNCH_CASE_ERROR
            kodi_dialog_OK('Logical error in SL launch case. This is a bug, please report it.')
            media_name = ''
            sl_launch_mode = SL_LAUNCH_NO_MEDIA

        # >> Display some DEBUG information.
        kodi_dialog_OK('Launch case {0}. '.format(launch_case) +
                       'Machine has {0} device interfaces and '.format(num_machine_interfaces) +
                       'SL ROM has {0} parts. '.format(num_SL_ROM_parts) + 
                       'Media name is "{0}"'.format(media_name))

        # >> Launch machine using subprocess module
        (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
        log_info('_run_SL_machine() mame_prog_FN "{0}"'.format(mame_prog_FN.getPath()))    
        log_info('_run_SL_machine() mame_dir     "{0}"'.format(mame_dir))
        log_info('_run_SL_machine() mame_exec    "{0}"'.format(mame_exec))
        log_info('_run_SL_machine() machine_name "{0}"'.format(machine_name))
        log_info('_run_SL_machine() machine_desc "{0}"'.format(machine_desc))
        log_info('_run_SL_machine() media_name   "{0}"'.format(media_name))

        # >> Build MAME arguments
        if sl_launch_mode == SL_LAUNCH_WITH_MEDIA:
            arg_list = [mame_prog_FN.getPath(), machine_name, '-{0}'.format(media_name), ROM_name]
        elif sl_launch_mode == SL_LAUNCH_NO_MEDIA:
            arg_list = [mame_prog_FN.getPath(), machine_name, '{0}:{1}'.format(SL_name, ROM_name)]
        else:
            kodi_dialog_OK('Unknown sl_launch_mode = {0}. This is a bug, please report it.'.format(sl_launch_mode))
            return
        log_info('arg_list = {0}'.format(arg_list))

        # >> Prevent a console window to be shown in Windows. Not working yet!
        if sys.platform == 'win32':
            log_info('_run_SL_machine() Platform is win32. Creating _info structure')
            _info = subprocess.STARTUPINFO()
            _info.dwFlags = subprocess.STARTF_USESHOWWINDOW
            _info.wShowWindow = 1
        else:
            log_info('_run_SL_machine() _info is None')
            _info = None

        # --- User notification ---
        if self.settings['display_launcher_notify']:
            kodi_notify('Launching MAME SL item "{0}"'.format(ROM_name))

        # --- Launch MAME ---
        log_info('_run_SL_machine() Calling subprocess.Popen()...')
        with open(PATHS.MAME_OUTPUT_PATH.getPath(), 'wb') as f:
            p = subprocess.Popen(arg_list, cwd = mame_dir, startupinfo = _info, stdout = f, stderr = subprocess.STDOUT)
        p.wait()
        log_info('_run_SL_machine() Exiting function')

    # ---------------------------------------------------------------------------------------------
    # Misc functions
    # ---------------------------------------------------------------------------------------------
    def _display_text_window(self, window_title, info_text):
        xbmcgui.Window(10000).setProperty('FontWidth', 'monospaced')
        dialog = xbmcgui.Dialog()
        dialog.textviewer(window_title, info_text)
        xbmcgui.Window(10000).setProperty('FontWidth', 'proportional')

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

    def _misc_url_3_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                              arg_name_3, arg_value_3):
        arg_value_1_escaped = arg_value_1.replace('&', '%26')
        arg_value_2_escaped = arg_value_2.replace('&', '%26')
        arg_value_3_escaped = arg_value_3.replace('&', '%26')

        return '{0}?{1}={2}&{3}={4}&{5}={6}'.format(self.base_url,
                                                    arg_name_1, arg_value_1_escaped,
                                                    arg_name_2, arg_value_2_escaped,
                                                    arg_name_3, arg_value_3_escaped)

    def _misc_url_4_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, 
                              arg_name_3, arg_value_3, arg_name_4, arg_value_4):
        arg_value_1_escaped = arg_value_1.replace('&', '%26')
        arg_value_2_escaped = arg_value_2.replace('&', '%26')
        arg_value_3_escaped = arg_value_3.replace('&', '%26')
        arg_value_4_escaped = arg_value_4.replace('&', '%26')

        return '{0}?{1}={2}&{3}={4}&{5}={6}&{7}={8}'.format(self.base_url,
                                                            arg_name_1, arg_value_1_escaped,
                                                            arg_name_2, arg_value_2_escaped,
                                                            arg_name_3, arg_value_3_escaped,
                                                            arg_name_4, arg_value_4_escaped)

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
