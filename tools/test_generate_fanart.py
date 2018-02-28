#!/usr/bin/python
#
#
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

#
# Scales and centers img into a box of size (new_x_size, new_y_size).
# Scaling keeps original img aspect ratio.
# Returns an image of size (new_x_size, new_y_size)
#
def PIL_resize_proportional(img, new_x_size, new_y_size):
    print('PIL_resize_proportional() Initialising ...')
    print('img    X_size = {0} | img Y_size = {1}'.format(img_title.size[0], img_title.size[1]))
    print('wanted X_size = {0} | img Y_size = {1}'.format(new_x_size, new_y_size))

    if new_x_size > new_y_size:
        wpercent = (new_x_size / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        t_x_size = new_x_size
        t_y_size = hsize
    else:
        wpercent = (new_y_size / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(wpercent)))
        t_x_size = wsize
        t_y_size = new_y_size
    # >> Resize
    img = img.resize((t_x_size, t_y_size), Image.ANTIALIAS)
    # >> Create a new image and paste original image centered.

    return img

# --- CONSTANTS ---
TITLE_X_SIZE = 450
TITLE_Y_SIZE = 450
TITLE_X_POS = 50
TITLE_Y_POS = 50

SNAP_X_SIZE = 450
SNAP_Y_SIZE = 450
SNAP_X_POS = 50
SNAP_Y_POS = 550

# --- Create fanart canvas ---
img = Image.new('RGB', (1920, 1080), (0, 0, 0))
# draw = ImageDraw.Draw(img)

# --- Title and Snap (colour rectangle for placement) ---
# img_title = Image.new('RGB', (TITLE_X_SIZE, TITLE_Y_SIZE), (25, 25, 25))
img_snap = Image.new('RGB', (SNAP_X_SIZE, SNAP_Y_SIZE), (0, 200, 0))

# --- Title and Snap (open PNG actual screenshot) ---
img_title = Image.open('dino_title.png')
print(img_title.format, img_title.size, img_title.mode)

# --- Resize keeping aspect ratio ---
img_title = PIL_resize_proportional(img_title, TITLE_X_SIZE, TITLE_Y_SIZE)
print(img_title.format, img_title.size, img_title.mode)

# --- Compsite fanart ---
# NOTE The box dimensions must have the same size as the pasted image.
img.paste(img_title, (TITLE_X_POS, TITLE_Y_POS, TITLE_X_POS + TITLE_X_SIZE, TITLE_Y_POS + TITLE_Y_SIZE))
img.paste(img_snap, (SNAP_X_POS, SNAP_Y_POS, SNAP_X_POS + SNAP_X_SIZE, SNAP_Y_POS + SNAP_Y_SIZE))

# --- Save test fanart ---
img.save('fanart.png')
