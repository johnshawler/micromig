.PHONY: all check
all:
	python3 tools/build.py
check: all
	python3 tests/check.py
	python3 tests/fixture_trace.py
