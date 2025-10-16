"""
Doubly Robust ATE Method

BaseMethod wrapper for causal inference using DR estimator.
"""

from ..base import BaseMethod, register
from .core import cbps_weight, standardized_mean_difference, doubly_robust_ate
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


@register
class DrAteCbps(BaseMethod):
    id = "dr_ate_cbps"
    name = "Doubly Robust ATE (CBPS-like weights)"
    requires = {"treatment": "binary", "y": "any"}

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str):
        """
        Execute Doubly Robust ATE estimation with balance diagnostics.

        Args:
            df: Input dataframe
            roles: Variable roles dict with 'treatment' and 'y' keys
            params: Method parameters (optional)
            out_dir: Output directory for results

        Returns:
            dict with metrics, figures, and summary
        """
        t_col = roles.get("treatment")
        y_col = roles.get("y")

        if not t_col or not y_col:
            raise ValueError("因果需要 roles.treatment 與 roles.y(outcome)")

        # Prepare data
        covs = [c for c in df.columns if c not in [t_col, y_col]]
        X = pd.get_dummies(df[covs], drop_first=True).fillna(0).values
        T = df[t_col].astype(int).values
        Y = df[y_col].astype(float).values

        # Calculate propensity weights
        w = cbps_weight(X, T)

        # Estimate ATE
        ate_result = doubly_robust_ate(X, T, Y, w)
        ate = ate_result["ate"]
        se = ate_result["se"]
        ci_lower = ate_result["ci_lower"]
        ci_upper = ate_result["ci_upper"]

        # Balance diagnostics
        x_df = pd.DataFrame(X)
        w_t = w[T == 1]
        w_c = w[T == 0]
        smd_after = [
            standardized_mean_difference(
                x_df.loc[T == 1, i].values,
                x_df.loc[T == 0, i].values,
                w_t,
                w_c
            )
            for i in range(X.shape[1])
        ]

        # Generate balance plot
        fig_path = os.path.join(out_dir, "balance.png")
        plt.figure(figsize=(10, 6))
        plt.scatter(range(len(smd_after)), np.abs(smd_after), alpha=0.6, s=50)
        plt.axhline(0.1, linestyle="--", color='red', linewidth=2, label='SMD = 0.1 threshold')
        plt.xlabel("Covariate Index", fontsize=12)
        plt.ylabel("|SMD| (weighted)", fontsize=12)
        plt.title("Weighted Balance Diagnostics (|SMD|)", fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig_path, dpi=300)
        plt.close()

        # Prepare metrics
        metrics = {
            "ATE": round(ate, 6),
            "SE": round(se, 6),
            "CI95_lower": round(ci_lower, 6),
            "CI95_upper": round(ci_upper, 6),
            "num_covariates": X.shape[1],
            "num_balanced": int(sum(abs(s) < 0.1 for s in smd_after)),
            "max_smd": round(float(max(abs(s) for s in smd_after)), 4)
        }

        # Generate summary
        summary_md = f"""
## Doubly Robust ATE 估計結果

### 因果效應估計
- **平均處置效應 (ATE)**: {metrics['ATE']:.4f}
- **標準誤 (SE)**: {metrics['SE']:.4f}
- **95% 信賴區間**: [{metrics['CI95_lower']:.4f}, {metrics['CI95_upper']:.4f}]

### 平衡診斷
- **共變數數量**: {metrics['num_covariates']}
- **平衡共變數數 (|SMD| < 0.1)**: {metrics['num_balanced']} / {metrics['num_covariates']}
- **最大 |SMD|**: {metrics['max_smd']:.4f}

### 方法說明
此方法使用 Doubly Robust 估計量，結合傾向分數加權與結果迴歸模型。
只要其中一個模型正確指定，估計量就是一致的。
"""

        return {
            "metrics": metrics,
            "figures": [fig_path],
            "summary_md": summary_md
        }
