import os
import re
from io import BytesIO
import unicodedata
from uuid import uuid1
from eor_settings import get_setting
from .image_ops import open_image, save_image, make_thumbnail_crop_to_size
from .exceptions import BadNameException

import logging
log = logging.getLogger(__name__)


# TODO config
DEFAULT_QUALITY = 60
SUBDIRS = 2
SUBDIR_CHARS = 1


class Image(object):
    """
    image = Image.new(fieldstorage.filename, fieldstorage.file)
    image.id

    image = Image.with_id(user.avatar).variant('800x600F').url()
    <img src="${Image.src(user.avatar_img, '800x600F')}">
    """

    @classmethod
    def new(cls, orig_name, data, category):
        """
        :return:
        """
        new_id = ImageID.generate(orig_name, category)
        image = cls(new_id)
        variant = image.variant()

        # TODO move this somewhere more appropriate
        pil_image = open_image(data)
        save_image(pil_image, variant.fs_path(), DEFAULT_QUALITY)  # TODO settable quality

        return image

    @classmethod
    def with_string_id(cls, id):
        return cls(ImageID.parse(id))

    def __init__(self, parsed_id):
        self.parsed_id = parsed_id

    def variant(self, variant=None):
        return Variant(self, variant)

    def make_permanent(self):
        """
        :return:
        """
        pass  # TODO 2nd stage

    def delete(self):
        """
        :return:
        """
        pass


class Variant(object):

    def __init__(self, image, variant=None):
        self.image = image
        self.variant = variant

    def exists(self):
        return os.path.exists(self.fs_path())

    # def get_file_obj(self):
    #     """
    #     :return:
    #     """
    #     return open(self.fs_path(), 'rb')

    def generate(self):
        """
        :return: (BytesIO object with image data, data length for Content-Length)
        """
        original = self.image.variant()
        pil_original_image = open_image(original.fs_path())
        size, algo = _parse_thumbspec(self.variant)

        pil_variant = make_thumbnail_crop_to_size(pil_original_image, size)  # TODO
        SAVE_VARIANT = False  # TODO
        if SAVE_VARIANT:
            save_image(pil_variant, self.fs_path(), DEFAULT_QUALITY)

        data = BytesIO()
        # Pillow uses name attribute to infer image format
        data.name = 'foo.{}'.format(self.image.parsed_id.ext)
        pil_variant.save(data)  # TODO quality
        data.seek(0, os.SEEK_END)
        length = data.tell()
        data.seek(0)

        return data, length

    # def url(self, variant=None):
    #     """
    #     :return: URL of the file
    #     """
    #     filename = self._filename(variant)
    #     return os.path.join(self._url_prefix(), self.type, self._subdirs(filename), filename)

    def fs_path(self):
        """
        :return: absolute filesystem path to the file
        """
        id = self.image.parsed_id
        comps = [get_setting('eor-filestore.path')]
        if id.category:
            comps.append(id.category)
        comps.append(_subdirs(id.uuid))
        comps.append(id.make_name(self.variant))

        return os.path.join(*comps)


class ImageID(object):

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
        return 'ImageID(slug={}, uuid={}, category={}, ext={})'.format(
            self.slug, self.uuid, self.category, self.ext)


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

def _subdirs(uuid):
    subdirs = [uuid[n*SUBDIR_CHARS:(n+1)*SUBDIR_CHARS]
               for n in range(SUBDIRS)]
    return os.path.join(*subdirs)

def _parse_thumbspec(spec):
    p = re.compile(r'(\d+)x(\d+)(.?)')
    m = p.match(spec)
    if not m:
        raise BadNameException(msg='bad thumbspec %r' % spec)

    size = (int(m.group(1)), int(m.group(2)))
    algo = m.group(3) or 'X'  # TODO default algo
    return size, algo

def src(request, id, variant=None):
    """
    :return: URL of the file
    """
    if not isinstance(id, ImageID):
        id = ImageID.parse(id)

    # TODO '//' + get_setting('static-domain') ?

    return request.route_url('eor-filestore.get-image',
        category=id.category, a=id.uuid[0], b=id.uuid[1],  # TODO respect SUBDIRS and SUBDIR_CHARS
        name=id.make_name(variant))
