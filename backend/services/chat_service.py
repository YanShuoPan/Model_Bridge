"""
對話式統計諮詢服務
使用 GPT 理解使用者問題並推薦統計方法
"""

import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# 載入環境變數
load_dotenv(dotenv_path="backend/.env")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 可用的統計方法知識庫
AVAILABLE_METHODS = {
    "logistic_regression": {
        "name": "Logistic Regression（邏輯迴歸）",
        "description": "用於預測二元結果（0/1）的統計方法，可以了解各因素對結果的影響程度",
        "suitable_for": ["二元分類", "機率預測", "風險因子分析"],
        "example_questions": [
            "如何預測客戶是否會流失？",
            "哪些因素會影響疾病發生的機率？",
            "如何分析違約風險？"
        ],
        "assumptions": ["對數勝算線性關係", "樣本獨立性", "無嚴重共線性"],
        "outputs": ["係數與勝算比", "預測機率", "ROC曲線", "混淆矩陣"],
        "example_data": {
            "name": "binary_demo.csv",
            "path": "backend/storage/demo/binary_demo.csv",
            "description": "模擬的二元分類數據集",
            "columns": {
                "y": "結果變數（0或1）",
                "x1, x2, x3...": "預測變數（連續型或類別型）"
            },
            "sample_size": "約 200-500 筆",
            "what_to_expect": "可以看到每個變數對結果的影響程度（勝算比）、預測準確度（AUC）、以及模型診斷圖表"
        }
    },
    "dr_ate_cbps": {
        "name": "Doubly Robust ATE（雙重穩健因果效應估計）",
        "description": "用於估計政策介入或處理的平均因果效應（ATE），適合因果推論研究",
        "suitable_for": ["因果效應估計", "政策評估", "實驗分析"],
        "example_questions": [
            "某項政策的實際效果是多少？",
            "教育訓練對績效的影響有多大？",
            "新藥物的治療效果如何？"
        ],
        "assumptions": ["可忽略性（無未觀測混淆）", "正性（overlap）", "正確模型規格"],
        "outputs": ["平均處理效應（ATE）", "信賴區間", "平衡診斷圖", "敏感性分析"],
        "example_data": {
            "name": "causal_demo.csv",
            "path": "backend/storage/demo/causal_demo.csv",
            "description": "模擬的因果推論數據集",
            "columns": {
                "treatment": "處理變數（0=未處理, 1=已處理）",
                "y": "結果變數（連續型）",
                "x1, x2, x3...": "共變數/混淆因子"
            },
            "sample_size": "約 200-500 筆",
            "what_to_expect": "可以看到平均處理效應（ATE）的估計值、信賴區間、處理組與對照組的平衡診斷，以及因果效應的顯著性"
        }
    }
}

# 範例問題（供使用者參考）
EXAMPLE_QUESTIONS = [
    {
        "category": "分類預測",
        "question": "我想預測員工是否會離職，手上有員工的基本資料、薪資、工作年資等資料",
        "expected_method": "logistic_regression"
    },
    {
        "category": "因果推論",
        "question": "我們公司推行了一個員工培訓計畫，想知道這個計畫對員工績效的實際影響有多大",
        "expected_method": "dr_ate_cbps"
    },
    {
        "category": "分類預測",
        "question": "醫院想分析哪些因素會增加病人再入院的風險",
        "expected_method": "logistic_regression"
    },
    {
        "category": "因果推論",
        "question": "政府想評估某項補助政策對企業營收的因果效應",
        "expected_method": "dr_ate_cbps"
    }
]


def detect_question_type(question: str) -> str:
    """
    判斷問題類型

    Returns:
        - "method_recommendation": 需要推薦統計方法
        - "explanation": 解釋概念或結果
        - "how_to": 操作指南
        - "general": 一般問答
    """
    try:
        prompt = f"""請判斷使用者問題的類型。

使用者問題：{question}

問題類型分類：
1. method_recommendation - 使用者有研究問題，需要推薦統計方法（例如：我想預測客戶流失、如何分析政策效果）
2. explanation - 解釋統計概念、方法、或結果（例如：什麼是勝算比、如何解讀 AUC、邏輯迴歸的假設是什麼）
3. how_to - 操作指南或技術問題（例如：如何檢查共線性、怎麼處理缺失值）
4. general - 一般性問答（例如：什麼是統計學）

請用 JSON 格式回答：
{{
    "question_type": "method_recommendation/explanation/how_to/general",
    "confidence": "high/medium/low"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是問題分類專家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("question_type", "general")

    except Exception as e:
        print(f"問題分類失敗: {e}")
        return "general"


def classify_user_question(question: str) -> Dict[str, Any]:
    """
    使用 GPT 分析使用者問題，判斷適合的統計方法

    Args:
        question: 使用者的問題

    Returns:
        包含分類結果、推薦方法、解釋的字典
    """
    try:
        methods_info = "\n".join([
            f"- {mid}: {info['name']}\n  適用於: {', '.join(info['suitable_for'])}"
            for mid, info in AVAILABLE_METHODS.items()
        ])

        prompt = f"""你是統計諮詢專家。請分析使用者的問題，判斷適合使用的統計方法。

可用的統計方法：
{methods_info}

使用者問題：{question}

請判斷：
1. 這個問題的核心目標是什麼？（預測、因果推論、分類等）
2. 最適合的統計方法是什麼？
3. 為什麼推薦這個方法？
4. 使用者需要準備什麼樣的數據？
5. 這個方法能回答什麼問題？
6. 接下來使用者可以詢問什麼問題來深入了解？

請用以下 JSON 格式回答：
{{
    "task_type": "classification/causal/prediction",
    "recommended_method": "logistic_regression 或 dr_ate_cbps 或 none",
    "confidence": "high/medium/low",
    "reasoning": "推薦理由（80字內，簡潔有力）",
    "data_requirements": ["需要的數據欄位1", "需要的數據欄位2"],
    "what_you_can_learn": "這個方法能回答什麼問題（50字內）",
    "next_steps": "建議的下一步行動（50字內）",
    "follow_up_questions": ["可以問的問題1", "可以問的問題2"],
    "show_example": true/false
}}

重要：
- 如果無法判斷或問題不適合現有方法，recommended_method 設為 "none"，reasoning 要簡短（30字內）
- show_example: 如果推薦了方法，設為 true（要主動展示範例）
- follow_up_questions: 提供 2-3 個使用者可以接著問的問題
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是專業的統計方法諮詢顧問，擅長理解研究問題並推薦適合的分析方法。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"GPT 分析失敗: {e}")
        return {
            "task_type": "unknown",
            "recommended_method": "none",
            "confidence": "low",
            "reasoning": "無法分析問題，請提供更多細節",
            "data_requirements": [],
            "what_you_can_learn": "",
            "next_steps": "請更詳細地描述您的研究問題"
        }


def answer_question_directly(question: str, question_type: str) -> Dict[str, Any]:
    """
    直接回答使用者問題（非方法推薦）

    Args:
        question: 使用者問題
        question_type: 問題類型

    Returns:
        直接回答的內容
    """
    try:
        # 準備知識庫內容
        methods_context = ""
        for method_id, info in AVAILABLE_METHODS.items():
            methods_context += f"\n**{info['name']}**\n"
            methods_context += f"- 說明: {info['description']}\n"
            methods_context += f"- 假設: {', '.join(info['assumptions'])}\n"
            methods_context += f"- 輸出: {', '.join(info['outputs'])}\n"

        system_prompt = """你是專業的統計諮詢顧問。請根據使用者的問題提供清晰、準確的回答。

回答時請：
1. 直接、簡潔地回答問題核心
2. 使用易懂的語言解釋專業概念
3. 必要時提供實際例子
4. 保持回答在 200 字內（除非需要詳細解釋）

可用的統計方法背景知識：
""" + methods_context

        user_prompt = f"""使用者問題：{question}

請提供專業、易懂的回答。"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )

        answer = response.choices[0].message.content

        return {
            "question": question,
            "question_type": question_type,
            "answer": answer,
            "is_direct_answer": True
        }

    except Exception as e:
        print(f"直接回答失敗: {e}")
        return {
            "question": question,
            "question_type": question_type,
            "answer": "抱歉，我無法回答這個問題。請嘗試換個方式問，或參考範例問題。",
            "is_direct_answer": True
        }


def load_pre_run_results(method_id: str, example_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    載入預執行結果

    Args:
        method_id: 方法 ID
        example_id: 範例 ID（可選，預設載入第一個範例）

    Returns:
        預執行結果字典，如果失敗返回 None
    """
    try:
        # 如果沒指定 example_id，載入第一個範例
        if not example_id:
            examples_dir = Path(f"backend/knowledge_base/methods/{method_id}/examples")
            if examples_dir.exists():
                # 獲取第一個範例目錄
                example_dirs = [d for d in examples_dir.iterdir() if d.is_dir()]
                if example_dirs:
                    example_id = example_dirs[0].name

        if not example_id:
            print(f"[載入預執行結果] 未找到 {method_id} 的範例")
            return None

        # 讀取 results.json
        results_path = Path(f"backend/knowledge_base/methods/{method_id}/examples/{example_id}/pre_run_results/results.json")

        if not results_path.exists():
            print(f"[載入預執行結果] 結果文件不存在: {results_path}")
            return None

        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)

        # 讀取解釋指南
        guide_path = results_path.parent / "interpretation_guide.md"
        if guide_path.exists():
            with open(guide_path, 'r', encoding='utf-8') as f:
                results["interpretation_guide"] = f.read()
        else:
            results["interpretation_guide"] = ""

        print(f"[載入預執行結果] 成功載入 {method_id}/{example_id}")
        return results

    except Exception as e:
        print(f"[載入預執行結果] 失敗: {e}")
        return None


def generate_result_explanation(results: Dict[str, Any]) -> str:
    """
    使用 GPT 根據預執行結果和解釋指南生成簡短解釋

    Args:
        results: 預執行結果（包含 interpretation_guide）

    Returns:
        GPT 生成的簡短解釋（150-200字）
    """
    try:
        interpretation_guide = results.get("interpretation_guide", "")
        metrics = results.get("metrics", {})
        summary = results.get("summary", {})
        coefficients = results.get("coefficients", {})

        # 提取關鍵係數（勝算比最大和最小的）
        if coefficients:
            coef_list = [(k, v.get("odds_ratio", 1.0)) for k, v in coefficients.items()]
            coef_list.sort(key=lambda x: abs(x[1] - 1.0), reverse=True)
            top_factors = coef_list[:3]  # 取影響最大的 3 個
        else:
            top_factors = []

        prompt = f"""你是統計分析解說員。請根據以下範例執行結果，用簡潔易懂的語言向用戶解釋這個範例展示了什麼。

**範例名稱**: {results.get('example_name', '統計分析範例')}
**樣本數**: {summary.get('sample_size')} 筆
**結果變數**: {summary.get('outcome_variable')}

**主要指標**:
{json.dumps(metrics, ensure_ascii=False, indent=2)}

**關鍵影響因素**:
{', '.join([f"{k} (勝算比={v:.2f})" for k, v in top_factors[:3]]) if top_factors else '無'}

**解釋指南重點**:
{interpretation_guide[:500] if len(interpretation_guide) > 500 else interpretation_guide}

請生成一段 **150-200 字**的解釋，包括：
1. 這個範例在做什麼分析（1句話）
2. 主要發現是什麼（用具體數字說明，2-3句）
3. 對實務的意義（1-2句）

要求：
- 簡潔明瞭，突出關鍵數字
- 適合非統計背景讀者
- 不要使用術語，用白話文
- 直接回答，不要加標題或前綴"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是專業的統計分析解說員，擅長將複雜結果轉化為易懂的語言。回答要簡潔、直接、突出關鍵數字。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )

        explanation = response.choices[0].message.content.strip()
        print(f"[生成結果解釋] 成功生成 {len(explanation)} 字解釋")
        return explanation

    except Exception as e:
        print(f"[生成結果解釋] 失敗: {e}")
        return "這個範例展示了如何使用統計方法進行數據分析，並提供了實際的執行結果和解釋。"


def generate_chat_response(question: str) -> Dict[str, Any]:
    """
    生成對話式回覆

    Args:
        question: 使用者問題

    Returns:
        完整的回覆內容，包含方法推薦、範例等
    """
    # 先判斷問題類型
    question_type = detect_question_type(question)

    print(f"[問題類型] {question_type}: {question}")

    # 如果不是方法推薦問題，直接回答
    if question_type in ["explanation", "how_to", "general"]:
        return answer_question_directly(question, question_type)

    # 如果是方法推薦問題，走原本流程
    # 使用 GPT 分析問題
    analysis = classify_user_question(question)

    # 準備回覆
    response = {
        "question": question,
        "question_type": question_type,
        "analysis": analysis,
        "recommended_methods": [],
        "can_proceed": False,
        "is_direct_answer": False
    }

    # 如果有推薦方法，提供詳細資訊
    recommended_method_id = analysis.get("recommended_method")
    if recommended_method_id and recommended_method_id != "none":
        if recommended_method_id in AVAILABLE_METHODS:
            method_info = AVAILABLE_METHODS[recommended_method_id].copy()

            # 【新增】載入預執行結果
            pre_run_results = load_pre_run_results(recommended_method_id)

            if pre_run_results:
                # 生成結果解釋
                result_explanation = generate_result_explanation(pre_run_results)

                # 添加到方法資訊中
                method_info["pre_run_results"] = pre_run_results
                method_info["result_explanation"] = result_explanation

                print(f"[推薦方法] 已包含預執行結果和解釋")
            else:
                print(f"[推薦方法] 未找到預執行結果，使用原始資訊")

            response["recommended_methods"] = [{
                "method_id": recommended_method_id,
                **method_info
            }]
            response["can_proceed"] = True

    return response


def get_example_questions() -> List[Dict[str, Any]]:
    """取得範例問題列表"""
    return EXAMPLE_QUESTIONS


def get_method_details(method_id: str) -> Dict[str, Any]:
    """取得特定方法的詳細資訊"""
    if method_id in AVAILABLE_METHODS:
        return {
            "method_id": method_id,
            **AVAILABLE_METHODS[method_id]
        }
    return {}
