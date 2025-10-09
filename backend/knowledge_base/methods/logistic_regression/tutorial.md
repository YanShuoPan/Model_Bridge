# 邏輯迴歸教學指南

## 快速開始

### 5 分鐘快速體驗

1. **選擇範例**: 從右側選擇「客戶流失預測」範例
2. **執行分析**: 點擊「執行此方法」按鈕
3. **查看結果**: 瀏覽自動生成的分析報告
4. **理解輸出**: 參考下方的「結果解讀指南」

### 使用自己的數據

1. **準備數據**:
   - CSV 格式
   - 包含一個二元結果變數 (0/1)
   - 至少一個預測變數（數值或類別）

2. **上傳並設定**:
   - 在首頁上傳 CSV
   - 描述你的研究問題（如「預測客戶是否會流失」）
   - 系統會自動推薦邏輯迴歸

3. **執行並解讀**:
   - 點擊執行
   - 查看係數、勝算比、模型指標
   - 閱讀自動生成的報告

---

## 詳細教學

### 步驟 1: 理解你的問題

在開始分析前，先明確：

**✅ 適合使用邏輯迴歸：**
- 你想預測某事是否會發生（二元結果）
- 你想了解各因素的影響大小
- 你需要模型具有可解釋性

**❌ 不適合使用邏輯迴歸：**
- 結果有 3 類以上 → 考慮多項邏輯迴歸或其他方法
- 關係高度非線性 → 考慮決策樹、隨機森林
- 數據有複雜時間結構 → 考慮時間序列模型

### 步驟 2: 準備數據

#### 數據檢查清單

```markdown
□ 結果變數是 0/1（或可轉換為 0/1）
□ 沒有過多缺失值（<5% 為佳）
□ 預測變數與結果有合理的因果或關聯邏輯
□ 樣本量足夠（經驗法則：每個預測變數至少 10-15 個「事件」）
□ 類別變數已適當編碼
```

#### 數據格式範例

```csv
customer_id,age,tenure_months,monthly_charges,churned
1001,25,3,65.5,1
1002,45,24,89.0,0
1003,32,12,55.0,0
...
```

**關鍵點**:
- 結果變數 `churned`: 0 = 未流失, 1 = 流失
- 每行代表一個客戶（觀測單位）
- 數值變數已是數字格式
- 類別變數需要編碼（如性別: 男=0, 女=1）

### 步驟 3: 執行分析

#### 在平台上執行

1. 上傳 CSV 檔案
2. 輸入問題描述（如「我想預測客戶是否會流失」）
3. 系統自動:
   - 識別結果變數
   - 推薦邏輯迴歸
   - 準備數據（編碼、分割訓練/測試集）
4. 點擊「執行此方法」

#### 使用 Python 手動執行（進階）

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

# 載入數據
df = pd.read_csv('customer_data.csv')

# 準備特徵與目標
X = df[['age', 'tenure_months', 'monthly_charges', 'satisfaction_score']]
y = df['churned']

# 分割數據
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# 訓練模型
model = LogisticRegression()
model.fit(X_train, y_train)

# 預測
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

# 評估
print(f"準確率: {accuracy_score(y_test, y_pred):.3f}")
print(f"AUC: {roc_auc_score(y_test, y_pred_proba):.3f}")
print("\n分類報告:")
print(classification_report(y_test, y_pred))

# 查看係數
coef_df = pd.DataFrame({
    'feature': X.columns,
    'coefficient': model.coef_[0],
    'odds_ratio': np.exp(model.coef_[0])
})
print("\n係數與勝算比:")
print(coef_df.sort_values('odds_ratio', ascending=False))
```

### 步驟 4: 解讀結果

#### 4.1 理解係數

**範例輸出**:
```
變數              係數    勝算比 (OR)   p-value
satisfaction     -0.95    0.39         <0.001 ***
tenure_months    -0.08    0.92         0.002 **
has_premium      -1.20    0.30         <0.001 ***
monthly_charges   0.02    1.02         0.156
```

**解讀**:
- **satisfaction (滿意度)**:
  - 係數 = -0.95（負值）→ 滿意度越高,流失越少
  - OR = 0.39 → 滿意度每增加 1 分,流失勝算降為 39%
  - p < 0.001 → 高度顯著

- **tenure_months (合約月數)**:
  - OR = 0.92 → 每多一個月,流失勝算降為 92%（減少 8%）
  - 顯著（p = 0.002）

- **has_premium (高級會員)**:
  - OR = 0.30 → 高級會員流失勝算僅為一般會員的 30%
  - 強烈保護效果

- **monthly_charges (月費用)**:
  - OR = 1.02 → 每增加 1 美元,流失勝算增加 2%
  - 不顯著（p = 0.156）→ 可能不是重要因素

#### 4.2 評估模型表現

**混淆矩陣範例**:
```
                預測: 不流失  預測: 流失
實際: 不流失         120         15
實際: 流失            20         45
```

**指標計算**:
- **準確率** = (120 + 45) / 200 = 0.825 (82.5%)
- **精確率** = 45 / (15 + 45) = 0.75 (75%)
  → 在預測會流失的客戶中,75% 真的流失了
- **召回率** = 45 / (20 + 45) = 0.69 (69%)
  → 在所有真正流失的客戶中,我們正確識別了 69%

**ROC AUC = 0.88**
→ 模型具有良好的區分能力

#### 4.3 業務應用

**風險分層**:
```
預測機率     風險等級    行動建議
0.8 - 1.0    極高風險    立即聯繫，提供最優惠方案
0.6 - 0.8    高風險      主動關懷，優惠提醒
0.4 - 0.6    中風險      監控，定期溝通
0.0 - 0.4    低風險      一般維護
```

**決策閾值調整**:
- 預設閾值 0.5: 平衡精確率與召回率
- 降低至 0.3: 寧可錯殺,不漏掉高風險客戶（提高召回率）
- 提高至 0.7: 只針對最有把握的高風險客戶（提高精確率）

選擇依據:
- 挽留成本低 → 降低閾值（廣撒網）
- 挽留成本高 → 提高閾值（精準出擊）

### 步驟 5: 模型診斷

#### 檢查多元共線性

使用 VIF (Variance Inflation Factor):
```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

vif_data = pd.DataFrame()
vif_data["feature"] = X.columns
vif_data["VIF"] = [variance_inflation_factor(X.values, i)
                   for i in range(len(X.columns))]
```

**解讀**:
- VIF < 5: 無問題
- VIF 5-10: 中度共線性,考慮處理
- VIF > 10: 嚴重共線性,必須處理（移除變數或主成分分析）

#### 檢查影響點

Cook's Distance 識別過度影響模型的觀測值：
```python
from statsmodels.stats.outliers_influence import OLSInfluence

# 需要使用 statsmodels 的 Logit
import statsmodels.api as sm
X_with_const = sm.add_constant(X_train)
logit_model = sm.Logit(y_train, X_with_const).fit()

influence = logit_model.get_influence()
cooks_d = influence.cooks_distance[0]

# 標記影響點 (Cook's D > 4/n)
threshold = 4 / len(X_train)
influential = cooks_d > threshold
```

**處理方式**:
- 檢查是否為數據錯誤
- 考慮移除或調整權重
- 報告對這些點的敏感性

### 步驟 6: 改進模型

#### 6.1 添加交互作用項

```python
# 假設：年輕客戶對滿意度更敏感
df['age_satisfaction'] = df['age'] * df['satisfaction_score']

# 重新訓練模型
X_new = df[['age', 'satisfaction_score', 'age_satisfaction', ...]]
```

#### 6.2 非線性轉換

```python
# 對數轉換（處理右偏分佈）
df['log_total_charges'] = np.log1p(df['total_charges'])

# 多項式項
df['tenure_squared'] = df['tenure_months'] ** 2
```

#### 6.3 使用正規化

```python
from sklearn.linear_model import LogisticRegressionCV

# 自動選擇最佳正規化強度
model_cv = LogisticRegressionCV(cv=5, penalty='l1', solver='saga')
model_cv.fit(X_train, y_train)
```

#### 6.4 處理類別不平衡

```python
# 方法 1: 調整類別權重
model = LogisticRegression(class_weight='balanced')

# 方法 2: SMOTE 過採樣
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
```

### 步驟 7: 報告結果

#### 報告架構建議

1. **研究問題**
   - 背景與動機
   - 具體問題陳述

2. **數據描述**
   - 樣本量、變數定義
   - 描述性統計
   - 數據處理步驟

3. **方法**
   - 為何選擇邏輯迴歸
   - 模型設定（變數選擇、參數）
   - 驗證策略（訓練/測試分割）

4. **結果**
   - 係數表（含勝算比、信賴區間、p 值）
   - 模型診斷（VIF、影響點）
   - 模型評估（準確率、AUC、混淆矩陣、ROC 曲線）

5. **討論**
   - 主要發現的解釋
   - 實務意義
   - 限制與注意事項
   - 未來方向

6. **建議**
   - 基於結果的具體行動建議
   - 決策支持工具（風險評分卡）

#### 視覺化建議

必備圖表:
- ✅ ROC 曲線
- ✅ 係數森林圖（顯示信賴區間）
- ✅ 混淆矩陣熱圖
- ✅ 預測機率分佈（分組比較）

進階圖表:
- 部分效應圖（Partial Effect Plots）
- 校準曲線（Calibration Plot）
- 決策曲線分析（Decision Curve Analysis）

---

## 常見問題 (FAQ)

### Q1: 我的結果變數是「高/中/低」三類，能用邏輯迴歸嗎？

**A**: 標準邏輯迴歸僅適用二元結果。你可以：
1. 合併類別為二元（如「高」vs「中或低」）
2. 使用多項邏輯迴歸（Multinomial Logistic Regression）
3. 如果是有序類別，使用有序邏輯迴歸（Ordinal Logistic Regression）

### Q2: 我的模型準確率很高（95%+）但 AUC 很低，為什麼？

**A**: 可能是類別嚴重不平衡。例如：
- 若 98% 樣本為「不流失」，模型只要全部預測「不流失」就有 98% 準確率
- 但它完全無法識別流失客戶，所以 AUC 接近 0.5（隨機）
- **解決方法**: 關注 AUC、F1、精確率/召回率，或使用類別平衡技術

### Q3: 某個變數的係數不顯著，應該移除嗎？

**A**: 不一定。考慮：
1. **理論重要性**: 若理論上重要，可保留
2. **控制變數**: 即使不顯著，作為控制變數仍有價值
3. **樣本量**: 可能是檢定力不足
4. **模型比較**: 用 AIC/BIC 比較有/無該變數的模型

### Q4: 如何處理缺失值？

**A**: 依情況選擇：
1. **完全刪除** (Listwise deletion): 若缺失<5% 且為隨機缺失
2. **填補 (Imputation)**:
   - 均值/中位數（數值變數）
   - 眾數（類別變數）
   - 模型預測（如 KNN、MICE）
3. **指示變數法**: 創建「是否缺失」的虛擬變數

### Q5: 我的數據有 100 個變數但只有 200 個樣本，怎麼辦？

**A**: 這是「高維度問題」，容易過度配適：
1. **變數選擇**:
   - 基於理論或先驗知識篩選
   - 單變量篩選（保留與結果顯著相關的）
2. **降維**:
   - 主成分分析（PCA）
   - 因素分析
3. **正規化**:
   - Lasso (自動變數選擇)
   - Ridge
   - Elastic Net
4. **收集更多數據**

### Q6: 如何選擇最佳的決策閾值？

**A**: 依業務目標：
1. **平衡精確率/召回率**: F1 分數最大化的閾值
2. **最大化商業價值**:
   ```
   利潤 = (TP × 挽留成功收益) - (FP × 挽留成本) - (FN × 流失損失)
   ```
   找出利潤最大的閾值
3. **使用 ROC 曲線**: Youden's Index (靈敏度 + 特異度 - 1) 最大化
4. **決策曲線分析**: 在不同閾值下比較淨效益

### Q7: 我的 ROC AUC 只有 0.65,模型是不是很差？

**A**: 不一定,需考慮：
1. **基準線**: 比隨機（0.5）好就有價值
2. **問題難度**: 有些問題本質上難以預測（如股市）
3. **業務價值**: 即使 0.65,若能帶來實際效益就有用
4. **改進空間**: 嘗試特徵工程、其他模型、收集更多數據

---

## 實戰技巧

### 技巧 1: 快速診斷模型合理性

在深入分析前,先檢查：
```python
# 係數符號是否符合直覺？
# 例如：滿意度應該降低流失（負係數）
print(model.coef_)

# 預測機率範圍是否合理？
# 應該分佈在 0-1,且有變異
print(y_pred_proba.describe())

# 訓練集與測試集表現差異
# 差異過大表示過度配適
print(f"訓練集 AUC: {roc_auc_score(y_train, model.predict_proba(X_train)[:, 1])}")
print(f"測試集 AUC: {roc_auc_score(y_test, y_pred_proba)}")
```

### 技巧 2: 建立可部署的風險評分卡

```python
# 將係數轉為評分（方便業務使用）
def create_scorecard(model, feature_names, base_score=600, pdo=20):
    """
    創建風險評分卡
    base_score: 基礎分數
    pdo: Points to Double the Odds (勝算翻倍所需分數)
    """
    factor = pdo / np.log(2)
    offset = base_score - (factor * np.log(base_odds))

    scorecard = {}
    for i, feature in enumerate(feature_names):
        scorecard[feature] = -factor * model.coef_[0][i]

    return scorecard, offset

# 使用評分卡
def calculate_score(customer_data, scorecard, offset):
    score = offset
    for feature, coefficient in scorecard.items():
        score += coefficient * customer_data[feature]
    return score
```

### 技巧 3: 解釋預測給非技術人員

```python
# 對單一預測的解釋
def explain_prediction(model, X, feature_names, sample_idx):
    """解釋為何模型做出此預測"""
    sample = X.iloc[sample_idx]
    contributions = model.coef_[0] * sample.values

    explanation = pd.DataFrame({
        'feature': feature_names,
        'value': sample.values,
        'contribution': contributions,
        'direction': ['增加流失' if c > 0 else '減少流失' for c in contributions]
    })

    explanation['abs_contribution'] = abs(explanation['contribution'])
    explanation = explanation.sort_values('abs_contribution', ascending=False)

    return explanation

# 使用
exp = explain_prediction(model, X_test, X.columns, sample_idx=0)
print(f"預測機率: {y_pred_proba[0]:.2%}")
print("\n主要因素:")
print(exp.head())
```

### 技巧 4: 監控模型性能

部署後定期檢查：
```python
# 每月評估
def monitor_model_performance(model, X_new, y_new, month):
    """監控模型在新數據上的表現"""
    y_pred = model.predict(X_new)
    y_pred_proba = model.predict_proba(X_new)[:, 1]

    metrics = {
        'month': month,
        'n_samples': len(y_new),
        'churn_rate': y_new.mean(),
        'accuracy': accuracy_score(y_new, y_pred),
        'auc': roc_auc_score(y_new, y_pred_proba),
        'brier_score': brier_score_loss(y_new, y_pred_proba)
    }

    return metrics

# 若性能顯著下降，考慮重新訓練
```

---

## 延伸學習路徑

### 初學者路徑
1. ✅ 完成「客戶流失預測」範例
2. 使用自己的簡單數據集練習
3. 學習解讀係數與勝算比
4. 理解混淆矩陣與 ROC 曲線
5. 嘗試調整決策閾值

### 進階路徑
1. 實作交互作用項與非線性轉換
2. 使用 statsmodels 獲得詳細統計摘要
3. 學習正規化邏輯迴歸 (Lasso, Ridge)
4. 處理類別不平衡問題
5. 建立可部署的評分卡系統

### 專家路徑
1. 貝氏邏輯迴歸
2. 多項與有序邏輯迴歸
3. 混合效應邏輯迴歸（處理分層數據）
4. 穩健邏輯迴歸（處理離群值）
5. 因果推論中的邏輯迴歸（傾向分數）

---

**準備好開始了嗎？**

👉 [執行「客戶流失預測」範例](./examples/customer_churn)

👉 [查看完整方法說明](./description.md)

👉 [返回方法列表](../../README.md)
