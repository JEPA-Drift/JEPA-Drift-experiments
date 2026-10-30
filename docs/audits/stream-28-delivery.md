# Stream 28 — schema /2 delivery contract

Schema: `pca_drift_benchmark/2`. Authoritative smoke evidence: `results/pca_drift_benchmark/smoke_predictive_v2_closeout/`.

The reviewed code and artifacts are accepted for delivery subject to the repository's mandatory final pre-commit `make check` gate. The delivery commit is created only if that gate succeeds; downstream planning remains blocked until this commit is integrated cleanly onto main. No full run or real post-2019 evaluation is authorized by this record.

## Frozen interface

The seven files, column order, types, enumerations, primary/foreign keys, hashing and temporal rules are defined in `docs/sections/pca_drift_benchmark.md`. The manifest scientific fingerprint is `9926b6652466a5b863ca23952b75beeffc7fc059a09bd46a6de881dfadad7443`.

- Tables and figures consume this producer's artifacts; they do not recalibrate or rerun detectors.
- Read CSVs with pandas `float_precision="round_trip"`. Axes are sorted 1-based JSON lists. Trials are normalized: common context is recovered through their group_id foreign key, not a duplicate schema_version column.
- E1/E2 prefixes reference exactly the same metric IDs and values; E3 mixture selection at k=20 reuses E2. Do not independently recompute shared aggregates.
- Calibration frequency, exchangeable predictive bound and observed holdout FPR are distinct. The predictive rule is floor(alpha*(n+1))-1; no bound is claimed for historical overlapping windows. The smoke is reproducibility/contract evidence, not an empirical performance conclusion.
- Gaussian mean-mixture scan, quadratic vech scan and energy CUSUM remain separate families. Joint covariance information is not an additive marginal sum; M is a model-based fluid surrogate, not exact delay.
- Real Covid standard split is NOT_EVALUABLE_STANDARD_SPLIT; prospective real evaluations remain BLOCKED_PRE_J4. Missing metrics remain NA.
- Any interface change requires an explicit schema revision and supervisor review. No downstream stream may reinterpret /2 silently.

## Artifact hashes

| File | Data rows | SHA-256 |
|---|---:|---|
| aggregates.csv | 387 | 6bd41250db9059abd19f4ec0976c8976fc54204e4321d66ad1b3a409c46e2f07 |
| calibration.csv | 106 | 04d463b42556dfcd784ef4833c9f4cec789f194cb436c093ce8c25b370c4378d |
| issues.csv | 10 | d7a276f9a52e5ed798e7f0e59a8b73d5a36e1478dd7d4754618d4ded2ce72caf |
| selection.csv | 2422 | f7b8406c7a73e0a19c905e9ef1104820b32d398269eecd6c40683c399f76655f |
| spectra.csv | 478 | 3718ed94123c0dad17505657383a1722d3e42d1f482b78b0d36f7efb28ca5e17 |
| trials.csv | 14320 | 3dcf83a82685a014fafef213358305239866eaf0851ffcc525cdbe6c455aa7be |
| manifest.json | — | 0dfe88dbae2a4d7fad21325a237edebdf8824a7eb1d13b11381fba5c9a62dfb9 |

The parent independently compared all seven files to the fresh repeat, recomputed the producer identity from the current code/config/environment/inputs, and obtained exact agreement. The repeat and partitions remain local.

## Review and verification

Both previously reported closeout defects are fixed: integer batch size under floating memory budgets, and homogeneous /2 configuration/manifest metadata. Independent re-review found no remaining blocker. Fresh stream verification: 50 tests passed in 7.95s and pyflakes exited 0. Actual Vibe export confirms mistral-large-4, alias large-4, thinking high, finished, exit 0.

Smoke cost measured by the implementer: primary wall 37.33s, maximum RSS 324596 KiB; repeat wall 37.18s, maximum RSS 322404 KiB. Full cost remains an extrapolation and was not measured. E2 disk/index CRLF and SHA-256 and historical E3 D8 FAIL are preserved.

## Publication and workflow

Only the current homogeneous closeout generation is published. Earlier /1 and pre-closeout /2 generations, repeat directories, partitions and CLI exports are preserved as local archives in the retained stream-28 worktree and are excluded from staging. They are not sealed evidence. Formal precommit handover: `prompts/wrapups/wrapup-28.md`.

The required index update uses Graphify's AST-only update and jCodeMunch with AI summaries explicitly disabled; neither semantic extraction nor paid LLM indexing is authorized. Final repository checks and Git operations run serially after stream processes exit, with explicit staging, anonymized Conventional Commit, no trailers and no proprietary/oversize files.

Indexing record: the first AST/source-index pass completed successfully. A later refresh after the delivery note was added completed Graphify but jCodeMunch refused the path because both local and Git identity indexes match it. No index was invalidated, as required by the closeout plan. This is a documented retrieval-cache ambiguity, not a scientific verification failure; targeted file discovery remains available. The final document refresh is not claimed as a successful jCodeMunch refresh.

After effective integration of 28, the authorized next work is sequential Claude plan generation for 29, then 30, then 31 (max/xhigh); no downstream implementation is authorized. Stream 31 owns discovery of the four PCA prompts and non-vacuous master synchronization, with IDs 28-PCA, 29, 30, 31; legacy E11 is unchanged.
