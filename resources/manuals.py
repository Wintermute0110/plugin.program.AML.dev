# -*- coding: utf-8 -*-
# Advanced MAME Launcher PDF/CBZ/CBR image extraction.
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
# NOTE String literals are needed in this file so unicode_literals cannot be defined.
# from __future__ import unicode_literals
from PIL import Image
import zlib
import pprint
import types
import StringIO

# --- Kodi stuff ---
import xbmcgui, xbmcaddon

# --- Modules/packages in this plugin ---
from utils import *
from utils_kodi import *
from ReaderPDF import *

# --- Load pdfrw module ---
__addon_id__ = xbmcaddon.Addon().getAddonInfo('id').decode('utf-8')
pdfrw_FN = FileName('special://home/addons').pjoin(__addon_id__).pjoin('pdfrw')
sys.path.insert(0, pdfrw_FN.getPath())
from pdfrw import PdfReader
from pdfrw.objects.pdfarray import PdfArray
from pdfrw.objects.pdfname import BasePdfName

def manuals_extract_pages_PDFReader(status_dic, man_file_FN, img_dir_FN):
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

#
# Extracs an image from an xobj_dic object.
# Returns a PIL image object or None
#
def _extract_image_from_XObject(xobj_dic):
    log_debug('extract_image_from_XObject() Initialising ...')

    # --- Get image type and parameters ---
    if type(xobj_dic['/Filter']) is PdfArray:
        num_filters = len(xobj_dic['/Filter'])
        if num_filters > 1:
            log_info('Filter list = "{0}"'.format(unicode(xobj_dic['/Filter'])))
            log_info('XObject has more than 1 filter. Exiting.')
            sys.exit(1)
        filter_name = xobj_dic['/Filter'][0]
    elif type(xobj_dic['/Filter']) is BasePdfName:
        filter_name = xobj_dic['/Filter']
    elif type(xobj_dic['/Filter']) is types.NoneType:
        log_info('type(xobj_dic[\'/Filter\']) is types.NoneType. Skipping.')
        log_info('--- xobj_dic ---')
        log_info(pprint.pformat(xobj_dic))
        log_info('----------------')
        return None
    else:
        log_info('Unknown type(xobj_dic[\'/Filter\']) = "{0}"'.format(type(xobj_dic['/Filter'])))
        sys.exit(1)
    color_space = xobj_dic['/ColorSpace']
    bits_per_component = xobj_dic['/BitsPerComponent']
    height = int(xobj_dic['/Height'])
    width = int(xobj_dic['/Width'])

    # --- Print info ---
    log_debug('/Filter            {0}'.format(filter_name))
    log_debug('/ColorSpace        {0}'.format(color_space))
    log_debug('/BitsPerComponent  {0}'.format(bits_per_component))
    log_debug('/Height            {0}'.format(height))
    log_debug('/Width             {0}'.format(width))

    # NOTE /Filter = /FlateDecode may be PNG images. Check for magic number.
    jpg_magic_number   = '\xff\xd8'
    jp2_magic_number   = '\x00\x00\x00\x0C\x6A\x50\x20\x20\x0D\x0A\x87\x0A'
    png_magic_number   = '\x89\x50\x4E\x47'
    gif87_magic_number = '\x47\x49\x46\x38\x37\x61'
    gif89_magic_number = '\x47\x49\x46\x38\x39\x61'

    # >> Check for magic numbers
    stream_raw = xobj_dic.stream
    if stream_raw[0:2] == jpg_magic_number:
        log_debug('JPEG magic number detected!')
    elif stream_raw[0:12] == jp2_magic_number:
        log_debug('JPEG 2000 magic number detected!')
    elif stream_raw[0:4] == png_magic_number:
        log_debug('PNG magic number detected!')
    elif stream_raw[0:6] == gif87_magic_number:
        log_debug('GIF87a magic number detected!')
    elif stream_raw[0:6] == gif89_magic_number:
        log_debug('GIF89a magic number detected!')
    else:
        log_debug('Not known image magic number')

    # --- PNG embedded images ---
    img = None
    if filter_name == '/DCTDecode':
        log_debug('extract_image_from_XObject() Converting JPG into PIL IMG')
        memory_f = StringIO.StringIO(xobj_dic.stream)
        img = Image.open(memory_f)

    elif filter_name == '/JPXDecode':
        log_debug('extract_image_from_XObject() Converting JPEG 2000 into PIL IMG')
        memory_f = StringIO.StringIO(xobj_dic.stream)
        img = Image.open(memory_f)

    # --- RGB images with FlateDecode ---
    elif color_space == '/DeviceRGB' and filter_name == '/FlateDecode':
        if filter_name == '/FlateDecode':
            log_debug('stream is compressed with /FlateDecode filter')
            contents_comp = xobj_dic.stream
            contents_plain = zlib.decompress(contents_comp)
            img = Image.frombytes('RGB', (width, height), contents_plain)
        else:
            log_debug('Unknown filter "{0}". Exiting.'.format(filter_name))

    # --- Monochrome images, 1 bit per pixel ---
    elif color_space == '/DeviceGray':
        log_debug('extract_image_from_XObject() Saving monochrome image')
        if filter_name == '/FlateDecode':
            log_debug('stream is compressed with /FlateDecode filter')
            contents_comp = xobj_dic.stream
            contents_plain = zlib.decompress(contents_comp)
            log_debug('len(contents_comp) = {0:,d}'.format(len(contents_comp)))
            log_debug('len(contents_plain) = {0:,d}'.format(len(contents_plain)))

            # --- Save image file ---
            img = Image.frombytes('1', (width, height), contents_plain)
        else:
            log_debug('Unknown filter "{0}". Exiting.'.format(filter_name))
    else:
        log_debug('Unrecognised image type. It cannot be extracted. Skipping.')

    return img

def manuals_extract_pages_pdfrw(status_dic, PDF_file_FN, img_dir_FN):
    # --- Load and parse PDF ---
    reader = PdfReader(PDF_file_FN.getPath())
    log_info('PDF file "{0}"'.format(PDF_file_FN.getPath()))
    log_info('PDF has {0} pages'.format(reader.numPages))

    # --- Iterate page by page ---
    image_counter = 0
    for i, page in enumerate(reader.pages):
        # --- Iterate /Resources in page ---
        # log_debug('###### Processing page {0} ######'.format(i))
        resource_dic = page['/Resources']
        for r_name, resource in resource_dic.iteritems():
            # >> Skip non /XObject keys in /Resources
            if r_name != '/XObject': continue

            # >> DEBUG dump /XObjects dictionary
            # print('--- resource ---')
            # pprint(resource)
            # print('----------------')

            # >> Traverse /XObject dictionary data. Each page may have 0, 1 or more /XObjects
            # >> If there is more than 1 image in the page there could be more than 1 /XObject.
            # >> Some /XObjects are not images, for example, /Subtype = /Form.
            # >> NOTE Also, images may be inside the /Resources of a /From /XObject.
            img_index = 0
            for xobj_name, xobj_dic in resource.iteritems():
                xobj_type = xobj_dic['/Type']
                xobj_subtype = xobj_dic['/Subtype']
                # >> Skip XObject forms
                if xobj_subtype == '/Form':
                    # >> NOTE There could be an image /XObject in the /From : /Resources dictionary.
                    log_info('Skipping /Form /XObject')
                    log_info('--- xobj_dic ---')
                    log_info(pprint.pformat(xobj_dic))
                    log_info('----------------')
                    continue

                # --- Print info ---
                log_debug('------ Page {0:02d} Image {1:02d} ------'.format(i, img_index))
                log_debug('xobj_name     {0}'.format(xobj_name))
                log_debug('xobj_type     {0}'.format(xobj_type))
                log_debug('xobj_subtype  {0}'.format(xobj_subtype))
                # log_debug('--- xobj_dic ---')
                # log_debug(pprint.pformat(xobj_dic))
                # log_debug('----------------')

                # --- Extract image ---
                # Returns a PIL image object or None
                img = _extract_image_from_XObject(xobj_dic)

                # --- Save image ---
                if img:
                    img_basename_str = 'Image_page{0:02d}_img{1:02d}.png'.format(i, img_index)
                    img_path_str = img_dir_FN.pjoin(img_basename_str).getPath()
                    log_debug('Saving IMG "{0}"'.format(img_path_str))
                    img.save(img_path_str, 'PNG')
                    image_counter += 1
                    img_index += 1
                else:
                    log_warning('Error extracting image from /XObject')
    log_info('Extracted {0} images from PDF'.format(image_counter))

    # --- Initialise status_dic ---
    status_dic['manFormat'] = 'PDF'
    status_dic['numImages'] = image_counter

#
# Detect manual file type (PDF, CBZ, CBR) and call extracter img function
#
def manuals_extract_pages(status_dic, man_file_FN, img_dir_FN):
    # manuals_extract_pages_PDFReader(status_dic, man_file_FN, img_dir_FN)
    manuals_extract_pages_pdfrw(status_dic, man_file_FN, img_dir_FN)
