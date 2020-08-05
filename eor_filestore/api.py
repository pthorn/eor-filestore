from .file_id import FileID
from .exceptions import (
    StoreException, BadCategoryException, BadNameException
)


def src(request, id, variant=None):
    """
    :return: URL of the file
    """
    if not isinstance(id, FileID):
        try:
            id = FileID.parse(id)
        except StoreException:
            return ''

    # TODO '//' + get_setting('static-domain') ?

    return request.route_url('eor-filestore.get-image',
        category=id.category, a=id.uuid[0], b=id.uuid[1],  # TODO respect SUBDIRS and SUBDIR_CHARS
        name=id.make_name(variant))


def delete_by_id(file_id):
    try:
        parsed_id = FileID.parse(file_id)
    except (BadCategoryException, BadNameException):
        return

    from . import registry

    try:
        Category = registry.get_category(parsed_id.category)
    except BadCategoryException:
        return

    category = Category(parsed_id)
    category.delete()
