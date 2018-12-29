window.python_ready = function() {
    window.pyexec = Module.cwrap('PyRun_SimpleString', 'number', ['string']);

    pyexec('import js')

    var next_promise_id = 0;
    window.py_encode = function(value) {
        if (typeof value == "string") {
            return "\"" + value + "\"";
        } else if (value == undefined) {
            return "_undefined"
        } else if (value instanceof Promise) {
            var promise_id = next_promise_id++;
            value.then(function(val) {
                window.pyexec('js._resolve_promise(' + promise_id + ',\"' +
                                    btoa(py_encode(val)) + '\")');
            }, function() {
                window.pyexec('js._reject_promise(' + promise_id + ',\"' + 
                                    btoa(py_encode(val)) + '\")');
            });
            return "_create_promise(" + promise_id + ")";
        } else {
            return String(value);
        }
    }

    window.js_eval = function(callId, code_encoded) {
        var result = undefined;
        var code = atob(code_encoded)
        console.log('running: ' + code)
        result = eval(code);
        var result_encoded = btoa(py_encode(result));
        pyexec('js._handle_eval_result(' + callId + ',\"' + result_encoded + '\")');
    }
}

function do_foo() {
    return new Promise((resolve, reject) => {
        setTimeout(function() {
            resolve('hi');
        }, 1000);
    });
}
