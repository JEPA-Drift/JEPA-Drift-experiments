"""Identity controls against the Article B reference code: ported sources, R01 outputs and the R08 exact lattice law (pytest)."""
import ast
from pathlib import Path

import numpy as np
import pytest

from experiments import identity_articleB as ib
from jepadrift.data_loader.articleB import ARTICLE_B
from jepadrift.monitors import cusum

pytestmark = pytest.mark.skipif(not ARTICLE_B.exists(), reason="Article B checkout absent")

REPO = Path(__file__).resolve().parents[1]
B_EXP = ARTICLE_B / "experiments"
R01 = B_EXP / "R01_real_world_backtest" / "exp_R01_real_world_backtest.py"
R15 = B_EXP / "R15_cross_sectional" / "exp_R15_cross_sectional_b.py"
PORTS = (
    (R01, REPO / "jepadrift" / "monitors" / "cusum.py", ("strict_cusum", "get_multiple_alarms", "get_cusum_trajectory")),
    (R01, REPO / "jepadrift" / "stats" / "garch.py", ("_garch_nll", "fit_garch_qmle", "compute_gamma_exact")),
    (R01, REPO / "experiments" / "identity_articleB.py", ("wilson_ci",)),
    (R15, REPO / "jepadrift" / "monitors" / "cusum.py", ("bilateral_delay", "cusum_max_bilateral")),
    (R15, REPO / "jepadrift" / "monitors" / "streams.py", ("fraction_stream",)),
    (R15, REPO / "jepadrift" / "monitors" / "calibration.py", ("worker_null_window_real", "worker_race_h1_real")),
    (R15, REPO / "jepadrift" / "pipelines.py", ("composition_for",)),
    (R15, REPO / "experiments" / "identity_articleB.py", ("get_deterministic_seed",)),
    (B_EXP / "R09_eprocess_anytime" / "exp_R09_eprocess_anytime.py", REPO / "jepadrift" / "monitors" / "eprocess.py",
     ("build_mixture_kernel",)),
    (B_EXP / "common" / "fair_harness.py", REPO / "jepadrift" / "pipelines.py", ("save_fair_csv",)),
)


def _segments(path):
    src = Path(path).read_text()
    return {n.name: ast.get_source_segment(src, n) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}


@pytest.fixture(scope="module")
def table():
    return ib.identity_table()


def test_ported_sources_byte_identical():
    for ref_path, our_path, names in PORTS:
        ref, ours = _segments(ref_path), _segments(our_path)
        for name in names:
            assert ours[name] == ref[name], (our_path.name, name)
    assert ast.dump(ast.parse(_segments(R15)["strict_cusum"])) == ast.dump(ast.parse(_segments(R01)["strict_cusum"]))


def test_r01_identity_d1_loader(table):
    rows = table[table["input"] == "d1_loader"]
    assert set(rows["source"]) == set(ib.R01_SOURCES)
    assert rows["pass"].all(), rows.loc[~rows["pass"], ["source", "row", "column", "rel_diff"]]
    spy = rows[(rows["source"] == "R01_garch_models") & (rows["row"] == 0)].set_index("column")["reproduced"]
    assert spy["Ticker"] == "SPY" and float(spy["alpha"]) == 0.211551 and float(spy["beta"]) == 0.729081
    assert float(spy["gamma_hat"]) == 14.998367977816738 and float(spy["q_hat"]) == 0.55864811133200798
    alarms = rows[rows["source"] == "R01_covid_alarms"].set_index("column")["reproduced"]
    assert alarms["n_alarms"] == "0"


def test_r01_reader_bit_identical_except_blas_sensitive_column(table):
    rows = table[table["input"] == "articleB_csv"]
    assert len(rows) > 0 and rows["pass"].all()
    assert set(rows.loc[~rows["bit_identical"], "column"]) <= set(ib.BLAS_SENSITIVE)


def test_r08_exact_law(table):
    rows = table[table["source"] == "R08_lattice_exact_law"]
    assert len(rows) == 32 and rows["pass"].all() and (rows["rel_diff"] <= 1e-12).all()
    for row, value in ((6, 0.051020717214682557), (7, 0.043428228893176074)):
        assert abs(float(rows.loc[rows["row"] == row, "reproduced"].iloc[0]) / value - 1.0) < 1e-12


def test_vectorized_cusum_on_r01_streams():
    frames = ib.r01_frames("d1_loader")
    models, _ = ib.r01_models(frames)
    recs = ib.injection_streams(frames, models)
    assert len(recs) == 576
    for tk in ib.TICKERS:
        sub = [r for r in recs if r["ticker"] == tk]
        energy, label = np.stack([r["energy"] for r in sub]), np.stack([r["label"] for r in sub])
        thr = sub[0]["thr_data"]
        assert (cusum.strict_cusum_vec(energy, 0.5, thr).tolist()
                == [cusum.strict_cusum(r["energy"], 0.5, thr) for r in sub])
        concept = cusum.bilateral_delay_vec(label, 0.1, 10.0)
        assert concept.tolist() == [cusum.bilateral_delay(r["label"], 0.1, 10.0) for r in sub]
        assert (concept >= 0).any()


def test_r15_identity_rng_free():
    rows = ib.r15_rows(bootstrap=False, race=False)
    assert len(rows) == 44 and rows["pass"].all(), rows.loc[~rows["pass"], ["source", "row", "column", "rel_diff"]]
    rho = rows[rows["column"] == "rho_sign_meas"].set_index("row")["reproduced"].astype(float)
    for K, value in ((5, 0.25774155995343417), (10, 0.25904514047705118), (20, 0.28810195766064206)):
        assert abs(rho[K] / value - 1.0) <= 1e-12


def test_r15_bootstrap_identity_k5():
    rows = ib.r15_rows(ks=(5,), race=False)
    assert rows["pass"].all()
    cells = rows.set_index("column")["reproduced"]
    assert float(cells["lambda_boot"]) == 34.200000000000003 and float(cells["FPR_boot"]) == 0.053
