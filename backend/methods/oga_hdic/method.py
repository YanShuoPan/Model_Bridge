from ..base import BaseMethod, register
from .ohit import oga_hdic
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

@register
class OGAHDICMethod(BaseMethod):
    id = "oga_hdic"
    name = "OGA-HDIC (高維度變數選擇)"
    requires = {"y": "continuous"}  # 適用於連續型結果變數

    def _interpret_results(self, metrics: dict, selected_vars: list, n: int, p: int) -> str:
        """
        生成結果的解讀說明

        Args:
            metrics: 模型指標
            selected_vars: 選擇的變數列表
            n: 樣本數
            p: 總變數數

        Returns:
            解讀文字
        """
        interpretation = []

        # 1. 維度評估
        dim_ratio = p / n
        if dim_ratio > 1:
            interpretation.append(
                f"**高維度情境確認**: 您的數據有 {p} 個變數但只有 {n} 筆樣本（p/n = {dim_ratio:.2f}），"
                "屬於典型的高維度問題，使用 OGA-HDIC 是合適的選擇。"
            )
        elif dim_ratio > 0.5:
            interpretation.append(
                f"**中度高維度**: 變數數相對於樣本數較多（p/n = {dim_ratio:.2f}），"
                "變數選擇方法可以幫助提升模型的穩定性和可解釋性。"
            )

        # 2. 變數篩選效果
        selection_rate = len(selected_vars) / p
        if selection_rate < 0.2:
            interpretation.append(
                f"**高度稀疏**: 只有 {len(selected_vars)}/{p} ({selection_rate*100:.1f}%) 的變數被保留，"
                "表示您的問題具有很強的稀疏性，大部分變數對預測貢獻不大。"
            )
        elif selection_rate < 0.5:
            interpretation.append(
                f"**中度稀疏**: {len(selected_vars)}/{p} ({selection_rate*100:.1f}%) 的變數被選中，"
                "模型成功地從大量變數中篩選出重要特徵。"
            )
        else:
            interpretation.append(
                f"**低稀疏性**: 保留了 {len(selected_vars)}/{p} ({selection_rate*100:.1f}%) 的變數，"
                "可能大部分變數都對結果有一定影響。"
            )

        # 3. 模型表現評估
        r_squared = metrics['Trim_R_squared']
        adj_r_squared = metrics['Trim_Adj_R_squared']

        if r_squared > 0.8:
            performance = "優秀"
            comment = "模型能夠很好地解釋結果變數的變異"
        elif r_squared > 0.6:
            performance = "良好"
            comment = "模型有不錯的預測能力"
        elif r_squared > 0.4:
            performance = "中等"
            comment = "模型捕捉了部分重要的關係，但仍有改進空間"
        else:
            performance = "較弱"
            comment = "可能需要考慮非線性關係或加入其他重要變數"

        interpretation.append(
            f"**預測表現 ({performance})**: R² = {r_squared:.3f}，調整 R² = {adj_r_squared:.3f}。{comment}。"
        )

        # 4. 建議
        interpretation.append("\n**建議下一步**:")
        suggestions = []

        if r_squared < 0.5:
            suggestions.append("- 考慮檢查是否有重要變數遺漏")
            suggestions.append("- 嘗試變數轉換（對數、平方等）來捕捉非線性關係")

        if abs(r_squared - adj_r_squared) > 0.05:
            suggestions.append("- R² 與調整 R² 差距較大，可能存在過度配適的風險")

        if len(selected_vars) > 0:
            suggestions.append(f"- 重點關注被選中的 {len(selected_vars)} 個變數，分析其與結果的關係")
            suggestions.append("- 檢查選中變數的係數方向和大小是否符合領域知識")

        if len(suggestions) > 0:
            interpretation.append("\n".join(suggestions))

        return "\n\n".join(interpretation)

    def _format_selected_variables(self, selected_vars: list, coefficients: dict) -> str:
        """
        格式化選擇的變數清單

        Args:
            selected_vars: 選擇的變數名稱列表
            coefficients: 係數字典

        Returns:
            格式化的變數清單
        """
        if len(selected_vars) == 0:
            return "*無變數被選中*"

        # 按係數絕對值排序
        var_info = []
        for var in selected_vars:
            if var in coefficients:
                coef = coefficients[var]['coefficient']
                p_val = coefficients[var].get('p_value')
                direction = "↑ 正向" if coef > 0 else "↓ 負向"
                sig = "***" if p_val and p_val < 0.001 else "**" if p_val and p_val < 0.01 else "*" if p_val and p_val < 0.05 else ""
                var_info.append((var, abs(coef), f"- **{var}** {direction} (係數: {coef:.4f}{sig})"))

        # 排序並格式化
        var_info.sort(key=lambda x: x[1], reverse=True)

        if len(var_info) <= 10:
            return "\n".join([info[2] for info in var_info])
        else:
            top_10 = "\n".join([info[2] for info in var_info[:10]])
            return f"{top_10}\n\n*...以及其他 {len(var_info) - 10} 個變數*"

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str):
        """
        執行 OGA-HDIC 高維度變數選擇與迴歸

        適用於：變數數量很多（高維度）的預測問題
        """
        y_col = roles.get("y")
        if y_col is None:
            raise ValueError("roles.y 未指定")

        # 準備數據
        X_cols = [c for c in df.columns if c != y_col]
        X = df[X_cols].copy()
        y = df[y_col].values

        # 處理類別變數（one-hot encoding）
        X_encoded = pd.get_dummies(X, drop_first=True).fillna(0)

        # 執行 OGA-HDIC
        result = oga_hdic(
            X=X_encoded,
            y=y,
            Kn=params.get("Kn", None),
            c1=params.get("c1", 5),
            HDIC_Type=params.get("HDIC_Type", "HDBIC"),
            c2=params.get("c2", 2),
            c3=params.get("c3", 2.01),
            intercept=True
        )

        # 提取結果
        n = result["n"]
        p = result["p"]
        Kn = result["Kn"]
        J_HDIC_names = result["J_HDIC_names"]
        J_Trim_names = result["J_Trim_names"]
        fit_HDIC = result["betahat_HDIC"]
        fit_Trim = result["betahat_Trim"]

        # 準備輸出指標
        metrics = {
            "sample_size": int(n),
            "total_predictors": int(p),
            "max_steps": int(Kn),
            "selected_by_HDIC": len(J_HDIC_names),
            "selected_after_trim": len(J_Trim_names),
            "HDIC_R_squared": float(fit_HDIC.rsquared),
            "Trim_R_squared": float(fit_Trim.rsquared),
            "HDIC_Adj_R_squared": float(fit_HDIC.rsquared_adj),
            "Trim_Adj_R_squared": float(fit_Trim.rsquared_adj)
        }

        # 準備係數資訊（使用 Trim 模型）
        coefficients = {}
        if hasattr(fit_Trim, 'params'):
            for var_name, coef_value in fit_Trim.params.items():
                if var_name != 'const':
                    coefficients[var_name] = {
                        "coefficient": float(coef_value),
                        "std_err": float(fit_Trim.bse[var_name]) if hasattr(fit_Trim, 'bse') else None,
                        "t_value": float(fit_Trim.tvalues[var_name]) if hasattr(fit_Trim, 'tvalues') else None,
                        "p_value": float(fit_Trim.pvalues[var_name]) if hasattr(fit_Trim, 'pvalues') else None
                    }

        # 生成圖表
        figures = []

        # 圖1: HDIC 曲線
        fig_hdic_path = os.path.join(out_dir, "hdic_curve.png")
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, Kn + 1), result["HDIC"], marker='o', linewidth=2)
        plt.axvline(x=len(J_HDIC_names), color='r', linestyle='--', label=f'Optimal k={len(J_HDIC_names)}')
        plt.xlabel("Number of Selected Variables (k)", fontsize=12)
        plt.ylabel("HDIC Value", fontsize=12)
        plt.title("High-Dimensional Information Criterion (HDIC)", fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig_hdic_path, dpi=300)
        plt.close()
        figures.append(fig_hdic_path)

        # 圖2: 選擇的變數係數圖
        if len(coefficients) > 0:
            fig_coef_path = os.path.join(out_dir, "coefficients.png")

            # 按係數絕對值排序
            coef_sorted = sorted(coefficients.items(), key=lambda x: abs(x[1]["coefficient"]), reverse=True)
            top_n = min(15, len(coef_sorted))  # 最多顯示15個
            coef_sorted = coef_sorted[:top_n]

            var_names = [item[0] for item in coef_sorted]
            coef_values = [item[1]["coefficient"] for item in coef_sorted]

            plt.figure(figsize=(10, max(6, top_n * 0.4)))
            colors = ['red' if c < 0 else 'blue' for c in coef_values]
            plt.barh(var_names, coef_values, color=colors, alpha=0.7)
            plt.xlabel("Coefficient Value", fontsize=12)
            plt.ylabel("Variables", fontsize=12)
            plt.title(f"Top {top_n} Selected Variables (After Trimming)", fontsize=14, fontweight='bold')
            plt.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            plt.savefig(fig_coef_path, dpi=300)
            plt.close()
            figures.append(fig_coef_path)

        # 圖3: 預測值 vs 實際值
        fig_pred_path = os.path.join(out_dir, "prediction_plot.png")
        y_pred_trim = fit_Trim.fittedvalues

        plt.figure(figsize=(8, 8))
        plt.scatter(y, y_pred_trim, alpha=0.5, s=30)

        # 45度線
        min_val = min(y.min(), y_pred_trim.min())
        max_val = max(y.max(), y_pred_trim.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')

        plt.xlabel("Actual Values", fontsize=12)
        plt.ylabel("Predicted Values", fontsize=12)
        plt.title(f"Prediction vs Actual (R² = {metrics['Trim_R_squared']:.3f})", fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(fig_pred_path, dpi=300)
        plt.close()
        figures.append(fig_pred_path)

        # 生成結果解讀
        interpretation = self._interpret_results(metrics, J_Trim_names, n, p)

        # 生成摘要報告
        summary_md = f"""
## OGA-HDIC 變數選擇結果

### 📊 資料概況
- **樣本數**: {n}
- **總變數數**: {p}
- **維度比 (p/n)**: {p/n:.2f}
- **最大選擇步數**: {Kn}

### 🎯 變數選擇結果
- **HDIC 選擇的變數數**: {len(J_HDIC_names)}
- **Trimming 後保留**: {len(J_Trim_names)}
- **變數篩選率**: {(1 - len(J_Trim_names)/p)*100:.1f}% ({p - len(J_Trim_names)}/{p} 個變數被移除)

### 📈 模型表現（Trimming 後）
- **R²**: {metrics['Trim_R_squared']:.4f}
- **調整 R²**: {metrics['Trim_Adj_R_squared']:.4f}
- **AIC**: {metrics['Trim_Adj_R_squared']:.2f} (越小越好)

### ✅ 選擇的重要變數
{self._format_selected_variables(J_Trim_names, coefficients)}

---

### 💡 結果解讀

{interpretation}

---

### 📖 方法說明

**OGA-HDIC** 是一種適用於高維度數據（變數數 >> 樣本數）的變數選擇方法。

**演算法步驟**：
1. **正交貪婪演算法 (OGA)**: 逐步選擇與殘差相關性最高的變數
2. **HDIC 準則**: 使用高維度資訊準則確定最佳變數數量
3. **Trimming**: 移除統計上不顯著的變數（p-value > 0.05）

**適用情境**：
- 基因體學研究（幾萬個基因 vs 幾百個樣本）
- 高維度經濟計量模型
- 文本分類（大量特徵詞）
- 任何 p >> n 的預測問題
"""

        # 保存詳細結果到 JSON
        detailed_results = {
            "metrics": metrics,
            "selected_variables_HDIC": J_HDIC_names,
            "selected_variables_Trim": J_Trim_names,
            "coefficients": coefficients,
            "model_summary": {
                "HDIC_model": {
                    "R_squared": float(fit_HDIC.rsquared),
                    "Adj_R_squared": float(fit_HDIC.rsquared_adj),
                    "AIC": float(fit_HDIC.aic) if hasattr(fit_HDIC, 'aic') else None,
                    "BIC": float(fit_HDIC.bic) if hasattr(fit_HDIC, 'bic') else None
                },
                "Trim_model": {
                    "R_squared": float(fit_Trim.rsquared),
                    "Adj_R_squared": float(fit_Trim.rsquared_adj),
                    "AIC": float(fit_Trim.aic) if hasattr(fit_Trim, 'aic') else None,
                    "BIC": float(fit_Trim.bic) if hasattr(fit_Trim, 'bic') else None
                }
            }
        }

        results_json_path = os.path.join(out_dir, "results.json")
        with open(results_json_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)

        return {
            "metrics": metrics,
            "figures": figures,
            "summary_md": summary_md,
            "coefficients": coefficients,
            "selected_variables": J_Trim_names
        }
