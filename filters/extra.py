# -*- coding: utf-8 -*-

import base64

from jinja2.ext import Extension


class GenericGlobal(Extension):
    def __init__(self, environment):
        super(GenericGlobal, self).__init__(environment)
        environment.filters['b64encode'] = self.b64encode

    @staticmethod
    def b64encode(s, encoding='utf-8'):
        return base64.b64encode(s.encode(encoding=encoding)).decode(encoding)
