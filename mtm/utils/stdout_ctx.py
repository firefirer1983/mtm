import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def redirect_to_buffer():
    _stdout = sys.stdout
    try:
        sys.stdout = mystdout = StringIO()
        yield mystdout
    except Exception as e:
        print(e)
        raise e
    finally:
        sys.stdout = _stdout
