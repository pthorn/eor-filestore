# coding: utf-8

import os
import re
import unicodedata
from uuid import uuid1

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

    def as_json(self):
        return dict(
            uuid=self.uuid,
            category=self.category,
            slug=self.slug,
            ext=self.ext
        )

    def __str__(self):
        return ','.join([self.uuid, self.category, self.slug, self.ext])

    def __repr__(self):
        return 'FileID(slug={}, uuid={}, category={}, ext={})'.format(
            self.slug, self.uuid, self.category, self.ext)


def src(request, id, variant=None):
    """
    :return: URL of the file
    """
    if not isinstance(id, FileID):
        id = FileID.parse(id)

    # TODO '//' + get_setting('static-domain') ?

    return request.route_url('eor-filestore.get-image',
        category=id.category, a=id.uuid[0], b=id.uuid[1],  # TODO respect SUBDIRS and SUBDIR_CHARS
        name=id.make_name(variant))


def _slugify(val, max_len=32):
    """
    from https://github.com/django/django/blob/master/django/utils/text.py#L413
    unicodedata.normalize(): http://stackoverflow.com/a/14682498/1092084
    """
    val = unicodedata.normalize('NFKD', val)
    val = val.replace('/', '-').replace('\\', '-')  # remove any path separators
    val = re.sub(r'[\s\.,]+', '-', val, flags=re.U)
    val = re.sub(r'[^\w-]', '', val, flags=re.U)
    val = val.strip('-').lower()
    return val[:max_len]
