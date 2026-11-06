2026-11-06T21:23:33Z

# Wrapup — stream 19-oracle: E4 analytic oracle reference of drift information in N

Refreshed after Codex review round 2 (`logs/stream_19_oracle/codex-review-round2.md`, ignored, SHA-256
`d1eb567b0675cdf9dff85f720de7b4b39c64565a606cf1542e1c9aeea1c8f835`). Round 1 is
`logs/stream_19_oracle/codex-review-round1.md`, SHA-256 `f12f8f825f7df8241f44a8f25416ad9ba7ef07b37ec91f3a3349908ce1ca454d`.

## Context

- **Mandate.** `logs/orchestration_20261106/plan-request.md` is a Codex request, ignored by Git (SHA-256
  `b0695f1f02d5171f3952582037e0d31037c1bded6e871698dd56fc84b8f5e456`). It asks for the smallest lot that produces and
  checks a serialisable reference in N of a drift's information, kept apart from delays, mixture costs and historical
  calibration defects. The reference uses a known Gaussian oracle: Σ_N = ρ11ᵀ + (1−ρ)I_N and Δμ = δ1. It estimates no
  representation and uses no detector and no Monte Carlo. Lot 19-oracle is distinct from the historical E4 campaign,
  which stays `À_REPLANIFIER`, and from the documentary lot 19. It closes neither.
- **Plan phase.** Claude wrote the native plan in plan mode, without a sub-agent, Graphify or jCodeMunch. The native
  approval screen was not the GO. Under the researcher's delegated mandate, Codex:
  - archived the native plan as `logs/orchestration_20261106/native-plan-reviewed.md` (SHA-256
    `fc966d66395b13481fe5708caba2f9797072a166ec4dcb455ae27398516593b6`, rechecked in this session);
  - reviewed it in `logs/orchestration_20261106/codex-plan-review.md` (ignored);
  - recorded the canonical plan `prompts/plans/plan-19-oracle.md`, whose §12 « Décision GO intégrée » prevails over the
    native proposal, and the GO `prompts/GO-stream-19-oracle.md` (2026-11-06, 20:10 UTC).
- **GO answers (§12).**
  - Q1: temporary outputs only. No CSV is tracked and no `docs/MAPPING.md` entry is added.
  - Q2: grid accepted. N ∈ {1, 8, 16, 32, 64, 128, 239, 500}, ρ ∈ {0, 0.4}, δ = 1: 16 rows, no grid option.
  - Q3: `gain_ceiling = inf` only for ρ = 0.
  - Q4: Claude runs targeted checks only. Codex runs the mandatory full `make check` after wrapup and reindexation,
    through the pre-commit hook; it is not duplicated here.
  - Q5: the Codex file names are confirmed.
- **Mandatory numerical precisions (§12).**
  - Out-of-domain parameters and values that float64 cannot represent raise `ValueError`.
  - δ²/2 is checked before the helper; underflow and overflow are both rejected.
  - Helper outputs must be finite, and information and gain strictly positive.
  - For ρ > 0, an overflowing 1/ρ is rejected.
  - Required witnesses: δ = 1e-200, δ = 1e200, and a positive ρ whose inverse overflows, at a tiny N.
  - Reception directories are created explicitly.
  - Tolerances and frozen routines are never touched to reach GREEN.
- **Codex review round 1** asked for three corrections, all applied test-first:
  1. Invalid scalar types for ρ and δ must raise `ValueError` before the helper.
  2. A ρ that the float64 conversion rounds onto 1 must never reach the helper, with warnings as errors.
  3. The note must not claim accuracy outside the pinned environment.

  Codex accepted the normal-float lower threshold on δ²/2 as a conservative precision guard.
- **Codex review round 2** accepted the exact float64 representability rule and the normal-baseline precision guard,
  and asked for no further policy change. It found one boundary bug: `oracle_row(2, np.float16(0.25), np.float16(2))`
  and the float32 equivalent returned the correct 3.2 but emitted `RuntimeWarning: overflow encountered in cast`. The
  comparison of δ with `sys.float_info.max` narrowed that Python float to the NumPy input dtype. Asked for: the two
  witnesses first, under warnings as errors, then a fix of the shared validation path. The fix must not silence the
  warnings and must leave the helper, formulas, grid, tolerances, policy and receipt bytes unchanged.
- **Session.** Interactive Claude Code, `claude-opus-5-5`, effort max throughout. The CLI enabled auto mode after the GO
  was recorded. No sub-agent was used. Skills: `superpowers:test-driven-development`, then the native `wrap-up` at
  each closure.
- **Ownership.** Claude wrote the four files of plan §3 and the ignored journals under `logs/stream_19_oracle/`. Codex
  owns the plan, the GO, the reviews, reindexation and Git.
- **Base.** `3467df4b7426fa15c1ab16ef94687f25a976636d`, branch `stream-19-oracle`.

## Validated Results

Every command ran from the worktree root with `.venv/bin/python` and `OMP_NUM_THREADS=MKL_NUM_THREADS=
OPENBLAS_NUM_THREADS=1 MKL_CBWR=COMPATIBLE PYTHONHASHSEED=42 MPLBACKEND=Agg`. Earlier journals are kept unchanged.

- **Codex files.** Their SHA-256 values were recorded at 2026-11-06T20:13:22Z, before any write, and still verify at
  the end of round 2:
  - `prompts/GO-stream-19-oracle.md`: `84b2089d1044a2da8bb6c12e57c0f005a879112718d8cb0c80540d3a3cad850c`;
  - `prompts/plans/plan-19-oracle.md`: `370c465db7d00a55a528244e406f3d45515da25e89db049e3e24b63091a270a3`.

### Round 0

- **RED** (20:18:42Z, `red.log`). The test file alone gave a collection error, exit 2: `ImportError: cannot import
  name 'e4_oracle_reference' from 'experiments' (unknown location)`.
- **GREEN** (20:19:28Z, `green.log`): `35 passed in 0.81s`, no warning summary; pyflakes 4.0.3 clean.
- **Reception** (`reception.log`, `note_command.log`): directories `a` and `b` created explicitly. Both exports have
  SHA-256 `b0d7f4fdeb6fc0ab404a0d059fd0210c73b81d11741d8c85c133d8ab54633996` and identical bytes. An export onto the
  existing file exits 1 with `FileExistsError` and leaves it unchanged.

### Round 1

- **RED** (20:50:11Z, `red_round1.log`): `10 failed, 29 passed`, exit 1, against the unchanged script. The failures:
  - 4 `TypeError` for text and `None` as ρ or δ;
  - 2 booleans accepted;
  - 3 calls into the helper, for `Decimal("0.9999999999999999999999")`, `Fraction(10**22 - 1, 10**22)` and
    `Fraction(1, 10**400)` as ρ;
  - 1 `OverflowError` for δ = 10**400.
- **Fix.** Before any conversion or helper call, `oracle_row` checks:
  1. that ρ and δ are non-boolean `numbers.Real`;
  2. the domain, 0 <= ρ < 1 and 0 < δ <= the largest finite float64;
  3. exact float64 representability.
- **GREEN** (20:50:48Z, `green_round1.log`): `45 passed in 0.68s`, no warning summary; pyflakes clean.
- **Reception** (`reception_round1.log`, `note_command_round1.log`): the bytes are unchanged, with the same SHA-256.

### Round 2

- **RED** (21:22:10Z, `red_round2.log`). The script was unchanged since round 1 (`fd3622d2…`) and the tests were
  extended.
  - Command: `.venv/bin/python -m pytest -q -rfE tests/test_e4_oracle_reference.py`.
  - Result: `3 failed, 39 passed`, exit 1.
  - The two requested witnesses, `test_narrow_numpy_floats_are_accepted_without_warning[float16]` and `[float32]`,
    each fail with `RuntimeWarning: overflow encountered in cast`.
  - An extra witness fails with `DID NOT RAISE ValueError`: `oracle_row(2, 0.4, np.int64(2**53 + 1))`. It is the same
    shared-path defect. NumPy promoted the int64 to float64 in the exactness comparison, which hid the rounding.
- **Fix.** NumPy scalars are now converted to Python scalars with `.item()` before the range and exactness checks.
  - This gives Python floats for float16, float32 and float64, and exact Python ints for NumPy integers.
  - A session check showed that `.item()` leaves NumPy long doubles as long doubles; they are then compared in their
    own, wider precision.
  - No warning is silenced. The type gate, the domain bounds, the exactness rule, the δ²/2 and 1/ρ guards, the helper
    call and the output checks are otherwise unchanged.
- **GREEN** (21:22:38Z, `green_round2.log`).
  - Command: `.venv/bin/python -m pytest -q -rw tests/test_e4_oracle_reference.py tests/test_floors.py`.
  - Result: `48 passed in 0.69s`, exit 0, no warning summary. pyflakes on the two Python files: clean.
  - Breakdown: 42 items from 10 test functions (29 parametrised rejection cases, 4 never-reach-the-helper cases,
    2 narrow-float cases), plus the 6 unchanged tests of `tests/test_floors.py`.
  - The review's witnesses, run as a standalone script under `python -W error`, print `float16 3.2` and
    `float32 3.2`.
- **Reception** (21:22:52Z, `reception_round2.log`).
  - New directories `a_round2` and `b_round2` were created explicitly.
  - Both exports pass `sha256sum -c`, and `cmp` finds them identical.
  - Their SHA-256 is `b0d7f4fdeb6fc0ab404a0d059fd0210c73b81d11741d8c85c133d8ab54633996`, unchanged. `cmp` finds the
    bytes identical to round 0's `a/` and round 1's `a_round1/`.
  - The refusal exits 1 with `FileExistsError`, prints nothing on stdout and leaves the file unchanged.
  - The receipts of rounds 0 and 1 still verify.
- **Note command** (21:23:17Z, `note_command_round2.log`). Run with `TMPDIR` set to the session scratchpad, outside
  the repository, it gave the same hash and bytes as `a_round2/`.
- **Note.**
  - The accepted-types item now states the `.item()` conversion.
  - The exactness item cites an integer δ such as 2^53 + 1.
  - The tested cases include (2, 0.25, 2) as NumPy float16 and float32, with warnings as errors.
- **Reference content (unchanged).** These are analytic values, not measurements.
  - Header: `N,rho,delta,factor_term,breadth_term,info_nats,gain_vs_single,gain_ceiling,qualification`, 17 lines.
  - `breadth_term` is `0` on every row.
  - At ρ = 0, `gain_ceiling` is `inf` and the gain equals N, printed `239.00000000000003` at N = 239.
  - At ρ = 0.4, `gain_ceiling` is `2.5`, and the gain rises from `1` at N = 1 to `2.4925224327018944` at N = 500.
- **Integrity** (`integrity_round2.log`, after this wrapup).
  - HEAD equals the base; `git diff --quiet` against the base passes; nothing is staged.
  - J1: `results/e2/e2_cells.csv` has SHA-256
    `e315e537ead0f656e4bcd3897e6ff04075f3780a8fbe642e258864739b570823` on disk and in the index, 47 CRLF lines and no
    bare LF.
  - No comment, linter pragma or absolute home path appears in the owned files.
- **SHA-256 of the produced files after round 2.** The wrapup's own value is reported outside this file.

| File | SHA-256 | Round 1 | Round 0 |
|---|---|---|---|
| `experiments/e4_oracle_reference.py` | `181375944853cf3cecd274015fd5dd774007cbe295a86314510eb573bde92c93` | `fd3622d2…` | `cb8bd35b…` |
| `tests/test_e4_oracle_reference.py` | `a79c65385eef97d4e4e2306c30f05d3a5b3cb7abe9c997a82fe4ec6d746f2c0f` | `10b01529…` | `ed76d390…` |
| `docs/sections/e4_oracle_reference.md` | `4dca48c45236650793f745e82d82a8d7ce29fef8df45d565e5f7edfac1759270` | `1bb06cd3…` | `22f7aee9…` |
| `logs/stream_19_oracle/a_round2/e4_oracle_reference.csv` (ignored) | `b0d7f4fdeb6fc0ab404a0d059fd0210c73b81d11741d8c85c133d8ab54633996` | same | same |

## Errors and Dead Ends

- **Round 2, NumPy weak-scalar promotion.** Under NumPy 2 promotion, comparing a NumPy scalar with a Python scalar
  casts the Python scalar to the NumPy dtype.
  - `delta <= sys.float_info.max` therefore cast the float64 maximum to float16 or float32, which overflowed with a
    `RuntimeWarning`. Valid inputs failed with warnings as errors.
  - The same promotion made `float(v) != v` compare a NumPy int64 after rounding it to float64, which hid the rounding
    of 2^53 + 1.
  - Root cause: the shared validation path compared NumPy scalars directly. It is fixed once, there, with `.item()`;
    the narrow-float witnesses and the int64 witness cover it.
- **Round 1, contract gaps.**
  - Text and `None` raised `TypeError`.
  - The float64 conversion after the domain check let a rounded ρ = 1 reach the helper.
  - A tiny positive ρ rounded to 0 and received an infinite ceiling.
  - δ = 10**400 raised `OverflowError`.
  - Booleans were accepted for ρ and δ.
  - All of these were fixed in round 1.
- **Settled decision.** Codex accepted the exact float64 representability rule in round 2. A real that the float64
  conversion would round is rejected, for instance `Fraction(1, 10)` or `np.int64(2**53 + 1)`.
- **RED message (round 0).** The plan predicted `ModuleNotFoundError`. `experiments/` is a namespace package, so the
  actual error was `ImportError`; the cause was the same.
- **Self-matching check (round 0).** The first post-wrapup grep for paths and pragmas matched the wrapup's own prose
  (`integrity_2_attempt1.log`). The sentence was reworded, and the rerun was clean (`integrity_2.log`).
- **Discarded draft (round 0).** A dead list expression in a test draft was removed before the RED run.
- **Mutation check.** Mutations were assessed by reading, not executed. The RED runs of rounds 1 and 2 did show that
  every new witness fails against the previous script.

## Current State

- **Repository.** Branch `stream-19-oracle`, HEAD `3467df4b7426fa15c1ab16ef94687f25a976636d` (the base). Nothing is
  staged and no tracked file is modified. Expected `git status --porcelain`, exactly:

```text
?? docs/sections/e4_oracle_reference.md
?? experiments/e4_oracle_reference.py
?? prompts/GO-stream-19-oracle.md
?? prompts/plans/plan-19-oracle.md
?? prompts/wrapups/wrapup-19-oracle.md
?? tests/test_e4_oracle_reference.py
```

- **Interfaces.**
  - `experiments/e4_oracle_reference.py` exposes `oracle_row(n, rho, delta=1.0) -> dict` and `main(argv=None)`, whose
    only option is `--out PATH`, a new file in an existing directory.
  - Constants: `N_GRID`, `RHO_GRID`, `DELTA` and `QUALIFICATION = "ORACLE_KNOWN_SIGMA_DELTA"`.
  - Order of checks in `oracle_row`:
    1. N type and value;
    2. ρ and δ types;
    3. NumPy scalars converted with `.item()`;
    4. exact domain;
    5. exact float64 representability;
    6. δ²/2 normal and finite;
    7. 1/ρ finite when ρ > 0;
    8. the helper call, under `np.errstate(over="ignore")`;
    9. finite, positive outputs.
  - `oracle_row` reuses `floors.factor_information` unchanged; `main` writes with `pipelines.save_fair_csv`.
- **Journals** (ignored, under `logs/stream_19_oracle/`).
  - Round 0: `red.log`, `green.log`, `reception.log`, `refusal.err`, `refusal.out` (empty), `note_command.log`,
    `integrity_1.log`, `integrity_2_attempt1.log`, `integrity_2.log`, `a.sha256`, `b.sha256` and
    `{a,b}/e4_oracle_reference.csv`.
  - Round 1: `red_round1.log`, `green_round1.log`, `reception_round1.log`, `refusal_round1.err`, `refusal_round1.out`
    (empty), `note_command_round1.log`, `integrity_round1.log`, `a_round1.sha256`, `b_round1.sha256` and
    `{a_round1,b_round1}/e4_oracle_reference.csv`.
  - Round 2: `red_round2.log`, `green_round2.log`, `reception_round2.log`, `refusal_round2.err`, `refusal_round2.out`
    (empty), `note_command_round2.log`, `integrity_round2.log`, `a_round2.sha256`, `b_round2.sha256` and
    `{a_round2,b_round2}/e4_oracle_reference.csv`.
  - Codex's reviews: `codex-review-round1.md` and `codex-review-round2.md`.
- **Environment.** Python 3.12.9 (`.venv`, built on the Trading 3.12.9 binary), numpy 2.4.4, pandas 3.0.6, scipy
  1.17.1, pytest 9.1.1, pyflakes 4.0.3. Nothing was installed.
- **Not done, as the GO and the reviews require:**
  - no full `make check`, reindexation, commit or push: these belong to Codex;
  - no tracked CSV and no `docs/MAPPING.md` or `docs/DEVIATIONS.md` entry;
  - no change to `jepadrift/` (including `floors.py` and `pipelines.py`), sealed PCA producers or artifacts,
    `paper/`, `prompts/streams/`, the master, the plan, the GO, lot 21-trace files or dependencies.
- **Preserved.** J1 was verified above. D8 stays FAIL at +5.2833 % as the GO states; it was not examined, and no
  tracked file changed.

## Vigilance Points

- **CSV hash scope.** The SHA-256 holds for the pinned environment only. Its evidence is six exports and three runs of
  the note command, all in this session and on this machine. The tests check the listed cases at the stated tolerances,
  in that environment only: no accuracy guarantee follows for untested inputs or other environments.
- **Long doubles untested.** NumPy long doubles follow the documented path (`.item()` leaves them as long doubles, then
  wider comparisons), but no test covers them, because their width depends on the platform.
- **Full suite not run.** The new test file has run only in the targeted command above. The Codex pre-commit hook will
  be the first full `make check` that includes it.
- **Patched helper.** The never-reach-the-helper test patches `jepadrift.floors.factor_information` for its own
  duration through pytest's `monkeypatch`.
- **Import chain.** The script imports `jepadrift.pipelines` for `save_fair_csv`. `floors.py` and `pipelines.py`,
  hashed by `CODE_MODULES` in `experiments/pca_drift_benchmark.py`, are unchanged.
- **Scope of the reference.** It covers the market (factor) term only: breadth is zero, ρ < 0 is excluded and variances
  are unit. It holds no delay, ADD, ARL0 or FPR, and it does not close E4.

## Recommendations

- **Codex final review.**
  - Recompute the SHA-256 values above.
  - Replay `.venv/bin/python -m pytest -q tests/test_e4_oracle_reference.py tests/test_floors.py`; 48 passed is
    expected.
  - Rerun the note's receipt command in a new directory and compare its hash with
    `b0d7f4fdeb6fc0ab404a0d059fd0210c73b81d11741d8c85c133d8ab54633996`.
  - Check the exact `git status --porcelain` above.
  - Then reindex and let the commit hook run the full `make check`.
- **Future E4 lot.**
  - If a second consumer of `oracle_row` appears, move it to `jepadrift/` with its tests, as `CLAUDE.md` requires.
  - Each extension needs its own plan and GO: breadth term, heterogeneous variances, ρ < 0, or Sharpe units through
    `floors.kl_from_sharpe`.
- **Combining with delays.** If I_N is ever combined with τ_γ, Φ or mixture costs, each derived delay must state its
  reading (budget, anytime-valid or exact) and stay out of this reference CSV.
