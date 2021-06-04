#!/usr/bin/python3
#
# Test script to generate 2D texture projections using Pillow.
# The destination coordinates are approximated by a simple model. For a true 3D model see
# test_artwork_3dbox_mesh.py
#
# https://stackoverflow.com/questions/53032270/perspective-transform-with-python-pil-using-src-target-coordinates
# https://stackoverflow.com/questions/14177744/how-does-perspective-transformation-work-in-pil
# https://stackoverflow.com/questions/32114054/matrix-inversion-without-numpy/39881366
#
import pprint
import sys
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

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
def perspective_coefficients_numpy(pa, pb):
    # Creates a 8x8 matrix of floats.
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = numpy.matrix(matrix, dtype = numpy.float)

    # numpy.array(source_coords) creates a matrix 2x4.
    # .reshape(8) creates a matrix 1x8
    B = numpy.array(pb).reshape(8)

    # A is 8x8, B is 1x8
    # numpy.dot() If a is an N-D array and b is a 1-D array, it is a sum product over the
    # last axis of a and b.
    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)

    return numpy.array(res).reshape(8)

# A pure Python version of perspective_coefficients_numpy()
def perspective_coefficients(source_coords, target_coords):
    A = []
    for s, t in zip(source_coords, target_coords):
        s = [float(i) for i in s]
        t = [float(i) for i in t]
        A.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
        A.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
    # print('A =\n{}'.format(pprint.pformat(A)))

    B = [float(item) for sublist in source_coords for item in sublist]
    # print('B =\n{}'.format(pprint.pformat(B)))

    A_T = math_MatrixTranspose(A)
    A_T_A = math_MatrixProduct(A_T, A)
    A_T_A_inv = math_MatrixInverse(A_T_A)
    A_T_A_inv_A_T = math_MatrixProduct(A_T_A_inv, A_T)
    res = math_MatrixProduct_Column(A_T_A_inv_A_T, B)
    # print('res =\n{}'.format(pprint.pformat(res)))

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
    # print('Image width {}, height {}'.format(width, height))

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

# --- Main code ----------------------------------------------------------------------------------
def generate_3dbox():
    # --- Parameters ---
    FONT_SIZE = 90
    CANVAS_SIZE = (1000, 1500)
    CANVAS_BG_COLOR = (0, 0, 0)

    # --- Load projection coordinates ---
    with open('3dbox.json') as json_file:
        coord_dic = json.load(json_file)

    # --- Create 3dbox canvas ---
    # Create RGB image with alpha channel.
    # Canvas size of destination transformation must have the same size as the final canvas.
    img = Image.new('RGBA', CANVAS_SIZE, CANVAS_BG_COLOR)

    # --- Frontbox ---
    img_front = Image.new('RGBA', CANVAS_SIZE, (200, 100, 100))
    img_t = project_texture(img_front, coord_dic['Frontbox'], CANVAS_SIZE)
    # img_t.save('img_front_transform_A.png')
    img.paste(img_t, mask = img_t)

    # --- Spine ---
    img_spine = Image.new('RGBA', CANVAS_SIZE, (100, 200, 100))
    img_t = project_texture(img_spine, coord_dic['Spine'], CANVAS_SIZE)
    # img_t.save('img_front_transform_B.png')
    img.paste(img_t, mask = img_t)

    # --- Front image ---
    # img_flyer = Image.open('../media/SL_assets/doom_boxfront.png')
    img_flyer = Image.open('../media/SL_assets/sonic3_boxfront.png')
    img_t = project_texture(img_flyer, coord_dic['Flyer'], CANVAS_SIZE)
    # img_t.save('img_front_transform_C.png')
    img.paste(img_t, mask = img_t)

    # --- Spine game clearlogo ---
    # img_clearlogo = Image.open('../media/SL_assets/doom_clearlogo.png')
    img_clearlogo = Image.open('../media/SL_assets/sonic3_clearlogo.png')
    img_t = project_texture(img_clearlogo, coord_dic['Clearlogo'], CANVAS_SIZE, rotate = True)
    # img_t.save('img_front_transform_D.png')
    img.paste(img_t, mask = img_t)

    # --- MAME background ---
    img_mame = Image.open('../media/MAME_clearlogo.png')
    img_t = project_texture(img_mame, coord_dic['Clearlogo_MAME'], CANVAS_SIZE, rotate = True)
    # img_t.save('img_front_transform_E.png')
    img.paste(img_t, mask = img_t)

    # --- Machine name ---
    font_mono = ImageFont.truetype('../fonts/Inconsolata.otf', FONT_SIZE)
    img_name = Image.new('RGBA', (1000, 100), (0, 0, 0))
    draw = ImageDraw.Draw(img_name)
    draw.text((0, 0), 'SL 32x Item sonic3', (255, 255, 255), font = font_mono)
    img_t = project_texture(img_name, coord_dic['Front_Title'], CANVAS_SIZE)
    # img_name.save('img_name.png')
    # img_t.save('img_front_transform_F.png')
    img.paste(img_t, mask = img_t)

    # --- Save test 3dbox ---
    img.save('3dbox.png')
    sys.exit()

#  Call main function
generate_3dbox()
