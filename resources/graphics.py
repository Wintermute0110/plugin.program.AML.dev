# -*- coding: utf-8 -*-
#
# Advanced MAME Launcher graphics plotting functions.
#

# Copyright (c) 2016-2019 Wintermute0110 <wintermute0110@gmail.com>
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
try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
    PILLOW_AVAILABLE = True
except:
    PILLOW_AVAILABLE = False

# --- Modules/packages in this addon ---
from .constants import *
from .utils import *
from .utils_kodi import *


# --- Math functions -----------------------------------------------------------------------------
# Here is a more elegant and scalable solution, imo. It'll work for any nxn matrix and 
# you may find use for the other methods. Note that getMatrixInverse(m) takes in an 
# array of arrays as input.
def math_MatrixTranspose(X):
    # return map(list, zip(*X))
    return [[X[j][i] for j in range(len(X))] for i in range(len(X[0]))]

def math_MatrixMinor(m, i, j):
    return [row[:j] + row[j+1:] for row in (m[:i]+m[i+1:])]

def math_MatrixDeterminant(m):
    # Base case for 2x2 matrix
    if len(m) == 2:
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]

    determinant = 0
    for c in range(len(m)):
        determinant += ((-1)**c)*m[0][c]*math_MatrixDeterminant(math_MatrixMinor(m,0,c))

    return determinant

def math_MatrixInverse(m):
    determinant = math_MatrixDeterminant(m)

    # Special case for 2x2 matrix:
    if len(m) == 2:
        return [
            [m[1][1]/determinant, -1*m[0][1]/determinant],
            [-1*m[1][0]/determinant, m[0][0]/determinant],
        ]

    # Find matrix of cofactors
    cofactors = []
    for r in range(len(m)):
        cofactorRow = []
        for c in range(len(m)):
            minor = math_MatrixMinor(m,r,c)
            cofactorRow.append(((-1)**(r+c)) * math_MatrixDeterminant(minor))
        cofactors.append(cofactorRow)
    cofactors = math_MatrixTranspose(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant

    return cofactors

# Both A and B have sizes NxM where N, M >= 2 (list of lists of floats).
def math_MatrixProduct(A, B):
    return [[sum(a*b for a,b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]

# A is a MxN matrix, B is a Nx1 matrix, result is a Mx1 matrix given as a list.
# Returns a list with the result. Note that this list corresponds to a column matrix.
def math_MatrixProduct_Column(A, B):
    return [sum(a*b for a,b in zip(A_row, B)) for A_row in A]

# --- Auxiliar functions -------------------------------------------------------------------------
#
# source_coords is the four vertices in the current plane and target_coords contains
# four vertices in the resulting plane.
# coords is a list of tuples (x, y)
#
def perspective_coefficients(source_coords, target_coords):
    A = []
    for s, t in zip(source_coords, target_coords):
        s = [float(i) for i in s]
        t = [float(i) for i in t]
        A.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        A.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    # print('A =\n{0}'.format(pprint.pformat(A)))

    B = [float(item) for sublist in source_coords for item in sublist]
    # print('B =\n{0}'.format(pprint.pformat(B)))

    A_T = math_MatrixTranspose(A)
    A_T_A = math_MatrixProduct(A_T, A)
    A_T_A_inv = math_MatrixInverse(A_T_A)
    A_T_A_inv_A_T = math_MatrixProduct(A_T_A_inv, A_T)
    res = math_MatrixProduct_Column(A_T_A_inv_A_T, B)
    # print('res =\n{0}'.format(pprint.pformat(res)))

    return res

def project_texture(img_boxfront, coordinates, CANVAS_SIZE, rotate = False):
    # print('project_texture() BEGIN ...')

    # --- Rotate 90 degress clockwise ---
    if rotate:
        # print('Rotating image 90 degress clockwise')
        img_boxfront = img_boxfront.rotate(-90, expand = True)
        # img_boxfront.save('rotated.png')

    # --- Info ---
    width, height = img_boxfront.size
    # print('Image width {0}, height {1}'.format(width, height))

    # --- Transform ---
    # Conver list of lists to list of tuples
    n_coords = [(int(c[0]), int(c[1])) for c in coordinates]
    # top/left, top/right, bottom/right, bottom/left
    coeffs = perspective_coefficients(
        [(0, 0), (width, 0), (width, height), (0, height)],
        n_coords
    )
    # print(coeffs)
    img_t = img_boxfront.transform(CANVAS_SIZE, Image.PERSPECTIVE, coeffs, Image.BICUBIC)

    # --- Add polygon with alpha channel for blending ---
    # In the alpha channel 0 means transparent and 255 opaque.
    mask = Image.new('L', CANVAS_SIZE, color = 0)
    draw = ImageDraw.Draw(mask)
    # print(n_coords)
    draw.polygon(n_coords, fill = 255)
    img_t.putalpha(mask)

    return img_t

# ------------------------------------------------------------------------------------------------
# Graphics high level interface functions
# ------------------------------------------------------------------------------------------------
# Cache font objects in global variables.
# Used in mame.py, mame_build_fanart() and mame_build_SL_fanart()
font_mono = None
font_mono_SL = None
font_mono_item = None
font_mono_debug = None

def graph_build_MAME_3Dbox(PATHS, coord_dic, m_name, assets_dic,
    image_FN, CANVAS_COLOR = (0, 0, 0), test_flag = False):
    global font_mono
    FONT_SIZE = 90
    CANVAS_SIZE = (1000, 1500)
    CANVAS_BG_COLOR = (50, 50, 75) if test_flag else (0, 0, 0)
    MAME_logo_FN = PATHS.ADDON_CODE_DIR.pjoin('media/MAME_clearlogo.png')

    # Quickly check if machine has valid assets, and skip fanart generation if not.
    # log_debug('mame_build_fanart() Building fanart for machine {0}'.format(m_name))
    machine_has_valid_assets = False
    for asset_key, asset_filename in assets_dic[m_name].iteritems():
        if asset_filename:
            machine_has_valid_assets = True
            break
    if not machine_has_valid_assets: return

    # --- If font object does not exists open font an cache it. ---
    if not font_mono:
        log_debug('graph_build_MAME_3Dbox() Creating font_mono object')
        log_debug('graph_build_MAME_3Dbox() Loading "{0}"'.format(PATHS.MONO_FONT_PATH.getPath()))
        font_mono = ImageFont.truetype(PATHS.MONO_FONT_PATH.getPath(), 90)

    # --- Create 3dbox canvas ---
    # Create RGB image with alpha channel.
    # Canvas size of destination transformation must have the same size as the final canvas.
    img = Image.new('RGBA', CANVAS_SIZE, CANVAS_BG_COLOR)

    # --- Frontbox ---
    img_front = Image.new('RGBA', CANVAS_SIZE, (200, 100, 100))
    img_t = project_texture(img_front, coord_dic['Frontbox'], CANVAS_SIZE)
    img.paste(img_t, mask = img_t)

    # --- Spine ---
    img_spine = Image.new('RGBA', CANVAS_SIZE, (100, 200, 100))
    img_t = project_texture(img_spine, coord_dic['Spine'], CANVAS_SIZE)
    img.paste(img_t, mask = img_t)

    # --- Front image ---
    img_flyer = Image.open(assets_dic[m_name]['flyer'])
    img_t = project_texture(img_flyer, coord_dic['Flyer'], CANVAS_SIZE)
    img.paste(img_t, mask = img_t)

    # --- Spine game clearlogo ---
    img_clearlogo = Image.open(assets_dic[m_name]['clearlogo'])
    img_t = project_texture(img_clearlogo, coord_dic['Clearlogo'], CANVAS_SIZE, rotate = True)
    img.paste(img_t, mask = img_t)

    # --- MAME background ---
    img_mame = Image.open(MAME_logo_FN.getPath())
    img_t = project_texture(img_mame, coord_dic['Clearlogo_MAME'], CANVAS_SIZE, rotate = True)
    img.paste(img_t, mask = img_t)

    # --- Machine name ---
    # font_mono = ImageFont.truetype('../fonts/Inconsolata.otf', 90)
    img_name = Image.new('RGBA', (1000, 100), (0, 0, 0))
    draw = ImageDraw.Draw(img_name)
    draw.text((0, 0), ' {0}'.format(m_name), (255, 255, 255), font = font_mono)
    img_t = project_texture(img_name, coord_dic['Front_Title'], CANVAS_SIZE)
    img.paste(img_t, mask = img_t)

    # --- Save fanart and update database ---
    log_debug('graph_build_MAME_3Dbox() Saving Fanart "{0}"'.format(image_FN.getPath()))
    img.save(image_FN.getPath())

# Returns a dictionary with all the data necessary to build the fanarts.
# The dictionary has the 'abort' field if an error was detected.
def graph_load_SL_Fanart_stuff(BUILD_MISSING):
    data_dic = {}
    data_dic['abort'] = False
    data_dic['BUILD_MISSING'] = BUILD_MISSING

    return data_dic

# Builds or rebuilds missing SL Fanarts.
def graph_build_SL_Fanart_stuff(g_PATHS, g_settings, data_dic):
    pass
