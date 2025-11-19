# 客戶流失預測範例

## 範例說明

這個範例展示如何使用邏輯迴歸預測電信公司的客戶流失情況。

### 業務背景

你是一家電信公司的數據分析師，公司面臨客戶流失率過高的問題。管理層希望你建立一個預測模型來：
1. 識別高風險客戶
2. 了解影響客戶流失的關鍵因素
3. 提供挽留策略建議

### 數據說明

**樣本量**: 200 位客戶

**變數說明**:
- `customer_id`: 客戶編號（不用於分析）
- `age`: 客戶年齡（歲）
- `tenure_months`: 合約月數（客戶使用服務的時間長度）
- `monthly_charges`: 月費用（美元）
- `total_charges`: 總費用（美元）
- `num_products`: 使用產品數量（1-4）
- `has_premium`: 是否為高級會員（0=否, 1=是）
- `satisfaction_score`: 滿意度評分（1-10，10 為最滿意）
- **`churned`**: 是否流失（0=留存, 1=流失）【目標變數】

### 預期發現

通過這個範例，你將發現：

1. **滿意度評分**是流失的最強預測因子
   - 滿意度越高，流失風險顯著降低
   - 勝算比 (OR) 約為 0.4，表示滿意度每增加 1 分，流失勝算降為 40%

2. **合約月數**與流失呈負相關
   - 新客戶（合約 < 6 個月）流失風險最高
   - 老客戶（> 24 個月）相對穩定

3. **高級會員**具有保護效果
   - 高級會員的流失率顯著低於一般會員
   - OR 約為 0.3，流失勝算僅為一般會員的 30%

4. **月費用**與流失的關係
   - 費用越高，流失傾向略增
   - 但效果不如滿意度顯著

5. **使用多項產品**的客戶較不易流失
   - 產品數量增加代表更高的黏著度

### 學習目標

完成這個範例後，你將學會：

1. ✅ 理解邏輯迴歸的基本概念與應用場景
2. ✅ 學會解讀迴歸係數與勝算比 (Odds Ratio)
3. ✅ 掌握模型評估指標（準確率、AUC、混淆矩陣）
4. ✅ 了解如何選擇適當的決策閾值
5. ✅ 將統計結果轉化為業務建議

### 業務應用建議

基於分析結果，你可以向管理層提出：

**立即行動**:
1. 對滿意度 ≤ 5 的客戶立即進行關懷
2. 針對新客戶（< 6 個月）加強關係維護
3. 推廣高級會員方案以降低流失

**中期策略**:
1. 改善服務品質以提升滿意度
2. 推出產品組合優惠增加黏著度
3. 建立客戶流失早期預警系統

**長期目標**:
1. 定期更新模型以反映市場變化
2. 結合其他數據源（客服互動、競爭對手）
3. 進行隨機實驗驗證挽留策略效果

### 進階練習

嘗試以下延伸分析：

1. **特徵工程**:
   - 創建交互作用項：`tenure_months × satisfaction_score`
   - 探索非線性關係：`tenure_months^2`

2. **模型比較**:
   - 與決策樹、隨機森林比較
   - 評估各模型的優缺點

3. **成本效益分析**:
   - 考慮挽留成本與客戶終身價值
   - 優化決策閾值以最大化利潤

4. **類別不平衡處理**:
   - 若流失率很低（如 5%），嘗試 SMOTE
   - 調整類別權重

### 如何執行

**方法 1: 在平台上執行**
1. 點擊「執行此範例」按鈕
2. 等待分析完成（約 10-30 秒）
3. 查看自動生成的報告

**方法 2: 使用自己的數據**
1. 下載 `data.csv` 作為模板
2. 替換為你的客戶數據（保持相同格式）
3. 在主頁面上傳並執行

**方法 3: 手動執行（進階）**
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score

# 載入數據
df = pd.read_csv('data.csv')

# 準備變數
X = df[['age', 'tenure_months', 'monthly_charges', 'total_charges',
        'num_products', 'has_premium', 'satisfaction_score']]
y = df['churned']

# 分割訓練/測試集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 訓練模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 評估
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
print(f"AUC: {roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]):.3f}")
```

### 相關資源

- [邏輯迴歸詳細說明](../../description.md)
- [邏輯迴歸教學指南](../../tutorial.md)
- [其他範例](../)

---

**難度**: 初級
**預估時間**: 5-10 分鐘
**標籤**: 商業分析, 分類, 客戶分析
