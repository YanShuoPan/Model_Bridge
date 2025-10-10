import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 載入環境變數
load_dotenv(dotenv_path="backend/.env")

# 初始化 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_question_with_gpt(question: str, df_summary: dict) -> dict:
    """
    使用 GPT 分析研究問題並識別任務類型

    Args:
        question: 使用者的研究問題
        df_summary: 數據框架的摘要資訊

    Returns:
        dict: 包含 task_type 和 reasoning 的字典
    """
    try:
        columns_info = ", ".join(df_summary.get('columns', []))
        n_rows = df_summary.get('n_rows', 0)

        prompt = f"""你是統計分析專家。請分析以下研究問題並判斷統計任務類型。

使用者問題: {question}
數據資訊:
- 欄位: {columns_info}
- 筆數: {n_rows}

請判斷這是哪種統計任務，從以下選項中選擇一個：
1. causal - 因果推論 (例如：估計政策效果、treatment effect、ATE)
2. classification - 分類問題 (例如：預測二元結果、機率預測)
3. prediction - 預測問題 (例如：迴歸分析、預測連續值)
4. survival - 存活分析 (例如：時間到事件分析、風險評估)

請用以下 JSON 格式回答：
{{
    "task_type": "causal/classification/prediction/survival",
    "reasoning": "簡短說明為什麼是這個任務類型",
    "confidence": "high/medium/low"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 使用較便宜的模型
            messages=[
                {"role": "system", "content": "你是統計分析專家，擅長識別研究問題的類型。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"GPT 分析失敗: {e}")
        return {"task_type": "unknown", "reasoning": str(e), "confidence": "low"}


def get_method_recommendation_with_gpt(question: str, task_type: str, df_info: dict, available_methods: list) -> dict:
    """
    使用 GPT 提供統計方法推薦與詳細說明

    Args:
        question: 使用者問題
        task_type: 任務類型
        df_info: 數據資訊
        available_methods: 可用的方法列表

    Returns:
        dict: 包含推薦理由和額外建議
    """
    try:
        methods_str = "\n".join([f"- {m['method_id']}: {m['name']}" for m in available_methods])

        prompt = f"""請為以下研究問題推薦最適合的統計方法。

使用者問題: {question}
任務類型: {task_type}
數據欄位: {", ".join(df_info.get('columns', []))}

可用的統計方法：
{methods_str}

請提供：
1. 最推薦的方法 (從上述列表選擇)
2. 推薦理由 (100字內)
3. 使用注意事項
4. 結果解讀建議

用 JSON 格式回答：
{{
    "recommended_method": "method_id",
    "reasoning": "推薦理由",
    "considerations": ["注意事項1", "注意事項2"],
    "interpretation_tips": "解讀建議"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是統計方法推薦專家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"GPT 推薦失敗: {e}")
        return {
            "recommended_method": available_methods[0]["method_id"] if available_methods else None,
            "reasoning": "使用預設推薦",
            "considerations": [],
            "interpretation_tips": ""
        }
