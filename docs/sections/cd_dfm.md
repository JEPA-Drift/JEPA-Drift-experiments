# Stream 18 — CD-DFM Baseline Status & Documentary Diagnostic

**Status:** Secondary Documentary Diagnostic (Excluded from Primary J4 Confirmatoire Gate)

**Context.** CD-DFM (Continuous-Discrete Dynamic Factor Model) was evaluated as a potential dynamic factor
baseline alongside IPCA (P4) and the zero-degree cross-sectional normalisation P3-CS(b), as part of the
benchmark comparison for Article C.

## Grounds for Exclusion from Primary Experimental Pipelines (E5 / J4)

- **Absence of Open-Source License.** The pinned upstream clone available in the local environment ships no
  explicit open-source license (MIT, Apache, BSD, or GPL). Under standard copyright law ("All rights
  reserved"), vendoring or redistributing this code inside the public replication package would violate the
  project publication policies and the CIFRE confidentiality / IP compliance rules recorded in `CLAUDE.md`.
- **Absence of Z-1 Data Ingestion Loader.** The upstream implementation provides no interface compatible with
  the project's Z-1 representation contract (`fit(X_calib, C_calib, dates)` and `_day(x_t, C_t)`). Ingesting
  the daily panel `d3_239` (`panel.parquet`) and the ex-ante characteristic tensors C_{i,t} (`chars.parquet`)
  without lookahead leakage or lookback boundary violations would require a full rewrite of its state-space
  ingestion layer.
- **Protocol Compliance** (`07_STREAM_22_E5_J4_REWRITE.md`, Section 2). The confirmatoire protocol states that
  CD-DFM enters primary benchmarking if and only if it is "réellement disponible, licite, préspécifié et gelé
  avant J4 ; sinon diagnostic secondaire ou « non disponible » sans remplacement caché". Neither the license nor
  the Z-1 ingestion condition is met, so CD-DFM is recorded as a secondary diagnostic, with no hidden
  replacement in the primary pipelines.

## Theoretical Positioning (Article C Benchmark Comparison)

- CD-DFM rests on linear dynamic latent factors with explicit Kalman transition dynamics, which carries a high
  parameter estimation cost under large cross-sections and requires multi-step dynamic transition modelling at
  inference time.
- JEPA, by contrast, is a non-linear daily cross-sectional self-supervised encoding with frozen inference and
  zero multi-step dynamic transition modelling: each day is encoded independently, so no state-space
  propagation is needed at monitoring time.
- IPCA (P4) already captures characteristic-guided linear factors, and P3-CS(b) captures instantaneous
  zero-degree scale invariance. Together they provide sufficient orthogonal coverage of the linear-factor and
  scale-invariance alternatives for the primary research question, which is why the absence of CD-DFM from the
  primary pipelines does not leave a coverage gap.
