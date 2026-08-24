CC ?= cc
EMCC ?= emcc
CFLAGS := -std=c11 -Wall -Wextra -Wpedantic
C_SOURCES := graph.c bfs.c pagerank.c

.PHONY: check wasm serve clean

check:
	mkdir -p build
	$(CC) $(CFLAGS) -c graph.c -o build/graph.o
	$(CC) $(CFLAGS) -c bfs.c -o build/bfs.o
	$(CC) $(CFLAGS) -c pagerank.c -o build/pagerank.o

wasm:
	$(EMCC) $(C_SOURCES) -O2 --no-entry \
		-sALLOW_MEMORY_GROWTH=1 \
		-sENVIRONMENT=web \
		-sFILESYSTEM=0 \
		-sMODULARIZE=1 \
		-sEXPORT_NAME=createGraphModule \
		-sEXPORTED_FUNCTIONS='["_malloc","_free","_graph_create","_graph_set_edges","_graph_free","_bfs","_bfs_paths","_compute_degrees","_pagerank"]' \
		-o docs/graph_module.js

serve:
	python3 -m http.server 8000 --directory docs

clean:
	rm -rf build docs/graph_module.js docs/graph_module.wasm
