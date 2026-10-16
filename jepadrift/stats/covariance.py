"""Shrinkage covariance estimators (numpy only)."""
import numpy as np


def ledoit_wolf(X):
    """Ledoit-Wolf (2004) shrinkage of the centred covariance (divided by n) towards mu*I: (sigma, shrinkage)."""
    Xc = X - X.mean(axis=0)
    n, p = Xc.shape
    S = Xc.T @ Xc / n
    mu = np.trace(S) / p
    d2 = np.sum((S - mu * np.eye(p)) ** 2)
    b2 = (np.sum((Xc.T ** 2) @ (Xc ** 2)) / n - np.sum(S ** 2)) / n
    shrinkage = 0.0 if d2 == 0 else float(min(b2, d2) / d2)
    return (1.0 - shrinkage) * S + shrinkage * mu * np.eye(p), shrinkage
