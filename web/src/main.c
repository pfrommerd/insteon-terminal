#include <stdlib.h>
#include <stdio.h>

#include <emscripten.h>
#include <Python.h>

// Let os.system run javascript muhahahahaha
int system(const char* command) {
    emscripten_run_script_string(command);
    return 0;
}

static int num_remaining = 2;
static void onload(const char *filename) {
    printf("Loaded %s.\n", filename);
    num_remaining--;
    if (num_remaining == 0) {
        PyRun_SimpleString("import sys");
        PyRun_SimpleString("sys.path.insert(0, '/app')");
        PyRun_SimpleString("import launch");
    }
}

static void onloaderror(const char *filename) {
    printf("Failed to load %s, aborting.\n", filename);
    PyRun_SimpleString("print('fail')");
}

int main(int argc, char** argv) {
    setenv("PYTHONHOME", "/", 0);

    Py_InitializeEx(0);

    // Fetch app.zip from the server.
    emscripten_async_wget("app.zip", "/app.zip", onload, onloaderror);
    emscripten_async_wget("launch.py", "/app/launch.py", onload, onloaderror);
    emscripten_exit_with_live_runtime();
    return 0;
}
