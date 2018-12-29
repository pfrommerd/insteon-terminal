PYVERSION=3.5.2
PYMINOR=$(basename $(PYVERSION))


DIR=$(shell pwd)
BUILD_DIR=$(DIR)/build

APP_FILES?=../insteonterminal ../../python-terminal/iterminal ../../python-insteon/insteon modules/*.py
EMPYTHON_BASE_PATH?=$(DIR)/../../cpython-emscripten/installs/python-$(PYVERSION)
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


all: serve-deps

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)


serve-deps: $(BUILD_DIR) \
	$(BUILD_DIR)/main.asm.js \
	$(BUILD_DIR)/app.zip \
	$(BUILD_DIR)/launch.py \
	$(BUILD_DIR)/callbacks.js \
	$(BUILD_DIR)/index.html

serve: serve-deps
	@echo "Serving on port 8062"
	cd $(BUILD_DIR) && python3 -m http.server 8062

clean:
	rm -rf $(BUILD_DIR)

$(BUILD_DIR)/main.bc: $(DIR)/src/main.c
	$(CC) -o $@ $< $(CFLAGS)

$(BUILD_DIR)/root: $(DIR)/src/python_stdlib_files
	mkdir -p $(BUILD_DIR)/root
	cd $(BUILD_DIR) && tar -C $(EMPYTHON_BASE_PATH) -cf - --files-from $(DIR)/src/python_stdlib_files | tar -C $(BUILD_DIR)/root -xvf -
	touch $(BUILD_DIR)/root

$(BUILD_DIR)/main.asm.js: $(BUILD_DIR)/main.bc $(BUILD_DIR)/root
	cd $(BUILD_DIR) && $(CC) -o $@ $(filter %.bc,$^) $(LDFLAGS) \
		$(foreach d,$(wildcard $(BUILD_DIR)/root/*),--preload-file $d@/$(notdir $d))

$(BUILD_DIR)/index.html: src/index.html
	cp src/index.html $(BUILD_DIR)/index.html

$(BUILD_DIR)/callbacks.js: src/callbacks.js
	cp src/callbacks.js $(BUILD_DIR)/callbacks.js

$(BUILD_DIR)/launch.py: src/launch.py
	cp src/launch.py $(BUILD_DIR)/launch.py

$(BUILD_DIR)/app.zip: $(APP_FILES)
	if [ -e $@ ]; then rm $@; fi
	cd ../../python-insteon && zip -r $(BUILD_DIR)/app.zip insteon
	cd ../../python-xmltree && zip -r $(BUILD_DIR)/app.zip xmltree
	cd ../../python-terminal && zip -r $(BUILD_DIR)/app.zip iterminal
	cd .. && zip -r $(BUILD_DIR)/app.zip insteonterminal
	# Add the special module files for stuff that is missing
	cd $(DIR)/modules && zip -r $(BUILD_DIR)/app.zip *
