# Contracts and decoupling rules (stream 08)

JEPA-Drift strictly separates representation from surveillance. An encoder that anticipates, is not odd,
is not deterministic, or adjusts on the test window corrupts every measurement. Four contract tests block
any fusion of code. They apply automatically to every registered representation, including the future JEPA.

## The four contracts

### (1) Non-anticipation

Perturbing `x_{t+1:T}` leaves `z_{1:t}` identical bit-for-bit. Each day is encoded independently:
`transform_panel` is the stack of `transform_day` over the rows of X with no operation across days.

### (2) Oddness

`||phi(-x) + phi(x)||_inf <= 1e-6` on the odd head. The odd head satisfies `phi(-x) = -phi(x)`,
which guarantees that under any centrally symmetric null the sign streams `1{u' phi(x_t) > 0}` are
i.i.d. Bernoulli(1/2) whatever the volatility (Article C, lemma "Whitening by an odd encoder").

### (3) Determinism

Two executions in fresh subprocesses (`PYTHONHASHSEED=42`, single thread, CPU) give identical SHA-256
for `z_*.npz` and the sidecar JSON. The extraction pipeline is bit-for-bit reproducible.

### (4) No test statistics

`fit` receives only `pretrain` or `calib` segments. Perturbing the `monitor` segment leaves
`state_hash` unchanged, and the normalization statistics in the sidecar JSON come only from the
declared segment. A representation that normalizes over the full series (fixture:
`_FaultyNormalization`) fails this contract.

## Decoupling rules (AST analysis)

| module | must not import |
|---|---|
| `jepadrift/monitors/**` | `torch`, `jepadrift.jepa`, `jepadrift.representations` |
| `jepadrift/jepa/**` | `jepadrift.injection`, `jepadrift.monitors` |
| `jepadrift/representations/**` | `torch`, `jepadrift.monitors`, `jepadrift.injection` |

`jepadrift/injection.py` accepts only return panels: it asserts on shape (2-D) and dtype (float64),
and explicitly refuses Z objects (dicts or any non-ndarray input) with `TypeError`.

## Torch model guards (JEPA)

When torch is installed, additional guards apply to any torch-based representation:

- **Eval-mode buffer stability**: in `eval` mode, no buffer changes after 10 forward passes.
- **No BatchNorm in training**: no `BatchNorm*` layer may be in training mode.
- **No temporal normalization**: no normalization computed on the temporal axis (dim=0 for `(T, N)` input).
- **EMA target inactive at extraction**: model output is deterministic in `eval` + `no_grad`.

If torch is not installed, these tests are skipped.

## Git hooks

### pre-commit (`tools/pre-commit`)

- Runs `make check` (pyflakes + unit tests + contract tests + decoupling tests).
- Blocks any file under `data/raw/eurofidai/` or `data/derived/d4_eurofidai/`.
- Blocks any file larger than 50 MB.

### pre-push (`tools/pre-push`)

- Blocks any push whose commit range contains a file under `data/raw/eurofidai/` or
  `data/derived/d4_eurofidai/`.
- Reminds that pushes are only authorized while the repository address is not shared publicly
  and not linked to a publication (anonymous submission).

Install with `make hooks`.

## Running

```bash
make hooks    # install git hooks
make check    # pyflakes + all tests (unit + contracts + decoupling)
```
