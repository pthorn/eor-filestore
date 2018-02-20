# coding: utf-8

from .file_id import FileID
from .variant import Variant
from .image_variants import AutoThumbnail
from .exceptions import BadVariantException


class Category(object):
    category = 'images'
    original = None
    variants = []

    @classmethod
    def save_new(cls, file_obj, client_filename):
        new_id = FileID.generate(client_filename, cls.category)
        category = cls(new_id)
        return category._save_new(file_obj)

    def __init__(self, parsed_id):
        self.parsed_id = parsed_id

        if not self.original:
            self.original = AutoThumbnail()  # TODO!

        # TODO do this once on app server startup
        if len(self.variants) == 0:
            self.variants.append(AutoThumbnail())

    def get_variant(self, variant_name=None):
        if variant_name is None:
            return self.original.get(
                category=self,
                parsed_id=self.parsed_id
            )  # TODO params?

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

        raise BadVariantException(self.category, variant_name)

    def _save_new(self, file_obj):
        # generate original
        self.original.get(
            category=self,
            parsed_id=self.parsed_id
        ).save(file_obj)

        # generate variants if reqd
        for v in self.variants:
            if v.generate_on_upload('WTF TODO'):
                v.get(
                    category=self,
                    parsed_id=self.parsed_id
                ).save(file_obj)

        return self
