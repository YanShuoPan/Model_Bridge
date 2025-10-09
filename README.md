# AI Agent 統計平台

一個 AI 驅動的統計方法推薦與執行平台，協助研究者和數據分析師快速找到並應用適合的統計方法。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## 🌟 核心功能

### 1. 智能問題解析與方法推薦
- 上傳數據並描述研究問題
- AI 自動解析問題類型與數據特徵
- 推薦適合的統計方法並說明理由

### 2. 統計方法知識庫
- 詳細的方法說明文檔（數學原理、假設、適用情境）
- 豐富的應用範例與教學
- 互動式範例執行與結果解釋

### 3. 一鍵執行與報告生成
- 自動執行統計分析
- 生成視覺化圖表
- 產出完整的 HTML 分析報告

## 🚀 快速開始

### 本地開發環境

#### 1) 後端 (FastAPI)

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動後端服務
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 測試: http://localhost:8000/api/health
```

#### 2) 前端 (Next.js)

```bash
cd frontend
npm install
npm run dev

# 開啟瀏覽器: http://localhost:3000
```

#### 3) 配置 API 端點

如果後端不在 `localhost:8000`，在 `frontend/.env.local` 設定：
```
NEXT_PUBLIC_API=http://your-backend-host/api
```

## 📦 專案結構

```
ai-agent-stat/
├── backend/                        # FastAPI 後端
│   ├── main.py                    # 主應用
│   ├── methods/                   # 統計方法實作
│   │   ├── base.py               # BaseMethod 基礎類別
│   │   ├── logistic_regression.py
│   │   └── dr_ate_cbps.py
│   ├── routers/                   # API 路由
│   │   ├── parse.py              # 解析 CSV 與問題
│   │   ├── recommend.py          # 推薦統計方法
│   │   └── run.py                # 執行分析
│   ├── services/                  # 核心服務
│   │   ├── parser.py             # 問題與數據解析
│   │   ├── recommender.py        # 方法推薦邏輯
│   │   ├── runner.py             # 方法執行引擎
│   │   └── reports.py            # 報告生成
│   ├── knowledge_base/            # 統計方法知識庫
│   │   └── methods/
│   │       └── logistic_regression/
│   │           ├── metadata.json
│   │           ├── description.md
│   │           ├── tutorial.md
│   │           └── examples/
│   └── storage/                   # 數據存儲
│       ├── uploads/              # 上傳的 CSV
│       ├── runs/                 # 執行結果
│       └── demo/                 # 示範數據
│
├── frontend/                      # Next.js 前端
│   ├── app/
│   │   ├── page.tsx              # 主頁面
│   │   └── layout.tsx
│   └── lib/
│       └── api.ts                # API 客戶端
│
├── ARCHITECTURE_DESIGN.md         # 架構設計文檔
├── CONTRIBUTION_GUIDE.md          # 貢獻指南
├── IMPLEMENTATION_ROADMAP.md      # 實施路線圖
├── requirements.txt               # Python 依賴
├── render.yaml                    # Render 部署配置
└── README.md                      # 本文件
```

## 🎓 使用範例

### 1. 二元分類問題（邏輯迴歸）

```
問題: "我想預測客戶是否會流失"
數據: customer_data.csv (包含 age, tenure, satisfaction, churned 欄位)

系統會:
1. 自動識別 churned 為二元結果變數
2. 推薦邏輯迴歸 (Logistic Regression)
3. 執行分析並產出:
   - 係數與勝算比
   - ROC 曲線與 AUC
   - 混淆矩陣
   - 完整的 HTML 報告
```

### 2. 因果效應估計（雙重穩健估計）

```
問題: "我想估計政策介入的平均因果效應 (ATE)"
數據: policy_data.csv (包含 treatment, outcome, covariates)

系統會:
1. 識別因果推論任務
2. 推薦 DR-ATE (Doubly Robust Estimator)
3. 執行分析並產出:
   - ATE 估計與信賴區間
   - 平衡診斷圖
   - 敏感性分析
   - 結果解釋
```

## 🌐 部署

### 後端部署 (Render)

**選項 A: 使用 Blueprint (推薦)**

1. 將此倉庫推送到 GitHub
2. 在 Render: **New +** → **Blueprint** → 選擇你的倉庫
3. Render 會自動讀取 `render.yaml` 並部署
4. 部署後訪問 `https://your-app.onrender.com/api/health` 確認

**選項 B: 手動建立 Web Service**

- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- 環境變數: `PORT=10000` (或由 Render 自動設定)

### 前端部署 (Vercel)

1. 在 Vercel 從 GitHub 匯入專案
2. Root Directory 設定為: `frontend`
3. 在 **Settings → Environment Variables** 添加:
   ```
   NEXT_PUBLIC_API=https://your-backend.onrender.com/api
   ```
4. 部署完成後網站會在 `https://your-frontend.vercel.app`

### 臨時公開 URL (開發測試用)

使用 ngrok 暴露本地後端：
```bash
ngrok http 8000
# 獲得 HTTPS URL: https://abcd-xxx.ngrok-free.app

# 然後在 frontend/.env.local 設定:
NEXT_PUBLIC_API=https://abcd-xxx.ngrok-free.app/api
```

## 📊 內建示範數據

在 `backend/storage/demo/` 目錄下提供兩個示範數據集：

### 1. binary_demo.csv
- **用途**: 二元分類問題
- **欄位**: `y` (0/1) + 特徵變數
- **適用方法**: Logistic Regression
- **範例問題**: "預測結果變數 y"

### 2. causal_demo.csv
- **用途**: 因果效應估計
- **欄位**: `treatment` (0/1), `y` (結果), `x1, x2...` (共變數)
- **適用方法**: DR-ATE (CBPS-like)
- **範例問題**: "我想估計處理的平均因果效應 (ATE)"

## 🛠️ 技術棧

### 後端
- **框架**: FastAPI
- **語言**: Python 3.8+
- **統計/ML**: NumPy, Pandas, Scikit-learn, SciPy, Statsmodels
- **視覺化**: Matplotlib
- **部署**: Render

### 前端
- **框架**: Next.js 14
- **語言**: TypeScript
- **UI**: React 18, 內聯樣式
- **部署**: Vercel

## 📚 文檔

- **[架構設計文檔](./ARCHITECTURE_DESIGN.md)**: 完整的平台擴展設計
- **[貢獻指南](./CONTRIBUTION_GUIDE.md)**: 研究者如何貢獻新方法
- **[實施路線圖](./IMPLEMENTATION_ROADMAP.md)**: 10 週開發計劃

## 🤝 貢獻

我們歡迎統計學家、數據科學家、開發者貢獻新的統計方法！

### 貢獻方式

1. **新增統計方法**: 實作新的分析方法並提供文檔
2. **創建範例**: 為現有方法提供應用範例
3. **改進文檔**: 完善方法說明、教學指南
4. **報告問題**: 提交 bug 或功能建議

詳見 **[貢獻指南](./CONTRIBUTION_GUIDE.md)**

### 開發流程

1. Fork 此倉庫
2. 創建功能分支 (`git checkout -b feature/AmazingMethod`)
3. 提交更改 (`git commit -m 'Add some AmazingMethod'`)
4. 推送到分支 (`git push origin feature/AmazingMethod`)
5. 開啟 Pull Request

## 📈 路線圖

### 當前狀態 (v0.1 - MVP)
- ✅ 基本問題解析與方法推薦
- ✅ 兩種統計方法 (Logistic Regression, DR-ATE)
- ✅ 一鍵執行與報告生成
- ✅ Vercel + Render 部署

### 近期計劃 (v0.2-0.5)
- 🔄 完整的統計方法知識庫
- 🔄 研究者貢獻系統
- 🔄 AI 推薦增強 (LLM 整合)
- 🔄 互動式範例與教學
- 🔄 使用者系統與歷史記錄

### 未來願景 (v1.0+)
- 📋 支援 20+ 統計方法
- 📋 多語言支援 (英文/中文/日文)
- 📋 整合 R、Stata 等工具
- 📋 線上課程與認證
- 📋 行動應用

詳見 **[實施路線圖](./IMPLEMENTATION_ROADMAP.md)**

## 🔧 開發指南

### 新增統計方法

所有統計方法必須繼承 `BaseMethod` 類別：

```python
from backend.methods.base import BaseMethod, register

@register
class YourMethod(BaseMethod):
    id = "your_method_id"
    name = "Your Method Name"
    requires = {"task": ["your_task"], "y_type": ["binary"]}

    def validate_input(self, df, roles):
        # 驗證輸入數據
        return True, ""

    def run(self, df, roles, params, out_dir):
        # 執行分析
        return {
            "metrics": {...},
            "figures": [...],
            "report_html_path": "..."
        }
```

完整範例請參考 `backend/methods/logistic_regression.py`

### 測試

```bash
# 運行後端測試
pytest backend/tests/

# 運行前端測試
cd frontend
npm test
```

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

感謝所有貢獻者讓這個平台更加完善！

特別感謝：
- 統計方法開發者
- 範例與文檔貢獻者
- 早期測試使用者
- 開源社群的支持

## 📧 聯絡方式

- **問題回報**: [GitHub Issues](https://github.com/YanShuoPan/Model_Bridge/issues)
- **功能建議**: [GitHub Discussions](https://github.com/YanShuoPan/Model_Bridge/discussions)
- **Email**: 你的聯絡信箱

---

**由 AI Agent 團隊用 ❤️ 打造**

如果這個專案對你有幫助，歡迎給我們一個 ⭐ Star！
