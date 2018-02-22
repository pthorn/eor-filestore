# coding: utf-8

import os
import errno
import math
from io import BytesIO

from PIL import Image

from ..exceptions import FileException, NotAnImageException

import logging
log = logging.getLogger(__name__)



def get_image_format(file_obj):
    ext = os.path.splitext(file_obj.filename)[1]
    if ext.lower() in('.gif', '.png'):
        return 'png'
    else:
        return 'jpg'


def open_image(source_file):
    try:
        image = Image.open(source_file)
    except IOError as e:
        if str(e).find('annot identify image file') != -1:
            raise NotAnImageException()
        else:
            raise FileException(exc=e)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    return image


def make_thumbnail_crop_to_size(image, size):
    image = image.copy()

    # calculate crop window centered on image
    # TODO!!! won't work if original is smaller than thumbnail

    factor = min(float(image.size[0]) / size[0],  float(image.size[1]) / size[1])
    crop_size = (size[0] * factor, size[1] * factor)

    crop_window = (
        math.trunc((image.size[0] - crop_size[0]) / 2),  # left
        math.trunc((image.size[1] - crop_size[1]) / 2),  # upper
        math.trunc((image.size[0] + crop_size[0]) / 2),  # right
        math.trunc((image.size[1] + crop_size[1]) / 2)   # lower
    )

    #print '\n----------', 'image.size', image.size, 'thumb_def.size', thumb_def.size, 'factor', factor, 'crop_size', crop_size, 'crop', crop

    image = image.crop(crop_window)
    image.thumbnail(size, Image.ANTIALIAS)

    return image


def make_thumbnail_keep_proportions(image, size):
    image = image.copy()

    if image.size[0] > size[0] or image.size[1] > size[1]:
            image.thumbnail(size, Image.ANTIALIAS)

    return image


def save_image(image, save_path, quality, progressive=False):
    """
    """
    if os.path.exists(save_path):
        log.warn('overwriting existing image: %s', save_path)

    image.save(save_path, quality=quality, progressive=progressive)


def save_image_to_buffer(image, extension, quality, progressive=False):
    data = BytesIO()
    # Pillow uses name attribute to infer image format
    data.name = 'foo.{}'.format(extension)
    image.save(data, quality=quality, progressive=progressive)

    # calculate size
    data.seek(0, os.SEEK_END)
    size = data.tell()
    data.seek(0)

    return data, size
