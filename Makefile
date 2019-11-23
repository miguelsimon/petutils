py_files := $(wildcard petutils/*.py)

gvs := $(wildcard media/*.gv)
svgs := $(patsubst %.gv,%.gv.svg,$(gvs))
pngs := $(patsubst %.gv,%.gv.png,$(gvs))

docs: $(svgs) $(pngs)

media/%.gv.svg: media/%.gv
	dot -Tsvg -o $@ $<

media/%.gv.png: media/%.gv
	dot -Tpng -o $@ $<

GATE:
	git clone git@next.ific.uv.es:nextsw/GATE.git

.PHONY: build-deps-image
build-deps-image:
	docker build -t nexus-deps -f DepsDockerfile .

.PHONY: build-gate-image
build-gate-image: build-deps-image GATE
	docker build -t gate -f GATEDockerfile .

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
