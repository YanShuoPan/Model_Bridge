# 研究者貢獻指南

歡迎貢獻統計方法到 AI Agent 統計平台！本指南將協助您準備和提交新的統計方法。

---

## 目錄

- [為什麼要貢獻？](#為什麼要貢獻)
- [貢獻類型](#貢獻類型)
- [準備貢獻包](#準備貢獻包)
- [提交流程](#提交流程)
- [審核標準](#審核標準)
- [範例模板](#範例模板)
- [技術規範](#技術規範)
- [常見問題](#常見問題)

---

## 為什麼要貢獻？

### 對學術社群的價值

- **知識共享**: 讓您的方法被更多研究者和實務工作者使用
- **學術影響力**: 貢獻將被引用，增加您的研究可見度
- **教育推廣**: 協助非專家理解和正確使用統計方法
- **開放科學**: 促進可重現研究和方法透明化

### 對貢獻者的好處

- 🏆 **署名**: 您的姓名、機構、ORCID 將顯示在方法頁面
- 📊 **使用統計**: 查看您的方法被使用的次數和領域
- 🔗 **引用追蹤**: 平台會追蹤引用您方法的分析
- 👥 **社群互動**: 與使用者互動，獲得反饋
- 📢 **宣傳**: 我們會在平台和社群媒體上推廣新方法

---

## 貢獻類型

### 1. 新統計方法
完整實作一個新的統計方法（如新的因果推論方法、機器學習模型等）

### 2. 現有方法的擴展
改進或擴展平台上已有的方法（如添加新功能、優化演算法）

### 3. 範例與教學
為現有方法提供新的應用範例或教學材料

### 4. 文檔改進
改善方法說明、修正錯誤、增加解釋

---

## 準備貢獻包

### 完整貢獻包結構

```
my_method_contribution/
├── manifest.json              # 貢獻清單（必填）
├── method/                    # 方法實作（必填）
│   ├── implementation.py      # Python 實作
│   ├── requirements.txt       # 依賴套件
│   └── tests.py              # 單元測試
├── documentation/             # 文檔（必填）
│   ├── metadata.json         # 方法元數據
│   ├── description.md        # 詳細說明
│   └── tutorial.md           # 教學指南（可選但建議）
└── examples/                  # 範例（至少一個）
    ├── example_1/
    │   ├── config.json       # 範例配置
    │   ├── data.csv          # 範例數據
    │   └── README.md         # 範例說明
    └── example_2/
        └── ...
```

### 各文件詳細說明

#### 1. manifest.json（貢獻清單）

```json
{
  "contribution_type": "new_method",
  "method_id": "your_method_id",
  "version": "1.0.0",
  "author": {
    "name": "Dr. Your Name",
    "email": "your.email@institution.edu",
    "institution": "Your University/Organization",
    "orcid": "0000-0000-0000-0000",
    "website": "https://yourwebsite.com"
  },
  "license": "MIT",
  "dependencies": {
    "python": ">=3.8",
    "packages": [
      "numpy>=1.20.0",
      "pandas>=1.3.0",
      "scipy>=1.7.0"
    ]
  },
  "submission_date": "2024-10-09",
  "checklist": {
    "implementation_complete": true,
    "tests_passing": true,
    "documentation_complete": true,
    "examples_provided": true,
    "license_approved": true
  },
  "additional_info": {
    "related_papers": [
      {
        "title": "Your Paper Title",
        "doi": "10.1234/your.doi",
        "year": 2024
      }
    ],
    "funding": "Grant XYZ from Funding Agency"
  }
}
```

#### 2. implementation.py（方法實作）

您的方法必須**繼承 `BaseMethod` 類別**：

```python
from backend.methods.base import BaseMethod, register
from typing import Dict, Any
import pandas as pd
import numpy as np

@register
class YourMethod(BaseMethod):
    """Your method brief description"""

    # 必填：方法 ID（唯一）
    id = "your_method_id"

    # 必填：方法名稱
    name = "Your Method Name"

    # 必填：方法需求
    requires = {
        "task": ["your_task_type"],  # e.g., "classification", "causal"
        "y_type": ["binary"],         # e.g., "binary", "continuous"
        "min_samples": 50
    }

    def validate_input(self, df: pd.DataFrame, roles: dict) -> tuple[bool, str]:
        """
        驗證輸入數據是否符合方法需求

        Args:
            df: 輸入數據框
            roles: 變數角色字典，如 {"y": "outcome", "X": ["x1", "x2"]}

        Returns:
            (is_valid, error_message)
        """
        # 檢查必要變數
        if "y" not in roles or roles["y"] not in df.columns:
            return False, "缺少結果變數 'y'"

        # 檢查樣本量
        if len(df) < self.requires["min_samples"]:
            return False, f"樣本量不足，至少需要 {self.requires['min_samples']} 筆"

        # 其他檢查...
        return True, ""

    def run(self, df: pd.DataFrame, roles: dict, params: dict, out_dir: str) -> Dict[str, Any]:
        """
        執行統計方法

        Args:
            df: 輸入數據框
            roles: 變數角色字典
            params: 方法參數
            out_dir: 輸出目錄（用於存圖表、報告）

        Returns:
            結果字典，必須包含：
            {
                "metrics": {...},           # 數值結果
                "figures": [...],           # 圖表路徑列表
                "report_html_path": "...",  # HTML 報告路徑
                "interpretation": {...}      # 結果解釋
            }
        """
        # 1. 數據準備
        y = df[roles["y"]]
        X = df[roles.get("X", [])]

        # 2. 執行分析
        # ... your implementation ...

        # 3. 生成結果
        metrics = {
            "metric_1": value_1,
            "metric_2": value_2,
            # ...
        }

        # 4. 生成圖表
        figures = []
        fig_path = f"{out_dir}/your_plot.png"
        # ... create and save plot ...
        figures.append(fig_path)

        # 5. 生成報告
        report_html = self._generate_report(metrics, figures)
        report_path = f"{out_dir}/report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_html)

        # 6. 返回結果
        return {
            "metrics": metrics,
            "figures": figures,
            "report_html_path": report_path,
            "interpretation": self.interpret_results(metrics)
        }

    def interpret_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """
        提供結果的解釋說明

        Args:
            results: run() 返回的結果字典

        Returns:
            解釋字典
        """
        interpretation = {
            "summary": "簡短摘要...",
            "key_findings": [
                "發現 1",
                "發現 2"
            ],
            "recommendations": [
                "建議 1",
                "建議 2"
            ]
        }
        return interpretation

    def _generate_report(self, metrics, figures):
        """生成 HTML 報告（內部輔助函數）"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{self.name} - Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .metric {{ margin: 10px 0; }}
                img {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>{self.name} 分析報告</h1>

            <h2>結果摘要</h2>
            <div class="metrics">
                {"".join([f'<div class="metric"><strong>{k}:</strong> {v}</div>'
                          for k, v in metrics.items()])}
            </div>

            <h2>視覺化結果</h2>
            {"".join([f'<img src="{fig}" />' for fig in figures])}
        </body>
        </html>
        """
        return html
```

#### 3. tests.py（單元測試）

```python
import unittest
import pandas as pd
import numpy as np
from .implementation import YourMethod

class TestYourMethod(unittest.TestCase):
    """測試 YourMethod"""

    def setUp(self):
        """準備測試數據"""
        np.random.seed(42)
        self.df = pd.DataFrame({
            "y": np.random.binomial(1, 0.3, 100),
            "x1": np.random.randn(100),
            "x2": np.random.randn(100)
        })
        self.roles = {"y": "y", "X": ["x1", "x2"]}
        self.method = YourMethod()

    def test_validate_input_success(self):
        """測試正確輸入的驗證"""
        is_valid, msg = self.method.validate_input(self.df, self.roles)
        self.assertTrue(is_valid)

    def test_validate_input_missing_y(self):
        """測試缺少 y 變數的情況"""
        roles_no_y = {"X": ["x1", "x2"]}
        is_valid, msg = self.method.validate_input(self.df, roles_no_y)
        self.assertFalse(is_valid)
        self.assertIn("y", msg.lower())

    def test_validate_input_insufficient_samples(self):
        """測試樣本量不足的情況"""
        small_df = self.df.head(10)  # 假設 min_samples > 10
        is_valid, msg = self.method.validate_input(small_df, self.roles)
        self.assertFalse(is_valid)

    def test_run_completes(self):
        """測試方法能成功執行"""
        result = self.method.run(
            self.df,
            self.roles,
            params={},
            out_dir="/tmp/test_output"
        )

        # 檢查必要的返回鍵
        self.assertIn("metrics", result)
        self.assertIn("figures", result)
        self.assertIn("report_html_path", result)

    def test_run_output_format(self):
        """測試輸出格式正確"""
        result = self.method.run(self.df, self.roles, {}, "/tmp/test_output")

        # metrics 應該是字典
        self.assertIsInstance(result["metrics"], dict)

        # figures 應該是列表
        self.assertIsInstance(result["figures"], list)

        # report_html_path 應該是字串
        self.assertIsInstance(result["report_html_path"], str)

    def test_deterministic_results(self):
        """測試結果的可重現性"""
        result1 = self.method.run(self.df, self.roles, {"random_state": 42}, "/tmp/test_output")
        result2 = self.method.run(self.df, self.roles, {"random_state": 42}, "/tmp/test_output")

        # 主要指標應該相同
        for key in result1["metrics"]:
            self.assertAlmostEqual(
                result1["metrics"][key],
                result2["metrics"][key],
                places=5
            )

if __name__ == "__main__":
    unittest.main()
```

#### 4. metadata.json（方法元數據）

詳見 [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md) 中的範例。

#### 5. description.md（詳細說明）

應包含以下章節：

```markdown
# 方法名稱

## 概述
簡要介紹方法的目的和用途

## 數學原理
詳細的數學公式和理論基礎

## 何時使用
適用情境、應用範例

## 假設與限制
方法的假設、限制、注意事項

## 結果解釋
如何解讀輸出結果

## 實作考量
數據準備、參數選擇、模型診斷

## 與其他方法比較
與相關方法的比較

## 最佳實踐
實務建議和檢查清單

## 參考文獻
相關論文、書籍、資源
```

#### 6. example config.json（範例配置）

```json
{
  "example_id": "example_name",
  "example_name": "Example Name",
  "example_name_zh": "範例名稱",
  "description": "範例簡介",
  "difficulty": "beginner",
  "estimated_time_minutes": 5,
  "data_source": "data.csv",
  "roles": {
    "y": "outcome_column",
    "X": ["predictor1", "predictor2"]
  },
  "parameters": {
    "param1": "value1"
  },
  "learning_objectives": [
    "學習目標 1",
    "學習目標 2"
  ],
  "expected_insights": [
    "預期發現 1",
    "預期發現 2"
  ]
}
```

---

## 提交流程

### 步驟 1: 準備貢獻包

1. 按照上述結構準備所有文件
2. 在本地測試確保一切正常
3. 運行單元測試：`python -m pytest method/tests.py`
4. 檢查文檔完整性

### 步驟 2: 提交到平台

#### 選項 A: 通過 Web 界面（推薦）

1. 登入平台
2. 前往「貢獻」頁面
3. 點擊「提交新方法」
4. 上傳貢獻包（ZIP 壓縮檔）
5. 填寫提交表單
6. 送出審核

#### 選項 B: 通過 GitHub Pull Request

1. Fork 平台倉庫
2. 在 `backend/knowledge_base/methods/` 下添加您的方法
3. 在 `backend/methods/` 下添加實作代碼
4. 提交 Pull Request
5. 在 PR 描述中填寫貢獻清單

### 步驟 3: 自動驗證

系統會自動執行：
- ✅ 結構完整性檢查
- ✅ 代碼語法檢查
- ✅ 單元測試
- ✅ 依賴安全掃描
- ✅ 文檔格式驗證

如有問題，您會收到詳細的錯誤報告。

### 步驟 4: 人工審核

審核人員會檢查：
- 方法的科學正確性
- 代碼品質與效率
- 文檔清晰度與完整性
- 範例的教學價值
- 與現有方法的整合性

審核通常需要 5-10 個工作天。

### 步驟 5: 修改與發布

- 若需要修改，審核人員會提供具體建議
- 修改後重新提交
- 通過審核後，方法將發布到平台
- 您會收到發布通知和方法頁面連結

---

## 審核標準

### 科學性 (40%)

- [ ] 方法理論基礎正確
- [ ] 數學公式無誤
- [ ] 假設明確陳述
- [ ] 引用適當的文獻
- [ ] 結果解釋科學準確

### 代碼品質 (30%)

- [ ] 遵循 PEP 8 風格指南
- [ ] 代碼註解清楚
- [ ] 錯誤處理完善
- [ ] 單元測試覆蓋率 > 80%
- [ ] 無安全漏洞
- [ ] 效能合理（不過度耗時）

### 文檔品質 (20%)

- [ ] 說明清晰易懂
- [ ] 適合目標受眾
- [ ] 範例具有教學價值
- [ ] 結果解釋詳盡
- [ ] 格式統一美觀

### 可用性 (10%)

- [ ] 易於整合到平台
- [ ] 依賴套件合理
- [ ] 輸出格式一致
- [ ] 使用者體驗良好

---

## 範例模板

我們提供完整的模板供您開始：

```bash
# 下載模板
git clone https://github.com/your-org/method-contribution-template.git

# 或使用我們的 CLI 工具
pip install ai-agent-stat-contrib
ai-agent-stat create-method --name "Your Method Name"
```

模板包含：
- 預先配置的文件結構
- 註解齊全的代碼範例
- 測試框架
- 文檔模板

---

## 技術規範

### Python 版本
- 最低: Python 3.8
- 推薦: Python 3.10+

### 必要依賴
平台已包含以下套件（無需在 requirements.txt 中列出）：
- numpy
- pandas
- scipy
- matplotlib
- scikit-learn

### 額外依賴
若需要其他套件：
- 必須在 requirements.txt 中明確指定版本
- 使用穩定的 PyPI 套件
- 避免使用未維護或有安全問題的套件

### 代碼風格
- 遵循 [PEP 8](https://pep8.org/)
- 使用類型提示（Type Hints）
- 函數必須有 docstring

### 測試要求
- 使用 unittest 或 pytest
- 測試覆蓋率 ≥ 80%
- 包含正常情況和邊界情況測試

### 輸出要求
- 圖表: PNG 格式，300 DPI
- 報告: HTML5，響應式設計
- 數值: 保留適當的有效位數

---

## 常見問題

### Q1: 我不是統計學家，可以貢獻嗎？

**A**: 可以！您可以：
- 貢獻範例和教學材料
- 改進現有方法的文檔
- 報告 bug 或提出改進建議
- 翻譯文檔

### Q2: 我的方法還在研究中（未發表），可以提交嗎？

**A**: 可以，但請在 metadata.json 中註明：
```json
"status": "experimental",
"publication_status": "unpublished"
```
我們會標示為「實驗性方法」。

### Q3: 可以貢獻非開源的方法嗎？

**A**: 平台僅接受開源貢獻（MIT, Apache 2.0, BSD, GPL 等授權）。這確保：
- 使用者可以自由使用
- 社群可以改進和擴展
- 符合開放科學原則

### Q4: 我的方法需要大量計算資源，如何處理？

**A**: 請在 metadata.json 中註明：
```json
"computational_requirements": {
  "memory_gb": 16,
  "estimated_runtime_minutes": 30,
  "gpu_required": false
}
```
平台會顯示警告並考慮排隊執行。

### Q5: 如何確保我的貢獻被正確引用？

**A**: 我們會：
1. 在方法頁面顯著顯示您的署名
2. 生成引用格式（BibTeX, APA, MLA）
3. 追蹤使用統計
4. 提供數位物件識別碼 (DOI)（如適用）

建議的引用格式：
```
您的姓名 (年份). 方法名稱 (Version X.X.X). AI Agent Statistics Platform.
https://platform-url/methods/your_method_id
```

### Q6: 我可以更新已貢獻的方法嗎？

**A**: 可以！請提交新版本：
1. 更新 `version` 欄位（遵循語意化版本）
2. 在 `CHANGELOG.md` 中記錄變更
3. 重新提交審核

我們會保留舊版本供向後相容。

### Q7: 貢獻後我有什麼權利和責任？

**權利**:
- 被列為方法作者
- 獲得使用統計和反饋
- 參與方法的維護和更新

**責任**:
- 回應使用者的問題（可選但建議）
- 修復嚴重 bug（我們會協助）
- 保持方法與平台的相容性

### Q8: 審核被拒絕怎麼辦？

**A**:
1. 仔細閱讀審核意見
2. 與審核人員討論疑問
3. 進行必要的修改
4. 重新提交
5. 若認為有誤，可申訴

大部分貢獻經過 1-2 輪修改後都會被接受。

---

## 支援與聯絡

### 獲得幫助

- **文檔**: [完整貢獻文檔](https://docs.platform.com/contribute)
- **範例**: [參考現有方法](./backend/knowledge_base/methods/)
- **討論區**: [GitHub Discussions](https://github.com/your-org/ai-agent-stat/discussions)
- **Email**: contribute@ai-agent-stat.com

### 貢獻者社群

加入我們的貢獻者社群：
- [Slack 頻道](https://ai-agent-stat.slack.com)
- [每月線上辦公室時間](https://calendar-link)
- [貢獻者郵件列表](mailto:contributors@ai-agent-stat.com)

---

## 致謝

感謝所有貢獻者讓這個平台更加豐富和有價值！

所有貢獻者將列於：
- [貢獻者名單](./CONTRIBUTORS.md)
- 平台首頁
- 年度報告

---

**準備好開始了嗎？**

1. 📥 [下載貢獻模板](https://github.com/your-org/method-contribution-template)
2. 📖 [閱讀技術文檔](./ARCHITECTURE_DESIGN.md)
3. 💬 [加入貢獻者社群](https://ai-agent-stat.slack.com)
4. 🚀 [提交您的第一個貢獻](#提交流程)

我們期待看到您的貢獻！
