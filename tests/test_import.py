import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_import():
    import insteonterminal

if __name__=='__main__':
    test_import()

