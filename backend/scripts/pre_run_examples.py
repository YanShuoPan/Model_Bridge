"""
預執行範例數據並儲存結果
"""
import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import shutil

# 添加後端路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.methods.base import METHODS_REGISTRY
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, confusion_matrix, precision_score, recall_score
from scipy import stats
import matplotlib.pyplot as plt


def run_logistic_regression_detailed(df, roles, params, out_dir):
    """
    執行 logistic regression 並返回詳細結果（包括係數、p值等）
    """
    y_col = roles.get("y")
    X_cols = roles.get("X", [c for c in df.columns if c != y_col])

    # 準備數據
    X = df[X_cols].values
    y = df[y_col].astype(int).values

    # 訓練模型
    model = LogisticRegression(
        max_iter=params.get("max_iter", 1000),
        solver=params.get("solver", "lbfgs"),
        random_state=params.get("random_state", 42)
    )
    model.fit(X, y)

    # 預測
    proba = model.predict_proba(X)[:, 1]
    yhat = (proba >= 0.5).astype(int)

    # 計算指標
    metrics = {
        "accuracy": round(float(accuracy_score(y, yhat)), 4),
        "auc": round(float(roc_auc_score(y, proba)), 4),
        "precision": round(float(precision_score(y, yhat)), 4),
        "recall": round(float(recall_score(y, yhat)), 4)
    }

    # 提取係數
    coefficients = {}
    for i, col in enumerate(X_cols):
        coef = float(model.coef_[0][i])
        odds_ratio = float(np.exp(coef))

        coefficients[col] = {
            "coefficient": round(coef, 4),
            "odds_ratio": round(odds_ratio, 4),
            "std_err": None,  # sklearn 不直接提供
            "p_value": None   # sklearn 不直接提供
        }

    # 生成圖表
    figures = []

    # ROC 曲線
    fpr, tpr, _ = roc_curve(y, proba)
    fig_path = os.path.join(out_dir, "roc_curve.png")
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"ROC (AUC = {metrics['auc']:.3f})", linewidth=2)
    plt.plot([0, 1], [0, 1], "k--", label="Random")
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("ROC Curve", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    figures.append("roc_curve.png")

    # 混淆矩陣
    cm = confusion_matrix(y, yhat)
    fig_path = os.path.join(out_dir, "confusion_matrix.png")
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title("Confusion Matrix", fontsize=14)
    plt.colorbar()
    tick_marks = np.arange(2)
    plt.xticks(tick_marks, ["Not Churned", "Churned"], fontsize=11)
    plt.yticks(tick_marks, ["Not Churned", "Churned"], fontsize=11)

    # 添加數字
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], 'd'),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=14)

    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    figures.append("confusion_matrix.png")

    # 係數圖
    fig_path = os.path.join(out_dir, "coefficients.png")
    coef_df = pd.DataFrame([
        {"variable": k, "odds_ratio": v["odds_ratio"]}
        for k, v in coefficients.items()
    ]).sort_values("odds_ratio")

    plt.figure(figsize=(10, 6))
    colors = ['red' if x < 1 else 'green' for x in coef_df['odds_ratio']]
    plt.barh(coef_df['variable'], coef_df['odds_ratio'], color=colors, alpha=0.7)
    plt.axvline(x=1, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Odds Ratio', fontsize=12)
    plt.title('Feature Importance (Odds Ratios)', fontsize=14)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()
    figures.append("coefficients.png")

    return {
        "metrics": metrics,
        "coefficients": coefficients,
        "figures": figures,
        "confusion_matrix": cm.tolist(),
        "model_info": {
            "intercept": round(float(model.intercept_[0]), 4),
            "n_features": len(X_cols),
            "n_samples": len(y),
            "n_positive": int(y.sum()),
            "n_negative": int(len(y) - y.sum())
        }
    }


def pre_run_example(method_id: str, example_path: str):
    """
    預執行單個範例

    Args:
        method_id: 方法 ID
        example_path: 範例目錄路徑
    """
    example_dir = Path(example_path)

    print(f"\n{'='*60}")
    print(f"執行範例: {example_dir.name}")
    print(f"方法: {method_id}")
    print(f"{'='*60}\n")

    # 1. 讀取配置
    config_path = example_dir / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    print(f"[OK] 載入配置: {config['example_name']}")

    # 2. 讀取數據
    data_path = example_dir / config["data_source"]
    df = pd.read_csv(data_path)

    print(f"[OK] 載入數據: {len(df)} 筆資料, {len(df.columns)} 個欄位")

    # 3. 創建輸出目錄
    output_dir = example_dir / "pre_run_results"
    output_dir.mkdir(exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # 4. 執行方法（使用詳細版本）
    start_time = time.time()

    if method_id == "logistic_regression":
        results = run_logistic_regression_detailed(
            df=df,
            roles=config["roles"],
            params=config.get("parameters", {}),
            out_dir=str(figures_dir)
        )
    else:
        # 使用註冊的方法
        method_cls = METHODS_REGISTRY.get(method_id)
        if not method_cls:
            raise ValueError(f"方法 {method_id} 未註冊")

        method = method_cls()
        results = method.run(
            df=df,
            roles=config["roles"],
            params=config.get("parameters", {}),
            out_dir=str(figures_dir)
        )

    execution_time = time.time() - start_time

    print(f"[OK] 執行完成 ({execution_time:.2f} 秒)")

    # 5. 構建結果數據
    results_data = {
        "method_id": method_id,
        "example_id": config["example_id"],
        "example_name": config["example_name_zh"],
        "executed_at": datetime.now().isoformat(),
        "execution_time_seconds": round(execution_time, 2),
        "metrics": results.get("metrics", {}),
        "coefficients": results.get("coefficients", {}),
        "model_info": results.get("model_info", {}),
        "confusion_matrix": results.get("confusion_matrix"),
        "figures": [],
        "summary": {
            "sample_size": len(df),
            "outcome_variable": config["roles"].get("y"),
            "variables_used": config["roles"].get("X", []),
            "n_variables": len(config["roles"].get("X", [])),
            "expected_insights": config.get("expected_insights", [])
        }
    }

    # 處理圖表
    if "figures" in results:
        for fig_name in results["figures"]:
            results_data["figures"].append({
                "filename": fig_name,
                "relative_path": f"figures/{fig_name}",
                "type": Path(fig_name).stem,
                "description": get_figure_description(fig_name)
            })

    # 6. 儲存 results.json
    results_path = output_dir / "results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] 結果已儲存: {results_path}")
    print(f"  - 指標: {list(results_data['metrics'].keys())}")
    print(f"  - 圖表: {len(results_data['figures'])} 張")
    print(f"  - 變數: {results_data['summary']['n_variables']} 個")

    return results_data


def get_figure_description(filename: str) -> str:
    """根據檔案名稱返回描述"""
    descriptions = {
        "roc_curve": "ROC 曲線 - 模型區分能力",
        "confusion_matrix": "混淆矩陣 - 預測準確度",
        "coefficients": "係數圖 - 變數影響力",
        "balance_plot": "平衡診斷圖",
        "ate_distribution": "ATE 分佈圖"
    }

    stem = Path(filename).stem
    return descriptions.get(stem, f"{stem} 圖表")


def pre_run_all():
    """預執行所有範例"""
    examples = [
        {
            "method_id": "logistic_regression",
            "path": "backend/knowledge_base/methods/logistic_regression/examples/customer_churn"
        },
        # 可以添加更多範例...
    ]

    print("\n" + "="*60)
    print("開始預執行所有範例")
    print("="*60)

    success_count = 0
    fail_count = 0

    for example in examples:
        try:
            pre_run_example(example["method_id"], example["path"])
            success_count += 1
        except Exception as e:
            print(f"\n[FAIL] {example['method_id']} - {example['path']} 執行失敗:")
            print(f"  錯誤: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1

    print("\n" + "="*60)
    print(f"執行完成: 成功 {success_count} 個, 失敗 {fail_count} 個")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        # 執行單個範例
        if len(sys.argv) < 4:
            print("用法: python pre_run_examples.py --single <method_id> <example_path>")
            sys.exit(1)

        method_id = sys.argv[2]
        example_path = sys.argv[3]
        pre_run_example(method_id, example_path)
    else:
        # 執行所有範例
        pre_run_all()
