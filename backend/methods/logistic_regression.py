from .base import BaseMethod, register
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score
import matplotlib.pyplot as plt
import os

@register
class LogisticRegressionMethod(BaseMethod):
    id = "logistic_regression"
    name = "Logistic Regression (sklearn)"
    requires = {"y":"binary"}

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str):
        y_col = roles.get("y")
        if y_col is None: raise ValueError("roles.y 未指定")
        X_cols = [c for c in df.columns if c != y_col]
        X = pd.get_dummies(df[X_cols], drop_first=True).fillna(0).values
        y = df[y_col].astype(int).values

        model = LogisticRegression(max_iter=200)
        model.fit(X, y)
        proba = model.predict_proba(X)[:,1]
        yhat = (proba >= 0.5).astype(int)

        fpr, tpr, _ = roc_curve(y, proba)
        fig_path = os.path.join(out_dir, "roc.png")
        plt.figure()
        plt.plot(fpr, tpr, label="ROC")
        plt.plot([0,1], [0,1], "--")
        plt.xlabel("FPR"); plt.ylabel("TPR"); plt.title("ROC Curve")
        plt.legend(); plt.tight_layout(); plt.savefig(fig_path); plt.close()

        metrics = {
            "accuracy": round(float(accuracy_score(y, yhat)), 4),
            "auc": round(float(roc_auc_score(y, proba)), 4)
        }
        summary = f"<p>Logistic 以所有非 <code>{y_col}</code> 欄位為自變數；AUC={metrics['auc']}，accuracy={metrics['accuracy']}。</p>"

        return {"metrics": metrics, "figures": [fig_path], "summary_md": summary}
