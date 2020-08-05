# coding: utf-8

from .exceptions import BadCategoryException

from .category import Category

import logging
log = logging.getLogger(__name__)


class Registry(object):

    def __init__(self):
        self.category_delegates = {}

    def category(self):
        """
        decorator that registers category delegates
        @registry.category()
        class FooCategory(CategoryDelegate):
            ...
        """
        def decorate(delegate):
            if delegate.category is None:
                raise ValueError('Registry.category(): %r must have attribute "category"' % delegate)

            if delegate.category in self.category_delegates:
                raise ValueError('Registry.category(): %r: name %r already registered for class %r' % (
                    delegate, delegate.category, cls.category_delegates[delegate.category]))

            self.category_delegates[delegate.category] = delegate

            log.debug('Registered category %r', delegate.category)

            return delegate

        return decorate

    def get_category(self, category_name):
        try:
            return self.category_delegates[category_name]
        except KeyError:
            if len(self.category_delegates) == 0 and category_name == 'images':
                c = Category
                self.category_delegates['images'] = c
                return c
            raise BadCategoryException(category_name)
