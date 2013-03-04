
import os.path

ROOT = os.path.join( os.path.dirname( __file__), 'fixtures')

def get_fixture(path):
    return os.path.join( ROOT, path)
