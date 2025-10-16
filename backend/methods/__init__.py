"""
Statistical Methods Module

Auto-register all available statistical methods.
Each method is organized as a self-contained module with:
- method.py: BaseMethod wrapper class
- core.py: Core algorithm implementation
- __init__.py: Module exports
"""

# Import all method modules to trigger @register decorator
from backend.methods import dr_ate_cbps
from backend.methods import logistic_regression
from backend.methods import oga_hdic

# Export base module contents for external use
from backend.methods.base import BaseMethod, METHODS_REGISTRY, register

__all__ = [
    'BaseMethod',
    'METHODS_REGISTRY',
    'register',
    'dr_ate_cbps',
    'logistic_regression',
    'oga_hdic',
]
