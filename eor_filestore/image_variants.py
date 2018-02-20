import os
import re
from io import BytesIO

from .variant import VariantFactory, Variant
from .image_ops import (
    open_image,
    save_image,
    save_image_to_buffer,
    make_thumbnail_crop_to_size
)
from .attrdict import AttrDict
from .exceptions import BadNameException


TODO = 0  # TODO

class AutoThumbnail(VariantFactory):
    def __init__(self, quality=40, resize=TODO, save_thumbs=False):
        self.config = AttrDict(
            quality = quality,
            resize = resize,
            save_thumbs=False
        )

    def matches_wildcard(self, variant_name):
        # TODO images only! extension or content type?
        # print("\n - - - - - variant_name", variant_name, type(variant_name))

        if variant_name is None:
            return True

        return thumbspec_regex.match(variant_name) is not None

    def get(self, **kwargs):
        return AutoThumbnailWorker(config=self.config, **kwargs)


class AutoThumbnailWorker(Variant):
    """
    generates thumbnails for variant name such as 800x600
    """

    def __init__(self, config, category, parsed_id, variant_name=None):
        super().__init__(category, parsed_id, variant_name)
        self.config = config

    def save(self, file_obj):
        pil_image = open_image(file_obj)
        save_image(pil_image, self.fs_path(), self.config.quality)

        #return image

    def generate(self):
        """
        :return: (BytesIO object with image data, data length for Content-Length)
        """
        original = self.category.get_variant()
        pil_original_image = open_image(original.fs_path())
        size, algo = _parse_thumbspec(self.variant_name)

        pil_variant = make_thumbnail_crop_to_size(pil_original_image, size)

        if self.config.save_thumbs:
            save_image(pil_variant, self.fs_path(), self.config.quality)

        data, size = save_image_to_buffer(
            pil_variant, self.parsed_id.ext, self.config.quality)

        return data, size


class Thumbnail(VariantFactory):
    def __init__(self, name, size, quality=50, resize=TODO, save_thumbs=False):
        self.config = AttrDict(
            name = name,
            size = size,
            quality = quality,
            resize = resize,
            save_thumbs=save_thumbs
        )

    def matches_exactly(self, variant_name):
        return variant_name == self.config.name

    def get(self, **kwargs):
        return ThumbnailWorker(config=self.config, **kwargs)


class ThumbnailWorker(Variant):
    def __init__(self, config, category, parsed_id, variant_name=None):
        super().__init__(category, parsed_id, variant_name)
        self.config = config

    # TODO
    def generate(self):
        """
        :return: (BytesIO object with image data, data length for Content-Length)
        """
        original = self.category.get_variant()
        pil_original_image = open_image(original.fs_path())

        pil_variant = make_thumbnail_crop_to_size(pil_original_image, self.config.size)

        if self.config.save_thumbs:
            save_image(pil_variant, self.fs_path(), self.config.quality)

        data, size = save_image_to_buffer(
            pil_variant, self.parsed_id.ext, self.config.quality)

        return data, size


thumbspec_regex = re.compile(r'(\d+)x(\d+)(.?)')

def _parse_thumbspec(spec):
    """
    :param spec: '800x600x'
    :return: ((800, 600), 'x')
    """

    m = thumbspec_regex.match(spec)
    if not m:
        raise BadNameException(msg='bad thumbspec %r' % spec)

    size = (int(m.group(1)), int(m.group(2)))
    algo = m.group(3) or 'X'  # TODO default algo
    return size, algo
