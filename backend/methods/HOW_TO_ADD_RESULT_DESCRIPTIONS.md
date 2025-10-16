# 如何為統計方法新增結果描述

本文件說明在不同位置新增結果描述的方法，以 OGA-HDIC 為例。

---

## 📍 結果描述的三個層級

### 1️⃣ 方法內部的結果摘要 (Method-level)

**位置**: `backend/methods/oga_hdic/method.py` 的 `run()` 方法

**用途**: 顯示在執行結果的報告中，提供詳細的結果解讀

**示範**:

```python
def run(self, df, roles, params, out_dir):
    # ... 執行分析 ...

    # 生成摘要報告
    summary_md = f"""
## OGA-HDIC 變數選擇結果

### 📊 資料概況
- **樣本數**: {n}
- **總變數數**: {p}
- **維度比 (p/n)**: {p/n:.2f}

### 🎯 變數選擇結果
- **HDIC 選擇的變數數**: {len(J_HDIC_names)}
- **Trimming 後保留**: {len(J_Trim_names)}
- **變數篩選率**: {篩選率}%

### 📈 模型表現
- **R²**: {r_squared:.4f}
- **調整 R²**: {adj_r_squared:.4f}

### 💡 結果解讀
{自動生成的解讀內容}

### 📖 方法說明
{方法的詳細說明}
"""

    return {
        "summary_md": summary_md,
        # ... 其他返回值
    }
```

**✅ 已實作**: OGA-HDIC 現在包含：
- `_interpret_results()` - 自動解讀結果
- `_format_selected_variables()` - 格式化變數清單
- 詳細的摘要報告

---

### 2️⃣ GPT 推薦時的方法說明 (Service-level)

**位置**: `backend/services/chat_service.py`

**用途**: GPT 在推薦方法時會讀取這些資訊，並向用戶解釋

**示範**:

```python
AVAILABLE_METHODS = {
    "oga_hdic": {
        "name": "OGA-HDIC（高維度變數選擇與迴歸）",

        # 方法描述（會被 GPT 讀取）
        "description": "適用於變數數量遠大於樣本數的高維度預測問題，使用正交貪婪演算法選擇重要變數並建立迴歸模型",

        # 適用情境
        "suitable_for": [
            "高維度預測（p >> n）",
            "變數篩選",
            "基因體學分析",
            "特徵選擇"
        ],

        # 假設條件
        "assumptions": [
            "真實模型是稀疏的（只有少數變數真正重要）",
            "樣本間相互獨立",
            "線性關係假設（可透過變數轉換放寬）"
        ],

        # 輸出結果（告訴用戶會得到什麼）
        "outputs": [
            "選擇的重要變數列表",
            "迴歸係數與顯著性檢定",
            "HDIC 曲線圖（顯示變數選擇過程）",
            "變數係數圖（展示影響方向與大小）",
            "預測表現評估（R²、調整 R²）"
        ],

        # 範例數據資訊
        "example_data": {
            "name": "高維度示範數據",
            "description": "100 筆樣本，50 個變數，只有前 5 個真正重要",
            "file": "highdim_demo.csv",
            # ... 更多資訊
        }
    }
}
```

**要修改的位置**: `backend/services/chat_service.py:124-144`

---

### 3️⃣ 規則推薦時的說明 (Recommender-level)

**位置**: `backend/services/recommender.py`

**用途**: 當系統自動偵測到適合的數據類型時，提供推薦理由

**示範**:

```python
def recommend_methods(task, y_type, roles, question, df_info, use_gpt):
    recs = []

    # 高維度變數選擇 (OGA-HDIC)
    if y_type == "continuous" and roles.get("y") and df_info:
        n_samples = df_info.get("n_rows", 0)
        n_features = df_info.get("n_cols", 0) - 1

        if n_features > n_samples * 0.3:  # 高維度判定
            recs.append({
                "method_id": "oga_hdic",
                "name": "OGA-HDIC (高維度變數選擇)",

                # 推薦理由（動態生成）
                "why": f"偵測到高維度問題（{n_features} 個變數 vs {n_samples} 筆樣本），"
                       f"適合使用變數選擇方法進行特徵篩選。",

                "assumptions": [...],
                "inputs_required": [...]
            })

    return recs
```

**要修改的位置**: `backend/services/recommender.py:30-42`

---

## 🎯 最佳實踐建議

### ✅ DO - 應該做的

1. **在 `method.py` 中加入詳細解讀**
   - 新增 `_interpret_results()` 方法來自動解讀結果
   - 根據指標數值給出具體建議
   - 說明結果的實務意義

2. **使用清楚的層次結構**
   - 用 Markdown 標題組織內容
   - 用 emoji 增加可讀性（📊 📈 💡 等）
   - 分段說明不同面向

3. **提供可操作的建議**
   - "下一步該做什麼"
   - "什麼情況需要注意"
   - "如何改進模型"

4. **客製化內容**
   - 根據實際結果動態生成描述
   - 針對不同情境給予不同解讀

### ❌ DON'T - 避免做的

1. **不要寫死的文字**
   ```python
   # ❌ 不好
   summary = "R² 很高，模型很好"

   # ✅ 好
   if r_squared > 0.8:
       summary = f"R² = {r_squared:.3f}，模型預測表現優秀"
   ```

2. **不要只列數字**
   ```python
   # ❌ 不好
   summary = f"R² = {r_squared}"

   # ✅ 好
   summary = f"R² = {r_squared:.3f}，表示模型能解釋 {r_squared*100:.1f}% 的變異"
   ```

3. **不要忽略統計意義**
   - 加入顯著性標記 (*, **, ***)
   - 說明 p-value 的意義
   - 提醒注意事項

---

## 📋 完整範例：新增方法時的檢查清單

當你新增一個統計方法時，確保以下三個位置都有適當的描述：

- [ ] **方法檔案** (`backend/methods/your_method/method.py`)
  - [ ] `run()` 方法返回詳細的 `summary_md`
  - [ ] 新增 `_interpret_results()` 自動解讀方法（可選但推薦）
  - [ ] 說明如何理解輸出結果
  - [ ] 提供下一步建議

- [ ] **Chat Service** (`backend/services/chat_service.py`)
  - [ ] 在 `AVAILABLE_METHODS` 新增方法資訊
  - [ ] 填寫 `description`, `suitable_for`, `assumptions`, `outputs`
  - [ ] 如果有範例數據，加入 `example_data`

- [ ] **Recommender** (`backend/services/recommender.py`)
  - [ ] 新增推薦規則（如何判斷適用）
  - [ ] 填寫推薦理由 `why`
  - [ ] 說明需要的資料類型

---

## 🔍 OGA-HDIC 完整實作參考

OGA-HDIC 現在包含完整的結果描述系統：

### 自動解讀功能

```python
def _interpret_results(self, metrics, selected_vars, n, p):
    """根據結果自動生成解讀"""

    # 1. 評估維度情境（高維度 vs 中度高維度）
    # 2. 評估稀疏性（高度稀疏 vs 中度稀疏 vs 低稀疏）
    # 3. 評估模型表現（優秀 vs 良好 vs 中等 vs 較弱）
    # 4. 提供具體建議

    return interpretation_text
```

### 變數格式化

```python
def _format_selected_variables(self, selected_vars, coefficients):
    """美化變數清單，加入係數和顯著性"""

    # 格式: **變數名** ↑正向/↓負向 (係數: xxx ***)
    # 按重要性排序
    # 超過 10 個只顯示前 10 個

    return formatted_list
```

### 完整摘要

包含：
- 📊 資料概況
- 🎯 變數選擇結果
- 📈 模型表現
- ✅ 選擇的重要變數（帶係數和顯著性）
- 💡 結果解讀（自動生成）
- 📖 方法說明

---

## 💡 總結

**簡單回答你的問題**：

> 如果我想在自己新增的方法上增加結果的描述，應該加在哪邊？

**主要位置**: `backend/methods/oga_hdic/method.py` 的 `run()` 方法中

**具體做法**:
1. 修改 `summary_md` 變數（第 148-192 行）
2. 新增輔助方法如 `_interpret_results()` 來自動生成解讀
3. 確保 `return` 的 `summary_md` 包含完整說明

**次要位置**（讓 GPT 能推薦你的方法）:
- `backend/services/chat_service.py` - GPT 推薦說明
- `backend/services/recommender.py` - 自動推薦規則

現在 OGA-HDIC 已經實作了完整的結果描述系統，你可以參考它的程式碼作為範本！
