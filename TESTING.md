# 測試指南

快速測試新的多領域推薦系統

---

## 🚀 啟動服務

```bash
cd backend
python -m uvicorn main:app --reload
```

---

## 🧪 單元測試

```bash
cd backend
python tests/test_domain_recommendation.py
```

**預期輸出**：`✅ 通過: 6/6`

---

## 🔍 API 測試

### 健康檢查

```bash
curl http://localhost:8000/api/health
```

### 測試 1：高維度問題

```bash
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"我有 500 個基因但只有 100 個樣本，想找出重要基因\", \"df_info\": {\"n_rows\": 100, \"n_cols\": 501}}"
```

**預期**：推薦 `oga_hdic`（高維度變數選擇）

### 測試 2：因果推論

```bash
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"評估教育政策對學生成績的因果效應\", \"df_info\": {\"n_rows\": 500, \"n_cols\": 10}}"
```

**預期**：推薦 `dr_ate_cbps`（因果推論）

### 測試 3：分類問題

```bash
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"預測客戶是否會流失\", \"df_info\": {\"n_rows\": 1000, \"n_cols\": 15}}"
```

**預期**：推薦 `logistic_regression`（分類）

---

## ✅ 驗證清單

- [ ] 單元測試全部通過
- [ ] 健康檢查成功
- [ ] 高維度問題推薦正確
- [ ] 因果推論問題推薦正確
- [ ] 分類問題推薦正確
- [ ] 回應包含所有必要欄位

---

## 📊 回應格式

```json
{
  "question_domains": {
    "high_dimensional": {"score": 0.9, "name": "高維度統計"}
  },
  "recommended_methods": [
    {
      "method_id": "oga_hdic",
      "name": "OGA-HDIC",
      "match_score": 0.9,
      "matched_domains": [...]
    }
  ],
  "reasoning": "GPT 分析理由",
  "primary_domain": "high_dimensional",
  "total_methods_evaluated": 3,
  "total_matched": 1
}
```

---

## 🐛 除錯

### 檢查日誌

後端應輸出：
```
成功載入領域配置：10 個領域
[GPT] 識別到 2 個相關領域
[推薦] 評估了 3 個方法，匹配到 2 個
```

### 檢查 API Key

```bash
# Windows
echo %OPENAI_API_KEY%

# Linux/Mac
echo $OPENAI_API_KEY
```

### 檢查 metadata

```bash
cat backend/knowledge_base/methods/logistic_regression/metadata.json | grep -A 5 "domains"
```

應看到 `domains` 欄位存在且格式正確。

---

**預期回應時間**：2-6 秒（主要是 GPT API）
