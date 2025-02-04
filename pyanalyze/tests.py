# static analysis: ignore
"""

Functions to be used in test_scope unit tests.

"""

from typing import ClassVar
from asynq import asynq, async_proxy, AsyncTask, ConstFuture, get_async_fn, result
from asynq.decorators import AsyncDecorator
import qcore

ASYNQ_METHOD_NAME = "asynq"
ASYNQ_METHOD_NAMES = ("asynq",)


class CacheDecorator(AsyncDecorator):
    def __init__(self, fn, async_fn):
        super(CacheDecorator, self).__init__(fn, AsyncTask)
        self.async_fn = async_fn
        self.cache = {}

    @asynq(pure=True)
    def _call_pure(self, args, kwargs):
        try:
            result(self.cache[args])
            return
        except KeyError:
            value = yield self.async_fn(*args)
            self.cache[args] = value
            result(value)
            return

    def dirty(self, *args):
        del self.cache[args]


def cached(fn):
    return qcore.decorators.decorate(CacheDecorator, get_async_fn(fn))(fn)


@async_proxy()
def proxied_fn():
    return ConstFuture("capybaras!")


@cached
@asynq()
def l0cached_async_fn():
    return "capybaras"


@asynq()
def autogenerated(aid):
    result((yield async_fn.asynq(aid)))
    return


@cached
def cached_fn(oid):
    return oid * 3


@asynq()
def async_fn(oid):
    result((yield cached_fn.asynq(oid)))
    return


class Wrapper(object):
    base: ClassVar[type]


def wrap(cls):
    """Decorator that wraps a class."""

    class NewWrapper(Wrapper):
        base = cls

    return NewWrapper


def takes_kwonly_argument(a, **kwargs):
    assert set(kwargs) == {"kwonly_arg"}


class ClassWithAsync(object):
    def get(self):
        return 1

    @asynq(pure=True)
    def get_async(self):
        yield async_fn.asynq(1)
        result(2)
        return


class PropertyObject(object):
    def __init__(self, poid):
        self.poid = poid

    def non_async_method(self):
        pass

    @property
    def string_property(self):
        return str(self.poid)

    @property
    def prop(self):
        return cached_fn(self.poid)

    prop_with_get = prop
    prop_with_is = prop

    @asynq()
    def get_prop_with_get(self):
        result((yield cached_fn.asynq(self.poid)))
        return

    @asynq()
    def is_prop_with_is(self):
        result((yield cached_fn.asynq(self.poid)))
        return

    @property
    def no_decorator(self):
        return cached_fn(self.poid)

    @asynq()
    @classmethod
    def load(cls, poid, include_deleted=False):
        result((yield cls(poid).get_prop_with_get.asynq()))
        return

    @classmethod
    def sync_load(cls, poid, include_deleted=False):
        return cls.load(poid, include_deleted=include_deleted)

    @asynq()
    def async_method(self):
        result((yield cached_fn.asynq(self.poid)))
        return

    @asynq()
    @classmethod
    def async_classmethod(cls, poid):
        result((yield cls(poid).get_prop_with_get.asynq()))
        return

    def _private_method(self):
        pass

    @cached
    @asynq()
    def l0cached_async_method(self):
        return "capybaras"

    @asynq()
    @staticmethod
    def async_staticmethod():
        pass

    @classmethod
    def no_args_classmethod(cls):
        pass


class Subclass(PropertyObject):
    pass


class CheckedForAsynq(object):
    """Subclasses of this class are checked for asynq in tests."""

    def not_checked(self):
        """Except in this method."""
        pass


class FixedMethodReturnType(object):
    def should_return_none(self):
        pass

    def should_return_list(self):
        return []


class KeywordOnlyArguments(object):
    def __init__(self, *args, **kwargs):
        assert set(kwargs) <= {"kwonly_arg"}


class WhatIsMyName:
    def __init__(self):
        pass


WhatIsMyName.__name__ = "Capybara"
WhatIsMyName.__init__.__name__ = "capybara"


class FailingImpl:
    def __init__(self) -> None:
        pass
