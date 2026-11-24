PY ?= python3

.PHONY: all glass components real xiao stand assembly schematic clean
all: assembly

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
	$(PY) docs/schematic.py

clean:
	rm -rf exports/*.step exports/*.stl exports/components cad/__pycache__
