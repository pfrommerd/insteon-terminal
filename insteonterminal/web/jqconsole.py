import sys

from ..terminal import InterpretError

class JQConsole:
    def __init__(self):
        # Change the stdout and std err
        # to print to the jqconsole
        sys.stdout.write = self.write
        sys.stderr.write = self.write
        sys.stdin = None # Disable stdin

        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.stderr = sys.stderr

    def setup(self, shell):
        # Setup custom functions only for the
        # web-based interface
        def load(sh):
            sh.interpreter.locals['reset'] = self.req_clear
        shell.add_comp((load, None))

    def set_prompt(self, label):
        import js
        js.run('window.term_prompt = \"' + label + '\";')
    
    def req_prompt(self):
        import js
        js.run('if(window.req_prompt) window.req_prompt();')

    def req_clear(self):
        import js
        js.run('if(window.req_reset) window.req_reset();')

    def write(self, text):
        import js
        import base64
        encoded = str(base64.standard_b64encode(bytes(text, 'utf-8')),'utf-8')
        js.run('window.req_write("' + encoded + '");')

    def on_input(self, val):
        import base64
        line = str(base64.standard_b64decode(val),'utf-8')
        if self._shell:
            more = False
            try:
                more = not self._shell.process_input(line, sys.stdout, sys.stderr, sys.stdin)
            except InterpretError as e:
                print(e)
            if more:
                self.set_prompt('... ')
            else:
                self.set_prompt('>>> ')

    def run(self, shell):
        # Return ourself so the java script
        # can call on_input and on_ready when it's ready
        self._shell = shell
        self.req_prompt()
        return self
