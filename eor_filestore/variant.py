# coding: utf-8

import os

from eor_settings import get_setting


class VariantFactory(object):
    def matches_exactly(self, variant_name):
        return False

    def matches_wildcard(self, variant_name):
        return False

    def generate_on_upload(self, variant_name):
        return False

    def get(self, **kwargs):
        return Variant(**kwargs)  # TODO pass self?


class Variant(object):

    def __init__(self, category, parsed_id, variant_name=None):
        #self.config = config  # passed from factory
        self.category = category
        self.parsed_id = parsed_id
        self.variant_name = variant_name

    def save(self):
        pass

    def exists(self):
        return os.path.exists(self.fs_path())

    def generate(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()  # TODO!

    def fs_path(self):
        """
        :return: absolute filesystem path to the file
        """
        id = self.parsed_id

        comps = [get_setting('eor-filestore.path')]
        if id.category:
            comps.append(id.category)
        comps.append(_subdirs(id.uuid))
        comps.append(id.make_name(self.variant_name))

        return os.path.join(*comps)


# TODO
SUBDIRS = 2
SUBDIR_CHARS = 1

def _subdirs(uuid):
    subdirs = [uuid[n*SUBDIR_CHARS:(n+1)*SUBDIR_CHARS]
               for n in range(SUBDIRS)]
    return os.path.join(*subdirs)
