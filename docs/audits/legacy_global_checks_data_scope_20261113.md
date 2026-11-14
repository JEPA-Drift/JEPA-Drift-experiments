# Historical global-check data scope, 2026-11-13

This source and log audit corrects the scope attributed to the global regression check. It grants no data-access
exception, changes no test outcome and is not an E4 scientific result. No Python, test, panel or panel metadata was
read/executed for this audit. Only source text, historical run logs and Git metadata were inspected.

## Established execution evidence

R0009 ran unfiltered `make check` in the E4 worktree with the pinned environment. It returned 37 PASS, then
1,308 PASS and five D4 availability skips only. The raw command, output, time and exit are retained under
`logs/stream_19_e4_production/codex-runs/R0009/`. No D3 skip is reported. The root `conftest.py` is empty and the
Makefile's second pytest call excludes only the separately run contract/decoupling files and external directory.

Combined with the source below, this implies that the data-backed D3 integration checks were included. Their
execution must not be described as synthetic-only or as a proof of pre-2020 I/O. No unrecorded syscall trace is
claimed: the inference follows the command, passed suite, skip list and called functions.

## Targeted source findings

| File | Finding | Boundary status |
|---|---|---|
| `tests/test_e4_alignment.py:423` | File readers are intercepted to refuse data/; generated paths and tmp_path CSVs are synthetic | False positive in the candidate grep list; no real panel identified |
| `tests/test_data_d3.py:267` | Explicit 2020 universe membership check; at :328 full-panel reconstruction; at :351 profile includes monitor/2022–2024 | Actual whole-period data integration, not a pre-2020-only unit check |
| `tests/test_data_d1_d2.py:47` | Full Article B reconstructions, terminal dates in 2025, full-return comparisons and panel statistics | Distinguish the existing Article B identity exception from descriptive calculations |
| `tests/test_chars.py:13` | Calendar selects pre-2020 rows after complete return/Parquet loads | Selected rows are pre-2020; bounded file I/O is not established |

The indices 4,000/4,250 in `test_chars.py` are absolute. They cannot be compared to E10's relative pre_monitor
length 3,775 to infer a year. Its line 42 explicitly requires `dates500[4249] < 2020`. The earlier native plan's
opposite claim was rejected and corrected.

Direct loader paths are `sp500._load_wide`, `articleB._load_wide`, `sp500.load_chars` and `chars._grid`/pivot. Several
load whole files before selecting dates. Neither a subsequent date filter nor delegation to Codex authorizes an
otherwise prohibited read. A list of twelve source filenames obtained by grep is only a candidate list, not twelve
established violations; mocks, synthetic inputs and already bounded calls require separate classification.

## Consequences and limits

The earlier broad statement that no real financial rows were used by all engineering verification was incorrect.
The production-pilot report now separates E4-specific tests/pilots/producer from the historical global baseline.
Future global checks must not silently repeat the incompatible reads or silently skip their contracts. Their
bounded-fixture/reader treatment, or a distinct explicit access decision, must be settled before those checks and
the associated integration. No exception is inferred from an earlier PASS or from a continuation instruction.

E4's scientific path remains `role_path -> draw_innov/t7_scale` and `fit_rows`, with synthetic fit/calibration/
holdout/alternative seed domains. It does not read the real panels above. Its source/configuration were frozen
before R0009 and no scientific choice was changed using these regression outcomes. The currently authorized
synthetic campaign continues; this audit opens no additional numerical job or real-data access.

This is a verification-scope limitation, not a reproduction failure or evidence of leaked real values into E4.
The global-suite issue remains distinct from the two open F2 design decisions and from Article B identity work.

## Subsequent researcher authorization

The researcher explicitly granted the requested authorizations on 2026-11-13. The decision is recorded in
`prompts/GO-legacy-global-check-access-20261113.md`, SHA-256
`5c81eb915837b3e2976840057a202b3045e3ce860711e4c602293d6e4aecde0e`.
It permits the unchanged local global baseline and hook for integrity/nonregression under the requested limits,
including the documented full-period legacy checks. It changes no scientific data window, design or result.
The historical findings above remain part of the record. New checks wait for the shared numerical slot after E4.
