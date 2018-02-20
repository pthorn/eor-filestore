# config: utf-8

import logging
log = logging.getLogger(__name__)


class StoreException(Exception):

    def __init__(self, code=None, msg=None, detail=None, exc=None):
        self.code = code
        self.msg = msg
        self.detail = detail
        self.exc = exc

    def __str__(self):
        s = '%s(%s)' % (self.__class__.__name__, self.msg)
        if self.exc:
            s = s + ': ' + str(self.exc)
        return s

    def __repr__(self):
        return self.__str__()

    def response(self):
        resp = {'status': 'error'}
        if self.code:
            resp['code'] = self.code
        if self.msg:
            resp['message'] = self.msg

        return resp


class BadCategoryException(StoreException):

    def __init__(self, category_name):
        super().__init__(
            code='bad-category',
            msg='Category not registered: %r' % category_name,
            detail=category_name
        )


class BadVariantException(StoreException):

    def __init__(self, category_name, variant_name):
        super().__init__(
            code='bad-variant',
            msg='Variant not registered: %r.%r' % (category_name, variant_name)
        )


class BadNameException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='bad-name', **kwargs)


class NotAnImageException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='not-an-image', **kwargs)


class FileException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='file-error', **kwargs)
