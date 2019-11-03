py_files := $(wildcard petutils/*.py)

gvs := $(wildcard media/*.gv)
svgs := $(patsubst %.gv,%.gv.svg,$(gvs))
pngs := $(patsubst %.gv,%.gv.png,$(gvs))

docs: $(svgs) $(pngs)

media/%.gv.svg: media/%.gv
	dot -Tsvg -o $@ $<

media/%.gv.png: media/%.gv
	dot -Tpng -o $@ $<

.PHONY: download_deps
download-deps:
	rm -rf deps

	mkdir deps

	curl -Lo deps/geant4.10.05.p01.tar.gz \
		http://geant4.cern.ch/support/source/geant4.10.05.p01.tar.gz
	cd deps && tar zxvf geant4.10.05.p01.tar.gz
	rm deps/geant4.10.05.p01.tar.gz

	curl -o deps/hdf5-1.10.5.tar.gz \
		https://support.hdfgroup.org/ftp/HDF5/current/src/hdf5-1.10.5.tar.gz
	cd deps && tar zxvf hdf5-1.10.5.tar.gz
	rm deps/hdf5-1.10.5.tar.gz

	curl -o deps/gsl-2.6.tar.gz \
		http://ftp.rediris.es/mirror/GNU/gsl/gsl-2.6.tar.gz
	cd deps && tar zxvf gsl-2.6.tar.gz
	rm deps/gsl-2.6.tar.gz

	curl -o deps/root_v6.18.04.Linux-ubuntu18-x86_64-gcc7.4.tar.gz \
		https://root.cern/download/root_v6.18.04.Linux-ubuntu18-x86_64-gcc7.4.tar.gz
	cd deps && tar zxvf root_v6.18.04.Linux-ubuntu18-x86_64-gcc7.4.tar.gz
	rm deps/root_v6.18.04.Linux-ubuntu18-x86_64-gcc7.4.tar.gz

	git clone git@next.ific.uv.es:nextsw/nexus.git deps/nexus
	cd deps/nexus && git checkout petalo

	git clone git@next.ific.uv.es:nextsw/GATE.git deps/GATE

.PHONY: build_nexus_image
build-nexus-image:
	docker build -t nexus .

.PHONY: fmt
fmt: env_ok
	env/bin/isort -sp .isort.cfg $(py_files)
	env/bin/black $(py_files)

env_ok: requirements.txt
	rm -rf env env_ok
	python3 -m venv env
	env/bin/pip install -r requirements.txt
	touch env_ok

.PHONY: test
test: check
	env/bin/python -m unittest discover petutils -p "*.py"

.PHONY: check
check: env_ok
	env/bin/python -m mypy --check-untyped-defs --ignore-missing-imports $(py_files)
	env/bin/python -m flake8 --select F $(py_files)
	env/bin/isort  -sp .isort.cfg  --check $(py_files)
	env/bin/black --check $(py_files)

.PHONY: run_notebook
run_notebook: env_ok
	env/bin/jupyter notebook

.PHONY: clean
clean:
	rm -rf env_ok env deps
