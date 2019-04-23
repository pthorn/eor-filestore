# config: utf-8

import logging
log = logging.getLogger(__name__)


class StoreException(Exception):

    def __init__(self, id=None, code=None, detail=None, exc=None):
        self.id = id
        self.code = code
        self.detail = detail or {}
        self.exc = exc

    def __str__(self):
        s = '%s(%s)' % (self.__class__.__name__, self.id)
        if self.detail:
            s = s + ' : %r' % (self.detail,)
        if self.exc:
            s = s + ' [%s]' % (str(self.exc),)
        return s

    def __repr__(self):
        return self.__str__()

    def response(self):
        resp = {'status': 'error'}
        if self.code:
            resp['code'] = self.code

        if self.id:
            self.detail['id'] = str(id)
        if self.detail:
            resp['detail'] = self.detail

        return resp


class BadCategoryException(StoreException):

    def __init__(self, category_name, **kwargs):
        super().__init__(
            code='bad-category',
            detail={
                'category': category_name,
            },
            **kwargs
        )


class BadVariantException(StoreException):

    def __init__(self, category_name, variant_name, **kwargs):
        super().__init__(
            code='bad-variant',
            detail={
                'category': category_name,
                'variant': variant_name
            },
            **kwargs
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
