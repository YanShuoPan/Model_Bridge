"""
Doubly Robust ATE Estimation with CBPS-like Weighting

Core algorithms for causal inference.
"""

import numpy as np


def cbps_weight(X: np.ndarray, T: np.ndarray) -> np.ndarray:
    """
    Calculate inverse propensity weights using logistic regression (CBPS-like).

    Args:
        X: Covariates matrix (n x p)
        T: Treatment indicator (n,) with values 0 or 1

    Returns:
        weights: Array of weights (n,)
    """
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(max_iter=300)
    lr.fit(X, T)
    ps = lr.predict_proba(X)[:, 1]
    ps = np.clip(ps, 1e-3, 1 - 1e-3)
    w = np.where(T == 1, 1 / ps, 1 / (1 - ps))
    return w


def standardized_mean_difference(x_t, x_c, w_t, w_c):
    """
    Calculate weighted standardized mean difference (SMD).

    Args:
        x_t: Covariate values for treated group
        x_c: Covariate values for control group
        w_t: Weights for treated group
        w_c: Weights for control group

    Returns:
        smd: Standardized mean difference
    """
    m1 = np.average(x_t, weights=w_t)
    m0 = np.average(x_c, weights=w_c)
    s = np.sqrt(
        0.5 * (
            np.average((x_t - m1) ** 2, weights=w_t) +
            np.average((x_c - m0) ** 2, weights=w_c)
        )
    )
    return (m1 - m0) / (s + 1e-8)


def doubly_robust_ate(X, T, Y, w):
    """
    Estimate Average Treatment Effect using Doubly Robust estimator.

    Args:
        X: Covariates matrix (n x p)
        T: Treatment indicator (n,)
        Y: Outcome variable (n,)
        w: Propensity weights (n,)

    Returns:
        dict with 'ate', 'se', 'ci_lower', 'ci_upper'
    """
    from sklearn.linear_model import LinearRegression

    # Fit outcome models
    mu1 = LinearRegression().fit(X[T == 1], Y[T == 1]).predict(X)
    mu0 = LinearRegression().fit(X[T == 0], Y[T == 0]).predict(X)

    # DR scores
    y1_hat = mu1
    y0_hat = mu0
    dr_scores = (
        (y1_hat - y0_hat) +
        (T * (Y - y1_hat)) * w / np.mean(w[T == 1]) -
        ((1 - T) * (Y - y0_hat)) * w / np.mean(w[T == 0])
    )
    ate = float(np.mean(dr_scores))

    # Bootstrap standard error
    rng = np.random.default_rng(42)
    idx = np.arange(len(Y))
    boots = [
        np.mean(dr_scores[rng.choice(idx, size=len(idx), replace=True)])
        for _ in range(200)
    ]
    se = float(np.std(boots, ddof=1))
    ci = (ate - 1.96 * se, ate + 1.96 * se)

    return {
        "ate": ate,
        "se": se,
        "ci_lower": ci[0],
        "ci_upper": ci[1]
    }
