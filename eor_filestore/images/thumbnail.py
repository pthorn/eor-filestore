import os
import re
from io import BytesIO

from ..variant import Variant, VariantWorker
from .image_ops import (
    open_image,
    save_image,
    save_image_to_buffer,
    make_thumbnail_crop_to_size,
    make_thumbnail_keep_proportions
)
from ..attrdict import AttrDict
from ..exceptions import BadNameException


class Thumbnail(Variant):
    FILL = 'FILL'
    FIT = 'FIT'

    algos = {
        FILL: make_thumbnail_crop_to_size,
        FIT: make_thumbnail_keep_proportions
    }

    def __init__(self, name, size, save=Variant.NEVER,
                 quality=50, resize=FIT, progressive_jpeg=False):
        super().__init__(name, save, size=size, quality=quality,
                         resize=resize, progressive_jpeg=progressive_jpeg)

    def get_worker_class(self):
        return ThumbnailWorker


class ThumbnailWorker(VariantWorker):

    def save(self, file_obj):
        pil_image = open_image(file_obj)
        resized_image = self._resize(pil_image)
        self._save_to_file(resized_image)

    def generate(self):
        """
        :return: (BytesIO object with image data, data length for Content-Length)
        """
        original = self.category.get_variant()
        pil_original_image = open_image(original.fs_path())

        pil_variant = self._resize(pil_original_image)

        if self.config.save in (Variant.ON_REQUEST, Variant.ON_UPLOAD):
            self._save_to_file(pil_variant)

        data, size = save_image_to_buffer(
            pil_variant, self.parsed_id.ext, self.config.quality
        )

        return data, size

    def _save_to_file(self, pil_image):
        print('ThumbnailWorker._save_to_file()', self.fs_path(), pil_image.size)
        self._mkdirs()
        save_image(pil_image, self.fs_path(), quality=self.config.quality,
                   progressive=self.config.progressive_jpeg)
        # TODO jpegoptim

    def _resize(self, pil_image, size=None, resize=None):
        size = size or self.config.size
        resize = resize or self.config.resize

        pil_thumb = Thumbnail.algos[resize](pil_image, size)
        return pil_thumb
