"""GARCH(1,1) QMLE and the exact variance-inflation factor: verbatim port of R01 l.72-108."""
import numpy as np
from scipy.optimize import minimize


def _garch_nll(params, eps, var_emp):
    alpha, beta = params
    omega = var_emp * (1.0 - alpha - beta)
    n = len(eps)
    sigma2 = np.zeros(n)
    sigma2[0] = var_emp
    for t in range(1, n):
        sigma2[t] = omega + alpha * eps[t-1]**2 + beta * sigma2[t-1]
        if sigma2[t] < 1e-10: sigma2[t] = 1e-10
    nll = 0.5 * np.sum(np.log(sigma2) + (eps**2) / sigma2)
    return nll


def fit_garch_qmle(eps_warmup):
    var_emp = np.var(eps_warmup)
    init = [0.05, 0.90]
    bounds = [(1e-6, 0.5), (1e-6, 0.99)]
    constraints = {'type': 'ineq', 'fun': lambda x: 0.999 - (x[0] + x[1])}
    try:
        res = minimize(_garch_nll, init, args=(eps_warmup, var_emp), 
                       method='SLSQP', bounds=bounds, constraints=constraints,
                       tol=1e-8, options={'maxiter': 1000, 'ftol': 1e-8, 'eps': 1e-5, 'disp': False})
        a, b = res.x if res.success else init
        a, b = round(float(a), 6), round(float(b), 6)
        converged = res.success and max(abs(a - 0.05), abs(b - 0.90)) > 1e-6
        if not converged:
            a, b = init
        return (var_emp * (1.0 - a - b), a, b), converged
    except (TypeError, np.linalg.LinAlgError) as e:
        return (var_emp * (1.0 - 0.05 - 0.90), 0.05, 0.90), False


def compute_gamma_exact(alpha, beta):
    phi = alpha + beta
    if phi >= 1.0: return np.inf
    denom = 1 - 2 * alpha * beta - beta**2
    if denom <= 0: return (1 + phi) / (1 - phi)
    rho1 = alpha * (1 - beta * phi) / denom
    return max(1.0, 1 + 2 * rho1 / (1 - phi))
