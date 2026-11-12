import copy
import itertools
import math

import numpy as np
import pandas as pd
import pytest

from experiments import e4_alignment as e4
from experiments import pca_drift_benchmark as pdb
from jepadrift import pipelines
from jepadrift.monitors import eprocess

BASE = {"stream": 19, "seed": 42, "rho": 0.4, "H": 30, "alpha": 0.05, "grid": [4, 6], "T_fit": 60, "n_cal": 20,
        "n_hold": 20, "n_alt": 20, "B_boot": 50, "pilot_n": 4, "prefix_k": 2, "info_divisor": 40.0,
        "backgrounds": {"gaussian": None, "t7": 7}, "fpr_margin": 0.01, "qualification": 0.95,
        "limits": {"rss_gib": 8.0, "invocation_seconds": 1800, "block_paths": 8}}


def cfg(**kw):
    c = copy.deepcopy(BASE)
    c.update(kw)
    return e4.validate_config(c)


def hadamard4():
    return np.array([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]], dtype=np.float64).T / 2.0


def fixed_orthonormal(n):
    return np.linalg.qr(np.arange(n * n, dtype=np.float64).reshape(n, n) + n * np.eye(n))[0]


@pytest.mark.parametrize("key,value", [("grid", []), ("grid", [True]), ("grid", [4.5]), ("grid", [0]), ("grid", [-3]),
                                       ("rho", float("nan")), ("rho", 1.0), ("alpha", 0.0), ("alpha", float("inf")),
                                       ("H", float("inf")), ("H", 0), ("info_divisor", float("nan")), ("n_cal", 18)])
def test_validate_config_refuses_invalid_inputs(key, value):
    c = copy.deepcopy(BASE)
    c[key] = value
    with pytest.raises(ValueError):
        e4.validate_config(c)


def test_validate_config_refuses_t7_nu_at_most_two():
    c = copy.deepcopy(BASE)
    c["backgrounds"] = {"gaussian": None, "t7": 2}
    with pytest.raises(ValueError):
        e4.validate_config(c)


def test_validate_config_accepts_rank_minimum_and_i_star_matches_journal():
    assert cfg(n_cal=19)["n_cal"] == 19
    assert e4.i_star(2000, 0.05) == pytest.approx(0.211932694662, rel=1e-11)


def test_shipped_config_holds_the_approved_protocol():
    c = e4.validate_config(e4.load_config(e4.CONFIG))
    assert c["grid"] == [8, 16, 32, 64, 128, 239, 500]
    assert (c["H"], c["alpha"], c["rho"], c["seed"], c["prefix_k"], c["pilot_n"]) == (2000, 0.05, 0.4, 42, 8, 40)
    assert (c["T_fit"], c["n_cal"], c["n_hold"], c["n_alt"], c["B_boot"]) == (2000, 2000, 2000, 2000, 2000)
    assert c["backgrounds"] == {"gaussian": None, "t7": 7}


def test_residual_direction_refuses_one_asset():
    with pytest.raises(ValueError):
        e4.residual_direction(np.ones(5), 1)


def test_residual_direction_of_two_assets_is_the_signed_difference():
    u = e4.residual_direction(np.array([0.3, -1.2, 5.0]), 2)
    assert u[0] == -u[1]
    assert abs(abs(u[0]) - 1.0 / math.sqrt(2.0)) <= 1e-15


def test_basis_methods_refuse_one_asset_while_ew_is_defined():
    with pytest.raises(ValueError):
        e4.fit_cell(cfg(), "gaussian", 1, "science")
    assert e4.ew_weights(1).tolist() == [1.0]


def test_prefix_larger_than_dimension_is_refused():
    with pytest.raises(ValueError):
        e4.prefix_channels(8, 4)
    assert e4.prefix_channels(2, 4) == [0, 1]


def test_seed_plan_raises_on_forced_crc32_collision(monkeypatch):
    monkeypatch.setattr(pdb, "label_code", lambda label: 7)
    with pytest.raises(ValueError, match="CRC32"):
        e4.seed_plan(cfg())


def test_seed_plan_keys_are_unique_and_spaces_disjoint():
    c = cfg()
    plan = e4.seed_plan(c)
    science = {tuple(k) for k in e4.planned_keys(c, "science")}
    pilot = {tuple(k) for k in e4.planned_keys(c, "pilot")}
    assert plan["n_keys"] == len(science) + len(pilot)
    assert not science & pilot
    assert tuple(e4.key(c, "science", "coins", "holdout", 3) + [7]) in science


def test_role_keys_are_disjoint():
    c = cfg()
    roles = {role: {tuple(e4.key(c, "science", "innov", role, i)) for i in range(20)}
             for role in ("calibration", "holdout", "alternative")}
    scalar = {tuple(e4.key(c, "science", "scalar_cal", i)) for i in range(20)}
    sets = list(roles.values()) + [scalar]
    assert all(not a & b for a, b in itertools.combinations(sets, 2))


def test_draws_leave_the_global_numpy_state_unchanged():
    c = cfg()
    before = np.random.get_state()
    e4.draw_innov(c, "science", "holdout", 0, c["H"])
    e4.t7_scale(c, "science", "holdout", 0, c["H"], 7)
    e4.direction_draw(c, "science", 0)
    after = np.random.get_state()
    assert before[0] == after[0] and np.array_equal(before[1], after[1]) and before[2:] == after[2:]


def test_nested_truncation_equals_first_columns():
    c = cfg()
    innov = e4.draw_innov(c, "science", "holdout", 0, c["H"])
    s = e4.t7_scale(c, "science", "holdout", 0, c["H"], 7)
    for scale in (None, s):
        assert np.array_equal(e4.panel(innov, scale, 6, c["rho"])[:, :4], e4.panel(innov, scale, 4, c["rho"]))


def test_residual_direction_is_unit_orthogonal_and_carries_i_star():
    c = cfg()
    u = e4.residual_direction(e4.direction_draw(c, "science", 0), 6)
    assert abs(u.sum()) <= 1e-12
    assert abs(np.linalg.norm(u) - 1.0) <= 1e-12
    scale = e4.drift_scale(c)
    assert math.isclose(scale ** 2 / (2.0 * (1.0 - c["rho"])), e4.i_star(c["H"], c["alpha"], c["info_divisor"]),
                        rel_tol=1e-14)


def test_ew_sign_stream_is_blind_to_the_residual_drift():
    c = cfg()
    X = e4.panel(e4.draw_innov(c, "science", "alternative", 1, c["H"]), None, 6, c["rho"])
    u = e4.residual_direction(e4.direction_draw(c, "science", 1), 6)
    w = e4.ew_weights(6)
    assert np.array_equal(X @ w > 0, (X + e4.drift_scale(c) * u) @ w > 0)


def test_t7_null_signs_equal_gaussian_null_signs_for_a_fixed_basis():
    c = cfg()
    innov = e4.draw_innov(c, "science", "holdout", 2, c["H"])
    s = e4.t7_scale(c, "science", "holdout", 2, c["H"], 7)
    V = fixed_orthonormal(6)
    assert np.array_equal(e4.panel(innov, None, 6, c["rho"]) @ V > 0, e4.panel(innov, s, 6, c["rho"]) @ V > 0)


def test_canonical_eigh_refuses_repeated_eigenvalues():
    Q = fixed_orthonormal(3)
    S = Q @ np.diag([2.0, 1.0, 1.0]) @ Q.T
    lam, V = np.linalg.eigh((S + S.T) / 2.0)
    with pytest.raises(e4.EigenTieUnresolved) as exc:
        e4.canonical_eigh(lam[::-1].copy(), V[:, ::-1])
    assert exc.value.code == "EIGENVALUE_TIE_UNRESOLVED"
    assert exc.value.blocks == [[1, 2]]
    with pytest.raises(e4.EigenTieUnresolved):
        e4.canonical_eigh(np.ones(3), np.eye(3))


def test_canonical_eigh_gap_boundary_is_inclusive():
    tol = 64 * np.finfo(np.float64).eps * 2.0
    with pytest.raises(e4.EigenTieUnresolved):
        e4.canonical_eigh(np.array([2.0, 2.0 - tol, 1.0]), np.eye(3))
    lam, _, _ = e4.canonical_eigh(np.array([2.0, 2.0 - 2.0 * tol, 1.0]), np.eye(3))
    assert lam.tolist() == [2.0, 2.0 - 2.0 * tol, 1.0]


def test_canonical_eigh_refuses_increasing_order():
    with pytest.raises(ArithmeticError):
        e4.canonical_eigh(np.array([1.0, 2.0]), np.eye(2))


def test_canonical_eigh_orients_by_the_first_maximum_absolute_coordinate():
    V = hadamard4()
    V[:, 1] *= -1.0
    lam, Ve, s = e4.canonical_eigh(np.array([4.0, 3.0, 2.0, 1.0]), V)
    assert s.tolist() == [1.0, -1.0, 1.0, 1.0]
    assert (Ve[0] > 0).all()
    assert lam.tolist() == [4.0, 3.0, 2.0, 1.0]


def test_canonical_eigh_is_invariant_to_input_signs_bitwise():
    V, lam = fixed_orthonormal(4), np.array([4.0, 3.0, 2.0, 1.0])
    ref = e4.canonical_eigh(lam, V)[1]
    for flips in itertools.product([1.0, -1.0], repeat=4):
        assert np.array_equal(e4.canonical_eigh(lam, V * np.array(flips))[1], ref)


def test_basis_hash_changes_when_a_sign_is_flipped():
    V, lam = hadamard4(), np.array([4.0, 3.0, 2.0, 1.0])
    V[:, 2] *= -1.0
    _, Ve, s = e4.canonical_eigh(lam, V)
    assert s[2] == -1.0
    assert pdb.array_sha256(lam, Ve) != pdb.array_sha256(lam, V)


def test_fit_cell_states_are_bitwise_coherent_with_the_canonical_basis():
    cell = e4.fit_cell(cfg(), "gaussian", 6, "science")
    W = cell["states"]["SPEC-full"]["rep"].state["W"]
    dz = cell["states"]["P3-CS(b)"]["rep"]
    assert np.array_equal(W, cell["V_e4"] / np.sqrt(cell["eigval"]))
    assert np.array_equal(dz.state["U"], cell["V_e4"][:, 1:])
    assert np.array_equal(np.abs(dz.state["b"]), np.abs(cell["V_e4"][:, 0]))
    assert cell["states"]["SPEC-full"]["rep"].fit_info["x_sha256"] == dz.fit_info["x_sha256"]
    assert cell["basis_hash_e4"] == pdb.array_sha256(cell["eigval"], cell["V_e4"])
    assert cell["states"]["SPEC-prefix8"] is cell["states"]["SPEC-full"]


def test_canonical_state_leaves_the_original_state_intact():
    c = cfg()
    X = e4.fit_rows(c, "gaussian", 4, "science")
    spec = e4.make_specs(c)["SPEC-full"]
    legacy = pipelines.fit_pipeline(spec, X, e4.fit_splits(len(X)))
    W0 = legacy["rep"].state["W"].copy()
    out = e4.canonical_state(legacy, -np.ones(4))
    assert np.array_equal(legacy["rep"].state["W"], W0)
    assert np.array_equal(out["rep"].state["W"], -W0)


def test_kernel_log_path_matches_registry_detection_offsets():
    c = cfg(grid=[8], prefix_k=8)
    cell = e4.fit_cell(c, "gaussian", 8, "science")
    u = e4.residual_direction(e4.direction_draw(c, "science", 0), 8)
    hits = 0
    for m in e4.DICTIONARY:
        spec = {**cell["specs"][m], "gamma": 3.0}
        state = cell["states"][m]
        x = np.stack([pipelines.PIPELINES[spec["pipeline"]][1](
            spec, state, e4.role_path(c, "science", "gaussian", "alternative", i, 8) + 3.0 * e4.drift_scale(c) * u,
            e4.coins_rec(c, "science", "alternative", i)) for i in range(4)])
        offsets = pipelines.PIPELINES[spec["pipeline"]][2](spec, state, x)
        assert np.array_equal(eprocess.first_alarm(e4.kernel_log_path(spec, x), spec["gamma"]), offsets)
        hits += int((offsets >= 0).sum())
    assert hits > 0


def test_prefix_state_reuse_equals_a_dedicated_fit():
    c = cfg(grid=[8], prefix_k=8)
    cell = e4.fit_cell(c, "gaussian", 8, "science")
    X = e4.fit_rows(c, "gaussian", 8, "science")
    dedicated = e4.canonical_state(pipelines.fit_pipeline(cell["specs"]["SPEC-prefix8"], X, e4.fit_splits(len(X))),
                                   cell["signs"])
    assert np.array_equal(dedicated["rep"].state["W"], cell["states"]["SPEC-prefix8"]["rep"].state["W"])
    assert dedicated["threshold"] == cell["states"]["SPEC-prefix8"]["threshold"]


def test_reading_labels_never_say_anytime_valid():
    assert e4.READINGS == ("predictive_rank", "anytime_valid_horizon")


def test_rank_first_hit_counts_days_from_one():
    assert e4.rank_first_hit(np.array([2.0, 0.0, 0.0, 0.0, 0.0]), 1.0) == 1
    assert e4.rank_first_hit(np.array([0.0, 0.0, 0.0, 0.0, 2.0]), 1.0) == 5
    assert e4.rank_first_hit(np.zeros(5), 1.0) == -1


def test_horizon_first_hit_counts_days_from_one():
    L = math.log(10.0)
    assert e4.horizon_first_hit(np.array([L, 0.0, 0.0, 0.0, 0.0]), 10.0) == 1
    assert e4.horizon_first_hit(np.array([0.0, 0.0, 0.0, 0.0, L]), 10.0) == 5
    assert e4.horizon_first_hit(np.zeros(5), 10.0) == -1


def test_censored_time_of_a_missing_alarm_is_the_horizon():
    assert e4.censored_time(-1, 5) == 5
    assert e4.censored_time(5, 5) == 5
    assert e4.censored_time(1, 5) == 1


def test_rank_threshold_tie_at_b_is_conservative():
    maxima = np.linspace(0.0, 1.9, 20)
    fields = e4.cell_calibration(maxima, 0.05)
    assert fields["rank_r"] == 0
    h = float.fromhex(fields["threshold_hex"])
    b = float(np.sort(maxima)[20 - fields["rank_r"] - 1])
    assert h == np.nextafter(b, np.inf)
    assert e4.rank_first_hit(np.array([0.0, b]), h) == -1
    assert e4.rank_first_hit(np.array([0.0, h]), h) == 2
    assert fields["calibration_alarms"] <= fields["rank_r"]


def test_threshold_round_trips_through_fair_csv_and_hex(tmp_path):
    h = float(np.nextafter(0.7, np.inf))
    path = tmp_path / "t.csv"
    pipelines.save_fair_csv(pd.DataFrame({"threshold": [h], "threshold_hex": [h.hex()]}), path)
    back = pd.read_csv(path, float_precision="round_trip")
    assert back["threshold"][0] == h
    assert float.fromhex(back["threshold_hex"][0]) == h


def test_insufficient_calibration_is_reported_as_failed():
    fields = e4.cell_calibration(np.arange(18.0), 0.05)
    assert fields["status"] == "CALIBRATION_FAILED"
    assert fields["threshold_hex"] is None


def small(**kw):
    return cfg(**{"grid": [4], **kw})


def test_scalar_calibration_feeds_fair_signs_to_the_shared_detector(monkeypatch):
    seen = []
    real = eprocess.log_edetector

    def spy(x, kind="cusum", eta0=eprocess.EDETECTOR_ETA0):
        seen.append((np.unique(x).tolist(), kind, tuple(eta0), np.shape(x)))
        return real(x, kind, eta0)

    monkeypatch.setattr(eprocess, "log_edetector", spy)
    fields = e4.scalar_calibration(cfg(), "science")
    assert seen == [([-1.0, 1.0], "cusum", eprocess.EDETECTOR_ETA0, (20, 30))]
    assert fields["status"] == "OK" and fields["n_cal"] == 20


def test_scalar_threshold_is_computed_once_and_shared_by_the_scalar_methods(monkeypatch):
    calls = []
    real = e4.scalar_calibration
    monkeypatch.setattr(e4, "scalar_calibration", lambda c, s: calls.append(s) or real(c, s))
    out = e4.run_cells(cfg(), "science")
    assert calls == ["science"]
    cal = out["calibration"]
    scalar = cal[cal["method"].isin(e4.SCALAR)]
    dictionary = cal[cal["method"].isin(e4.DICTIONARY)]
    assert len(scalar) == 3 * 2 * 2 and scalar["calibration_hash"].nunique() == 1
    assert dictionary["calibration_hash"].nunique() == len(dictionary) == 3 * 2 * 2
    fpr = e4.holdout_fpr(out["trials"])
    assert len(fpr) == len(e4.METHODS) * 2 * 2 * len(e4.READINGS)


def test_the_frozen_scalar_threshold_is_applied_to_holdout_and_alternatives():
    c = small()
    out = e4.run_cells(c, "science")
    h = float.fromhex(e4.scalar_calibration(c, "science")["threshold_hex"])
    cell = {"N": 4}
    t = out["trials"]
    for role in ("holdout", "alternative"):
        X = e4.role_path(c, "science", "gaussian", role, 3, 4)
        if role == "alternative":
            X = X + e4.drift_scale(c) * e4.residual_direction(e4.direction_draw(c, "science", 3), 4)
        log_m = e4.method_log_path("EW", cell, X, e4.coins_rec(c, "science", role, 3))
        row = t[(t.background == "gaussian") & (t.N == 4) & (t.method == "EW") & (t.role == role)
                & (t.replicate == 3) & (t.reading == "predictive_rank")]
        assert row["first_hit"].tolist() == [e4.rank_first_hit(log_m, h)]


def test_trial_readings_are_labelled_rank_or_horizon_only():
    t = e4.run_cells(small(), "science")["trials"]
    assert set(t["reading"]) == set(e4.READINGS)
    assert set(t["first_hit"]) <= set(range(1, 31)) | {-1}


def test_monitoring_is_non_anticipating_for_every_method():
    c = cfg(grid=[6])
    cell = e4.fit_cell(c, "gaussian", 6, "science")
    u = e4.residual_direction(e4.direction_draw(c, "science", 0), 6)
    X = e4.role_path(c, "science", "gaussian", "alternative", 0, 6) + e4.drift_scale(c) * u
    X2 = X.copy()
    X2[12:] = e4.role_path(c, "science", "gaussian", "holdout", 5, 6)[12:]
    rec = e4.coins_rec(c, "science", "alternative", 0)
    for m in e4.METHODS:
        given = u if m in e4.ORACLE else None
        a = e4.method_log_path(m, cell, X, rec, given)
        b = e4.method_log_path(m, cell, X2, rec, given)
        assert np.array_equal(a[:12], b[:12])


def test_ex_ante_methods_never_receive_the_drift():
    import inspect
    assert list(inspect.signature(e4.fit_cell).parameters) == ["cfg", "background", "N", "space"]
    c = cfg(grid=[4])
    cell = e4.fit_cell(c, "gaussian", 4, "science")
    X = e4.role_path(c, "science", "gaussian", "holdout", 0, 4)
    with pytest.raises(ValueError):
        e4.method_log_path("SPEC-full", cell, X, e4.coins_rec(c, "science", "holdout", 0), np.ones(4) / 2.0)


def test_oracle_rows_are_flagged_and_excluded_from_ex_ante_tables():
    out = e4.run_cells(small(), "science")
    t = out["trials"]
    assert set(t[t.method.isin(e4.ORACLE)]["claim_flag"]) == {"ORACLE_DIRECTION", "ORACLE_SCORE1"}
    assert set(t[~t.method.isin(e4.ORACLE)]["claim_flag"]) == {"NONE"}
    assert not set(e4.ex_ante(t)["method"]) & set(e4.ORACLE)
    assert set(out["diagnostics"]["claim_flag"]) == {"ORACLE_DIAGNOSTIC"}


def test_oracle_j_has_the_closed_form_on_the_residual_axis():
    c = cfg()
    sigma = pdb.equicorrelation(2, c["rho"])
    v = np.array([[1.0], [-1.0]]) / math.sqrt(2.0)
    dmu = e4.drift_scale(c) * v[:, 0]
    assert math.isclose(e4.oracle_j(v, dmu, sigma)[0], e4.i_star(c["H"], c["alpha"]), rel_tol=1e-13)


def test_prefix_retention_is_not_a_sum_of_j_and_full_retention_is_one():
    c = cfg()
    sigma = pdb.equicorrelation(4, c["rho"])
    V = fixed_orthonormal(4)
    dmu = e4.drift_scale(c) * e4.residual_direction(e4.direction_draw(c, "science", 0), 4)
    info = e4.i_star(c["H"], c["alpha"])
    J = e4.oracle_j(V, dmu, sigma)
    assert abs(e4.prefix_retention(V, 2, dmu, sigma, info) - J[:2].sum() / info) > 1e-6
    assert math.isclose(e4.prefix_retention(V, 4, dmu, sigma, info), 1.0, rel_tol=1e-12)


def test_jobs_and_replicate_order_leave_scientific_csv_bytes_unchanged(tmp_path):
    c = small()
    digests = []
    for name, kw in (("j1", {"jobs": 1}), ("j3", {"jobs": 3}), ("perm", {"jobs": 1, "permute": True})):
        digests.append(e4.write_tables(tmp_path / name, e4.run_cells(c, "science", **kw)))
    assert digests[0] == digests[1] == digests[2]
    other = e4.write_tables(tmp_path / "seed", e4.run_cells(small(seed=43), "science"))
    assert other["trials"] != digests[0]["trials"]


def test_the_scientific_route_reads_no_data_file(monkeypatch):
    import builtins
    from pathlib import Path
    roots = [str(e4.REPO_ROOT / "data"), str((e4.REPO_ROOT / "data").resolve())]

    def forbidden(path):
        p = Path(path)
        return any(str(q).startswith(r) for q in (p.absolute(), p.resolve()) for r in roots)

    def guard(real):
        def wrapped(path, *a, **k):
            if isinstance(path, (str, Path)) and forbidden(path):
                raise AssertionError(f"data access {path}")
            return real(path, *a, **k)
        return wrapped

    monkeypatch.setattr(builtins, "open", guard(builtins.open))
    monkeypatch.setattr(np, "load", guard(np.load))
    monkeypatch.setattr(pd, "read_csv", guard(pd.read_csv))
    monkeypatch.setattr(pd, "read_parquet", guard(pd.read_parquet))
    with pytest.raises(AssertionError):
        open(e4.REPO_ROOT / "data" / "raw" / "probe.csv")
    assert len(e4.run_cells(small(), "science")["trials"]) > 0


def fake_trials(grid, alt, hold, methods=e4.METHODS, background="gaussian", reading="predictive_rank"):
    rows = []
    for N in grid:
        for m in methods:
            for role, source in (("alternative", alt), ("holdout", hold)):
                for i, f in enumerate(source(m, N)):
                    rows.append({"background": background, "N": N, "method": m, "role": role, "replicate": i,
                                 "reading": reading, "first_hit": int(f), "claim_flag": e4.ORACLE.get(m, "NONE")})
    return pd.DataFrame(rows, columns=e4.TRIAL_COLUMNS)


def acfg(n=80, **kw):
    return cfg(**{"grid": [8, 16, 32], "n_alt": n, "n_hold": n, "H": 100, "B_boot": 200,
                  "backgrounds": {"gaussian": None}, **kw})


def test_rmst_witness_h5():
    first = np.array([1, 5, -1])
    assert e4.censored_times(first, 5).tolist() == [1, 5, 5]
    f = e4.rmst_cell(first, 5)
    assert f["rmst"] == pytest.approx(11.0 / 3.0, abs=1e-12)
    assert f["det_rate"] == pytest.approx(2.0 / 3.0, abs=1e-12)
    assert f["deff"] == 1.0
    assert f["rmst_se"] == pytest.approx(4.0 / 3.0, abs=1e-12)


def growing(m, N):
    return np.full(80, 10 * N // 8 if m == "SPEC-full" else 10)


def test_delta_decomposition_holds_per_draw_with_common_indices():
    rng = np.random.default_rng(0)
    table = {(m, N): rng.integers(1, 101, 80) for m in e4.METHODS for N in (8, 16, 32)}
    trials = fake_trials([8, 16, 32], lambda m, N: table[(m, N)], lambda m, N: np.full(80, -1))
    out = e4.analyse(trials, acfg())
    d = out["draws"]
    assert np.allclose(d[("gaussian", "Delta")], d[("gaussian", "Delta_1")] + d[("gaussian", "Delta_2")],
                       rtol=0, atol=1e-12)
    assert out["contrasts"]["boot_index_sha256"].nunique() == 1


def test_identical_cells_across_n_give_a_zero_slope_in_every_draw():
    trials = fake_trials([8, 16, 32], lambda m, N: np.arange(1, 81) if m == "SPEC-full" else np.full(80, 7),
                         lambda m, N: np.full(80, -1))
    d = e4.analyse(trials, acfg())["draws"]
    assert np.all(np.abs(e4.ols_slope(np.log([8.0, 16.0, 32.0]), d[("gaussian", "Delta")])) <= 1e-12)


def test_delta_labels_on_the_full_grid():
    hold = lambda m, N: np.full(80, -1)
    c = e4.analyse(fake_trials([8, 16, 32], growing, hold), acfg())["contrasts"].set_index("contrast")
    assert c.loc["Delta", "label"] == "COST_GROWS"
    assert c.loc["Delta_1", "label"] == "DESCRIPTIVE" and c.loc["Delta_2", "label"] == "DESCRIPTIVE"
    shrink = lambda m, N: np.full(80, 40 * 8 // N if m == "SPEC-full" else 10)
    assert e4.analyse(fake_trials([8, 16, 32], shrink, hold), acfg())["contrasts"].set_index(
        "contrast").loc["Delta", "label"] == "COST_SHRINKS"
    flat = lambda m, N: np.full(80, 10)
    assert e4.analyse(fake_trials([8, 16, 32], flat, hold), acfg())["contrasts"].set_index(
        "contrast").loc["Delta", "label"] == "NO_GROWTH_DETECTED"


def test_a_refused_cell_makes_its_contrasts_not_identified_without_dropping_rows():
    trials = fake_trials([8, 16, 32], growing, lambda m, N: np.full(80, -1))
    trials = trials[~((trials.method == "SPEC-full") & (trials.N == 16))]
    out = e4.analyse(trials, acfg())
    c = out["contrasts"].set_index("contrast")
    assert c.loc["Delta", "label"] == "NOT_IDENTIFIED" and c.loc["Delta_2", "qualification"] == "NOT_IDENTIFIED"
    assert c.loc["Delta_1", "qualification"] == "QUALIFIED"
    assert len(out["cells"]) == len(e4.METHODS) * 3 - 1


@pytest.mark.parametrize("n,missed,expected", [(80, 0, "QUALIFIED"), (80, 1, "NOT_IDENTIFIED"),
                                               (40, 0, "NOT_IDENTIFIED")])
def test_wilson_low_censoring_qualification(n, missed, expected):
    def alt(m, N):
        f = np.full(n, 10 * N // 8 if m == "SPEC-full" else 10)
        if m == "SPEC-full" and N == 32:
            f[:missed] = -1
        return f
    out = e4.analyse(fake_trials([8, 16, 32], alt, lambda m, N: np.full(n, -1)), acfg(n=n))
    c = out["contrasts"].set_index("contrast")
    assert c.loc["Delta", "qualification"] == expected
    assert c.loc["Delta_1", "qualification"] == ("NOT_IDENTIFIED" if n == 40 else "QUALIFIED")
    assert len(out["cells"]) == len(e4.METHODS) * 3


def test_ew_negative_control_does_not_gate_the_contrasts():
    def alt(m, N):
        return np.full(80, -1) if m == "EW" else np.full(80, 10 * N // 8 if m == "SPEC-full" else 10)
    c = e4.analyse(fake_trials([8, 16, 32], alt, lambda m, N: np.full(80, -1)), acfg())["contrasts"]
    assert c.set_index("contrast").loc["Delta", "label"] == "COST_GROWS"


def test_paired_fpr_comparability_both_branches():
    same = lambda m, N: np.where(np.arange(80) < 4, 3, -1)
    c = e4.analyse(fake_trials([8, 16, 32], growing, same), acfg())["contrasts"].set_index("contrast")
    assert c.loc["Delta", "fpr_comparability"] == "COMPARABLE_FPR"
    apart = lambda m, N: np.where(np.arange(80) < (20 if m == "SPEC-full" else 4), 3, -1)
    c = e4.analyse(fake_trials([8, 16, 32], growing, apart), acfg())["contrasts"].set_index("contrast")
    assert c.loc["Delta", "fpr_comparability"] == "COMMON_NOMINAL_ALPHA_ONLY"
    assert c.loc["Delta", "label"] == "COST_GROWS"


def test_fpr_above_nominal_is_a_label_only():
    noisy = lambda m, N: np.where(np.arange(80) < (40 if m == "EW" else 0), 2, -1)
    out = e4.analyse(fake_trials([8, 16, 32], growing, noisy), acfg())
    cells = out["cells"].set_index(["N", "method"])
    assert cells.loc[(8, "EW"), "fpr_label"] == "FPR_ABOVE_NOMINAL"
    assert cells.loc[(8, "O-dir"), "fpr_label"] == "NONE"
    assert len(out["cells"]) == len(e4.METHODS) * 3


def test_precheck_reproduces_the_deterministic_journal(monkeypatch):
    def refuse(*a, **k):
        raise AssertionError("the analytic precheck must not draw")
    monkeypatch.setattr(np.random, "default_rng", refuse)
    p = e4.analytic_precheck(e4.validate_config(e4.load_config(e4.CONFIG))).set_index(["row_kind", "background", "N"])
    g8 = p.loc[("DICTIONARY_ONE_ATOM", "gaussian", 8)]
    assert g8[["a95_upper", "p95_upper", "best_grid_log_growth_upper", "one_atom_anytime_clock_days",
               "clock_over_H"]].tolist() == pytest.approx(
        [0.7383868289, 0.7120703349, 0.09251004744, 159.5017863, 0.07975089315], rel=1e-9)
    t500 = p.loc[("DICTIONARY_ONE_ATOM", "t7_INFO_GAUSS_PROXY_T7", 500)]
    assert t500[["a95_upper", "p95_upper", "best_grid_log_growth_upper", "one_atom_anytime_clock_days",
                 "clock_over_H"]].tolist() == pytest.approx(
        [0.02996725008, 0.5511663672, 0.00524242256, 3603.4265, 1.80171325], rel=1e-9)
    odir = p.loc[("O_DIR_SCALAR", "gaussian", 1)]
    assert odir[["p95_upper", "best_grid_log_growth_upper", "one_atom_anytime_clock_days"]].tolist() == pytest.approx(
        [0.7424927176, 0.1182868672, 107.1638515], rel=1e-9)
    assert len(p) == 2 * 7 + 2


import json
import types

import yaml


def pcfg(**kw):
    return cfg(**{"grid": [4], "pilot_n": 4, "H": 20, "T_fit": 40, **kw})


def write_cfg(tmp_path, c):
    path = tmp_path / "e4.yaml"
    path.write_text(yaml.safe_dump(c), encoding="utf-8")
    return str(path)


def snapshot(root):
    return {str(p.relative_to(root)): (pdb.file_sha256(p) if p.is_file() else None) for p in sorted(root.rglob("*"))}


def writer(content):
    calls = []

    def compute(tmp):
        calls.append(tmp)
        (tmp / "cost.csv").write_text(content, encoding="utf-8")
        return "COMPLETE", {}
    return compute, calls


def test_two_partitions_share_one_session_and_resume_without_recompute(tmp_path):
    ident = e4.session_identity(small(), "pilot")
    assert e4.run_partition(tmp_path, "gaussian:4", ident, writer("a\n")[0]) == ("COMPLETE", [])
    assert e4.run_partition(tmp_path, "t7:4", ident, writer("b\n")[0]) == ("COMPLETE", [])
    before = snapshot(tmp_path)
    again, calls = writer("zzz\n")
    assert e4.run_partition(tmp_path, "gaussian:4", ident, again) == ("SKIPPED_COMPLETE", [])
    assert calls == [] and snapshot(tmp_path) == before


def test_leftover_temporary_partition_is_not_success_and_is_recomputed(tmp_path):
    ident = e4.session_identity(small(), "pilot")
    stale = tmp_path / "partitions" / "gaussian_N4.tmp-999-x"
    stale.mkdir(parents=True)
    compute, calls = writer("a\n")
    assert e4.run_partition(tmp_path, "gaussian:4", ident, compute) == ("COMPLETE", ["gaussian_N4.tmp-999-x"])
    assert len(calls) == 1 and stale.exists()


def test_blocked_partition_is_final_and_not_rerun(tmp_path):
    ident = e4.session_identity(small(), "pilot")

    def blocked(tmp):
        (tmp / "cost.csv").write_text("x\n", encoding="utf-8")
        return "BLOCKED_RESOURCE", {}
    assert e4.run_partition(tmp_path, "gaussian:4", ident, blocked) == ("BLOCKED_RESOURCE", [])
    compute, calls = writer("a\n")
    with pytest.raises(e4.PartitionBlocked):
        e4.run_partition(tmp_path, "gaussian:4", ident, compute)
    assert calls == []


def test_divergent_identity_or_tampered_file_is_refused_without_mutation(tmp_path):
    e4.run_partition(tmp_path, "gaussian:4", e4.session_identity(small(), "pilot"), writer("a\n")[0])
    before = snapshot(tmp_path)
    compute, calls = writer("b\n")
    with pytest.raises(pdb.PartitionMismatch):
        e4.run_partition(tmp_path, "t7:4", e4.session_identity(small(seed=43), "pilot"), compute)
    assert calls == [] and snapshot(tmp_path) == before
    (tmp_path / "partitions" / "gaussian_N4" / "cost.csv").write_text("tampered\n", encoding="utf-8")
    tampered = snapshot(tmp_path)
    with pytest.raises(pdb.PartitionMismatch):
        e4.run_partition(tmp_path, "gaussian:4", e4.session_identity(small(), "pilot"), compute)
    assert calls == [] and snapshot(tmp_path) == tampered


def test_an_exception_during_compute_leaves_no_final_directory(tmp_path):
    def boom(tmp):
        (tmp / "cost.csv").write_text("half\n", encoding="utf-8")
        raise RuntimeError("crash")
    with pytest.raises(RuntimeError):
        e4.run_partition(tmp_path, "gaussian:4", e4.session_identity(small(), "pilot"), boom)
    assert not (tmp_path / "partitions" / "gaussian_N4").exists()
    assert len(list((tmp_path / "partitions").glob("gaussian_N4.tmp-*"))) == 1


def test_environment_validation_is_separate_from_the_hashed_identity():
    assert isinstance(pdb.check_env(), list)
    snap = e4.env_snapshot()
    assert {"python", "numpy", "scipy", "pandas", "statsmodels", "blas", "variables"} <= set(snap)
    a = e4.session_identity(small(), "pilot")
    assert set(a) == e4.SESSION_KEYS
    assert a == e4.session_identity(small(), "pilot")
    assert a["session_id"] != e4.session_identity(small(), "precheck")["session_id"]
    assert not {"jobs", "cpu_s", "wall_s", "peak_rss_kib"} & set(a["config"])
    assert all(not p.startswith("/") for p in a["code"])


def test_fair_tables_round_trip_to_identical_bytes(tmp_path):
    digests = e4.write_tables(tmp_path / "a", e4.run_cells(small(), "science"))
    for name, digest in digests.items():
        back = pd.read_csv(tmp_path / "a" / f"{name}.csv", float_precision="round_trip")
        pipelines.save_fair_csv(back, tmp_path / f"{name}.csv")
        assert pdb.file_sha256(tmp_path / f"{name}.csv") == digest


def cli(tmp_path, c, mode, pid, out="pilot_x", jobs="1"):
    return e4.main(["--mode", mode, "--partition", pid, "--jobs", jobs, "--out", str(tmp_path / out),
                    "--log-dir", str(tmp_path / "logs"), "--config", write_cfg(tmp_path, c)])


def test_pilot_writes_only_whitelisted_files_and_schemas(tmp_path):
    c = pcfg()
    assert cli(tmp_path, c, "pilot", "scalar_cal") == 0
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 0
    out = tmp_path / "pilot_x"
    files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file())
    assert files == ["partitions/gaussian_N4/cost.csv", "partitions/gaussian_N4/partition.json",
                     "partitions/scalar_cal/cost.csv", "partitions/scalar_cal/partition.json", "session.json"]
    assert not [p for p in out.rglob("*") if p.is_dir() and ".tmp-" in p.name]
    for d in ("scalar_cal", "gaussian_N4"):
        cost = pd.read_csv(out / "partitions" / d / "cost.csv", float_precision="round_trip")
        assert list(cost.columns) == e4.COST_COLUMNS
        assert set(cost.loc[~cost.stage.isin(["invocation", "orchestration"]), "status"]) == {"COMPLETE"}
        record = json.loads((out / "partitions" / d / "partition.json").read_text(encoding="utf-8"))
        assert set(record) == e4.PARTITION_KEYS and record["objects"] == {}
    stages = set(pd.read_csv(out / "partitions" / "gaussian_N4" / "cost.csv")["stage"])
    assert {"startup", "fit_cell", "draw:calibration", "stream:EW:holdout", "logpath:SPEC-full:alternative",
            "dict_calibration", "readings:holdout", "io"} <= stages
    assert {"scalar_cal", "analysis_fixture:predictive_rank", "analysis_fixture:anytime_valid_horizon"} <= set(
        pd.read_csv(out / "partitions" / "scalar_cal" / "cost.csv")["stage"])
    assert set(json.loads((out / "session.json").read_text(encoding="utf-8"))) == e4.SESSION_KEYS
    lines = (tmp_path / "logs" / "pilot_x.jsonl").read_text(encoding="utf-8").splitlines()
    assert lines and all(set(json.loads(line)) == e4.LOG_KEYS for line in lines)
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 0


def test_pilot_resource_block_keeps_completed_stages_and_marks_the_rest(tmp_path):
    c = pcfg(limits={"rss_gib": 1e-9, "invocation_seconds": 1800, "block_paths": 2})
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 4
    cost = pd.read_csv(tmp_path / "pilot_x" / "partitions" / "gaussian_N4" / "cost.csv").set_index("stage")
    assert cost.loc["fit_cell", "status"] == "COMPLETE" and cost.loc["fit_cell", "cpu_s"] >= 0
    assert cost.loc["draw:calibration", "status"] == "NOT_MEASURED" and math.isnan(cost.loc["draw:calibration", "cpu_s"])
    assert cost.loc["io", "status"] == "COMPLETE"
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 5


def test_simulated_getrusage_gives_user_plus_system_cpu_and_cumulative_peak(monkeypatch):
    seq = iter([types.SimpleNamespace(ru_utime=1.0, ru_stime=0.5, ru_maxrss=100),
                types.SimpleNamespace(ru_utime=3.0, ru_stime=1.5, ru_maxrss=150)])
    monkeypatch.setattr(e4.resource, "getrusage", lambda who: next(seq))
    meter = e4.Meter()
    with meter.stage("x", 2):
        pass
    assert meter.rows["x"]["cpu_s"] == 3.0
    assert meter.rows["x"]["peak_rss_kib"] == 150
    assert meter.rows["x"]["n_paths"] == 2 and meter.rows["x"]["n_runs"] == 1


def test_pilot_refuses_parallel_jobs_and_full_mode_writes_nothing(tmp_path):
    c = pcfg()
    assert cli(tmp_path, c, "pilot", "scalar_cal", jobs="3") == 5
    assert e4.main(["--mode", "full", "--out", str(tmp_path / "full"), "--log-dir", str(tmp_path / "full_logs")]) == 3
    assert not (tmp_path / "pilot_x").exists() and not (tmp_path / "full").exists()
    assert not (tmp_path / "full_logs").exists()


def test_precheck_cli_is_resumable(tmp_path):
    c = pcfg(grid=[8, 16])
    assert cli(tmp_path, c, "precheck", "precheck", out="precheck_x") == 0
    first = snapshot(tmp_path / "precheck_x")
    assert cli(tmp_path, c, "precheck", "precheck", out="precheck_x") == 0
    assert snapshot(tmp_path / "precheck_x") == first
    table = pd.read_csv(tmp_path / "precheck_x" / "partitions" / "precheck" / "analytic_precheck.csv",
                        float_precision="round_trip")
    assert len(table) == 2 * 2 + 2


def fake_cost(c, missing=None):
    rows = [{"partition": "precheck", "stage": "precheck", "cpu_s": 0.5},
            {"partition": "scalar_cal", "stage": "startup", "cpu_s": 1.0},
            {"partition": "scalar_cal", "stage": "scalar_cal", "cpu_s": 2.0},
            {"partition": "scalar_cal", "stage": "analysis_fixture:predictive_rank", "cpu_s": 5.0}]
    for bg in c["backgrounds"]:
        for N in c["grid"]:
            pid = f"{bg}:{N}"
            for stage, cpu in (("startup", 1.0), ("fit_cell", 3.0), ("draw:holdout", 1.0), ("dict_calibration", 0.1),
                               ("stream:EW:holdout", 1.0), ("logpath:EW:holdout", 2.0), ("readings:holdout", 0.5),
                               ("io", 0.2)):
                rows.append({"partition": pid, "stage": stage, "cpu_s": cpu})
    df = pd.DataFrame(rows)
    df["wall_s"], df["n_paths"], df["n_runs"], df["peak_rss_kib"], df["status"] = df["cpu_s"], 40, 1, 1000, "COMPLETE"
    if missing:
        df.loc[(df.partition == missing) & (df.stage == "draw:holdout"), ["cpu_s", "wall_s", "status"]] = [
            math.nan, math.nan, "NOT_MEASURED"]
    return df[e4.COST_COLUMNS]


def test_stage_factors_follow_the_cost_table():
    c = e4.validate_config(e4.load_config(e4.CONFIG))
    assert e4.stage_factor("draw:holdout", c) == 50.0
    assert e4.stage_factor("logpath:SPEC-full:calibration", c) == 50.0
    assert e4.stage_factor("scalar_cal", c) == 50.0
    assert e4.stage_factor("fit_cell", c) == 1.0 and e4.stage_factor("analysis_fixture:predictive_rank", c) == 1.0
    assert e4.stage_factor("dict_calibration", c) == pytest.approx(2000 * math.log(2000) / (40 * math.log(40)))
    with pytest.raises(ValueError):
        e4.stage_factor("mystery", c)


def test_forecast_adds_consumed_cost_and_orders_fallbacks():
    c = e4.validate_config(e4.load_config(e4.CONFIG))
    frozen = copy.deepcopy(c)
    out = e4.forecast(fake_cost(c), c)
    s = out["scenarios"].set_index("scenario")
    assert list(out["scenarios"]["scenario"]) == ["FULL_GRID", "DROP_N500", "T7_ON_8_64_239"]
    consumed = fake_cost(c)["cpu_s"].sum()
    per_cell = 1.0 + 3.0 + 50 * (1.0 + 1.0 + 2.0 + 0.5 + 0.2) + 0.1 * 2000 * math.log(2000) / (40 * math.log(40))
    assert out["consumed_cpu_s"] == pytest.approx(consumed)
    assert s.loc["FULL_GRID", "total_cpu_s"] == pytest.approx(consumed + 1.0 + 2.0 * 50 + 5.0 + 14 * per_cell)
    assert s.loc["T7_ON_8_64_239", "total_cpu_s"] == pytest.approx(consumed + 1.0 + 2.0 * 50 + 5.0 + 9 * per_cell)
    assert set(s["status"]) == {"WITHIN_CAP"} and out["label"] == "ESTIMATE"
    assert set(out["unmeasured"]["status"]) == {"UNMEASURED_ASSUMPTION"}
    assert c == frozen
    partial = e4.forecast(fake_cost(c, missing="t7:500"), c)["scenarios"].set_index("scenario")
    assert partial.loc["FULL_GRID", "status"] == "INCOMPLETE" and partial.loc["DROP_N500", "status"] == "WITHIN_CAP"


def test_the_script_runs_as_a_file_and_refuses_full_before_writing(tmp_path):
    import os
    import subprocess
    import sys
    run = subprocess.run([sys.executable, str(e4.REPO_ROOT / "experiments" / "e4_alignment.py"), "--mode", "full",
                          "--out", str(tmp_path / "full"), "--log-dir", str(tmp_path / "logs")],
                         capture_output=True, text=True, cwd=tmp_path, env=dict(os.environ))
    assert run.returncode == 3, run.stderr
    assert "refused" in run.stderr
    assert sorted(p.name for p in tmp_path.iterdir()) == []


def test_a_block_during_the_fit_is_recorded_as_blocked_resource(tmp_path, monkeypatch):
    def blocked(*args, **kwargs):
        raise pdb.ResourceBlocked("simulated invocation time limit")
    monkeypatch.setattr(e4, "fit_cell", blocked)
    assert cli(tmp_path, pcfg(), "pilot", "gaussian:4") == 4
    cost = pd.read_csv(tmp_path / "pilot_x" / "partitions" / "gaussian_N4" / "cost.csv").set_index("stage")
    assert cost.loc["startup", "status"] == "COMPLETE"
    assert cost.loc["fit_cell", "status"] == "BLOCKED_RESOURCE"
    assert cost.loc["draw:alternative", "status"] == "NOT_MEASURED"


def test_integrity_warnings_for_an_o_dir_slope_and_ew_detection():
    def alt(m, N):
        if m == "O-dir":
            return np.full(80, 5 * N // 8)
        return np.full(80, 3) if m == "EW" else np.full(80, 10)
    w = e4.analyse(fake_trials([8, 16, 32], alt, lambda m, N: np.full(80, -1)), acfg())["warnings"]
    assert set(w["warning"]) == {"WARN_ODIR_SLOPE", "WARN_EW_DETECTION"}
    assert set(w.loc[w.warning == "WARN_EW_DETECTION", "N"]) == {8, 16, 32}
    calm = lambda m, N: np.where(np.arange(80) < 4, 3, -1) if m == "EW" else np.full(80, 10)
    assert e4.analyse(fake_trials([8, 16, 32], calm, lambda m, N: np.where(np.arange(80) < 4, 3, -1)),
                      acfg())["warnings"].empty


def test_an_unresolved_eigen_tie_refuses_the_basis_methods_of_its_cell_only(monkeypatch):
    real = e4.fit_cell

    def tied(c, background, N, space):
        if N == 6:
            raise e4.EigenTieUnresolved("EIGENVALUE_TIE_UNRESOLVED: forced", [[0, 1]], [0.0])
        return real(c, background, N, space)
    monkeypatch.setattr(e4, "fit_cell", tied)
    out = e4.run_cells(cfg(), "science")
    cells = out["cells"].set_index(["background", "N"])
    assert cells.loc[("gaussian", 6), "status"] == "EIGENVALUE_TIE_UNRESOLVED"
    assert cells.loc[("gaussian", 4), "status"] == "OK"
    t = out["trials"]
    assert set(t[t.N == 6]["method"]) == {"EW", "O-dir"}
    assert set(t[t.N == 4]["method"]) == set(e4.METHODS)
    cal = out["calibration"].set_index(["background", "N", "method"])
    assert {cal.loc[("t7", 6, m), "status"] for m in e4.BASIS_METHODS} == {"EIGENVALUE_TIE_UNRESOLVED"}
    assert out["diagnostics"]["N"].eq(4).all()


def known_cell(rho):
    V = fixed_orthonormal(3)
    sigma = pdb.equicorrelation(3, rho)
    return {"background": "gaussian", "N": 3, "V_e4": V, "eigval": np.array([3.0, 2.0, 1.0]), "sigma": sigma,
            "k_mp": 0, "mp_count_total": 1, "vsv": (V * (sigma @ V)).sum(axis=0)}


def test_k_mp_counts_residual_axes_only():
    assert [e4.k_mp_residual(n) for n in (0, 1, 3)] == [0, 0, 2]
    cell = e4.fit_cell(cfg(), "gaussian", 6, "science")
    assert cell["mp_count_total"] == 1 and cell["k_mp"] == 0


def test_oracle_diagnostics_export_the_approved_quantities():
    c = e4.validate_config(e4.load_config(e4.CONFIG))
    cell = known_cell(c["rho"])
    u = e4.residual_direction(np.array([0.3, -1.1, 0.4]), 3)
    d = e4.oracle_diagnostics(cell, u, c)
    info = 0.211932694662
    dmu = math.sqrt(2.0 * (1.0 - c["rho"]) * info) * u
    proj = cell["V_e4"].T @ dmu
    J = proj ** 2 / (2.0 * np.diag(cell["V_e4"].T @ cell["sigma"] @ cell["V_e4"]))
    z = proj ** 2 / cell["eigval"]
    p = 0.7424927176
    assert d["i_star"] == pytest.approx(info, rel=1e-11) and d["i_star_label"] == "GAUSSIAN_KL"
    assert d["odir_sign_p"] == pytest.approx(p, rel=1e-9)
    assert d["odir_sign_kl_bernoulli"] == pytest.approx(p * math.log(2 * p) + (1 - p) * math.log(2 * (1 - p)), rel=1e-8)
    assert np.allclose(d["j_k"], J, rtol=1e-10, atol=0)
    assert d["a_best"] == pytest.approx(J.max() / info, rel=1e-10)
    assert d["a_max_plugin"] == pytest.approx(z.max() / z.sum(), rel=1e-10)
    assert abs(d["a_max_plugin"] - d["a_best"]) > 1e-6
    t7 = e4.oracle_diagnostics({**cell, "background": "t7"}, u, c)
    assert t7["i_star_label"] == "INFO_GAUSS_PROXY_T7"
    assert t7["odir_sign_p"] == pytest.approx(0.7668495751, rel=1e-9)


def test_run_cells_exports_diagnostics_axes_and_oracle_metadata():
    out = e4.run_cells(small(), "science")
    d = out["diagnostics"]
    assert {"i_star", "i_star_label", "odir_sign_p", "odir_sign_kl_bernoulli", "a_best", "a_max_plugin",
            "prefix_retention", "k_mp", "mp_count_total"} <= set(d.columns)
    assert set(d.loc[d.background == "t7", "i_star_label"]) == {"INFO_GAUSS_PROXY_T7"}
    axes = out["diagnostics_axes"]
    assert set(axes["claim_flag"]) == {"ORACLE_DIAGNOSTIC"} and len(axes) == len(d) * 4
    cal = out["calibration"]
    assert set(cal[cal.method.isin(e4.ORACLE)]["claim_flag"]) == {"ORACLE_DIRECTION", "ORACLE_SCORE1"}
    assert set(cal[~cal.method.isin(e4.ORACLE)]["claim_flag"]) == {"NONE"}


def test_the_drift_free_fit_terms_are_reused_exactly():
    cell = e4.fit_cell(cfg(), "gaussian", 6, "science")
    V, sigma = cell["V_e4"], cell["sigma"]
    assert np.allclose(cell["vsv"], np.einsum("ik,ij,jk->k", V, sigma, V), rtol=1e-13, atol=0)
    u = e4.residual_direction(e4.direction_draw(cfg(), "science", 2), 6)
    assert e4.oracle_k_star(V, u, sigma, cell["vsv"]) == e4.oracle_k_star(V, u, sigma)


def test_meter_keeps_the_cost_of_an_interrupted_stage(monkeypatch):
    seq = iter([types.SimpleNamespace(ru_utime=1.0, ru_stime=0.5, ru_maxrss=100),
                types.SimpleNamespace(ru_utime=3.0, ru_stime=1.5, ru_maxrss=150)])
    monkeypatch.setattr(e4.resource, "getrusage", lambda who: next(seq))
    meter = e4.Meter()
    with pytest.raises(pdb.ResourceBlocked):
        with meter.stage("x", 2):
            raise pdb.ResourceBlocked("stop")
    row = meter.rows["x"]
    assert row["cpu_s"] == 3.0 and row["peak_rss_kib"] == 150
    assert row["n_paths"] == 0 and row["interrupted"] == 1


def pilot_cost(tmp_path, pid="gaussian:4"):
    return pd.read_csv(tmp_path / "pilot_x" / "partitions" / e4.partition_dir(pid) / "cost.csv",
                       float_precision="round_trip").set_index("stage")


def test_a_stop_after_a_first_completed_block_keeps_its_consumed_cost(tmp_path, monkeypatch):
    calls, real = [], e4.guard

    def second_block_blocks(b, c, d):
        calls.append(b)
        if len(calls) == 2:
            raise pdb.ResourceBlocked("simulated memory cap")
        return real(b, c, d)
    monkeypatch.setattr(e4, "guard", second_block_blocks)
    c = pcfg(limits={"rss_gib": 8.0, "invocation_seconds": 1800, "block_paths": 2})
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 4
    cost = pilot_cost(tmp_path)
    assert cost.loc["fit_cell", "status"] == "COMPLETE"
    assert cost.loc["draw:calibration", "status"] == "BLOCKED_RESOURCE"
    assert cost.loc["draw:calibration", "n_paths"] == 2 and cost.loc["draw:calibration", "cpu_s"] >= 0
    assert cost.loc["draw:holdout", "status"] == "NOT_MEASURED"
    out = e4.forecast(cost.reset_index().assign(partition="gaussian:4"), e4.validate_config(c))
    spent = cost.loc[cost.status.isin(["COMPLETE", "BLOCKED_RESOURCE"]) & ~cost.index.isin(["invocation", "orchestration"]),
                     "cpu_s"].sum()
    assert out["consumed_cpu_s"] >= spent
    assert set(out["scenarios"]["status"]) == {"INCOMPLETE"}


def test_a_stop_inside_a_measured_context_is_charged_and_not_extrapolated(tmp_path, monkeypatch):
    calls, real = [], e4.method_stream

    def third_call_blocks(*args, **kwargs):
        calls.append(args[0])
        if len(calls) == 3:
            raise pdb.ResourceBlocked("simulated time limit")
        return real(*args, **kwargs)
    monkeypatch.setattr(e4, "method_stream", third_call_blocks)
    assert cli(tmp_path, pcfg(), "pilot", "gaussian:4") == 4
    cost = pilot_cost(tmp_path)
    row = cost.loc[f"stream:{calls[2]}:calibration"]
    assert row["status"] == "BLOCKED_RESOURCE" and row["n_paths"] == 0 and math.isfinite(row["cpu_s"])
    assert cost.loc[f"stream:{calls[0]}:calibration", "status"] == "BLOCKED_RESOURCE"


def test_pilot_measures_oracle_diagnostics_and_the_effective_analysis(tmp_path):
    c = pcfg()
    assert cli(tmp_path, c, "pilot", "scalar_cal") == 0
    assert cli(tmp_path, c, "pilot", "gaussian:4") == 0
    assert "oracle_diagnostics:alternative" in set(pilot_cost(tmp_path).index)
    stages = set(pilot_cost(tmp_path, "scalar_cal").index)
    assert {"analysis_fixture:predictive_rank", "analysis_fixture:anytime_valid_horizon"} <= stages
    assert "bootstrap_fixture" not in stages
    full = e4.validate_config(e4.load_config(e4.CONFIG))
    assert e4.stage_factor("oracle_diagnostics:alternative", full) == 50.0
    assert e4.stage_factor("analysis_fixture:anytime_valid_horizon", full) == 1.0


def test_analysis_fixture_runs_the_effective_analysis_at_the_given_dimensions(monkeypatch):
    seen, real = [], e4.analyse

    def spy(trials, c, space="science", reading="predictive_rank", n=None):
        seen.append((len(trials), space, reading, n))
        return real(trials, c, space, reading, n)
    monkeypatch.setattr(e4, "analyse", spy)
    c = small()
    assert e4.analysis_fixture(c, "anytime_valid_horizon") is None
    assert seen == [(2 * 1 * 6 * (20 + 20), "pilot", "anytime_valid_horizon", {"alternative": 20, "holdout": 20})]


def test_invocation_cpu_covers_the_stages_and_its_surplus_is_counted(tmp_path):
    assert cli(tmp_path, pcfg(), "pilot", "gaussian:4") == 0
    cost = pilot_cost(tmp_path)
    stages = cost.drop(index=["invocation", "orchestration"])
    assert cost.loc["invocation", "status"] == "MEASURED_PROCESS_TOTAL"
    assert cost.loc["orchestration", "status"] == "MEASURED_RESIDUAL"
    assert cost.loc["invocation", "cpu_s"] >= stages["cpu_s"].sum()
    assert cost.loc["orchestration", "cpu_s"] == pytest.approx(cost.loc["invocation", "cpu_s"] - stages["cpu_s"].sum(),
                                                               abs=1e-9)
    events = [json.loads(line) for line in (tmp_path / "logs" / "pilot_x.jsonl").read_text().splitlines()]
    end = [e for e in events if e["event"] == "invocation_end"]
    assert len(end) == 1 and end[0]["cpu_s"] >= cost.loc["invocation", "cpu_s"]


def test_forecast_counts_the_invocation_surplus_once():
    c = e4.validate_config(e4.load_config(e4.CONFIG))
    rows = fake_cost(c)
    extra = []
    for pid, part in rows.groupby("partition"):
        total = part["cpu_s"].sum() + 5.0
        extra += [{"partition": pid, "stage": "invocation", "n_paths": 0, "n_runs": 1, "cpu_s": total, "wall_s": total,
                   "peak_rss_kib": 1000, "status": "MEASURED_PROCESS_TOTAL"},
                  {"partition": pid, "stage": "orchestration", "n_paths": 0, "n_runs": 1, "cpu_s": 5.0, "wall_s": 5.0,
                   "peak_rss_kib": 1000, "status": "MEASURED_RESIDUAL"}]
    both = pd.concat([rows, pd.DataFrame(extra, columns=e4.COST_COLUMNS)], ignore_index=True)
    out = e4.forecast(both, c)
    assert out["consumed_cpu_s"] == pytest.approx(rows["cpu_s"].sum() + 5.0 * rows["partition"].nunique())
    assert "invocation_orchestration" not in set(out["unmeasured"]["item"])
    assert "invocation_orchestration" in set(e4.forecast(rows, c)["unmeasured"]["item"])


def test_the_session_identity_covers_the_extract_module(tmp_path, monkeypatch):
    assert "jepadrift/representations/extract.py" in e4.CODE_FILES
    ident = e4.session_identity(small(), "pilot")
    e4.run_partition(tmp_path, "gaussian:4", ident, writer("a\n")[0])
    real = pdb.file_sha256
    monkeypatch.setattr(pdb, "file_sha256",
                        lambda p: "0" * 64 if str(p).endswith("representations/extract.py") else real(p))
    changed = e4.session_identity(small(), "pilot")
    assert changed["session_id"] != ident["session_id"]
    with pytest.raises(pdb.PartitionMismatch):
        e4.run_partition(tmp_path, "t7:4", changed, writer("b\n")[0])


def test_a_refused_basis_keeps_the_six_method_stages_and_no_complete_forecast(tmp_path, monkeypatch):
    def tied(*args, **kwargs):
        raise e4.EigenTieUnresolved("EIGENVALUE_TIE_UNRESOLVED: forced", [[0, 1]], [0.0])
    monkeypatch.setattr(e4, "fit_cell", tied)
    assert cli(tmp_path, pcfg(), "pilot", "gaussian:4") == 0
    cost = pilot_cost(tmp_path)
    assert {f"stream:{m}:holdout" for m in e4.METHODS} <= set(cost.index)
    refused = [s for s in cost.index if any(f":{m}:" in s for m in e4.BASIS_METHODS)] + ["dict_calibration",
                                                                                         "oracle_diagnostics:alternative"]
    assert set(cost.loc[refused, "status"]) == {"EIGENVALUE_TIE_UNRESOLVED"}
    assert cost.loc[refused, "cpu_s"].isna().all()
    assert cost.loc["stream:EW:holdout", "status"] == "COMPLETE"
    full = e4.validate_config(e4.load_config(e4.CONFIG))
    rows = fake_cost(full)
    rows = pd.concat([rows[rows.partition != "gaussian:8"], cost.reset_index().assign(partition="gaussian:8")[
        e4.COST_COLUMNS]], ignore_index=True)
    assert set(e4.forecast(rows, full)["scenarios"]["status"]) == {"INCOMPLETE"}


def test_a_single_n_grid_gives_no_slope_and_no_numerical_warning():
    import warnings
    trials = fake_trials([8], growing, lambda m, N: np.full(80, -1))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        out = e4.analyse(trials, acfg(grid=[8]))
    c = out["contrasts"].set_index("contrast")
    assert set(c["reason"]) == {"FEWER_THAN_TWO_N"}
    assert c.loc["Delta", "label"] == "NOT_IDENTIFIED" and "WARN_ODIR_SLOPE" not in set(out["warnings"]["warning"])


def test_forecast_counts_external_cpu_when_a_killed_partition_has_no_csv():
    rows = pd.DataFrame([{"partition": "precheck", "stage": "precheck", "n_paths": 1, "n_runs": 1,
                          "cpu_s": 2.0, "wall_s": 2.0, "peak_rss_kib": 1000, "status": "COMPLETE"}],
                        columns=e4.COST_COLUMNS)
    out = e4.forecast(rows, cfg(), invocation_totals={"gaussian:4": 13.0})
    assert out["consumed_cpu_s"] == 15.0
    assert set(out["scenarios"]["status"]) == {"INCOMPLETE"}
