# 開發者指南

**適用對象**: 貢獻統計方法的工程師

---

## 🎯 快速開始

### 你需要準備的資料

1. **方法程式碼** (`method.py`) - 實作統計方法
2. **說明文件** (`description.md`) - 方法的完整說明
3. **領域標記** - 選擇 1-3 個統計領域（參考下方領域表）

### 工作流程

```
研究方法 → 實作程式碼 → 撰寫文件 → 選擇領域 → 提交給 Claude 整合 → 測試上線
```

預估時間：每個方法約 4-8 小時

---

## 📚 可用的統計領域

查看完整定義：[`backend/knowledge_base/domains.json`](backend/knowledge_base/domains.json)

| 領域 ID | 中文名稱 | 適用情況 |
|---------|---------|---------|
| `high_dimensional` | 高維度統計 | 變數數 >> 樣本數 (p > 0.3n) |
| `time_series` | 時間序列分析 | 數據有時間順序 |
| `spatial_statistics` | 空間統計 | 數據有地理位置 |
| `causal_inference` | 因果推論 | 評估處置/政策效果 |
| `classification` | 分類問題 | 預測離散類別 |
| `regression` | 迴歸分析 | 預測連續數值 |
| `survival_analysis` | 存活分析 | 時間至事件數據 |
| `bayesian` | 貝氏統計 | 使用貝氏框架 |
| `machine_learning` | 機器學習 | 強調預測準確性 |
| `multivariate` | 多變量分析 | 多個結果變數 |

---

## 💻 程式碼範本

### method.py 基本結構

```python
"""
方法名稱與簡短描述
"""

from ..base import BaseMethod, register
import pandas as pd
import numpy as np

@register  # ⚠️ 必須加上這個裝飾器
class YourMethodName(BaseMethod):
    id = "your_method_id"  # 唯一ID，小寫+底線
    name = "Your Method Name"  # 英文名稱
    requires = {"y": "continuous"}  # 或 "binary", "any"

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str) -> dict:
        """
        執行統計方法

        Args:
            df: 輸入數據
            roles: 變數角色 {"y": "outcome", ...}
            params: 方法參數
            out_dir: 輸出目錄

        Returns:
            {
                "metrics": {"r_squared": 0.85, ...},
                "figures": {"plot": "path/to/plot.png"},
                "summary": "文字摘要"
            }
        """
        # 1. 取得變數
        y = df[roles["y"]].values
        X = df[[c for c in df.columns if c != roles["y"]]].values

        # 2. 執行演算法
        # ... 你的實作 ...

        # 3. 生成圖表（選填）
        import matplotlib.pyplot as plt
        import os

        fig, ax = plt.subplots()
        # ... 繪圖 ...
        fig_path = os.path.join(out_dir, "plot.png")
        fig.savefig(fig_path)
        plt.close()

        # 4. 返回結果
        return {
            "metrics": {"metric_name": value},
            "figures": {"plot_name": fig_path},
            "summary": "結果摘要"
        }
```

### 注意事項

✅ **必做**：
- 繼承 `BaseMethod`
- 加上 `@register` 裝飾器
- 返回正確格式的結果字典

❌ **避免**：
- 使用絕對路徑
- 假設特定欄位名稱（應由 roles 決定）
- 忘記關閉 matplotlib 圖表

---

## 📝 說明文件範本

建立 `description.md`：

```markdown
# {方法名稱}

## 簡介
簡短說明這個方法（100-200字）

## 適用情境
- 情境 1
- 情境 2

## 方法假設
1. 假設 1
2. 假設 2

## 結果解讀
- **指標 1**: 說明與解讀方式
- **指標 2**: 說明與解讀方式

## 注意事項
- 注意事項 1
- 注意事項 2

## 參考文獻
1. 作者 (年份). 論文標題. 期刊.
```

---

## 🏷️ 領域標記

為方法選擇 1-3 個領域，並決定重要性：

| Relevance | 權重 | 說明 |
|-----------|------|------|
| **primary** | 1.0 | 方法的核心領域 |
| **secondary** | 0.5-0.8 | 也適用的領域 |
| **applicable** | 0.3-0.5 | 某些情況可用 |

**範例**：Random Forest

```json
{
  "domains": [
    {
      "domain_id": "machine_learning",
      "relevance": "primary",
      "weight": 1.0,
      "reason": "核心的機器學習集成方法"
    },
    {
      "domain_id": "classification",
      "relevance": "secondary",
      "weight": 0.7,
      "reason": "可用於分類問題"
    }
  ]
}
```

---

## 🚀 提交給 Claude 整合

準備好以下資料後：

```
我要新增統計方法到 Model_Bridge，請協助整合。

【方法資訊】
- 方法ID: your_method_id
- 方法名稱: Your Method / 你的方法
- 領域標記:
{
  "domains": [
    {"domain_id": "xxx", "relevance": "primary", "weight": 1.0, "reason": "..."}
  ]
}

【程式碼】
<貼上 method.py>

【說明文件】
<貼上 description.md>

請協助：
1. 生成 metadata.json
2. 建立資料夾結構
3. 驗證程式碼
4. 註冊方法
```

Claude 會自動完成整合！

---

## 🧪 測試

### 1. 單元測試

```bash
cd backend
python tests/test_domain_recommendation.py
```

### 2. API 測試

啟動後端：
```bash
cd backend
python -m uvicorn main:app --reload
```

測試推薦：
```bash
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d '{"question": "你的測試問題"}'
```

---

## ❓ 常見問題

**Q: 需要額外的 Python 套件怎麼辦？**
A: 將套件加入 `requirements.txt`

**Q: 不確定該標記哪些領域？**
A:
1. 查看 `backend/knowledge_base/domains.json`
2. 參考已有方法（logistic_regression, oga_hdic, dr_ate_cbps）
3. 詢問 Claude

**Q: 測試時出現 "method not registered" 錯誤？**
A: 檢查是否加上 `@register` 裝飾器並重啟後端

---

## 📞 需要協助？

- 💬 **技術問題**：詢問 Claude 或團隊技術負責人
- 📖 **領域知識**：參考 `domains.json` 和已有方法的 metadata
- 🐛 **Bug 回報**：記錄錯誤訊息並提供給團隊

---

## ✅ 完成檢查表

- [ ] 方法程式碼完成並可執行
- [ ] 說明文件清楚完整
- [ ] 領域標記合理
- [ ] 已提交給 Claude 並生成 metadata.json
- [ ] 單元測試通過
- [ ] API 可以正確推薦此方法

---

**文件版本**: v1.1 (精簡版)
**最後更新**: 2025-01-19
