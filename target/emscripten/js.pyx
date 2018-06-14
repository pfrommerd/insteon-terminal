cdef extern from "emscripten.h":
    char *emscripten_run_script_string(const char *)


def run(code):
    return emscripten_run_script_string(bytes(code, 'utf-8'))
