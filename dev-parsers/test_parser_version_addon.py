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
# All version numbers must be less than 100, except the major version.
# AML version is like this: aa.bb.cc[-|~][alpha[dd]|beta[dd]]
# It gets converted to: aa.bb.cc Rdd -> int aab,bcc,Rdd
# The number 2,147,483,647 is the maximum positive value for a 32-bit signed binary integer.
#
# aa.bb.cc.Xdd    formatted aab,bcc,Xdd
#  |  |  | | |--> Beta/Alpha flag 0, 1, ..., 99
#  |  |  | |----> Release kind flag
#  |  |  |        5 for non-beta, non-alpha, non RC versions.
#  |  |  |        2 for RC versions
#  |  |  |        1 for beta versions
#  |  |  |        0 for alpha versions
#  |  |  |------> Build version 0, 1, ..., 99
#  |  |---------> Minor version 0, 1, ..., 99
#  |------------> Major version 0, ..., infinity
#
def fs_AML_version_str_to_int(AML_version_str):
    log_debug('fs_AML_version_str_to_int() AML_version_str = "{}"'.format(AML_version_str))
    version_int = 0
    # Parse versions like "0.9.8[-|~]alpha[jj]"
    m_obj_alpha_n = re.search('^(\d+?)\.(\d+?)\.(\d+?)[\-\~](alpha|beta)(\d+?)$', AML_version_str)
    # Parse versions like "0.9.8[-|~]alpha[jj]"
    m_obj_alpha = re.search('^(\d+?)\.(\d+?)\.(\d+?)[\-\~](alpha|beta)$', AML_version_str)
    # Parse versions like "0.9.8"
    m_obj_standard = re.search('^(\d+?)\.(\d+?)\.(\d+?)$', AML_version_str)

    if m_obj_alpha_n:
        major  = int(m_obj_alpha_n.group(1))
        minor  = int(m_obj_alpha_n.group(2))
        build  = int(m_obj_alpha_n.group(3))
        kind_str = m_obj_alpha_n.group(4)
        beta   = int(m_obj_alpha_n.group(5))
        if kind_str == 'alpha':  release_flag = 0
        elif kind_str == 'beta': release_flag = 1
        # log_debug('fs_AML_version_str_to_int() major        {}'.format(major))
        # log_debug('fs_AML_version_str_to_int() minor        {}'.format(minor))
        # log_debug('fs_AML_version_str_to_int() build        {}'.format(build))
        # log_debug('fs_AML_version_str_to_int() kind_str     {}'.format(kind_str))
        # log_debug('fs_AML_version_str_to_int() release_flag {}'.format(release_flag))
        # log_debug('fs_AML_version_str_to_int() beta         {}'.format(beta))
        version_int = major * 10000000 + minor * 100000 + build * 1000 + release_flag * 100 + beta
    elif m_obj_alpha:
        major  = int(m_obj_alpha.group(1))
        minor  = int(m_obj_alpha.group(2))
        build  = int(m_obj_alpha.group(3))
        kind_str = m_obj_alpha.group(4)
        if kind_str == 'alpha':  release_flag = 0
        elif kind_str == 'beta': release_flag = 1
        # log_debug('fs_AML_version_str_to_int() major        {}'.format(major))
        # log_debug('fs_AML_version_str_to_int() minor        {}'.format(minor))
        # log_debug('fs_AML_version_str_to_int() build        {}'.format(build))
        # log_debug('fs_AML_version_str_to_int() kind_str     {}'.format(kind_str))
        # log_debug('fs_AML_version_str_to_int() release_flag {}'.format(release_flag))
        version_int = major * 10000000 + minor * 100000 + build * 1000 + release_flag * 100
    elif m_obj_standard:
        major = int(m_obj_standard.group(1))
        minor = int(m_obj_standard.group(2))
        build = int(m_obj_standard.group(3))
        release_flag = 5
        # log_debug('fs_AML_version_str_to_int() major {}'.format(major))
        # log_debug('fs_AML_version_str_to_int() minor {}'.format(minor))
        # log_debug('fs_AML_version_str_to_int() build {}'.format(build))
        version_int = major * 10000000 + minor * 100000 + build * 1000 + release_flag * 100
    else:
        log_error('AML addon version "{}" cannot be parsed.'.format(AML_version_str))
        raise TypeError
    log_debug('fs_AML_version_str_to_int() version_int = {}'.format(version_int))

    return version_int

# --- Main ----------------------------------------------------------------------------------------
input_str_list = [
    ['0.9.9-alpha',  909000],
    ['0.9.9-alpha1', 909001],
    ['0.9.9-beta',   909100],
    ['0.9.9-beta2',  909102],
    ['0.9.9',        909500],
    ['0.9.10',       910500],
    ['0.10.0',      1000500],
    ['1.1.1',      10101500],
    ['1.10.1',     11001500],
    ['2.1.1',      20101500],
    ['10.10.10',  101010500],
]

print('Unitary tests fs_AML_version_str_to_int()\n')
for test_list in input_str_list:
    version_str = test_list[0]
    expected_int = test_list[1]
    version_int = fs_AML_version_str_to_int(version_str)
    print('Input  {}'.format(version_str))
    print('Output {:,}'.format(version_int))
    if expected_int != version_int:
        print('Expected {0:,} and obtained {1:,}'.format(expected_int, version_int))
        print('Test failed.')
        sys.exit(1)
    print(' ')
sys.exit(0)
