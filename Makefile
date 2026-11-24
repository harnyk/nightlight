PY ?= python3

.PHONY: all glass components stand assembly clean
all: assembly

glass:
	cd cad && $(PY) glass.py
components: glass
	cd cad && $(PY) components.py
stand:
	cd cad && $(PY) stand.py
assembly: components stand
	cd cad && $(PY) assembly.py

clean:
	rm -rf exports/*.step exports/*.stl exports/components cad/__pycache__
