export OMP_NUM_THREADS := 1
export MKL_NUM_THREADS := 1
export OPENBLAS_NUM_THREADS := 1
export MKL_CBWR := COMPATIBLE
export PYTHONHASHSEED := 42

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: test j1 check

test:
	pytest -q --ignore=external

j1:
	python experiments/e2_floor_validation.py --reps 2000 --out results/e2 2>&1 | tee logs/e2/run.log

check:
	pyflakes $(filter-out jepadrift/stats/garch.py,$(shell find jepadrift experiments tests -name '*.py'))
	pytest -q --ignore=external
