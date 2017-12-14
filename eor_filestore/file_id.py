# coding: utf-8

import os
from .exceptions import BadNameException

import logging
log = logging.getLogger(__name__)


class FileID(object):

    @classmethod
    def generate(cls, orig_filename, category):
        name, ext = os.path.splitext(os.path.basename(orig_filename))
        return cls(
            slug=_slugify(name),
            uuid=uuid1().hex,
            category=category,
            ext=ext.lstrip('.').lower()
        )

    @classmethod
    def parse(cls, id):
        split = id.split(',')
        if len(split) != 4:
            raise BadNameException(msg='bad id %r' % id)

        return cls(
            slug=split[2],
            uuid=split[0],
            category=split[1],
            ext=split[-1]
        )

    @classmethod
    def parse_name(cls, name, category):
        split = name.split('.')
        if len(split) not in (3, 4):
            raise BadNameException(msg='bad name %r' % name)

        # TODO check uuid using regex

        # return (id, variant)
        return cls(
            slug=split[0],
            uuid=split[1],
            category=category,
            ext=split[-1]
        ), None if len(split) == 3 else split[2]

    def __init__(self, slug, uuid, category, ext):
        self.slug = slug
        self.uuid = uuid
        self.category = category
        self.ext = ext

    def make_name(self, variant=None):
        name_split = [self.slug, self.uuid]
        if variant:
            name_split.append(variant)
        name_split.append(self.ext)
        return '.'.join(name_split)

    def __str__(self):
        return ','.join([self.uuid, self.category, self.slug, self.ext])

    def __repr__(self):
        return 'FileID(slug={}, uuid={}, category={}, ext={})'.format(
            self.slug, self.uuid, self.category, self.ext)
