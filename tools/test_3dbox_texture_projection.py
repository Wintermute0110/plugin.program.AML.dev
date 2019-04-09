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
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

# --- Math functions -----------------------------------------------------------------------------
# Here is a more elegant and scalable solution, imo. It'll work for any nxn matrix and 
# you may find use for the other methods. Note that getMatrixInverse(m) takes in an 
# array of arrays as input.
def getMatrixTranspose(X):
    # return map(list, zip(*X))
    return [[X[j][i] for j in range(len(X))] for i in range(len(X[0]))]

def getMatrixMinor(m, i, j):
    return [row[:j] + row[j+1:] for row in (m[:i]+m[i+1:])]

def getMatrixDeterminant(m):
    # Base case for 2x2 matrix
    if len(m) == 2:
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]

    determinant = 0
    for c in range(len(m)):
        determinant += ((-1)**c)*m[0][c]*getMatrixDeterminant(getMatrixMinor(m,0,c))

    return determinant

def getMatrixInverse(m):
    determinant = getMatrixDeterminant(m)

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
            minor = getMatrixMinor(m,r,c)
            cofactorRow.append(((-1)**(r+c)) * getMatrixDeterminant(minor))
        cofactors.append(cofactorRow)
    cofactors = getMatrixTranspose(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant

    return cofactors

# Both A and B have sizes NxM where N, M >= 2 (list of lists of floats).
def getMatrixProduct(A, B):
    return [[sum(a*b for a,b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]

# A is a MxN matrix, B is a Nx1 matrix, result is a Mx1 matrix given as a list.
# Returns a list with the result. Note that this list corresponds to a column matrix.
def getMatrixProductColumn(A, B):
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
    # print('A =\n{0}'.format(pprint.pformat(A)))

    B = [float(item) for sublist in source_coords for item in sublist]
    # print('B =\n{0}'.format(pprint.pformat(B)))

    A_T = getMatrixTranspose(A)
    A_T_A = getMatrixProduct(A_T, A)
    A_T_A_inv = getMatrixInverse(A_T_A)
    A_T_A_inv_A_T = getMatrixProduct(A_T_A_inv, A_T)
    res = getMatrixProductColumn(A_T_A_inv_A_T, B)
    # print('res =\n{0}'.format(pprint.pformat(res)))

    return res

# --- Main code ----------------------------------------------------------------------------------
# --- Parameters ---
FONT_SIZE = 32
CANVAS_SIZE = (1000, 1500)
CANVAS_BG_COLOR = (100, 100, 100)

# Box dimensions
left, center, right = 100, 225, 900
top, offset, bottom = 100, 100, 1400
logoOffset, logoHeight = 10, 400
alpha_blend = 0.5
topOff, bottomOff = top + offset, bottom - offset

# --- Create 3dbox canvas ---
img = Image.new('RGB', CANVAS_SIZE, CANVAS_BG_COLOR)

# Box front (1000, 1500) and box spine (1000, 150).
# Canvas size of destination transformation must have the same size as the final canvas.
img_front = Image.new('RGB', (1000, 1500), (100, 0, 0))


# --- Front image ---
img_boxfront = Image.open('../media/SL_assets/doom_boxfront.png')
width, height = img_boxfront.size
print('boxfront width {0}, height {1}'.format(width, height))

# top/left, top/right, bottom/right, bottom/left
coeffs = perspective_coefficients(
    [(0, 0), (width, 0), (width, height), (0, height)],
    [(center, top), (right, top+offset), (right, bottom-offset), (center, bottom)]
)
print(coeffs)
img_t = img_boxfront.transform(CANVAS_SIZE, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
img_t.save('img_front_transform_A.png')
img = Image.blend(img, img_t, alpha = alpha_blend)

# --- Spine background ---
img_spine = Image.new('RGB', (1000, 150),  (0, 100, 0))
width, height = 1000, 150
coeffs = perspective_coefficients(
    [(0, 0), (width, 0), (width, height), (0, height)],
    [(left, top+offset), (center, top), (center, bottom), (left, bottom-offset)]
)
print(coeffs)
img_t = img_spine.transform(CANVAS_SIZE, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
img_t.save('img_front_transform_B.png')
img = Image.blend(img, img_t, alpha = alpha_blend)

# --- MAME background ---
# img_mame = Image.new('RGB', (4500, 1500), (200, 0, 0))
img_mame = Image.open('../media/MAME_clearlogo.jpg')
width, height = img_mame.size
print('boxfront width {0}, height {1}'.format(width, height))
coeffs = perspective_coefficients(
    [(0, 0), (width, 0), (width, height), (0, height)],
    [(center-logoOffset, top+logoOffset+15), (center-logoOffset, top+logoOffset+logoHeight+70), 
     (left+logoOffset, topOff+logoOffset+logoHeight), (left+logoOffset, topOff+logoOffset)]
)
print(coeffs)
img_t = img_mame.transform(CANVAS_SIZE, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
img_t.save('img_front_transform_C.png')
img = Image.blend(img, img_t, alpha = alpha_blend)

# --- Spine game clearlogo ---
# img_mame = Image.new('RGB', (4500, 1500), (0, 0, 200))
img_mame = Image.open('../media/MAME_clearlogo.jpg')
width, height = img_mame.size
print('boxfront width {0}, height {1}'.format(width, height))
coeffs = perspective_coefficients(
    [(0, 0), (width, 0), (width, height), (0, height)],
    [(center-logoOffset, bottom-logoOffset-logoHeight-70), (center-logoOffset, bottom-logoOffset-15), 
     (left+logoOffset, bottomOff-logoOffset), (left+logoOffset, bottomOff-logoOffset-logoHeight)]
)
print(coeffs)
img_t = img_mame.transform(CANVAS_SIZE, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
img_t.save('img_front_transform_D.png')
img = Image.blend(img, img_t, alpha = alpha_blend)

# --- Print machine name ---
# Cannot use font-related Pillow functions at the moment in Cygwin.
# font_mono = ImageFont.truetype('../fonts/Inconsolata.otf', FONT_SIZE)
# draw.text((0,0), 'doom', (255, 255, 255), font = font_mono)

# --- Save test 3dbox ---
img.save('3dbox.png')
