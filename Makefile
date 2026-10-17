export OMP_NUM_THREADS := 1
export MKL_NUM_THREADS := 1
export OPENBLAS_NUM_THREADS := 1
export MKL_CBWR := COMPATIBLE
export PYTHONHASHSEED := 42

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: test j1 check hooks

test:
	pytest -q --ignore=external

j1:
	python experiments/e2_floor_validation.py --reps 2000 --out results/e2 2>&1 | tee logs/e2/run.log

hooks:
	ln -sf ../../tools/pre-commit .git/hooks/pre-commit
	ln -sf ../../tools/pre-push .git/hooks/pre-push
	chmod +x tools/pre-commit tools/pre-push
	@echo "hooks installed: pre-commit, pre-push"

check:
	pyflakes $(filter-out jepadrift/stats/garch.py,$(shell find jepadrift experiments tests -name '*.py'))
	pytest -q --ignore=external tests/test_contracts.py tests/test_decoupling.py
	pytest -q --ignore=external --ignore=tests/test_contracts.py --ignore=tests/test_decoupling.py
