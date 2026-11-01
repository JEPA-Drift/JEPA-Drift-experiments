# Stream 30 implementation plan review

Date: 2026-10-31. Verdict: ACCEPT_WITH_MINOR_AMENDMENTS, plan only.

## Scope and evidence

An isolated Codex reviewer read only the full stream-30 proposal, its assigned prompt/scientific references, the sealed producer /2 contract and code/artifacts, and stream-29 GO/interface facts. No other full plan was loaded in that review context. Original proposal: 389 lines, 35149 bytes, SHA-256 12651c01a932d482622fd861c142e763491ba6eaaa1e50b0bfccdec01337c7b7.

The declared C/B30 Gaussian primary scenarios and separate mean-t7 robustness entry, detector families, proxy/heuristic labels, energy comparator, lineage, H250, missing-data rules, deterministic formats and planned visual QC match the assigned scope. The three declared specifications have all k=1..20 and finite source V values. All 129 real event metrics remain NOT_EXECUTED.

The sealed manifest and six CSV hashes, scientific identity, E2 disk/index SHA-256 and CRLF, and historical E3/D8 FAIL were checked. Parent independently confirmed upstream identity and invariants, and verified the two narrow findings against source excerpts and producer metadata.

## Minor amendments applied by Codex

1. Original PLAN.md line 109 could require numerically equal M denominators for prefix and selected subsets. The rule now requires a common cost function/gamma and checks each source M_cost at its own d, without recomputing V. Parent verified unequal M_cost in 114/114 paired synthetic source rows at k=2..20; this is legitimate when dimensions differ.
2. Original line 97 could require the manifest hash in manifest.outputs. The producer map contains six CSVs only. CSV hashes are checked there; manifest hash is checked through table input provenance.

The raw proposal is retained byte-for-byte. Only these two substitutions and the integrated GO section are present in the canonical plan.

## Boundaries and deferred checks

Wilson overlap is explicitly descriptive, not evidence of equal achieved FPR. Marginal RMST intervals are not paired-difference intervals. The table assembler and its artifacts are not implemented; exact future reader APIs, interval suffixes and nested code-hash keys remain G0 checks. No implementation compatibility, rendering, visual inspection, application test, Monte Carlo run or real post-2019 evaluation is claimed.

There is no substantive finding requiring a Claude revision. Execution requires the appropriate GO and available reviewed stream-29 outputs. Git integration and full repository checks remain Codex-controlled and serialized after stream processes exit.

