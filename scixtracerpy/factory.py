# -*- coding: utf-8 -*-
"""SciXtracerPy factory module.

Generic Interface to Object Factory

Classes
-------
ObjectFactory

"""

from .request_local import RequestLocalServiceBuilder


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


class RequestServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


requestServices = RequestServiceProvider()
requestServices.register_builder('LOCAL', RequestLocalServiceBuilder())
