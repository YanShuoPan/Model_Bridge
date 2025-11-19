# 統計方法諮詢助手

一個 AI 驅動的統計方法諮詢平台，透過對話式介面協助研究者和數據分析師找到適合的統計方法。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## 🌟 核心功能

### 1. 多領域智能推薦 ⭐ NEW
- **GPT 領域識別**：自動分析問題涉及的統計領域（高維度、時間序列、因果推論等 10 個領域）
- **智能匹配**：基於領域匹配度計算，推薦最適合的統計方法
- **詳細說明**：每個推薦都包含匹配原因、適用情境、假設條件、注意事項

### 2. 智能對話式諮詢
- 以聊天方式描述你的研究問題
- AI 自動理解問題類型並提供適當回答
- 支援統計方法推薦、結果解釋、操作指導等多種問題類型

### 3. 內建統計方法
- **Logistic Regression（邏輯迴歸）**: 二元分類問題
- **Doubly Robust ATE（雙重穩健因果效應）**: 政策評估與因果推論
- **OGA-HDIC（高維度變數選擇）**: 基因體學與大數據分析

### 4. 擴展性設計
- 工程師可透過標準化流程貢獻新方法
- 自動整合到推薦系統
- 完整的領域標記與 metadata 管理

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Node.js 18+
- OpenAI API Key

### 本地開發環境

#### 1) 後端設定 (FastAPI)

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

# 設定環境變數
# 在 backend/ 目錄下建立 .env 檔案
echo "OPENAI_API_KEY=your-api-key-here" > backend/.env

# 啟動後端服務
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 測試: http://localhost:8000/api/health
```

#### 2) 前端設定 (Next.js)

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
Model_Bridge/
├── backend/                        # FastAPI 後端
│   ├── main.py                    # 主應用
│   ├── .env                       # 環境變數 (需自行建立)
│   ├── methods/                   # 統計方法實作
│   │   ├── base.py               # BaseMethod 基礎類別
│   │   ├── logistic_regression.py
│   │   └── dr_ate_cbps.py
│   ├── routers/                   # API 路由
│   │   ├── chat.py               # 聊天介面 API
│   │   ├── parse.py              # 解析 CSV 與問題
│   │   ├── recommend.py          # 推薦統計方法
│   │   └── run.py                # 執行分析
│   ├── services/                  # 核心服務
│   │   ├── ai_service.py         # GPT API 整合
│   │   ├── chat_service.py       # 對話邏輯與方法知識庫
│   │   ├── parser.py             # 問題與數據解析
│   │   ├── recommender.py        # 方法推薦邏輯
│   │   ├── runner.py             # 方法執行引擎
│   │   └── reports.py            # 報告生成
│   └── storage/                   # 數據存儲
│       ├── uploads/              # 上傳的 CSV
│       ├── runs/                 # 執行結果
│       └── demo/                 # 示範數據
│
├── frontend/                      # Next.js 前端
│   ├── app/
│   │   ├── page.tsx              # 聊天介面主頁面
│   │   └── layout.tsx
│   └── lib/
│       └── api.ts                # API 客戶端
│
├── ARCHITECTURE_DESIGN.md         # 架構設計文檔
├── DEPLOYMENT_GUIDE.md            # 部署指南
├── requirements.txt               # Python 依賴
└── README.md                      # 本文件
```

## 🎓 使用範例

### 範例問題

**方法推薦類：**
- "我想預測客戶是否會流失，應該用什麼方法？"
- "如何估計政策介入的因果效應？"
- "我有二元結果變數，適合用什麼分析方法？"

**方法解釋類：**
- "什麼是邏輯迴歸？"
- "Doubly Robust Estimator 的原理是什麼？"
- "什麼情況下適合使用 logistic regression？"

**操作指導類：**
- "如何解釋邏輯迴歸的結果？"
- "ATE 的信賴區間怎麼看？"
- "如何檢查模型的假設是否滿足？"

### 系統回應模式

系統會根據問題類型自動選擇適當的回應模式：

1. **方法推薦模式**：提供問題分析、推薦方法、範例資料、後續步驟
2. **直接回答模式**：針對解釋類、操作類問題提供簡潔明確的回答

## 🌐 部署

### 環境變數設定

**後端 (backend/.env):**
```
OPENAI_API_KEY=sk-proj-xxxxx
```

**前端 (.env.local):**
```
NEXT_PUBLIC_API=https://your-backend-url.onrender.com/api
```

### 後端部署 (Render)

1. 前往 [Render](https://render.com) 註冊/登入
2. 點擊「New +」→「Web Service」
3. 連接 GitHub 倉庫
4. 設定：
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. 環境變數：
   - Key: `OPENAI_API_KEY`
   - Value: 你的 OpenAI API key
6. 點擊「Create Web Service」

### 前端部署 (Vercel)

1. 前往 [Vercel](https://vercel.com) 註冊/登入
2. 點擊「Add New」→「Project」
3. Import GitHub 倉庫
4. 設定：
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. 環境變數：
   - Key: `NEXT_PUBLIC_API`
   - Value: 你的 Render 後端 URL + `/api`
6. 點擊「Deploy」

詳細部署步驟請參考 **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**

## 🛠️ 技術棧

### 後端
- **框架**: FastAPI
- **語言**: Python 3.8+
- **AI**: OpenAI GPT-4o-mini
- **統計/ML**: NumPy, Pandas, Scikit-learn, SciPy
- **視覺化**: Matplotlib
- **部署**: Render

### 前端
- **框架**: Next.js 14
- **語言**: TypeScript
- **UI**: React 18
- **部署**: Vercel

## 📊 內建統計方法

目前支援兩種統計方法：

### 1. Logistic Regression（邏輯迴歸）
- **適用情境**: 二元分類問題
- **輸出**: 係數、勝算比、ROC 曲線、混淆矩陣
- **範例資料**: binary_demo.csv

### 2. Doubly Robust ATE (DR-ATE)
- **適用情境**: 因果效應估計
- **輸出**: ATE 估計、信賴區間、平衡診斷
- **範例資料**: causal_demo.csv

## 📚 文件導航

| 文件 | 說明 | 適用對象 |
|------|------|---------|
| [README.md](README.md) | 專案總覽與快速開始 | 所有人 |
| [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) | 貢獻統計方法指南 | 方法工程師 |
| [TESTING.md](TESTING.md) | 測試指南與 API 範例 | 開發者 |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | 部署到 Render/Vercel | DevOps |
| [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) | 系統架構詳細說明 | 架構師 |

## 🤝 貢獻

### 貢獻統計方法
1. 閱讀 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
2. 準備方法程式碼與說明文件
3. 選擇統計領域標記
4. 提交給 Claude 或團隊進行整合

### 貢獻程式碼
1. Fork 此倉庫
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權

本專案採用 MIT 授權條款

## 📧 聯絡方式

- **問題回報**: [GitHub Issues](https://github.com/YanShuoPan/Model_Bridge/issues)
- **功能建議**: [GitHub Discussions](https://github.com/YanShuoPan/Model_Bridge/discussions)

---

如果這個專案對你有幫助，歡迎給我們一個 ⭐ Star！
