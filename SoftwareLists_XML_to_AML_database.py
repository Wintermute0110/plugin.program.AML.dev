#!/usr/bin/python
# -*- coding: utf-8 -*-
# Converts MAME output XML into AML database
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

# --- INSTRUCTIONS -------------------------------------------------------------
#
# ------------------------------------------------------------------------------

# --- Python standard library ---
import xml.etree.ElementTree as ET 
import re
import sys
import json
import io
import os

# --- "Constants" -------------------------------------------------------------


