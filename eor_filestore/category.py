# coding: utf-8

import os
import pathlib

from eor_settings import get_setting

from .file_id import FileID
from .variant import Variant, _subdirs
from .images.autothumbnail import AutoThumbnail
from .exceptions import BadVariantException


class Category(object):
    category = 'images'
    #original = None
    variants = []

    @classmethod
    def save_new(cls, file_obj, client_filename):
        new_id = FileID.generate(client_filename, cls.category)
        category = cls(new_id)
        return category._save_new(file_obj)

    def __init__(self, parsed_id):
        self.parsed_id = parsed_id

        # TODO do this once on app server startup
        if len(self.variants) == 0:
            self.variants.append(Variant(save=Variant.ON_UPLOAD))
            self.variants.append(AutoThumbnail())

    def get_variant(self, variant_name=None):
        for v in self.variants:
            if v.matches_exactly(variant_name):
                return v.get(
                    category=self,
                    parsed_id=self.parsed_id,
                    variant_name=variant_name
                )  # TODO params?

        for v in self.variants:
            if v.matches_wildcard(variant_name):
                return v.get(
                    category=self,
                    parsed_id=self.parsed_id,
                    variant_name=variant_name
                )  # TODO params?

        raise BadVariantException(self.category, variant_name, id=self.parsed_id)

    def delete(self):
        path = pathlib.Path(self.get_fs_path(), _subdirs(self.parsed_id.uuid))

        for p in path.glob(self.parsed_id.make_wildcard()):
            os.unlink(str(p))

    def list_files(self):
        p = pathlib.Path(self.get_fs_path())
        return [
            FileID.parse_name(f.name, self.category)[0].as_json()
            for f in p.rglob("*") if f.is_file()
        ]

    def get_fs_path(self):
        """Get path to directory where files for this category are stored."""
        comps = [get_setting('eor-filestore.path'), self.category]
        return os.path.abspath(os.path.join(*comps))

    def _save_new(self, file_obj):
        for v in self.variants:
            print('v.config', v.config)
            if v.config.save == Variant.ON_UPLOAD:
                v.get(
                    category=self,
                    parsed_id=self.parsed_id,
                    variant_name=v.config.name
                ).save(file_obj)
                file_obj.seek(0)  # rewind

        return self
