PY ?= uv run --project .. python

.PHONY: setup all glass components real xiao stand assembly schematic clean distclean
all: assembly

setup:
	uv sync

glass:
	cd cad && $(PY) glass.py
components: glass
	cd cad && $(PY) components.py
real:
	cd cad && $(PY) parts_real.py
xiao:
	cd cad && $(PY) xiao_seeed.py
stand:
	cd cad && $(PY) stand.py
assembly: components real xiao stand
	cd cad && $(PY) assembly.py

schematic:
	uv run python docs/schematic.py

clean:
	rm -rf exports/*.step exports/*.stl exports/components cad/__pycache__

distclean: clean
	rm -rf .venv
