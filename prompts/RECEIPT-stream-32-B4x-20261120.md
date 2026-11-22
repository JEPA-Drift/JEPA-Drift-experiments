# Stream 32 — B4x receipt

20 November 2026. **T39 and T42 pass on the fitted Gaussian CLI fixture.**

The two `ORACLE_INFO_MIX` rows carry `ORACLE_DIAGONAL_SURROGATE`
and `ANALYTIC_PROXY`. CAL uses `NON_DEPLOYABLE_ORACLE_CALIBRATION`
for both rows. The selection fields below are means over three
synthetic paths per family at horizon six.

| Family | I_mean | I_joint_mean | V_bar | V_joint_bar |
| --- | ---: | ---: | ---: | ---: |
| F2_STRUCTURED_RESIDUAL | 0.2157644131580411 | 0.20647919900274614 | 0.10071596918243547 | 0.096527922882422415 |
| F_HEAD_RESIDUAL | 0.2985662409960686 | 0.22985640264195828 | 0.16620507927057052 | 0.12785761806962787 |

The test verifies all four means against independent per-path
computations from the committed ALT masks. The manifest binds
selections.csv, and each selection binds its own ALT partition and
CAL record. Three successive test drafts supplied the accepted
append. Locked C0 measured **1,057 passes in 92.81 seconds**.
Matrix totals are **59 PASS and 9 NOT_RUN**.

| Artifact | SHA-256 |
| --- | --- |
| `experiments/pca_info_online.py` | `a62038ff441757ead73bc01cf5cf5c341404de7acc8ccade8c94d5dc4e012b64` |
| `tests/test_pca_info_online.py` | `b7b7ebef8c4de643913b5f61cfec769729e44fb1688ecd7edd886601e9ffc8a8` |
| `logs/stream-32/lot-B4x-tests.pytest.log` | `b9d343d26b1c061155a7ccd15fd9c53c838fb3fd8790f2232c3be19a8f9c8561` |
| `prompts/MATRIX-stream-32-T1-T68-20261114.md` | `2392b06315ff0ec864114d923f6e4fa2df8c37d074804486169d76e84305f8e3` |
| Full fixture manifest.json | `4565ca339f89aac0c8c947ba118b19874def7d5713ba2748c3f939cd4b3be6d7` |
| Full fixture selections.csv | `8532511523d18db7bef08a5b58e672892bd7e998bbc161f887dd0f199c6a5714` |
| Full fixture calibration.csv | `1de3a82ea8358cb73150897d8e18d920f753ee036eae4053493443f973720f56` |
