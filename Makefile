PY ?= python3

.PHONY: all glass components xiao stand assembly clean
all: assembly

glass:
	cd cad && $(PY) glass.py
components: glass
	cd cad && $(PY) components.py
xiao:
	cd cad && $(PY) xiao_seeed.py
stand:
	cd cad && $(PY) stand.py
assembly: components xiao stand
	cd cad && $(PY) assembly.py

clean:
	rm -rf exports/*.step exports/*.stl exports/components cad/__pycache__
