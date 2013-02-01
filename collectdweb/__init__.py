
import os.path
ROOT = os.path.join( os.path.dirname( __file__), 'share/')

def get_shared( name):
    return os.path.join( ROOT, name)
