PYVERSION=3.5.2
PYMINOR=$(basename $(PYVERSION))



EMPYTHON_BASE_PATH?=../../../cpython-emscripten/installs/python-$(PYVERSION)
EMPYTHON_INCLUDE_PATH?=$(EMPYTHON_BASE_PATH)/include/python$(PYMINOR)/
EMPYTHON_LINK_LIBRARY_PATH?=$(EMPYTHON_BASE_PATH)/lib/libpython$(PYMINOR).a
EMPYTHON_STDLIB_PATH?=$(EMPYTHON_BASE_PATH)/lib/python3.5/

CC=emcc
OPTFLAGS=-O2
CFLAGS=-std=gnu99 $(OPTFLAGS) -g -I $(EMPYTHON_INCLUDE_PATH) -Wno-warn-absolute-paths
LDFLAGS=$(OPTFLAGS) $(EMPYTHON_LINK_LIBRARY_PATH) \
  -s TOTAL_MEMORY=268435456 \
  -s ASSERTIONS=2 \
  -s EMULATE_FUNCTION_POINTER_CASTS=1 \
  -s EXTRA_EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
  -s EXPORTED_FUNCTIONS='["_main","_PyRun_SimpleString"]' \
  --memory-init-file 0


all: main.asm.js app.zip

main.asm.js: main.bc js.bc root
	$(CC) -o $@ $(filter %.bc,$^) $(LDFLAGS) \
		$(foreach d,$(wildcard root/*),--preload-file $d@/$(notdir $d))

app.zip: ../../insteon
	if [ -e $@ ]; then rm $@; fi
	cd ../.. && zip -r target/emscripten/app.zip insteon


serve: main.asm.js
	@echo "Serving on port 8062"
	python3 -m http.server 8062

clean:
	-rm -fr root
	-rm python.asm.js python.asm.data
	-rm *.bc


%.bc: %.c
	$(CC) -o $@ $< $(CFLAGS)


%.c: %.pyx
	cython $<

root: 
	mkdir -p root
	tar -C $(EMPYTHON_BASE_PATH) -cf - --files-from python_stdlib_files | tar -C root -xvf -
	touch root
