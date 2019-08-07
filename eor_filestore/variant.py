# coding: utf-8

import logging
log = logging.getLogger(__name__)

import os
import shutil
import errno

from eor_settings import get_setting

from .attrdict import AttrDict


class Variant(object):
    NEVER      = 'NEVER'
    ON_UPLOAD  = 'ON_UPLOAD'
    ON_REQUEST = 'ON_REQUEST'

    def __init__(self, name=None, save=NEVER, **kwargs):
        """
        Extend in subclasses to pass more config parameters
        :param name: variant name
        :param save: one of Variant.NEVER, ON_UPLOAD, ON_REQUEST
        :param kwargs: additional config parameters (will be saved into self.config)
        """
        self.config = AttrDict(
            name = name,
            save = save,
            **kwargs
        )

    def matches_exactly(self, variant_name):
        return variant_name == self.config.name

    def matches_wildcard(self, variant_name):
        """
        Implement in a subclass to support wilcard matching.
        :param variant_name:
        :return: boolean
        """
        return False

    def get_worker_class(self):
        """
        Implement in a subclass
        :return: worker class
        """
        return VariantWorker

    def get(self, category, parsed_id, variant_name):
        """
        Called by Category.get_variant()
        """
        return self.get_worker_class()(
            factory=self, config=self.config,
            category=category, parsed_id=parsed_id, variant_name=variant_name
        )


class VariantWorker(object):
    def __init__(self, factory, config, category, parsed_id, variant_name):
        """
        This constructor is called by Variant.get()
        """
        self.factory = factory
        self.config = config
        self.category = category
        self.parsed_id = parsed_id
        self.variant_name = variant_name

    def exists(self):
        return os.path.exists(self.fs_path())

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

        return os.path.abspath(os.path.join(*comps))

    def save(self, file_obj):
        """
        Save newly uploaded file
        :param file_obj: cgi.FieldStorage object
        """
        save_path = self.fs_path()

        if os.path.exists(save_path):
            log.warn('VariantWorker.save(): overwriting existing file: %s', save_path)
        else:
            log.debug('VariantWorker.save(): saving to path: %s', save_path)

        self._mkdirs()

        out_file = open(save_path, 'wb')
        shutil.copyfileobj(file_obj, out_file)

    def generate(self):
        """
        :return: tuple (file-like object, size for Content-Length)
        """
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()  # TODO!

    def _mkdirs(self):
        save_dir = os.path.dirname(self.fs_path())
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except OSError as e:
                # this can happen if multiple files are uploaded concurrently
                if e.errno != errno.EEXIST:
                    raise

# TODO
SUBDIRS = 2
SUBDIR_CHARS = 1

def _subdirs(uuid):
    subdirs = [uuid[n*SUBDIR_CHARS:(n+1)*SUBDIR_CHARS]
               for n in range(SUBDIRS)]
    return os.path.join(*subdirs)
