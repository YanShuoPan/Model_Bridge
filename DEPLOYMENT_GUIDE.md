# 🚀 部署指南

這份指南將幫助你將專案部署到線上。

---

## 📋 前置準備

### 1. GitHub 帳號
- 前往 https://github.com 註冊（如果還沒有的話）
- 登入你的 GitHub 帳號

### 2. Render 帳號（後端部署）
- 前往 https://render.com 註冊
- 建議使用 GitHub 帳號登入

### 3. Vercel 帳號（前端部署）
- 前往 https://vercel.com 註冊
- 建議使用 GitHub 帳號登入

---

## 步驟 1️⃣：推送到 GitHub

### 1.1 在 GitHub 創建新倉庫

1. 前往 https://github.com/new
2. 填寫倉庫資訊：
   - **Repository name**: `Model_Bridge` （或你喜歡的名字）
   - **Description**: AI 驅動的統計方法諮詢系統
   - **Public** 或 **Private**（選擇公開或私有）
   - ⚠️ **不要** 勾選 "Add a README file"
3. 點擊 **Create repository**

### 1.2 推送本地代碼到 GitHub

在專案目錄下執行以下命令（將 `YourUsername` 替換成你的 GitHub 用戶名）：

```bash
# 添加遠端倉庫
git remote add origin https://github.com/YourUsername/Model_Bridge.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

**範例**：
```bash
git remote add origin https://github.com/YanShuoPan/Model_Bridge.git
git branch -M main
git push -u origin main
```

如果需要輸入帳號密碼，輸入你的 GitHub 用戶名和 Personal Access Token（不是密碼）。

> **如何獲取 Personal Access Token？**
> 1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
> 2. Generate new token (classic)
> 3. 勾選 `repo` 權限
> 4. 複製生成的 token（只會顯示一次！）

---

## 步驟 2️⃣：部署後端到 Render

### 2.1 創建 Web Service

1. 登入 Render: https://dashboard.render.com
2. 點擊 **New +** → **Web Service**
3. 連接 GitHub 倉庫：
   - 點擊 **Connect account** 授權 GitHub
   - 找到並選擇 `Model_Bridge` 倉庫
   - 點擊 **Connect**

### 2.2 配置 Web Service

填寫以下資訊：

| 欄位 | 值 |
|------|-----|
| **Name** | `model-bridge-backend` （或你喜歡的名字） |
| **Region** | `Singapore` （或離你最近的區域） |
| **Branch** | `main` |
| **Root Directory** | *留空* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### 2.3 設定環境變數

在 **Environment** 區塊點擊 **Add Environment Variable**，添加：

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `你的 OpenAI API Key` |

⚠️ **重要**：這裡要用**新的** API key（記得撤銷之前暴露的那個）

### 2.4 部署

1. 點擊 **Create Web Service**
2. 等待部署完成（約 3-5 分鐘）
3. 部署成功後，你會看到一個 URL，例如：
   ```
   https://model-bridge-backend.onrender.com
   ```
4. 測試後端：訪問 `https://your-backend-url.onrender.com/api/health`
   - 應該會看到 `{"ok":true}`

---

## 步驟 3️⃣：部署前端到 Vercel

### 3.1 導入專案

1. 登入 Vercel: https://vercel.com/dashboard
2. 點擊 **Add New...** → **Project**
3. 點擊 **Import Git Repository**
4. 找到並選擇 `Model_Bridge` 倉庫
5. 點擊 **Import**

### 3.2 配置專案

| 欄位 | 值 |
|------|-----|
| **Framework Preset** | `Next.js` （應該會自動偵測） |
| **Root Directory** | `frontend` ⚠️ 重要！ |
| **Build Command** | `npm run build` （預設值） |
| **Output Directory** | `.next` （預設值） |
| **Install Command** | `npm install` （預設值） |

### 3.3 設定環境變數

在 **Environment Variables** 區塊添加：

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API` | `https://your-backend-url.onrender.com/api` |

⚠️ **重要**：將 `your-backend-url` 替換成你在步驟 2 獲得的 Render URL

**範例**：
```
NEXT_PUBLIC_API=https://model-bridge-backend.onrender.com/api
```

### 3.4 部署

1. 點擊 **Deploy**
2. 等待部署完成（約 2-3 分鐘）
3. 部署成功後，你會獲得一個 URL，例如：
   ```
   https://model-bridge.vercel.app
   ```

---

## 步驟 4️⃣：測試部署

### 測試後端

訪問後端健康檢查：
```
https://your-backend-url.onrender.com/api/health
```

應該看到：
```json
{"ok":true}
```

### 測試前端

1. 訪問你的前端 URL（例如 `https://model-bridge.vercel.app`）
2. 應該會看到統計諮詢助手的對話介面
3. 試著問一個問題，例如：「我想預測客戶流失」
4. 系統應該會推薦 Logistic Regression 並展示範例資料

---

## 🎉 完成！

你的專案現在已經部署到線上了！

### 你的網址

- **前端**: https://your-frontend.vercel.app
- **後端**: https://your-backend.onrender.com
- **API 文檔**: https://your-backend.onrender.com/docs

### 📝 分享給其他人

現在你可以分享前端 URL 給其他人使用！

---

## ⚙️ 更新部署

### 當你修改代碼後

1. **提交修改**：
   ```bash
   git add .
   git commit -m "你的修改說明"
   git push
   ```

2. **自動部署**：
   - Render 和 Vercel 都會自動偵測 GitHub 更新
   - 每次 push 到 main 分支都會自動重新部署
   - 無需手動操作！

---

## 🔧 常見問題

### Q: 後端部署失敗，顯示 "Build failed"

A: 檢查以下幾點：
1. 確認 `requirements.txt` 文件存在
2. 確認 Python 版本正確（應該是 3.10+）
3. 查看 Render 的 Logs 找出錯誤原因

### Q: 前端無法連接後端

A: 檢查：
1. `NEXT_PUBLIC_API` 環境變數是否設定正確
2. 後端 URL 是否包含 `/api` 結尾
3. 後端是否正常運行（訪問 `/api/health`）

### Q: Render Free Plan 會休眠

A:
- Render 的免費方案在 15 分鐘無流量後會休眠
- 下次訪問時需要 30-60 秒喚醒
- 如果需要保持運行，可以升級到付費方案

### Q: 如何更新環境變數？

A:
- **Render**: Dashboard → 選擇你的服務 → Environment → 修改變數 → Save Changes
- **Vercel**: Dashboard → 選擇你的專案 → Settings → Environment Variables → 修改變數 → Save → Redeploy

---

## 📞 需要幫助？

如果部署遇到問題：
1. 查看 Render/Vercel 的 Logs
2. 檢查環境變數是否設定正確
3. 確認 GitHub 代碼已經推送成功
4. 參考官方文檔：
   - [Render Docs](https://render.com/docs)
   - [Vercel Docs](https://vercel.com/docs)
