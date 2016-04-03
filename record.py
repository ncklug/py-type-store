
import builtins
import contextlib
import os
import sys
import traceback

import models

_debug = None

BUILTINS_NAME = '__builtin__'


def _fullname(o):
    if o is None:
        return None
    if o.__class__.__name__ in dir(builtins):
        module = BUILTINS_NAME
    else:
        module = o.__module__
    return module + "." + o.__class__.__name__


class _Tracer(object):

    def __init__(self, include_dir):
        self.include_dir = include_dir

    def trace(self, frame, event, arg):
        global _debug
        _debug = [frame, event, arg]

        if not frame.f_code.co_filename.startswith(self.include_dir):
            return

        if event == 'return':
            ret = models.Return(
                function_name=frame.f_code.co_name,
                type_name=_fullname(arg))
            session = models.get_session()
            session.add(ret)
            session.flush()
        if event == 'call' and frame.f_lineno == frame.f_code.co_firstlineno:
            session = models.get_session()

            args = []
            for arg_key in frame.f_code.co_varnames:
                arg_value = frame.f_locals[arg_key]
                args.append(models.Arg(
                    function_name=frame.f_code.co_name,
                    arg_name=arg_key,
                    type_name=_fullname(arg_value)))
            session.add_all(args)
            session.flush()
        if event == 'line':
            pass
        return self.trace


@contextlib.contextmanager
def record(include=None):
    if include is None:
        include = os.getenv('PYTHONPATH', '/').partition(':')[0]
    tracer = _Tracer(include)
    old_trace = sys.gettrace()
    sys.settrace(tracer.trace)
    try:
        yield
    finally:
        sys.settrace(old_trace)


def get_all_returns():
    return models.get_session().query(models.Return)


def get_all_args():
    return models.get_session().query(models.Arg)
