import os
import builtins
import base64

def exec(code):
    os.system(code)

# Transforms the js return string to
# proper python
def _jsret_to_python(result_encoded):
    result = base64.b64decode(result_encoded.encode('utf-8')).decode('utf-8')
    return builtins.eval(result)

_eval_counter = 0
_eval_results = {}

# A marker for undefined things
_undefined = {}

def eval(code):
    global _eval_counter
    global _eval_results
    eval_id = _eval_counter
    _eval_counter = _eval_counter + 1

    code_encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')
    exec('window.js_eval({}, "{}")'.format(eval_id, code_encoded))

    val = None
    if eval_id in _eval_results:
        val = _eval_results[eval_id]
        del _eval_results[eval_id]

    if val is _undefined:
        return None
    return val

def call(func, *args):
    code = func + '('
    for i, a in enumerate(list(args)):
        if i > 0:
            code = code + ','
        if isinstance(a,str):
            a_encoded = base64.b64encode(a.encode('utf-8')).decode('utf-8')
            code = code + 'atob(\"' + a_encoded + '\")'
        else:
            code = code + str(a) # aaaaah

    code = code + ')'
    return eval(code)


def _handle_eval_result(eval_id, result_encoded):
    global _eval_results
    _eval_results[eval_id] = _jsret_to_python(result_encoded)

# Outstanding callbacks
_promises = {}

class Promise:
    def __init__(self, run=None):
        self._listeners = []
        if run:
            run(self.resolve, self.reject)

    def _resolve(self, value=_undefined):
        self._resolved = value
        for l in self._listeners:
            if l[0]:
                if value is not _undefined:
                    l[0](value)
                else:
                    l[0]()
        self._listeners = []
        

    def _reject(self, value=_undefined):
        self._rejected = value
        for l in self._listeners:
            if l[1]:
                if value is not _undefined:
                    l[1](value)
                else:
                    l[1]()
        self._listeners = []

    def then(self, resolve, reject=None):
        self._listeners.append( (resolve, reject) );
        if hasattr(self, '_resolved'):
            self._resolve(self._resolved)
        elif hasattr(self, '_rejected'):
            self._reject(self._rejected)

def _create_promise(promise_id):
    promise = Promise()
    _promises[promise_id] = promise
    return promise

def _resolve_promise(promise_id, val_encoded):
    _promises[promise_id]._resolve(_jsret_to_python(val_encoded))
    del _promises[promise_id]

def _reject_promise(promise_id, val_encoded):
    _promises[promise_id]._reject(_jsret_to_python(val_encoded))
    del _promises[promise_id]
