from .base import BaseMethod, register
import pandas as pd, numpy as np
import os, matplotlib.pyplot as plt

def _cbps_weight(X: np.ndarray, T: np.ndarray) -> np.ndarray:
    from sklearn.linear_model import LogisticRegression
    lr = LogisticRegression(max_iter=300)
    lr.fit(X, T)
    ps = lr.predict_proba(X)[:,1]
    ps = np.clip(ps, 1e-3, 1-1e-3)
    w = np.where(T==1, 1/ps, 1/(1-ps))
    return w

def _smd(x_t, x_c, w_t, w_c):
    m1 = np.average(x_t, weights=w_t)
    m0 = np.average(x_c, weights=w_c)
    s = np.sqrt(0.5*(np.average((x_t-m1)**2, weights=w_t)+np.average((x_c-m0)**2, weights=w_c)))
    return (m1 - m0) / (s + 1e-8)

@register
class DrAteCbps(BaseMethod):
    id = "dr_ate_cbps"
    name = "Doubly Robust ATE (CBPS-like weights)"
    requires = {"treatment":"binary", "y":"any"}

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str):
        t_col = roles.get("treatment"); y_col = roles.get("y")
        if not t_col or not y_col: raise ValueError("因果需要 roles.treatment 與 roles.y(outcome)")

        covs = [c for c in df.columns if c not in [t_col, y_col]]
        X = pd.get_dummies(df[covs], drop_first=True).fillna(0).values
        T = df[t_col].astype(int).values
        Y = df[y_col].astype(float).values

        w = _cbps_weight(X, T)

        from sklearn.linear_model import LinearRegression
        mu1 = LinearRegression().fit(X[T==1], Y[T==1]).predict(X)
        mu0 = LinearRegression().fit(X[T==0], Y[T==0]).predict(X)

        y1_hat = mu1
        y0_hat = mu0
        dr_scores = (y1_hat - y0_hat) + (T*(Y - y1_hat))*w/np.mean(w[T==1]) - ((1-T)*(Y - y0_hat))*w/np.mean(w[T==0])
        ate = float(np.mean(dr_scores))

        import numpy as np
        rng = np.random.default_rng(42)
        idx = np.arange(len(Y))
        boots = [np.mean(dr_scores[rng.choice(idx, size=len(idx), replace=True)]) for _ in range(200)]
        se = float(np.std(boots, ddof=1))
        ci = (ate - 1.96*se, ate + 1.96*se)

        x_df = pd.DataFrame(X)
        w_t = w[T==1]; w_c = w[T==0]
        smd_after = [ _smd(x_df.loc[T==1,i].values, x_df.loc[T==0,i].values, w_t, w_c) for i in range(X.shape[1]) ]

        fig_path = os.path.join(out_dir, "balance.png")
        plt.figure()
        plt.scatter(range(len(smd_after)), np.abs(smd_after))
        plt.axhline(0.1, linestyle="--")
        plt.xlabel("Covariate Index"); plt.ylabel("|SMD| (weighted)")
        plt.title("Weighted Balance (|SMD|)")
        plt.tight_layout(); plt.savefig(fig_path); plt.close()

        metrics = {
            "ATE": round(ate, 6),
            "SE": round(se, 6),
            "CI95_lower": round(ci[0], 6),
            "CI95_upper": round(ci[1], 6)
        }
        summary = f"<p>DR-ATE 估計量（教學版）完成。ATE={metrics['ATE']} (95% CI {metrics['CI95_lower']}, {metrics['CI95_upper']})。</p>"

        return {"metrics": metrics, "figures": [fig_path], "summary_md": summary}
