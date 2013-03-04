
import sys
import os.path
import unittest

ROOT = os.path.join( os.path.dirname( __file__), 'fixtures')


def get_fixture(path):
    return os.path.join( ROOT, path)

if sys.version_info < (2,7):
    class TestCaseCompat( unittest.TestCase):
        def assertIsInstance( self, obj, cls):
            self.assertTrue( isinstance( obj, cls))
        def assertRaises( self, exc, *args, **kw):
            if args or kw:
                return super( TestCaseCompat, self).assertRaises( exc, *args, **kw)
            return AssertRaises( self, exc)

    class AssertRaises( object):
        def __init__( self, test_case, exc):
            self.test_case = test_case
            self.exc = exc
        def __enter__(self):
            pass
        def __exit__(self, exc_type, exc_obj, tb):
            if exc_type == self.exc:
                return True
            self.test_case.fail(u'{0} was not raised'.format( self.exc.__name__))


else:
    TestCaseCompat = unittest.TestCase

