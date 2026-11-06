"""Tests of experiments/e4_oracle_reference.py (stream 19-oracle): I_N against independent closed forms and float64."""
import hashlib
import math
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pandas as pd
import pytest

from experiments import e4_oracle_reference as e4o

FLOAT_COLUMNS = ("rho", "delta", "factor_term", "breadth_term", "info_nats", "gain_vs_single", "gain_ceiling")
GRID = [(n, rho) for rho in (0.0, 0.4) for n in (1, 8, 16, 32, 64, 128, 239, 500)]


def closed_info(n, rho, delta):
    return delta * delta * n / (2.0 * (1.0 + (n - 1) * rho))


def closed_gain(n, rho):
    return n / (1.0 + (n - 1) * rho)


def test_closed_form_and_dense_solve():
    for n in (1, 2, 3, 5, 8, 13):
        for rho in (0.0, 0.25, 0.9):
            sigma = rho * np.ones((n, n)) + (1.0 - rho) * np.eye(n)
            for delta in (0.5, 2.0):
                row = e4o.oracle_row(n, rho, delta)
                dmu = np.full(n, delta)
                assert math.isclose(row["info_nats"], closed_info(n, rho, delta), rel_tol=1e-12)
                assert math.isclose(row["info_nats"], 0.5 * float(dmu @ np.linalg.solve(sigma, dmu)), rel_tol=1e-10)
                assert math.isclose(row["gain_vs_single"], closed_gain(n, rho), rel_tol=1e-12)
                assert row["breadth_term"] == 0.0


def test_info_is_half_the_quadratic_form():
    for rho in (0.0, 0.4, 0.9):
        row = e4o.oracle_row(1, rho, 2.0)
        assert math.isclose(row["info_nats"], 2.0, rel_tol=1e-12)
        assert math.isclose(row["factor_term"] + row["breadth_term"], 4.0, rel_tol=1e-12)
        assert math.isclose(row["gain_vs_single"], 1.0, rel_tol=1e-12)
    row = e4o.oracle_row(239, 0.4, 2.0)
    assert row["info_nats"] == (row["factor_term"] + row["breadth_term"]) / 2.0


def test_rho_zero_gain_is_n_without_finite_ceiling():
    for n in (1, 8, 239, 500, 2 ** 20):
        row = e4o.oracle_row(n, 0.0, 1.0)
        assert math.isclose(row["gain_vs_single"], n, rel_tol=1e-12)
        assert row["gain_ceiling"] == math.inf


def test_rho_near_one_stays_finite():
    for rho in (1.0 - 1e-6, 1.0 - 1e-12, float(np.nextafter(1.0, 0.0))):
        for n in (1, 2, 500):
            row = e4o.oracle_row(n, rho, 1.0)
            assert all(math.isfinite(row[c]) for c in FLOAT_COLUMNS)
            assert math.isclose(row["info_nats"], closed_info(n, rho, 1.0), rel_tol=1e-12)
            assert math.isclose(row["gain_vs_single"], closed_gain(n, rho), rel_tol=1e-12)


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize("n, rho, delta", [
    (0, 0.4, 1.0), (-1, 0.4, 1.0), (2.5, 0.4, 1.0), (8.0, 0.4, 1.0), (True, 0.4, 1.0),
    (8, -0.1, 1.0), (8, 1.0, 1.0), (8, 1.5, 1.0), (8, math.nan, 1.0), (8, math.inf, 1.0), (8, -math.inf, 1.0),
    (8, 0.4, 0.0), (8, 0.4, -1.0), (8, 0.4, math.nan), (8, 0.4, math.inf), (8, 0.4, -math.inf),
    (8, 0.4, 1e-200), (8, 0.4, 1e-155), (8, 0.4, 1e200),
    (1, 5e-324, 1.0), (2, 1e-310, 1.0),
    (8, 0.0, 1e154),
    (1, "0.4", 1.0), (1, None, 1.0), (1, 0.4, "1"), (1, 0.4, None), (8, False, 1.0), (8, 0.4, True),
    (2, 0.4, np.int64(2 ** 53 + 1)),
])
def test_out_of_domain_or_float64_limit_raises(n, rho, delta):
    with pytest.raises(ValueError):
        e4o.oracle_row(n, rho, delta)


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize("rho, delta", [
    (Decimal("0.9999999999999999999999"), 1.0), (Fraction(10 ** 22 - 1, 10 ** 22), 1.0),
    (Fraction(1, 10 ** 400), 1.0), (0.4, 10 ** 400),
])
def test_rounded_or_unconvertible_parameters_never_reach_the_helper(monkeypatch, rho, delta):
    def forbidden(*args):
        raise AssertionError("factor_information reached")

    monkeypatch.setattr(e4o.fl, "factor_information", forbidden)
    with pytest.raises(ValueError):
        e4o.oracle_row(2, rho, delta)


@pytest.mark.filterwarnings("error")
@pytest.mark.parametrize("kind", [np.float16, np.float32])
def test_narrow_numpy_floats_are_accepted_without_warning(kind):
    row = e4o.oracle_row(2, kind(0.25), kind(2))
    assert math.isclose(row["info_nats"], 3.2, rel_tol=1e-12)


@pytest.mark.filterwarnings("error")
def test_representable_extremes_are_accepted():
    assert e4o.oracle_row(np.int64(8), 0.4, 1.0)["N"] == 8
    row = e4o.oracle_row(8, np.float32(0.25), 2)
    assert math.isclose(row["info_nats"], closed_info(8, 0.25, 2.0), rel_tol=1e-12)
    for n, rho, delta in ((8, 0.4, 1e-150), (8, 0.4, 1e150), (2, 1e-300, 1.0)):
        row = e4o.oracle_row(n, rho, delta)
        assert math.isclose(row["info_nats"], closed_info(n, rho, delta), rel_tol=1e-12)
    assert math.isclose(e4o.oracle_row(2, 1e-300, 1.0)["gain_ceiling"], 1e300, rel_tol=1e-12)


def test_saturation_toward_one_over_rho():
    for rho in (0.1, 0.4):
        rows = [e4o.oracle_row(2 ** k, rho, 1.0) for k in range(21)]
        gains = [r["gain_vs_single"] for r in rows]
        assert all(a < b for a, b in zip(gains, gains[1:]))
        for r in rows:
            gap = (1.0 - rho) / (rho * (1.0 + (r["N"] - 1) * rho))
            assert math.isclose(r["gain_ceiling"], 1.0 / rho, rel_tol=1e-12)
            assert r["gain_vs_single"] < r["gain_ceiling"]
            assert abs(r["gain_ceiling"] - r["gain_vs_single"] - gap) <= 1e-12 / rho
            assert r["info_nats"] <= 1.0 / (2.0 * rho)


def test_cli_writes_exclusive_deterministic_hashed_grid(tmp_path, capsys):
    paths = (tmp_path / "a.csv", tmp_path / "b.csv")
    for path in paths:
        assert e4o.main(["--out", str(path)]) == 0
        assert capsys.readouterr().out == f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path}\n"
    assert paths[0].read_bytes() == paths[1].read_bytes()
    df = pd.read_csv(paths[0], float_precision="round_trip", dtype=dict.fromkeys(FLOAT_COLUMNS, "float64"))
    assert list(df.columns) == ["N", "rho", "delta", "factor_term", "breadth_term", "info_nats", "gain_vs_single",
                                "gain_ceiling", "qualification"]
    assert list(zip(df["N"], df["rho"])) == GRID
    for r in df.itertuples():
        assert math.isclose(r.info_nats, closed_info(r.N, r.rho, 1.0), rel_tol=1e-12)
        assert math.isclose(r.gain_vs_single, closed_gain(r.N, r.rho), rel_tol=1e-12)
        assert r.gain_ceiling == (math.inf if r.rho == 0.0 else 2.5)
        assert r.delta == 1.0 and r.qualification == "ORACLE_KNOWN_SIGMA_DELTA"
    pd.testing.assert_frame_equal(df, pd.DataFrame([e4o.oracle_row(n, rho) for n, rho in GRID]), check_exact=True)
    before = paths[0].read_bytes()
    with pytest.raises(FileExistsError):
        e4o.main(["--out", str(paths[0])])
    assert paths[0].read_bytes() == before
    assert capsys.readouterr().out == ""
