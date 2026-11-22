# Stream 32 — B4y receipt

20 November 2026. **T35 and T36 pass on the spectral CLI fixture.**

The fixture runs EXACT N=32 and N=239 and FITTED_LW_GAUSSIAN
N=32, on RESIDUAL and MARKET. It verifies the restricted
covariance EIGENMEAN prefixes against the independent reference.
The two EXACT setups use PC 2–9 for RESIDUAL and PC 1–7 for
MARKET. Residual CPV90 uses PC 2–16 in the EXACT setups. Global
CPV90 reaches 17 PCs in EXACT MARKET N=32 and is outside the
20-axis universe in EXACT MARKET N=239. It retains its explicit
OUTSIDE_UNIVERSE status in RESIDUAL. Inapplicable rows have no
CAL identity. These statuses are recorded in committed SETUP
and DEV.

The fixture publishes 16 selections: six EIGENMEAN, six FULL_K,
three residual CPV90 and one global CPV90. Each published
cardinality matches the frozen HOLD and ALT masks. Locked C0
measured **1,058 passes in 92.91 seconds**. Matrix totals are
**61 PASS and 7 NOT_RUN**.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |
| `tests/test_pca_info_online.py` | `67ce92d1a9a191be9755356bdefe5f9818ad9439e381b62d63ec96c66317fb9d` |
| `logs/stream-32/lot-B4y-tests.pytest.log` | `f33e3a9bc679fd39caf406c9314c59264eb029a17dad18d3d11ba2cdac753917` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `6c0314837c7236d3fcef67a51ec9379c29e0d8f2002d9f16b29eec08b733bc73` |
| Fixture manifest.json | `7884b201282f37a5c32a0c5054599c8a0a21e6da735119017d8621d815163595` |
| Fixture selections.csv | `826f036a059098023516c7fb3cf349335940f51831d0b58867cecddab4970470` |
| Fixture calibration.csv | `6d4add25bd32601fa05329c8cf6a279bac7411a5fd68c86cf2a7c296b03de5b0` |
