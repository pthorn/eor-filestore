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
        if self.exc:
            return self.__class__.__name__ + ': ' + str(self.exc)
        else:
            return self.__class__.__name__

    def response(self):
        resp = {'status': 'error'}
        if self.code:
            resp['code'] = self.code
        if self.msg:
            resp['message'] = self.msg

        return resp


class BadNameException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='bad-name', **kwargs)


class NotAnImageException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='not-an-image', **kwargs)


class FileException(StoreException):

    def __init__(self, **kwargs):
        super().__init__(code='file-error', **kwargs)
