
import os.path
ROOT = os.path.join( os.path.dirname( __file__), '../share/collectdweb/')

def get_shared( name):
    return os.path.join( ROOT, name)
