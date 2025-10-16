"""
Doubly Robust ATE Estimation Module

Provides causal inference methods using doubly robust estimators
with CBPS-like propensity score weighting.
"""

from .method import DrAteCbps

__all__ = ['DrAteCbps']
