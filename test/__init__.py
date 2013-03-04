
import sys
import os.path
import unittest

ROOT = os.path.join( os.path.dirname( __file__), 'fixtures')

def get_fixture(path):
    return os.path.join( ROOT, path)


if sys.version_info <= (2,6):
    class TestCaseAssertRaises( unittest.TestCase):
        def assertRaises( self, exc, *args, **kw):
            if args or kw:
                return super( TestCaseAssertRaises, self).assertRaises( exc, *args, **kw)

    class AssertRaises( object):
        def __init__( self, test_case, exc):
            self.test_case = test_case
            self.exc = exc
        def __enter__(self):
            pass
        def __exit__(self, exc_type, exc_obj, tb):
            if exc_type == self.exc:
                return True
            return None


else:
    TestCaseAssertRaises = unittest.TestCase

