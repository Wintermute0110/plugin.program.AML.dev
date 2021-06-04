#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# Copyright (c) 2019 Wintermute0110 <wintermute0110@gmail.com>
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
import os
import pprint
import re
import sys

# --- Helper code ---------------------------------------------------------------------------------
def log_debug(string): print(string)

# --- AML code ------------------------------------------------------------------------------------
#
# Numerical MAME version. Allows for comparisons like ver_mame >= MAME_VERSION_0190
# Support MAME versions higher than 0.53 August 12th 2001.
# See header of MAMEINFO.dat for a list of all MAME versions.
#
# M.mmm.Xbb
# |   | | |-> Beta flag 0, 1, ..., 99
# |   | |---> Release kind flag
# |   |       5 for non-beta, non-alpha, non RC versions.
# |   |       2 for RC versions
# |   |       1 for beta versions
# |   |       0 for alpha versions
# |   |-----> Minor version 0, 1, ..., 999
# |---------> Major version 0, ..., infinity
#
# See https://retropie.org.uk/docs/MAME/
# See https://www.mamedev.org/oldrel.html
#
# Examples:
#   '0.37b5'  ->  37105  (mame4all-pi, lr-mame2000 released 27 Jul 2000)
#   '0.37b16' ->  37116  (Last unconsistent MAME version, released 02 Jul 2001)
#   '0.53'    ->  53500  (MAME versioning is consistent from this release, released 12 Aug 2001)
#   '0.78'    ->  78500  (lr-mame2003, lr-mame2003-plus)
#   '0.139'   -> 139500  (lr-mame2010)
#   '0.160'   -> 160500  (lr-mame2015)
#   '0.174'   -> 174500  (lr-mame2016)
#   '0.206'   -> 206500
#
# mame_version_raw examples:
#   a) '0.194 (mame0194)' from '<mame build="0.194 (mame0194)" debug="no" mameconfig="10">'
#
# re.search() returns a MatchObject https://docs.python.org/2/library/re.html#re.MatchObject
def mame_get_numerical_version(mame_version_str):
    log_debug('mame_get_numerical_version() mame_version_str = "{}"'.format(mame_version_str))
    version_int = 0
    # Search for old version scheme x.yyybzz
    m_obj_old = re.search('^(\d+)\.(\d+)b(\d+)', mame_version_str)
    # Search for modern, consistent versioning system x.yyy
    m_obj_modern = re.search('^(\d+)\.(\d+)', mame_version_str)

    if m_obj_old:
        major = int(m_obj_old.group(1))
        minor = int(m_obj_old.group(2))
        beta  = int(m_obj_old.group(3))
        release_flag = 1
        # log_debug('mame_get_numerical_version() major = {}'.format(major))
        # log_debug('mame_get_numerical_version() minor = {}'.format(minor))
        # log_debug('mame_get_numerical_version() beta  = {}'.format(beta))
        version_int = major * 1000000 + minor * 1000 + release_flag * 100 + beta
    elif m_obj_modern:
        major = int(m_obj_modern.group(1))
        minor = int(m_obj_modern.group(2))
        release_flag = 5
        # log_debug('mame_get_numerical_version() major = {}'.format(major))
        # log_debug('mame_get_numerical_version() minor = {}'.format(minor))
        version_int = major * 1000000 + minor * 1000 + release_flag * 100
    else:
        log_error('MAME version "{}" cannot be parsed.'.format(mame_version_str))
        raise TypeError
    log_debug('mame_get_numerical_version() version_int = {}'.format(version_int))

    return version_int

# --- Main ----------------------------------------------------------------------------------------
input_str_list = [
    ['0.37b5',  37105],
    ['0.37b16', 37116],
    ['0.78',    78500],
    ['0.139',  139500],
    ['0.206 (mame0206)', 206500],
    ['1.001', 1001500],
    ['1.50',  1050500],
    ['1.100', 1100500],
]

print('Unitary tests mame_get_numerical_version()\n')
for test_list in input_str_list:
    version_str = test_list[0]
    expected_int = test_list[1]
    version_int = mame_get_numerical_version(version_str)
    print('Input  {}'.format(version_str))
    print('Output {:,}'.format(version_int))
    if expected_int != version_int:
        print('Expected {0:,} and obtained {1:,}'.format(expected_int, version_int))
        print('Test failed.')
        sys.exit(1)
    print(' ')
sys.exit(0)
