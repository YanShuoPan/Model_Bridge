"""
Logistic Regression Method

BaseMethod wrapper for binary classification using logistic regression.
"""

from ..base import BaseMethod, register
from .core import (
    train_logistic_model,
    predict_probabilities,
    calculate_metrics,
    get_roc_curve_data
)
import pandas as pd
import matplotlib.pyplot as plt
import os


@register
class LogisticRegressionMethod(BaseMethod):
    id = "logistic_regression"
    name = "Logistic Regression (sklearn)"
    requires = {"y": "binary"}

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str):
        """
        Execute logistic regression for binary classification.

        Args:
            df: Input dataframe
            roles: Variable roles dict with 'y' key
            params: Method parameters (optional, supports 'max_iter', 'threshold')
            out_dir: Output directory for results

        Returns:
            dict with metrics, figures, and summary
        """
        y_col = roles.get("y")
        if y_col is None:
            raise ValueError("roles.y 未指定")

        # Prepare data
        X_cols = [c for c in df.columns if c != y_col]
        X = pd.get_dummies(df[X_cols], drop_first=True).fillna(0)
        X_values = X.values
        y = df[y_col].astype(int).values

        # Get parameters
        max_iter = params.get("max_iter", 200)
        threshold = params.get("threshold", 0.5)

        # Train model
        model = train_logistic_model(X_values, y, max_iter=max_iter)

        # Predictions
        proba = predict_probabilities(model, X_values)

        # Calculate metrics
        metrics = calculate_metrics(y, proba, threshold=threshold)

        # ROC curve
        fpr, tpr, _ = get_roc_curve_data(y, proba)

        # Generate ROC plot
        fig_roc_path = os.path.join(out_dir, "roc.png")
        plt.figure(figsize=(8, 8))
        plt.plot(fpr, tpr, linewidth=2, label=f'ROC (AUC = {metrics["auc"]:.3f})')
        plt.plot([0, 1], [0, 1], "--", color='gray', linewidth=2, label='Random Classifier')
        plt.xlabel("False Positive Rate (FPR)", fontsize=12)
        plt.ylabel("True Positive Rate (TPR)", fontsize=12)
        plt.title("ROC Curve", fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig_roc_path, dpi=300)
        plt.close()

        # Generate confusion matrix plot
        fig_cm_path = os.path.join(out_dir, "confusion_matrix.png")
        cm = [
            [metrics["true_negatives"], metrics["false_positives"]],
            [metrics["false_negatives"], metrics["true_positives"]]
        ]

        plt.figure(figsize=(7, 6))
        plt.imshow(cm, interpolation='nearest', cmap='Blues')
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.colorbar()
        tick_marks = [0, 1]
        plt.xticks(tick_marks, ['Predicted 0', 'Predicted 1'])
        plt.yticks(tick_marks, ['Actual 0', 'Actual 1'])

        # Add text annotations
        for i in range(2):
            for j in range(2):
                plt.text(j, i, str(cm[i][j]),
                        ha="center", va="center",
                        color="white" if cm[i][j] > max(max(cm)) / 2 else "black",
                        fontsize=20, fontweight='bold')

        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig(fig_cm_path, dpi=300)
        plt.close()

        # Round metrics for display
        display_metrics = {
            "accuracy": round(metrics["accuracy"], 4),
            "auc": round(metrics["auc"], 4),
            "precision": round(metrics["precision"], 4),
            "recall": round(metrics["recall"], 4),
            "f1_score": round(metrics["f1_score"], 4)
        }

        # Generate summary
        summary_md = f"""
## Logistic Regression 分類結果

### 模型表現
- **準確率 (Accuracy)**: {display_metrics['accuracy']:.4f}
- **AUC**: {display_metrics['auc']:.4f}
- **精確率 (Precision)**: {display_metrics['precision']:.4f}
- **召回率 (Recall)**: {display_metrics['recall']:.4f}
- **F1 分數**: {display_metrics['f1_score']:.4f}

### 混淆矩陣
|               | 預測為 0 | 預測為 1 |
|---------------|---------|---------|
| **實際為 0**  | {metrics['true_negatives']} (TN) | {metrics['false_positives']} (FP) |
| **實際為 1**  | {metrics['false_negatives']} (FN) | {metrics['true_positives']} (TP) |

### 資料概況
- **樣本數**: {len(y)}
- **特徵數**: {X.shape[1]} (經 one-hot encoding 後)
- **正類比例**: {sum(y) / len(y):.2%}
- **決策閾值**: {threshold}

### 方法說明
Logistic Regression 使用邏輯函數建立二元分類模型，輸出類別機率。
此方法適合線性可分或接近線性可分的問題。
"""

        return {
            "metrics": display_metrics,
            "figures": [fig_roc_path, fig_cm_path],
            "summary_md": summary_md,
            "model_coefficients": model.coef_[0].tolist() if hasattr(model, 'coef_') else None,
            "feature_names": X.columns.tolist()
        }
