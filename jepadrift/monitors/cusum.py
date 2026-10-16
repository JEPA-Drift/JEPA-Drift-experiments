"""CUSUM detectors: Article B ports (R01 l.110-142, R15_b l.350-360), vectorized equivalents, P1 configurations."""
import numpy as np


def strict_cusum(stream, delta_P, threshold):
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta_P)
        if S > threshold: return t
    return -1


def get_multiple_alarms(stream, delta_P, threshold, bilateral=False):
    alarms = []
    idx = 0
    while idx < len(stream):
        remaining = stream[idx:]
        pos_alarm = strict_cusum(remaining, delta_P, threshold)
        if bilateral:
            neg_alarm = strict_cusum(-remaining, delta_P, threshold)
        else:
            neg_alarm = -1
        valid_alarms = [a for a in [pos_alarm, neg_alarm] if a != -1]
        if not valid_alarms:
            break
        first_alarm = min(valid_alarms)
        actual_idx = idx + first_alarm
        alarms.append(actual_idx)
        idx = actual_idx + 1
    return alarms


def get_cusum_trajectory(stream, delta_P):
    S_traj = np.zeros(len(stream))
    S = 0.0
    for t in range(len(stream)):
        S = max(0.0, S + stream[t] - delta_P)
        S_traj[t] = S
    return S_traj


def bilateral_delay(stream, delta, thr):
    i1=strict_cusum(stream,delta,thr); i2=strict_cusum(-stream,delta,thr)
    cs=[i for i in (i1,i2) if i!=-1]; return min(cs) if cs else -1


def cusum_max_bilateral(stream, delta):
    Sp=Sn=M=0.0
    for x in stream:
        Sp=max(0.0,Sp+x-delta); Sn=max(0.0,Sn-x-delta)
        if Sp>M: M=Sp
        if Sn>M: M=Sn
    return M


def _paths(streams):
    x = np.asarray(streams, dtype=np.float64)
    if not np.isfinite(x).all():
        raise ValueError("stream contains non-finite values")
    return x.reshape(-1, x.shape[-1]), x.shape[:-1]


def cusum_trajectory_vec(streams, delta_P):
    """get_cusum_trajectory along the last axis of a (..., T) array."""
    x, lead = _paths(streams)
    S = np.zeros(x.shape[0])
    out = np.empty_like(x)
    for t in range(x.shape[1]):
        S = np.maximum(0.0, S + x[:, t] - delta_P)
        out[:, t] = S
    return out.reshape(lead + x.shape[1:])


def strict_cusum_vec(streams, delta_P, threshold):
    """strict_cusum along the last axis of a (..., T) array; -1 when no alarm."""
    x, lead = _paths(streams)
    S = np.zeros(x.shape[0])
    first = np.full(x.shape[0], -1, dtype=np.int64)
    for t in range(x.shape[1]):
        S = np.maximum(0.0, S + x[:, t] - delta_P)
        first[(first < 0) & (S > threshold)] = t
        if (first >= 0).all():
            break
    return first.reshape(lead)


def bilateral_delay_vec(streams, delta, thr):
    """bilateral_delay along the last axis of a (..., T) array; -1 when no alarm."""
    x, lead = _paths(streams)
    Sp = np.zeros(x.shape[0])
    Sn = np.zeros(x.shape[0])
    first = np.full(x.shape[0], -1, dtype=np.int64)
    for t in range(x.shape[1]):
        Sp = np.maximum(0.0, Sp + x[:, t] - delta)
        Sn = np.maximum(0.0, Sn - x[:, t] - delta)
        first[(first < 0) & ((Sp > thr) | (Sn > thr))] = t
        if (first >= 0).all():
            break
    return first.reshape(lead)


def cusum_max_bilateral_vec(streams, delta):
    """cusum_max_bilateral along the last axis of a (..., T) array."""
    x, lead = _paths(streams)
    Sp = np.zeros(x.shape[0])
    Sn = np.zeros(x.shape[0])
    M = np.zeros(x.shape[0])
    for t in range(x.shape[1]):
        Sp = np.maximum(0.0, Sp + x[:, t] - delta)
        Sn = np.maximum(0.0, Sn - x[:, t] - delta)
        M = np.maximum(M, np.maximum(Sp, Sn))
    return M.reshape(lead)


def multiple_alarms_vec(streams, delta_P, threshold, bilateral=False):
    """get_multiple_alarms along the last axis of a (..., T) array, as a boolean alarm mask."""
    x, lead = _paths(streams)
    Sp = np.zeros(x.shape[0])
    Sn = np.zeros(x.shape[0])
    alarm = np.zeros(x.shape, dtype=bool)
    for t in range(x.shape[1]):
        Sp = np.maximum(0.0, Sp + x[:, t] - delta_P)
        hit = Sp > threshold
        if bilateral:
            Sn = np.maximum(0.0, Sn - x[:, t] - delta_P)
            hit |= Sn > threshold
        alarm[:, t] = hit
        Sp[hit] = 0.0
        Sn[hit] = 0.0
    return alarm.reshape(lead + x.shape[1:])


P1 = {
    "P1-C/B": {"stream": "label", "delta": 0.1, "threshold": 10.0, "bilateral": True,
               "q_hat_window": ("2018-01-02", "2019-12-31"), "trailing_days": 250},
    "P1-C/C": {"stream": "exact_sign", "delta": 0.1, "threshold": "lattice", "bilateral": True,
               "comparison": "strict", "rule": "at_or_below"},
    "P1-D/B": {"stream": "energy", "delta": 0.5, "lambda_iid": 65.0, "bilateral": False,
               "gamma_hat_window": ("2018-01-02", "2019-12-31"), "trailing_days": 250},
}
