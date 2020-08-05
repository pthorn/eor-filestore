import cgi
from pyramid.view import view_config
from pyramid.response import Response, FileResponse, FileIter, _guess_type
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest

from . import registry
from .file_id import FileID
from .api import src
from .exceptions import StoreException, FileException

import logging
log = logging.getLogger(__name__)


# TODO config
FILE_PARAM = 'file'
DEFAULT_CATEGORY='images'


@view_config(route_name='eor-filestore.get-image')
def get(request):
    image_name = request.matchdict['name']
    category_name = request.matchdict['category']

    # TODO exceptions
    parsed_id, variant_name = FileID.parse_name(image_name, category_name)

    try:
        Category = registry.get_category(category_name)
        variant = Category(parsed_id).get_variant(variant_name)
    except StoreException as e:
        log.warn('1 %r', e)  # TODO
        raise HTTPNotFound()

    if variant.exists():
        return FileResponse(variant.fs_path(), request=request)

    try:
        data, length = variant.generate()
    except FileException as e:
        log.warn('2 %r', e)
        raise HTTPNotFound()
    except StoreException as e:
        log.warn('2 %r', e)
        raise HTTPNotFound()

    content_type, content_encoding = _guess_type('x.' + variant.parsed_id.ext)

    return Response(
        request=request,
        app_iter=FileIter(data),
        content_type=content_type,
        content_encoding=content_encoding,
        content_length = length
        #last_modified = now TODO
    )


@view_config(route_name='eor-filestore.get-list', renderer='json')
def get_list(request):
    category_name = request.matchdict['category']

    try:
        Category = registry.get_category(category_name)
    except StoreException as e:
        log.warn('1 %r', e)  # TODO
        raise HTTPNotFound()

    category = Category(None)  # TODO API workaroud

    return {
        'status': 'ok',
        'data': category.list_files()
    }


@view_config(route_name='eor-filestore.upload-default', renderer='json')
@view_config(route_name='eor-filestore.upload', renderer='json')
def upload(request):
    category_name = request.matchdict.get('category', DEFAULT_CATEGORY)

    try:
        fieldstorage = request.params[FILE_PARAM]
    except KeyError:
        raise HTTPBadRequest()

    if not isinstance(fieldstorage, cgi.FieldStorage):
        raise HTTPBadRequest()

    try:
        Category = registry.get_category(category_name)
        category = Category.save_new(fieldstorage.file, fieldstorage.filename)
    except StoreException as e:
        return e.response()

    return {
        'status': 'ok',
        'data': {
            'id': str(category.parsed_id),
            'id_parts': category.parsed_id.as_json(),
            'src': src(request, category.parsed_id)  # TODO variant_name = first variant name?
        }
    }


@view_config(route_name='eor-filestore.delete', renderer='json')
def delete(request):
    image_name = request.matchdict['name']
    category_name = request.matchdict['category']

    # TODO exceptions
    parsed_id, variant_name = FileID.parse_name(image_name, category_name)

    try:
        Category = registry.get_category(category_name)
        category = Category(parsed_id)
        category.delete()
    except StoreException as e:
        return e.response()

    return {'status': 'ok'}
