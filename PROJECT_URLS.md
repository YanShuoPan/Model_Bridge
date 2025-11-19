# 專案網址紀錄

本文件記錄 Model_Bridge 專案的所有重要網址，方便查詢與維護。

---

## 📦 GitHub 倉庫

**倉庫 URL**: `[請填寫 GitHub 倉庫 URL]`

例如：`https://github.com/YanShuoPan/Model_Bridge`

---

## 🌐 前端部署 (Vercel)

**部署 URL**: `[請填寫 Vercel 前端 URL]`

例如：`https://model-bridge.vercel.app`

**Vercel 專案管理**:
- Dashboard: `https://vercel.com/[your-username]/[project-name]`
- 部署狀態: `https://vercel.com/[your-username]/[project-name]/deployments`

---

## 🔧 後端部署 (Render)

**後端 API URL**: `[請填寫 Render 後端 URL]`

例如：`https://modelbridge.onrender.com`

**API 端點**:
- Health Check: `[後端 URL]/api/health`
- Chat API: `[後端 URL]/api/chat`
- Methods API: `[後端 URL]/api/methods`

**Render 專案管理**:
- Dashboard: `https://dashboard.render.com/`
- Service URL: `https://dashboard.render.com/web/[your-service-id]`

---

## 🔑 重要配置

### 環境變數設定位置

**後端環境變數** (Render):
- `OPENAI_API_KEY`: 在 Render Dashboard → Environment 設定

**前端環境變數** (Vercel):
- `NEXT_PUBLIC_API`: 指向後端 API URL
- 設定位置: Vercel Dashboard → Settings → Environment Variables

---

## 📝 快速連結

### 開發相關
- [ ] GitHub Issues: `[GitHub URL]/issues`
- [ ] GitHub Actions: `[GitHub URL]/actions`
- [ ] Pull Requests: `[GitHub URL]/pulls`

### 部署監控
- [ ] Vercel Analytics: `https://vercel.com/[username]/[project]/analytics`
- [ ] Render Logs: Render Dashboard → Logs

### 文件
- [ ] API 文件: `[後端 URL]/docs` (FastAPI 自動生成)
- [ ] README: `[GitHub URL]/blob/main/README.md`
- [ ] 部署指南: `[GitHub URL]/blob/main/DEPLOYMENT_GUIDE.md`

---

## 🧪 測試用 API 端點

測試後端是否正常運行：

```bash
# Health Check
curl [後端 URL]/api/health

# 測試對話 API
curl -X POST [後端 URL]/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "什麼是邏輯迴歸？"}'
```

---

## 📅 最後更新

**更新日期**: 2025-10-13
**更新者**: [你的名字]
**當前版本**: v1.0

---

## 💡 使用說明

1. 請在部署完成後，將上方 `[請填寫...]` 的部分替換為實際的 URL
2. 定期檢查連結是否正常運作
3. 如有更新部署 URL，請同步更新此文件
4. 可將此文件加入 `.gitignore`（如果包含敏感資訊）
