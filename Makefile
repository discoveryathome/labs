CXX ?= c++
CXXFLAGS ?= -O3 -std=c++17 -Wall -Wextra -pedantic

.PHONY: check build
build: build/search

build/search: src/search.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@

check: build
	python3 -m unittest discover -s tests -v
	./build/search --self-test
	python3 scripts/check_frontier.py
