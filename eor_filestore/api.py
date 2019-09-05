from .file_id import FileID
from .exceptions import BadCategoryException, BadNameException


def delete_by_id(file_id):
    try:
        parsed_id = FileID.parse(file_id)
    except (BadCategoryException, BadNameException):
        return

    from . import registry

    Category = registry.get_category(parsed_id.category)
    category = Category(parsed_id)
    category.delete()
