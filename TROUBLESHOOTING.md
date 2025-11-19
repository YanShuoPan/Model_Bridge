# 故障排除指南

## 問題 1: 推薦系統只返回一個方法

### 原因分析

推薦系統會返回**所有匹配到的方法**（最多 `top_n` 個，預設 5 個）。如果只返回一個方法，可能的原因：

#### 1.1 GPT 只識別到一個領域
- **情況**: GPT 分析問題後，只識別到一個統計領域
- **結果**: 如果只有一個方法標記了該領域，就只會推薦一個方法
- **檢查方式**: 查看 API 返回的 `question_domains` 欄位
  ```json
  {
    "question_domains": {
      "classification": {"score": 1.0, "name": "分類問題"}
    }
  }
  ```

#### 1.2 問題描述不夠詳細
- **情況**: 使用者問題太簡短或模糊
- **範例**: "幫我分析數據" → GPT 難以識別具體領域
- **解決**: 提供更詳細的問題描述

#### 1.3 方法庫太小
- **情況**: 目前只有 3 個方法 (logistic_regression, oga_hdic, dr_ate_cbps)
- **影響**: 某些領域可能沒有方法或只有一個方法
- **解決**: 增加更多方法到系統中

### 解決方案

#### 方案 1: 提供更詳細的問題描述（推薦）
```bash
# ❌ 不好的問題
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d '{"question": "分析數據"}'

# ✅ 好的問題
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d '{
    "question": "我想預測客戶流失(二元分類)，同時也想了解哪些特徵最重要(變數選擇)，數據有1000筆樣本和50個特徵",
    "df_info": {"n_rows": 1000, "n_cols": 51}
  }'
```

#### 方案 2: 調整 GPT prompt 使其識別更多領域

修改 [backend/services/ai_service.py](backend/services/ai_service.py:208-241)，在 prompt 中加入：
```python
注意：
1. 只返回分數 > 0 的領域
2. 一個問題可能涉及多個領域  # <-- 強調這點
3. 盡量識別 2-3 個相關領域    # <-- 新增
4. 根據問題特性判斷，不要勉強配對
```

#### 方案 3: 增加更多方法（長期）
- 讓工程師使用 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 貢獻更多方法
- 確保每個領域都有至少 2-3 個方法

---

## 問題 2: [Request interrupted by user] 錯誤

### 原因分析

這個錯誤通常由以下原因造成：

#### 2.1 GPT API 呼叫超時
- **原因**: 網路不穩定或 OpenAI API 回應緩慢
- **位置**: [backend/services/ai_service.py:243](backend/services/ai_service.py#L243)
- **目前設定**: 30 秒超時

#### 2.2 缺少 OPENAI_API_KEY
- **症狀**: 錯誤訊息提到 "api_key client option must be set"
- **檢查**: 確認環境變數是否設定
  ```bash
  # Windows
  echo %OPENAI_API_KEY%

  # Linux/Mac
  echo $OPENAI_API_KEY
  ```

#### 2.3 API Key 無效或額度不足
- **檢查**: 登入 OpenAI 平台查看 API 使用狀況
- **解決**: 更新 API Key 或充值額度

### 解決方案

#### 方案 1: 檢查環境變數
```bash
# Windows
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key-here
```

或在 `backend/.env` 檔案中設定：
```env
OPENAI_API_KEY=sk-your-api-key-here
```

#### 方案 2: 增加超時時間

修改 [backend/services/ai_service.py:251](backend/services/ai_service.py#L251):
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...],
    temperature=0.1,
    response_format={"type": "json_object"},
    timeout=60.0  # 從 30 秒增加到 60 秒
)
```

#### 方案 3: 添加重試機制

```python
import time

def identify_question_domains(question: str, df_info: dict = None, max_retries: int = 3) -> dict:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(...)
            # 成功則返回
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"GPT 呼叫失敗 (嘗試 {attempt + 1}/{max_retries}): {e}")
                time.sleep(2)  # 等待 2 秒後重試
                continue
            else:
                # 最後一次嘗試失敗
                raise
```

---

## 問題 3: 查看後端日誌

### 重要的日誌訊息

啟動後端時，查看以下關鍵訊息：

```
成功載入領域配置：10 個領域                    # 領域載入成功
成功載入 3/3 個方法 metadata                    # 方法載入成功
[API] 收到推薦請求: question='...', top_n=5    # API 收到請求
[GPT] 識別到 2 個相關領域                       # GPT 識別結果
[推薦] 識別到 2 個領域: ['high_dimensional', 'regression']
[推薦] 評估了 3 個方法，匹配到 2 個，返回前 2 個  # 匹配結果
[API] 推薦成功: 返回 2 個方法                   # API 成功返回
```

### 如果出現錯誤

```
[API] 推薦失敗: ...       # 查看錯誤詳情
GPT 領域識別失敗: ...    # GPT 呼叫失敗
```

---

## 問題 4: 驗證推薦結果

### 檢查返回的 JSON

完整的 API 返回應包含以下欄位：

```json
{
  "question_domains": {
    "high_dimensional": {
      "score": 0.9,
      "name": "高維度統計",
      "name_en": "High-Dimensional Statistics"
    },
    "regression": {
      "score": 0.7,
      "name": "迴歸分析",
      "name_en": "Regression"
    }
  },
  "recommended_methods": [
    {
      "method_id": "oga_hdic",
      "name": "OGA-HDIC",
      "name_zh": "正交貪婪演算法與高維度資訊準則",
      "match_score": 1.73,
      "matched_domains": [
        {
          "domain_id": "high_dimensional",
          "domain_name": "高維度統計",
          "question_score": 0.9,
          "method_weight": 1.0,
          "contribution": 0.9,
          "relevance": "primary"
        },
        {
          "domain_id": "regression",
          "domain_name": "迴歸分析",
          "question_score": 0.7,
          "method_weight": 0.9,
          "contribution": 0.63,
          "relevance": "primary"
        }
      ]
    }
  ],
  "reasoning": "GPT 分析理由...",
  "primary_domain": "high_dimensional",
  "total_methods_evaluated": 3,
  "total_matched": 2
}
```

### 關鍵指標

1. **question_domains 數量**: 應該有 1-3 個領域
2. **recommended_methods 數量**: 應該有多個方法（如果可用）
3. **match_score**: 匹配分數 = Σ(question_score × method_weight)
4. **total_matched**: 匹配到的方法總數

---

## 診斷工具

### 1. 本地測試腳本（不需 API Key）

使用 `test_recommendation_mock.py` 測試匹配邏輯：
```bash
python test_recommendation_mock.py
```

### 2. API 測試

```bash
# 健康檢查
curl http://localhost:8000/api/health

# 測試推薦（詳細問題）
curl -X POST http://localhost:8000/api/recommend/by-domains \
  -H "Content-Type: application/json" \
  -d '{
    "question": "我有高維度數據(500個基因，100個樣本)想做變數選擇，同時也想建立預測模型",
    "df_info": {"n_rows": 100, "n_cols": 501},
    "top_n": 5
  }'
```

### 3. 單元測試

```bash
cd backend
python tests/test_domain_recommendation.py
```

---

## 常見問題 FAQ

**Q: 為什麼只推薦一個方法？**
A: 查看 `question_domains`，可能 GPT 只識別到一個領域。提供更詳細的問題描述。

**Q: [Request interrupted by user] 怎麼辦？**
A: 檢查 OPENAI_API_KEY 是否設定，網路是否穩定。

**Q: 如何增加推薦的方法數量？**
A:
1. 提供更詳細的問題（讓 GPT 識別更多領域）
2. 增加更多統計方法到系統
3. 調整 `top_n` 參數（但這只影響返回數量，不影響匹配數量）

**Q: 推薦的方法不符合預期？**
A: 查看 `matched_domains` 欄位，了解匹配理由。可能需要：
1. 調整方法的 metadata 中的領域標記
2. 修改 GPT prompt 的評分標準

---

**文件版本**: v1.0
**最後更新**: 2025-01-19
