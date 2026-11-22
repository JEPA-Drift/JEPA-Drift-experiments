# Stream 32 — B3a receipt

19 November 2026. **B3a ACCEPTED ON DETERMINISTIC FIXTURES** under the B-TDD GO.

`calibrate_nonoracle` and `calibrate_oracle` reuse the received scans with the supplied
frozen prior and policy. The resulting timewise maxima are passed once to the sealed GE rank.
The oracle uses only its supplied q and carries `NON_DEPLOYABLE_ORACLE_CALIBRATION`.
T43 passes. T10, T15, T19 and T26 have additional slice evidence and remain partial.

| Step | Observed result | Pytest log SHA-256 |
| --- | --- | --- |
| RED | Exit 1. 14 expected absent-API failures, 840 passed in 30.39 s | `04b67d56b1d1de238ae10cfff4a25dffc7a4f6143233e2aa49bad3a987823861` |
| GREEN | Exit 0. 854 passed in 20.43 s. Pyflakes and git diff check clean | `08f41b7c7fbb63783eee5460849ae8aa0fd28b53a691d0b3eacfab09072cddd2` |

C0 used `tests/test_pca_info_online.py` and `tests/test_check_prompts.py` under the shared lock,
deterministic environment and pinned venv. Both logs are under `logs/stream-32/`.
The received source and test prefixes retain their B2 hashes.

- Source SHA-256 `035843db0d233d587e4bcb6a716f362033ca80e9139a351931bbbae06e4c089c`.
- Tests SHA-256 `85517c2b219e025cec1a03789e3502f6725025e3a5ddabbf5de378bd1c686c6c`.
- Sealed PCA producer SHA-256 `8324b47b505ca935cd6bbd8ad6757db59bf78795678f4d94af128da0d9c0b373`.

The RED and GREEN reviews record each Claude Code UUID and effort, the withheld V1 and
the mechanical omissions. Phase-level calibration, identity reuse and subsequent inference
remain open in B3. T34 and T41 remain NOT_RUN.
