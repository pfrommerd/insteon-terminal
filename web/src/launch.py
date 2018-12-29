import os,sys,zipfile

print('Unzipping app...')
with zipfile.ZipFile('/app.zip', 'r') as zr:
    zr.extractall('/app/')

sys.path.insert(0, '/app/')

import _dummy_thread
sys.modules['_thread'] = _dummy_thread

os.system('window.python_ready()')

import insteonterminal
insteonterminal.run()
