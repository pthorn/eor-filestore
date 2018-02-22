import os
import re
from io import BytesIO

from .thumbnail import Thumbnail, ThumbnailWorker
from ..variant import VariantFactory, Variant
from .image_ops import (
    open_image,
    save_image,
    save_image_to_buffer,
    make_thumbnail_crop_to_size
)
from ..attrdict import AttrDict
from ..exceptions import BadNameException


class AutoThumbnail(Thumbnail):
    """
    generates thumbnails for variant name such as 800x600
    """
    def __init__(self, save=VariantFactory.NEVER, quality=50,
                 default_resize=Thumbnail.FIT, progressive_jpeg=False):
        super().__init__(None, save, quality=quality, resize=default_resize,
                         progressive_jpeg=progressive_jpeg)

    def matches_wildcard(self, variant_name):
        return thumbspec_regex.match(variant_name) is not None

    def get_worker_class(self):
        return AutoThumbnailWorker


class AutoThumbnailWorker(ThumbnailWorker):

    def generate(self):
        """
        :return: (BytesIO object with image data, data length for Content-Length)
        """
        original = self.category.get_variant()
        pil_original_image = open_image(original.fs_path())
        size, algo = _parse_thumbspec(self.variant_name)

        pil_variant = self._resize(pil_original_image, size=size, resize=algo)

        if self.config.save in (VariantFactory.ON_REQUEST, VariantFactory.ON_UPLOAD):
            self._save_to_file(pil_variant)

        data, size = save_image_to_buffer(
            pil_variant, self.parsed_id.ext, self.config.quality,
            progressive=self.config.progressive_jpeg
        )

        return data, size


thumbspec_regex = re.compile(r'(\d+)x(\d+)([a-zA-Z]?)')

def _parse_thumbspec(spec):
    """
    :param spec: '800x600F'
    :return: ((800, 600), Thumbnail.FILL)
    """
    m = thumbspec_regex.match(spec)
    if not m:
        raise BadNameException(msg='bad thumbspec %r' % spec)

    size = (int(m.group(1)), int(m.group(2)))
    algo = m.group(3).upper() or 'T'

    algos = {
        'L': Thumbnail.FILL,
        'T': Thumbnail.FIT
    }

    try:
        return size, algos[algo]
    except KeyError:
        raise BadNameException(msg='bad resize modifier %r' % algo)
