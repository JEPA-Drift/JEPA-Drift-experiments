# D1 (ETF-4) and D2 (US-97) — derived datasets from Article B

D1 and D2 are rebuilt from the local, read-only Article B checkout
(`~/The-Whitening-Advantage-Experiments`, commit recorded in
`data/derived/MANIFEST.json`). The remote repository is never cloned. Every
derived file is produced by a single entry point:

```bash
python -m jepadrift.data_loader.articleB --build
```

which writes `data/derived/{d1_etf4,d2_us97}/`, `data/derived/MANIFEST.json`
and `results/data/d1_d2_profile.csv` (log: `logs/data/build.log`).

## Sources and expected counts

| dataset | source (Article B) | content |
|---|---|---|
| D1 | `data/derived_firstrate/R01_daily_{SPY,PFF,VNQ,BWX}.csv` | SPY 6414 rows from 2000-01-04; PFF 4403 from 2007-12-27; VNQ 5014 from 2005-01-04; BWX 4451 from 2007-10-09; all end 2025-07-07; no NaN |
| D1 phases | `results/R16_regime_census/data/R16_regime_census{,_strict_ps,_symmetric}.csv` | 66 / 48 / 102 phases (see below) |
| D2 | `data/derived_equities/R15_panel_logreturns.csv` | 5154 days x 97 survivors, 2005-01-04 to 2025-06-30, no NaN, ~0.66% zero returns |

## Layout (identical for both datasets)

- `panel.parquet` — long format `date, asset_id, ret (float64), close, in_universe`.
  Full date x asset grid. D1: `ret`/`close` are NaN and `in_universe` is False
  outside each series' period (staggered starts). D2: `in_universe` is always
  True and `close` is NaN everywhere (R15 carries log returns only).
- `ret_wide.npy` — float64 `(T, N)` matrix, NaN outside each series' period (D1).
- `dates.npy` — `datetime64[D]`, the panel calendar (D1: the union of the four
  series, equal to the SPY calendar, 6414 days).
- `assets.json` — asset identifiers in column order of `ret_wide`.
- `splits.yaml` (both datasets), `phases_{lt_spy,strict_ps,symmetric}.csv` (D1).

Returns are ingested with `float_precision='round_trip'` and stored as float64:
CSV -> parquet -> numpy is bit-identical (deviation `C-interface-f64`, tested in
`tests/test_data_d1_d2.py`).

## Phase datations (D1)

Copies of the R16 census with a `dating_variant` column added:

- `lt_spy` (66 phases): Pagan–Sossounov on PFF, VNQ, BWX; Lunde–Timmermann on SPY (canonical).
- `strict_ps` (48 phases): Pagan–Sossounov on the four ETF.
- `symmetric` (102 phases): symmetric variant (Lunde–Timmermann throughout).

## Splits and embargo

`pretrain [2005-01-01, 2016-01-01)`, `calib [2016-01-01, 2020-01-01)`,
`monitor [2020-01-01, end]`. The 65 trading days after each internal boundary
(2016-01-01, 2020-01-01) are embargoed and excluded from the following segment.
Pretrain starts at the first panel day (D1: start of each series, 2000-01-04;
D2: 2005-01-04). Realized first/last trading day per segment:

| segment | first day | last day |
|---|---|---|
| pretrain (D1 / D2) | 2000-01-04 / 2005-01-04 | 2015-12-31 |
| calib | 2016-04-07 | 2019-12-31 |
| monitor (D1 / D2) | 2020-04-06 | 2025-07-07 / 2025-06-30 |

## Descriptive profile

`results/data/d1_d2_profile.csv`, per dataset and segment: `days`, `assets`,
`zero_ret_share`, `mean_sign_corr` (mean pairwise correlation of the sign
indicators `1{r>0}`), `k_eff = 1/rho_hat`, `pc1_var_share` (share of variance of
the first principal component, complete days). The D2 mean sign correlation is
~0.26 (reported, non-blocking; Article B `R15` prints 0.26 over K >= 5).

## Loaders

`jepadrift/data_loader/articleB.py` exposes `load_d1()`, `load_d2()` (returning
`(ret, dates, assets)` — float64 wide matrix, `datetime64[D]` dates, asset ids,
no transformation), `load_phases(variant)` (DataFrame) and `load_splits(dataset)`
(dict, dates as `datetime.date`).

## Verification

```bash
python -m jepadrift.data_loader.articleB --build
pytest -q tests/test_data_d1_d2.py
python -c "from jepadrift.data_loader.articleB import load_d2; r,d,a=load_d2(); print(r.shape, d[0], d[-1])"
```
