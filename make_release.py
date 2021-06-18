#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# Prepare files for a new AML release.
#
#   1) Clean pyo and pyc files.
#      Clean __pycache__ directories (Python 3 interpreter, must be empty).
#   2) Create directory plugin.program.AML
#   3) Copy required files to run AML. Do not copy unnecessary files.
#   4) Create file version.sha, which contains current git version.
#   5) Edit addon.xml to change plugin id, name and version.
#   6) Edit resources/settings.xml to change instances of
#      'plugin.program.AML.dev' into 'plugin.program.AML.dev'.

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

# --- Python standard library ---
import glob
import os
import re
import shutil
import sys

# --- configuration ---
AML_DEV_ID  = 'plugin.program.AML.dev'
AML_ID      = 'plugin.program.AML'
AML_NAME    = 'Advanced MAME Launcher'
AML_VERSION = '1.0.3'
root_file_list = [
    'addon.py',
    'addon.xml',
    'AUTHORS.md',
    'changelog.txt',
    'LICENSE.txt',
    'NOTES.md',
    'README.md',
    'SKINNING.md',
    'pdfrw/LICENSE.txt',
    'pdfrw/README.rst',
]
# No leading '/' in directory names.
root_directory_list = [
    'filters/',
    'fonts/',
    'media/',
    'resources/',
    'templates/',
    'pdfrw/pdfrw/',
]

# --- functions ----------------------------------------------------------------------------------
#
# Changes the content of a XML attribute in a given tag.
# Tags that span more than one line are not supported.
# Attributes must use double quote ".
# No spaces, for example, id="plugin.program.AML.dev" OK, id = " plugin.program.AML.dev" wrong.
#
def edit_xml_attribute(xml_file_path, tag_name, attrib_name, attrib_value):
    # Read XML file contents.
    print('Reading XML file "{}"'.format(xml_file_path))
    with open(xml_file_path) as file:
        str_list = file.readlines()

    # Traverse the file and search for <tag_name xxxxx attrib_name="attrib_value" xxxxx >
    # If a match is found then substitute the attribute value.
    # <img\s+                    # start of the tag
    # [^>]*?                     # any attributes that precede the src
    # src=                       # start of the src attribute
    # (?:
    #     (?P<quote>["'])            # opening quote
    #     (?P<qimage>[^\1>]+?)       # image filename
    #     (?P=quote)                 # closing quote matching the opening quote
    #     |                          # ---or alternatively---
    #     (?P<uimage>[^"' >]+)       # unquoted image filename
    # )
    # [^>]*?                     # any attributes that follow the src
    # >                          # end of the tag
    expression = '<{}\s+[^>]*?{}="([^\1>]+?)"[^>]*?>'.format(tag_name, attrib_name)
    # print(expression)
    prog = re.compile(expression)
    match_found = False
    for line_idx in range(len(str_list)):
        line = str_list[line_idx]
        m = prog.search(line)
        if m:
            current_attrib_value = m.group(1)
            print('Matched tag name "{}", attribute name "{}", attribute value "{}"'.format(
                tag_name, attrib_name, current_attrib_value))
            old_str = '{}="{}"'.format(attrib_name, current_attrib_value)
            new_str = '{}="{}"'.format(attrib_name, attrib_value)
            print("Replacing '{}' with '{}'".format(old_str, new_str))
            str_list[line_idx] = line.replace(old_str, new_str)
            match_found = True
            break

    # Write file if a match was found. If not, warn user and abort.
    if match_found:
        print('Writing XML file "{}"'.format(xml_file_path))
        with open(xml_file_path, 'w') as file:
            file.write(''.join(str_list))
    else:
        print('Not matches found. Aborting.')
        sys.exit(1)
    print(' ')

#
# Replaces ocurrences of a string in a text file.
# The string must be in a line of text. No multiline strings allowed.
#
def edit_text_file(file_path, old_str, new_str):
    print('Reading XML file "{}"'.format(file_path))
    with open(file_path) as file:
        str_list = file.readlines()

    match_found = False
    for line_idx in range(len(str_list)):
        line = str_list[line_idx]
        position = line.find(old_str)
        if position > 1:
            match_found = True
            print("Match found, replacing '{}' with '{}'".format(old_str, new_str))
            # str.replace() changes all occurences.
            str_list[line_idx] = line.replace(old_str, new_str)

    if match_found:
        print('Writing XML file "{}"'.format(file_path))
        with open(file_path, 'w') as file:
            file.write(''.join(str_list))
    else:
        print('Not matches found. Aborting.')
        sys.exit(1)

# --- main ---------------------------------------------------------------------------------------
def main():
    print('Starting {}'.format(sys.argv[0]))
    print('AML_DEV_ID  {}'.format(AML_DEV_ID))
    print('AML_ID      {}'.format(AML_ID))
    print('AML_NAME    {}'.format(AML_NAME))
    print('AML_VERSION {}'.format(AML_VERSION))

    # Clean pyo and pyc files.
    num_pyo, num_pyc = 0, 0
    print('\nCleaning pyo and pyc files...')
    current_dir = os.getcwd()
    print('The current directory is "{}"'.format(current_dir))
    for filename in glob.iglob(current_dir + '/**/*.pyo', recursive = True):
         # print('Removing file "{}"'.format(filename))
         os.unlink(filename)
         num_pyo += 1
    for filename in glob.iglob(current_dir + '/**/*.pyc', recursive = True):
         # print('Removing file "{}"'.format(filename))
         os.unlink(filename)
         num_pyc += 1
    print('Cleaned {} pyo files and {} pyc files'.format(num_pyo, num_pyc))

    # Clean (empty) __pycache__ directories.
    num_cache_dirs = 0
    print('\nCleaning __pycache__ (empty) directories...')
    for root, dirs, files in os.walk(current_dir, topdown=False):
        # print('\nroot "{}"'.format(root))
        (head, tail) = os.path.split(root)
        # print('head "{}"'.format(head))
        # print('tail "{}"'.format(tail))
        if tail == '__pycache__':
            print('Removing dir "{}"'.format(root))
            os.rmdir(root)
            num_cache_dirs += 1
        # for name in files: print('file "{}"'.format(name))
        # for name in dirs: print('dir "{}"'.format(name))
    print('Cleaned {} directories'.format(num_cache_dirs))

    # Create directory AML_ID. If exists, then purge it.
    print('\nCreating target directory...')
    release_dir = os.path.join(current_dir, AML_ID)
    print('The target directory is "{}"'.format(release_dir))
    if os.path.isdir(release_dir):
        print('Directory "{}" exists'.format(release_dir))
        print('Purging contents in "{}"'.format(release_dir))
        shutil.rmtree(release_dir)
    os.mkdir(release_dir)
    print('Created directory "{}"'.format(release_dir))

    # Copy required files to run AML
    print('\nCopying root files ...')
    for file in root_file_list:
        src = os.path.join(current_dir, file)
        dst = os.path.join(release_dir, file)
        print('Copy "{}"'.format(src))
        # print('Into "{}"'.format(dst))
        # If target directory does not exists then create it, otherwise shutil.copy() will fail.
        target_dir = os.path.dirname(dst)
        if not os.path.exists(target_dir):
            print('Creating directory "{}"'.format(target_dir))
            os.makedirs(target_dir)
        shutil.copy(src, dst)
    print('\nCopying root whole directories ...')
    for directory in root_directory_list:
        src = os.path.join(current_dir, directory)
        dst = os.path.join(release_dir, directory)
        print('Recursive copy "{}"'.format(src))
        # print('Into "{}"'.format(dst))
        shutil.copytree(src, dst)

    # Create file version.txt, which contains current git version.
    print('\nCreating file version.sha ...')
    src = os.path.join(current_dir, '.git/refs/heads/master')
    dst = os.path.join(release_dir, 'version.sha')
    shutil.copyfile(src, dst)

    # Edit addon.xml to change plugin id, name and version.
    print('\nEditing addon.xml ...')
    addon_xml_path = os.path.join(release_dir, 'addon.xml')
    edit_xml_attribute(addon_xml_path, 'addon', 'id', AML_ID)
    edit_xml_attribute(addon_xml_path, 'addon', 'name', AML_NAME)
    edit_xml_attribute(addon_xml_path, 'addon', 'version', AML_VERSION)

    # Edit resources/settings.xml.
    # print('\nEditing settings.xml ...')
    # settings_xml_path = os.path.join(release_dir, 'resources/settings.xml')
    # edit_text_file(settings_xml_path, AML_DEV_ID, AML_ID)

    # So long and thanks for all the fish.
    print('All operations finished. Exiting.')
    print('Exiting {}'.format(sys.argv[0]))

if __name__ == "__main__":
    main()
    sys.exit()
