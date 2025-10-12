# 範例結果預執行系統設計

## 🎯 目標

優化推薦系統的表達方式，在推薦方法時直接展示：
1. 範例資料的簡述
2. 執行方法的實際結果（圖表、指標）
3. 結果的專業解釋

**關鍵優化**：預先執行範例，減少 GPT token 消耗

---

## 📁 知識庫結構設計

```
backend/knowledge_base/
├── methods/
│   ├── logistic_regression/
│   │   ├── metadata.json              # 方法元數據
│   │   ├── description.md             # 方法說明
│   │   ├── tutorial.md                # 教學文檔
│   │   └── examples/
│   │       └── customer_churn/
│   │           ├── config.json        # 範例配置
│   │           ├── data.csv           # 範例數據
│   │           ├── pre_run_results/   # 【新增】預執行結果
│   │           │   ├── results.json   # 執行結果數據
│   │           │   ├── figures/       # 生成的圖表
│   │           │   │   ├── roc.png
│   │           │   │   └── confusion_matrix.png
│   │           │   └── interpretation_guide.md  # 結果解釋指南
│   │           └── README.md          # 範例說明
│   └── dr_ate_cbps/
│       └── examples/
│           └── policy_evaluation/
│               ├── config.json
│               ├── data.csv
│               └── pre_run_results/
│                   ├── results.json
│                   ├── figures/
│                   │   └── balance_plot.png
│                   └── interpretation_guide.md
```

---

## 📄 文件格式定義

### 1. `results.json` - 執行結果數據

```json
{
  "method_id": "logistic_regression",
  "example_id": "customer_churn",
  "executed_at": "2025-10-13T10:30:00Z",
  "execution_time_seconds": 2.3,
  "metrics": {
    "accuracy": 0.8542,
    "auc": 0.9123,
    "precision": 0.82,
    "recall": 0.78
  },
  "coefficients": {
    "age": {"value": 0.042, "odds_ratio": 1.043, "p_value": 0.001},
    "tenure": {"value": -0.088, "odds_ratio": 0.916, "p_value": 0.003},
    "monthly_charges": {"value": 0.025, "odds_ratio": 1.025, "p_value": 0.012}
  },
  "figures": [
    {
      "filename": "roc.png",
      "path": "backend/knowledge_base/methods/logistic_regression/examples/customer_churn/pre_run_results/figures/roc.png",
      "type": "roc_curve",
      "description": "ROC 曲線顯示模型區分能力"
    },
    {
      "filename": "confusion_matrix.png",
      "path": "backend/knowledge_base/methods/logistic_regression/examples/customer_churn/pre_run_results/figures/confusion_matrix.png",
      "type": "confusion_matrix",
      "description": "混淆矩陣展示預測準確度"
    }
  ],
  "summary": {
    "sample_size": 500,
    "variables_used": ["age", "tenure", "monthly_charges", "contract_type"],
    "outcome_variable": "churned",
    "model_performance": "良好，AUC = 0.91"
  }
}
```

### 2. `interpretation_guide.md` - 結果解釋指南

```markdown
# 客戶流失預測 - 結果解釋指南

## 執行概況
- **樣本數**：500 筆客戶資料
- **結果變數**：是否流失（0=留存, 1=流失）
- **預測變數**：年齡、合約期限、月費用、合約類型

## 關鍵發現

### 1. 模型整體表現
- **AUC = 0.91**：模型具有優秀的區分能力
- **準確率 = 85.4%**：整體預測準確度良好

### 2. 重要影響因素

**合約期限（tenure）**
- 係數 = -0.088，勝算比 = 0.916
- **解釋**：合約期限每增加 1 個月，流失機率下降約 8.4%
- **意義**：長期客戶更不容易流失

**月費用（monthly_charges）**
- 係數 = 0.025，勝算比 = 1.025
- **解釋**：月費用每增加 1 元，流失機率增加約 2.5%
- **意義**：高費用客戶更容易流失

**年齡（age）**
- 係數 = 0.042，勝算比 = 1.043
- **解釋**：年齡每增加 1 歲，流失機率增加約 4.3%
- **意義**：年長客戶略微容易流失

## 圖表解讀

### ROC 曲線
- AUC = 0.91 表示模型有 91% 的機率正確區分流失與留存客戶
- 曲線越接近左上角，模型越好

### 混淆矩陣
- 真陽性率（召回率）：78%
- 真陰性率：89%
- 模型對留存客戶的預測更準確

## 實務應用建議

1. **重點關注高月費客戶**：提供優惠或客製化方案
2. **強化新客戶體驗**：合約初期提供更多支援
3. **建立預警系統**：當客戶風險分數 > 0.7 時主動聯繫

## 假設檢驗

所有變數的 p-value < 0.05，表示影響均達統計顯著水平。
```

---

## 🔧 實作步驟

### Step 1: 創建預執行腳本

`backend/scripts/pre_run_examples.py`

```python
"""
預執行範例數據並儲存結果
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# 添加後端路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.methods.base import METHODS_REGISTRY
import pandas as pd


def pre_run_example(method_id: str, example_path: str):
    """
    預執行單個範例

    Args:
        method_id: 方法 ID
        example_path: 範例目錄路徑
    """
    example_dir = Path(example_path)

    # 1. 讀取配置
    config_path = example_dir / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 2. 讀取數據
    data_path = example_dir / config["data_source"]
    df = pd.read_csv(data_path)

    # 3. 創建輸出目錄
    output_dir = example_dir / "pre_run_results"
    output_dir.mkdir(exist_ok=True)
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    # 4. 執行方法
    method_cls = METHODS_REGISTRY[method_id]
    method = method_cls()

    print(f"執行 {method_id} - {config['example_name']}...")

    results = method.run(
        df=df,
        roles=config["roles"],
        params=config.get("parameters", {}),
        out_dir=str(figures_dir)
    )

    # 5. 儲存結果
    results_data = {
        "method_id": method_id,
        "example_id": example_dir.name,
        "executed_at": datetime.now().isoformat(),
        "execution_time_seconds": None,  # 可以添加計時
        "metrics": results.get("metrics", {}),
        "coefficients": results.get("coefficients", {}),
        "figures": [],
        "summary": {
            "sample_size": len(df),
            "variables_used": config["roles"].get("X", []),
            "outcome_variable": config["roles"].get("y"),
            "model_performance": results.get("summary_md", "")
        }
    }

    # 處理圖表
    if "figures" in results:
        for fig_path in results["figures"]:
            fig_name = Path(fig_path).name
            results_data["figures"].append({
                "filename": fig_name,
                "path": f"backend/knowledge_base/methods/{method_id}/examples/{example_dir.name}/pre_run_results/figures/{fig_name}",
                "type": Path(fig_name).stem,
                "description": f"{fig_name} 圖表"
            })

    # 儲存 results.json
    with open(output_dir / "results.json", 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 結果已儲存到 {output_dir}")

    return results_data


def pre_run_all():
    """預執行所有範例"""
    # 定義範例路徑
    examples = [
        {
            "method_id": "logistic_regression",
            "path": "backend/knowledge_base/methods/logistic_regression/examples/customer_churn"
        },
        # 添加更多範例...
    ]

    for example in examples:
        try:
            pre_run_example(example["method_id"], example["path"])
        except Exception as e:
            print(f"✗ {example['method_id']} 執行失敗: {e}")


if __name__ == "__main__":
    pre_run_all()
```

---

### Step 2: 修改 `chat_service.py`

添加讀取預執行結果並生成解釋的功能：

```python
def load_pre_run_results(method_id: str, example_id: str = None) -> Dict[str, Any]:
    """
    載入預執行結果

    Args:
        method_id: 方法 ID
        example_id: 範例 ID（可選，預設載入第一個範例）

    Returns:
        預執行結果字典
    """
    try:
        # 如果沒指定 example_id，載入第一個範例
        if not example_id:
            examples_dir = Path(f"backend/knowledge_base/methods/{method_id}/examples")
            if examples_dir.exists():
                example_id = next(examples_dir.iterdir()).name

        # 讀取 results.json
        results_path = Path(f"backend/knowledge_base/methods/{method_id}/examples/{example_id}/pre_run_results/results.json")

        if not results_path.exists():
            return None

        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

        # 讀取解釋指南
        guide_path = results_path.parent / "interpretation_guide.md"
        if guide_path.exists():
            with open(guide_path, 'r', encoding='utf-8') as f:
                results["interpretation_guide"] = f.read()

        return results

    except Exception as e:
        print(f"載入預執行結果失敗: {e}")
        return None


def generate_result_explanation(results: Dict[str, Any], interpretation_guide: str) -> str:
    """
    使用 GPT 根據預執行結果和解釋指南生成解釋

    Args:
        results: 預執行結果
        interpretation_guide: 解釋指南內容

    Returns:
        GPT 生成的解釋
    """
    try:
        prompt = f"""你是統計分析專家。請根據以下範例執行結果，用簡潔易懂的語言向用戶解釋：

**執行結果摘要：**
- 樣本數：{results['summary']['sample_size']}
- 結果變數：{results['summary']['outcome_variable']}
- 預測變數：{', '.join(results['summary']['variables_used'])}
- 主要指標：{json.dumps(results['metrics'], ensure_ascii=False)}

**解釋指南：**
{interpretation_guide}

請生成一段 150-200 字的解釋，包括：
1. 這個範例在做什麼分析
2. 主要發現是什麼（用數據說話）
3. 對實務的意義

回答要：
- 簡潔明瞭
- 突出關鍵數字
- 適合非統計背景讀者
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是專業的統計分析解說員，擅長將複雜結果轉化為易懂的語言。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"生成解釋失敗: {e}")
        return "無法生成結果解釋"
```

---

### Step 3: 更新 `generate_chat_response` 函數

在推薦方法時包含預執行結果：

```python
def generate_chat_response(question: str) -> Dict[str, Any]:
    """生成對話式回覆"""
    question_type = detect_question_type(question)

    if question_type in ["explanation", "how_to", "general"]:
        return answer_question_directly(question, question_type)

    # 分析問題
    analysis = classify_user_question(question)

    response = {
        "question": question,
        "question_type": question_type,
        "analysis": analysis,
        "recommended_methods": [],
        "can_proceed": False,
        "is_direct_answer": False
    }

    recommended_method_id = analysis.get("recommended_method")
    if recommended_method_id and recommended_method_id != "none":
        if recommended_method_id in AVAILABLE_METHODS:
            method_info = AVAILABLE_METHODS[recommended_method_id]

            # 【新增】載入預執行結果
            pre_run_results = load_pre_run_results(recommended_method_id)

            if pre_run_results:
                # 生成結果解釋
                interpretation_guide = pre_run_results.get("interpretation_guide", "")
                result_explanation = generate_result_explanation(pre_run_results, interpretation_guide)

                # 添加到回覆
                method_info["pre_run_results"] = pre_run_results
                method_info["result_explanation"] = result_explanation

            response["recommended_methods"] = [{
                "method_id": recommended_method_id,
                **method_info
            }]
            response["can_proceed"] = True

    return response
```

---

## 🎨 前端顯示調整

在 `frontend/app/page.tsx` 中添加結果顯示區塊：

```typescript
// 顯示預執行結果
if (method.pre_run_results) {
  const preRun = method.pre_run_results;

  assistantContent += `\n---\n\n### 📊 範例執行結果\n\n`;
  assistantContent += `**資料集**：${preRun.summary.sample_size} 筆資料\n\n`;

  // 顯示指標
  assistantContent += `**主要指標：**\n`;
  Object.entries(preRun.metrics).forEach(([key, value]) => {
    assistantContent += `• ${key}: ${value}\n`;
  });

  // 顯示圖表（提供連結）
  if (preRun.figures && preRun.figures.length > 0) {
    assistantContent += `\n**圖表：**\n`;
    preRun.figures.forEach(fig => {
      assistantContent += `• [查看 ${fig.description}](${API_BASE}/${fig.path})\n`;
    });
  }

  // 顯示 GPT 解釋
  if (method.result_explanation) {
    assistantContent += `\n**🎯 結果解釋：**\n${method.result_explanation}\n`;
  }
}
```

---

## 📋 使用流程

### 新增方法時的步驟：

1. **準備範例數據** → `data.csv`
2. **創建配置文件** → `config.json`
3. **實作統計方法** → `your_method.py`
4. **撰寫解釋指南** → `interpretation_guide.md`
5. **執行預運行腳本**：
   ```bash
   python backend/scripts/pre_run_examples.py
   ```
6. **檢查生成的結果** → `pre_run_results/results.json`
7. **註冊到 AVAILABLE_METHODS**

---

## ✅ 優點

1. **減少 Token 消耗**：不用每次都讓 GPT 分析執行結果
2. **響應速度快**：預先生成，立即展示
3. **結果一致性**：範例結果固定，解釋穩定
4. **易於維護**：結果和解釋分離，方便更新
5. **用戶體驗佳**：直接看到實際效果

---

## 🔄 下一步

1. 為現有的 `logistic_regression` 和 `dr_ate_cbps` 創建完整範例
2. 執行預運行腳本生成結果
3. 撰寫解釋指南
4. 測試前端顯示
