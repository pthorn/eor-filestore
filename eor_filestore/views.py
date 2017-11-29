import cgi
from pyramid.view import view_config
from pyramid.response import Response, FileResponse, FileIter, _guess_type
from pyramid.httpexceptions import HTTPNotFound, HTTPBadRequest
from .image import Image, parse_name, src
from .exceptions import StoreException, FileException

import logging
log = logging.getLogger(__name__)


# TODO config
FILE_PARAM = 'file'
DEFAULT_CATEGORY='images'


@view_config(route_name='eor-filestore.get-image')
def get(request):
    image_name = request.matchdict['name']
    category = request.matchdict['category']

    parsed_id, variant = parse_name(image_name, category)

    #try:
    variant = Image(parsed_id).variant(variant)
    #except NoImage:
    #    raise HTTPNotFound()

    if variant.exists():
        return FileResponse(variant.fs_path(), request=request)

    try:
        data, length = variant.generate()
    except FileException as e:
        raise HTTPNotFound()
    except StoreException as e:
        log.warn('%r', e)
        raise HTTPNotFound()

    content_type, content_encoding = _guess_type('x.' + variant.image.parsed_id.ext)

    return Response(
        request=request,
        app_iter=FileIter(data),
        content_type=content_type,
        content_encoding=content_encoding,
        content_length = length
        #last_modified = now TODO
    )


@view_config(route_name='eor-filestore.upload-default', renderer='json')
@view_config(route_name='eor-filestore.upload', renderer='json')
def upload(request):
    category = request.matchdict.get('category', DEFAULT_CATEGORY)

    try:
        fieldstorage = request.params[FILE_PARAM]
    except KeyError:
        raise HTTPBadRequest()

    if not isinstance(fieldstorage, cgi.FieldStorage):
        raise HTTPBadRequest()

    try:
        image = Image.new(fieldstorage.filename, fieldstorage.file, category)
    except StoreException as e:
        return e.response()

    return {
        'status': 'ok',
        'data': {
            'id': str(image.parsed_id),
            'src': src(request, image.parsed_id)
        }
    }


@view_config(route_name='eor-filestore.delete', renderer='json')
def delete(request):
    image_name = request.matchdict['name']

    #try:
    image = Image.with_name(image_name)
    image.delete()
    #except:
    #    raise HTTPNotFound()
    # return {'status': 'error', 'message': '...'}

    return {'status': 'ok'}
