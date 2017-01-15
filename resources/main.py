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
        self.MACHINES_IDX_CHD_PATH       = PLUGIN_DATA_DIR.pjoin('idx_Machines_CHD.json')
        self.MACHINES_IDX_SAMPLES_PATH   = PLUGIN_DATA_DIR.pjoin('idx_Machines_Samples.json')
        self.MACHINES_IDX_BIOS_PATH      = PLUGIN_DATA_DIR.pjoin('idx_Machines_BIOS.json')
        self.MACHINES_IDX_DEVICES_PATH   = PLUGIN_DATA_DIR.pjoin('idx_Machines_Devices.json')

        # >> Catalogs
        self.CATALOG_CATVER_PATH         = PLUGIN_DATA_DIR.pjoin('catalog_catver.json')
        self.CATALOG_CATLIST_PATH        = PLUGIN_DATA_DIR.pjoin('catalog_catlist.json')
        self.CATALOG_GENRE_PATH          = PLUGIN_DATA_DIR.pjoin('catalog_genre.json')
        self.CATALOG_MANUFACTURER_PATH   = PLUGIN_DATA_DIR.pjoin('catalog_manufacturer.json')
        self.CATALOG_YEAR_PATH           = PLUGIN_DATA_DIR.pjoin('catalog_year.json')
        self.CATALOG_DRIVER_PATH         = PLUGIN_DATA_DIR.pjoin('catalog_driver.json')
        self.CATALOG_CONTROL_PATH        = PLUGIN_DATA_DIR.pjoin('catalog_control.json')
        self.CATALOG_DISPLAY_TAG_PATH    = PLUGIN_DATA_DIR.pjoin('catalog_display_tag.json')
        self.CATALOG_DISPLAY_TYPE_PATH   = PLUGIN_DATA_DIR.pjoin('catalog_display_type.json')
        self.CATALOG_DISPLAY_ROTATE_PATH = PLUGIN_DATA_DIR.pjoin('catalog_display_rotate.json')
        self.CATALOG_SL_PATH             = PLUGIN_DATA_DIR.pjoin('catalog_SL.json')

        # >> Software Lists
        self.SL_DB_DIR                   = PLUGIN_DATA_DIR.pjoin('db_SoftwareLists')        
        self.SL_INDEX_PATH               = PLUGIN_DATA_DIR.pjoin('SoftwareLists_index.json')
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
        if 'list' in args:
            list_name = args['list'][0]
            if 'parent' in args:
                parent_name = args['parent'][0]
                if list_name == 'Machines':     self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'NoCoin':     self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'Mechanical': self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'Dead':       self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'CHD':        self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'Samples':    self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'BIOS':       self._render_machine_clone_list(list_name, parent_name)
                elif list_name == 'Devices':    self._render_machine_clone_list(list_name, parent_name)
            else:
                if list_name == 'Machines':     self._render_machine_parent_list(list_name)
                elif list_name == 'NoCoin':     self._render_machine_parent_list(list_name)
                elif list_name == 'Mechanical': self._render_machine_parent_list(list_name)
                elif list_name == 'Dead':       self._render_machine_parent_list(list_name)
                elif list_name == 'CHD':        self._render_machine_parent_list(list_name)
                elif list_name == 'Samples':    self._render_machine_parent_list(list_name)
                elif list_name == 'BIOS':       self._render_machine_parent_list(list_name)
                elif list_name == 'Devices':    self._render_machine_parent_list(list_name)

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
                machine_name = args['machine_name'][0]
                log_info('Launching MAME machine "{0}"'.format(machine_name))
                self._run_machine(machine_name)
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
        self.settings['rom_path']     = __addon_obj__.getSetting('rom_path').decode('utf-8')

        self.settings['assets_path']  = __addon_obj__.getSetting('assets_path').decode('utf-8')        
        self.settings['SL_hash_path'] = __addon_obj__.getSetting('SL_hash_path').decode('utf-8')
        self.settings['SL_rom_path']  = __addon_obj__.getSetting('SL_rom_path').decode('utf-8')
        self.settings['chd_path']     = __addon_obj__.getSetting('chd_path').decode('utf-8')
        self.settings['samples_path'] = __addon_obj__.getSetting('samples_path').decode('utf-8')
        self.settings['catver_path']  = __addon_obj__.getSetting('catver_path').decode('utf-8')
        self.settings['catlist_path'] = __addon_obj__.getSetting('catlist_path').decode('utf-8')
        self.settings['genre_path']   = __addon_obj__.getSetting('genre_path').decode('utf-8')

        # --- Display ---

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
    # NOTE Devices are excluded from main PClone list.
    def _render_root_list(self):
        # >> Code Machines/Manufacturer/SF first. Rest are variations of those three.
        self._render_root_list_row('Machines (with coin slot)',      self._misc_url_1_arg('list',  'Machines'))
        self._render_root_list_row('Machines (no coin slot)',        self._misc_url_1_arg('list',  'NoCoin'))
        self._render_root_list_row('Machines (mechanical)',          self._misc_url_1_arg('list',  'Mechanical'))
        self._render_root_list_row('Machines (dead)',                self._misc_url_1_arg('list',  'Dead'))
        self._render_root_list_row('Machines [with CHDs]',           self._misc_url_1_arg('list',  'CHD'))
        self._render_root_list_row('Machines [with Samples]',        self._misc_url_1_arg('list',  'Samples'))
        self._render_root_list_row('Machines [BIOS]',                self._misc_url_1_arg('list',  'BIOS'))
        # self._render_root_list_row('Machines [Devices]',             self._misc_url_1_arg('list',  'Devices'))
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
        ICON_OVERLAY = 6
        listitem = xbmcgui.ListItem(root_name, iconImage = icon)

        # listitem.setProperty('fanart_image', category_dic['fanart'])
        listitem.setInfo('video', {'Title'   : root_name, 'Overlay' : ICON_OVERLAY } )

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
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_PATH.getPath())
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_NOCOIN_PATH.getPath())
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_MECHA_PATH.getPath())
        elif list_name == 'Dead':       Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEAD_PATH.getPath())
        elif list_name == 'CHD':        Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_CHD_PATH.getPath())
        elif list_name == 'Samples':    Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_SAMPLES_PATH.getPath())
        elif list_name == 'BIOS':       Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_BIOS_PATH.getPath())
        elif list_name == 'Devices':    Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEVICES_PATH.getPath())

        # >> Render parent main list
        self._set_Kodi_all_sorting_methods()
        for parent_name in Machines_PClone_dic:
            machine = MAME_db_dic[parent_name]
            assets  = MAME_assets_dic[parent_name]
            self._render_machine_row(parent_name, machine, assets, True, list_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Also render parent together with clones
    # If user clicks in this list then ROM is launched.
    #
    def _render_machine_clone_list(self, list_name, parent_name):
        # >> Load main MAME info DB and PClone index
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        if   list_name == 'Machines':   Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_PATH.getPath())
        elif list_name == 'NoCoin':     Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_NOCOIN_PATH.getPath())
        elif list_name == 'Mechanical': Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_MECHA_PATH.getPath())
        elif list_name == 'Dead':       Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEAD_PATH.getPath())
        elif list_name == 'CHD':        Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_CHD_PATH.getPath())
        elif list_name == 'Samples':    Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_SAMPLES_PATH.getPath())
        elif list_name == 'BIOS':       Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_BIOS_PATH.getPath())
        elif list_name == 'Devices':    Machines_PClone_dic = fs_load_JSON_file(PATHS.MACHINES_IDX_DEVICES_PATH.getPath())

        # >> Render parent first
        self._set_Kodi_all_sorting_methods()
        machine = MAME_db_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_machine_row(parent_name, machine, assets, False)
        # >> Render clones
        for clone_name in Machines_PClone_dic[parent_name]:
            machine = MAME_db_dic[clone_name]
            assets  = MAME_assets_dic[clone_name]
            self._render_machine_row(clone_name, machine, assets, False)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Render parent or clone machines.
    # Information and artwork/assets are the same for all machines.
    # URL is different: parent URL leads to clones, clone URL launchs machine.
    #
    def _render_machine_row(self, machine_name, machine, machine_assets, is_parent_list, list_name = ''):
        display_name = machine['description']
        
        # --- Mark Status ---
        status = '{0}{1}{2}{3}'.format(machine['status_ROM'], machine['status_CHD'], 
                                       machine['status_SAM'], machine['status_SL'])
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
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATVER_PATH.getPath())
        elif clist_name == 'Catlist':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATLIST_PATH.getPath())
        elif clist_name == 'Genre':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_GENRE_PATH.getPath())
        elif clist_name == 'Manufacturer':
            catalog_name = 'manufacturer'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_MANUFACTURER_PATH.getPath())
        elif clist_name == 'Year':
            catalog_name = 'year'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_YEAR_PATH.getPath())
        elif clist_name == 'Driver':
            catalog_name = 'driver'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DRIVER_PATH.getPath())
        elif clist_name == 'Controls':
            catalog_name = 'control'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CONTROL_PATH.getPath())
        elif clist_name == 'Display_Tag':
            catalog_name = 'tag'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TAG_PATH.getPath())
        elif clist_name == 'Display_Type':
            catalog_name = 'type'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TYPE_PATH.getPath())
        elif clist_name == 'Display_Rotate':
            catalog_name = 'rotate'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_ROTATE_PATH.getPath())
        elif clist_name == 'BySL':
            catalog_name = 'SL'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_SL_PATH.getPath())

        # >> Render categories in catalog index
        self._set_Kodi_all_sorting_methods()
        for catalog_key in catalog_dic:
            self._render_indexed_list_row(clist_name, catalog_name, catalog_key)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    #
    # Renders a Parent list knowing the index (category)
    #
    def _render_indexed_parent_list(self, clist_name, catalog_item_name):
        # >> Load main MAME info DB
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())

        # >> Load catalog index
        if clist_name == 'Catver':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATVER_PATH.getPath())
        elif clist_name == 'Catlist':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CATLIST_PATH.getPath())
        elif clist_name == 'Genre':
            catalog_name = 'category'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_GENRE_PATH.getPath())
        elif clist_name == 'Manufacturer':
            catalog_name = 'manufacturer'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_MANUFACTURER_PATH.getPath())
        elif clist_name == 'Year':
            catalog_name = 'year'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_YEAR_PATH.getPath())
        elif clist_name == 'Driver':
            catalog_name = 'driver'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DRIVER_PATH.getPath())
        elif clist_name == 'Controls':
            catalog_name = 'control'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_CONTROL_PATH.getPath())
        elif clist_name == 'Display_Tag':
            catalog_name = 'tag'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TAG_PATH.getPath())
        elif clist_name == 'Display_Type':
            catalog_name = 'type'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_TYPE_PATH.getPath())
        elif clist_name == 'Display_Rotate':
            catalog_name = 'rotate'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_DISPLAY_ROTATE_PATH.getPath())
        elif clist_name == 'BySL':
            catalog_name = 'SL'
            catalog_dic = fs_load_JSON_file(PATHS.CATALOG_SL_PATH.getPath())

        # >> Get parents for this category
        Machines_PClone_dic = catalog_dic[catalog_item_name]

        # >> Render parent main list
        self._set_Kodi_all_sorting_methods()
        for parent_name in Machines_PClone_dic:
            machine = MAME_db_dic[parent_name]
            assets  = MAME_assets_dic[parent_name]
            self._render_indexed_machine_row(parent_name, machine, assets, True, clist_name, catalog_name, catalog_item_name)
        xbmcplugin.endOfDirectory(handle = self.addon_handle, succeeded = True, cacheToDisc = False)

    def _render_indexed_clone_list(self, clist_name, catalog_item_name, parent_name):
        # >> Load main MAME info DB
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())

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
        self._set_Kodi_all_sorting_methods()
        machine = MAME_db_dic[parent_name]
        assets  = MAME_assets_dic[parent_name]
        self._render_indexed_machine_row(parent_name, machine, assets, False, clist_name, catalog_name, catalog_item_name)

        # >> Render clones belonging to parent in this category
        for p_name in main_pclone_dic[parent_name]:
            machine = MAME_db_dic[p_name]
            assets  = MAME_assets_dic[p_name]
            self._render_indexed_machine_row(p_name, machine, assets, False, clist_name, catalog_name, catalog_item_name)
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
    def _render_indexed_machine_row(self, machine_name, machine, machine_assets, is_parent_list, clist_name, catalog_name, catalog_item_name):
        display_name = machine['description']
        
        # --- Mark Status ---
        status = '{0}{1}{2}{3}'.format(machine['status_ROM'], machine['status_CHD'], 
                                       machine['status_SAM'], machine['status_SL'])
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
        SL_catalog_dic = fs_load_JSON_file(PATHS.SL_INDEX_PATH.getPath())

        self._set_Kodi_all_sorting_methods()
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

        self._set_Kodi_all_sorting_methods()
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
        MAME_db_dic     = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
        MAME_assets_dic = fs_load_JSON_file(PATHS.MAIN_ASSETS_DB_PATH.getPath())
        machine = MAME_db_dic[machine_name]
        assets  = MAME_assets_dic[machine_name]

        # --- Make information string ---
        info_text  = '[COLOR orange]Machine {0}[/COLOR]\n'.format(machine_name)
        info_text += "[COLOR skyblue]CHDs[/COLOR]: {0}\n".format(machine['CHDs'])
        info_text += "[COLOR violet]catlist[/COLOR]: '{0}'\n".format(machine['catlist'])
        info_text += "[COLOR violet]catver[/COLOR]: '{0}'\n".format(machine['catver'])        
        info_text += "[COLOR violet]cloneof[/COLOR]: '{0}'\n".format(machine['cloneof'])
        info_text += "[COLOR skyblue]coins[/COLOR]: {0}\n".format(machine['coins'])
        info_text += "[COLOR skyblue]control_type[/COLOR]: {0}\n".format(machine['control_type'])
        info_text += "[COLOR violet]description[/COLOR]: '{0}'\n".format(machine['description'])
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
        dialog = xbmcgui.Dialog()
        menu_item = dialog.select('Setup plugin',
                                 ['Extract MAME.xml...',
                                  'Build main MAME database...',
                                  'Build MAME indices/catalogs...',
                                  'Build Software Lists indices/catalogs...', 
                                  'Scan ROMs/CHDs/Samples...',
                                  'Scan assets/artwork...'])
        if menu_item < 0: return

        # --- Extract MAME.xml ---
        if menu_item == 0:
            if not self.settings['mame_prog']:
                kodi_dialog_OK('MAME executable is not set.')
                return
            mame_prog_FN = FileName(self.settings['mame_prog'])

            # --- Extract MAME XML ---
            filesize = fs_extract_MAME_XML(PATHS, mame_prog_FN)
            kodi_dialog_OK('Extracted MAME XML database. Size is {0} MB.'.format(filesize / (1000000)))

        # --- Build main MAME database and PClone list ---
        elif menu_item == 1:
            # --- Error checks ---
            # >> Check that MAME_XML_PATH exists
        
            # --- Parse MAME XML and generate main database and PClone list ---
            log_info('_command_setup_plugin() Generating MAME main database and PClone list...')
            fs_build_MAME_main_database(PATHS, self.settings)
            kodi_notify('Main MAME database built')

        # --- Build MAME indices/catalogs ---
        elif menu_item == 2:
            # --- Error checks ---
            # >> Check that main MAME database exists

            # --- Read main database and control dic ---
            kodi_busydialog_ON()
            machines        = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            main_pclone_dic = fs_load_JSON_file(PATHS.MAIN_PCLONE_DIC_PATH.getPath())
            control_dic     = fs_load_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath())
            kodi_busydialog_OFF()

            # --- Generate indices ---
            fs_build_MAME_indices(PATHS, machines, main_pclone_dic, control_dic)
            
            # --- Generate catalogs ---
            fs_build_MAME_catalogs(PATHS, machines, main_pclone_dic, control_dic)

            # --- Write update control dictionary ---
            fs_write_JSON_file(PATHS.MAIN_CONTROL_PATH.getPath(), control_dic)
            kodi_notify('Indices and catalogs built')

        # --- Build Software Lists indices/catalogs ---
        elif menu_item == 3:
            # --- Error checks ---
            if not self.settings['SL_hash_path']:
                kodi_dialog_OK('Software Lists hash path not set.')
                return

            # --- Build Software List indices ---
            fs_build_SoftwareLists_index(PATHS, self.settings)
            kodi_notify('Software Lists indices and catalogs built')

        # --- Scan ROMs/CHDs/Samples and updates ROM status ---
        elif menu_item == 4:
            log_info('_command_setup_plugin() Scanning ROMs/CHDs/Samples ...')
            
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

            # >> Load machine database
            kodi_busydialog_ON()
            machines = fs_load_JSON_file(PATHS.MAIN_DB_PATH.getPath())
            kodi_busydialog_OFF()

            # >> Iterate machines, check if ROMs exits. Update status field
            pDialog = xbmcgui.DialogProgress()
            pDialog_canceled = False
            pDialog.create('Advanced MAME Launcher', 'Scanning MAME ROMs...')
            total_machines = len(machines)
            processed_machines = 0
            for key, machine in machines.iteritems():
                machine = machines[key]
                # log_info('_command_setup_plugin() Checking machine {0}'.format(key))

                # >> Scan ROMs
                if machine['hasROM']:
                    # >> Machine has ROM. Get ROM filename and check if file exist
                    ROM_FN = ROM_path_FN.pjoin(key + '.zip')
                    if ROM_FN.exists(): machine['status_ROM'] = 'R'
                    else:               machine['status_ROM'] = 'r'
                else:
                    machine['status_ROM'] = '-'
                    
                # >> Scan CHDs
                if machine['CHDs']:
                    if scan_CHDs:
                        hasCHD_list = [False] * len(machine['CHDs'])
                        for idx, CHD_name in enumerate(machine['CHDs']):
                            CHD_FN = CHD_path_FN.pjoin(CHD_name + '.chd')
                            if CHD_FN.exists(): hasCHD_list[idx] = True
                        if all(hasCHD_list): machine['status_CHD'] = 'C'
                        else:                machine['status_CHD'] = 'c'
                    else:
                        machine['status_CHD'] = 'c'
                else:
                    machine['status_CHD'] = '-'

                # >> Scan Samples
                if machine['sampleof']:
                    if scan_CHDs:
                        Sample_FN = Samples_path_FN.pjoin(key + '.zip')
                        if Sample_FN.exists(): machine['status_SAM'] = 'S'
                        else:                  machine['status_SAM'] = 's'
                    else:
                        machine['status_SAM'] = 's'
                else:
                    machine['status_SAM'] = '-'

                # >> Progress dialog
                processed_machines = processed_machines + 1
                pDialog.update(100 * processed_machines / total_machines)
            pDialog.close()

            # >> Save database
            kodi_busydialog_ON()
            fs_write_JSON_file(PATHS.MAIN_DB_PATH.getPath(), machines)
            kodi_busydialog_OFF()
            kodi_notify('Scanning of ROMs, CHDs and Samples finished')

        # --- Scans assets/artwork ---
        elif menu_item == 5:
            log_info('_command_setup_plugin() Scanning ROMs/CHDs/Samples ...')
            
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

    def _run_machine(self, machine_name):
        log_info('_run_machine() Launching MAME machine "{0}"'.format(machine_name))

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
        if not ROM_FN.exists():
            kodi_dialog_OK('ROM "{0}" not found.'.format(ROM_FN.getBase()))
            return

        # >> Launch machine using subprocess module
        (mame_dir, mame_exec) = os.path.split(mame_prog_FN.getPath())
        log_info('_run_machine() mame_prog_FN "{0}"'.format(mame_prog_FN.getPath()))    
        log_info('_run_machine() mame_dir     "{0}"'.format(mame_dir))
        log_info('_run_machine() mame_exec    "{0}"'.format(mame_exec))
        log_info('_run_machine() machine_name "{0}"'.format(machine_name))

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
        log_info('_run_machine() Calling subprocess.Popen()...')
        with open(PATHS.MAME_STDOUT_PATH.getPath(), 'wb') as _stdout, \
             open(PATHS.MAME_STDERR_PATH.getPath(), 'wb') as _stderr:
            p = subprocess.Popen([mame_prog_FN.getPath(), '-window', machine_name], 
                                 stdout = _stdout, stderr = _stderr, cwd = mame_dir, startupinfo = _info)
        p.wait()
        log_info('_run_machine() Exiting function')

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
        return '{0}?{1}={2}'.format(self.base_url, arg_name, arg_value)

    def _misc_url_2_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return '{0}?{1}={2}&{3}={4}'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)

    def _misc_url_3_arg(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2, arg_name_3, arg_value_3):
        return '{0}?{1}={2}&{3}={4}&{5}={6}'.format(self.base_url, arg_name_1, arg_value_1, 
                                                    arg_name_2, arg_value_2, arg_name_3, arg_value_3)

    def _misc_url_1_arg_RunPlugin(self, arg_name_1, arg_value_1):
        return 'XBMC.RunPlugin({0}?{1}={2})'.format(self.base_url, arg_name_1, arg_value_1)

    def _misc_url_2_arg_RunPlugin(self, arg_name_1, arg_value_1, arg_name_2, arg_value_2):
        return 'XBMC.RunPlugin({0}?{1}={2}&{3}={4})'.format(self.base_url, arg_name_1, arg_value_1, arg_name_2, arg_value_2)
