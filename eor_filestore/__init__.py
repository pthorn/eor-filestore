from .registry import Registry
from .file_id import src
from .category import Category
from .variant import Variant, VariantWorker
from .images.thumbnail import Thumbnail
from .images.autothumbnail import AutoThumbnail


registry = Registry()


def includeme(config):
    settings = config.get_settings()
    #my_settings = settings.get('eor-filestore', {})

    from eor_settings import ParseSettings

    ParseSettings(settings, prefix='eor-filestore')\
        .path('path', default='../store')

    config.add_route('eor-filestore.upload-default', R'/', request_method='POST')
    config.add_route('eor-filestore.upload', R'/:category', request_method='POST')
    # TODO generate URL pattern from SUBDIRS and SUBDIR_CHARS
    config.add_route('eor-filestore.get-image', R'/:category/:a/:b/:name', request_method='GET')
    config.add_route('eor-filestore.delete', R'/:name', request_method='DELETE')

    config.scan('.views')
