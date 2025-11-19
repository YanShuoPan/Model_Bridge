import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# 載入環境變數
load_dotenv(dotenv_path="backend/.env")

# 初始化 OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 全域快取
_DOMAINS_CONFIG = None

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


def load_domains_config() -> dict:
    """
    載入領域定義配置檔

    Returns:
        dict: 領域配置資訊
    """
    global _DOMAINS_CONFIG

    # 如果已快取，直接返回
    if _DOMAINS_CONFIG is not None:
        return _DOMAINS_CONFIG

    try:
        # 找到 domains.json 的路徑
        base_dir = Path(__file__).parent.parent
        domains_path = base_dir / "knowledge_base" / "domains.json"

        if not domains_path.exists():
            print(f"警告：找不到 domains.json 於 {domains_path}")
            return {"domains": {}}

        with open(domains_path, 'r', encoding='utf-8') as f:
            _DOMAINS_CONFIG = json.load(f)

        print(f"成功載入領域配置：{len(_DOMAINS_CONFIG.get('domains', {}))} 個領域")
        return _DOMAINS_CONFIG

    except Exception as e:
        print(f"載入領域配置失敗: {e}")
        return {"domains": {}}


def identify_question_domains(question: str, df_info: dict = None) -> dict:
    """
    使用 GPT 識別問題涉及的統計領域並評分

    Args:
        question: 使用者的研究問題
        df_info: 數據資訊（選填）

    Returns:
        dict: 包含領域分數和推理說明
        格式: {
            "domains": {"domain_id": score, ...},
            "reasoning": "識別理由",
            "primary_domain": "主要領域ID"
        }
    """
    try:
        # 載入領域配置
        domains_config = load_domains_config()
        domains = domains_config.get("domains", {})

        if not domains:
            print("警告：沒有可用的領域定義")
            return {"domains": {}, "reasoning": "無領域定義", "primary_domain": None}

        # 建立領域資訊摘要給 GPT
        domains_summary = []
        for domain_id, domain_info in domains.items():
            domains_summary.append({
                "id": domain_id,
                "name": domain_info.get("name", ""),
                "name_en": domain_info.get("name_en", ""),
                "description": domain_info.get("description", ""),
                "keywords": domain_info.get("keywords", [])[:5]  # 只取前5個關鍵字
            })

        # 建立數據資訊摘要
        data_context = ""
        if df_info:
            n_rows = df_info.get("n_rows", 0)
            n_cols = df_info.get("n_cols", 0)
            columns = df_info.get("columns", [])
            data_context = f"""
數據資訊:
- 樣本數: {n_rows}
- 變數數: {n_cols}
- 欄位: {", ".join(columns[:10])}{"..." if len(columns) > 10 else ""}
"""

        prompt = f"""你是統計領域專家。請分析以下研究問題，識別它涉及哪些統計領域，並為每個相關領域評分 (0-1)。

使用者問題: {question}
{data_context}

可用的統計領域：
{json.dumps(domains_summary, ensure_ascii=False, indent=2)}

評分標準：
- 1.0: 該領域是問題的核心，解決此問題必須使用該領域的方法
- 0.7-0.9: 該領域高度相關，是解決問題的主要途徑之一
- 0.4-0.6: 該領域中度相關，可能需要結合使用
- 0.1-0.3: 該領域低度相關，某些情況下可能有幫助
- 0: 不相關

請用以下 JSON 格式回答：
{{
    "domains": {{
        "domain_id": score,
        ...
    }},
    "reasoning": "為何識別這些領域的詳細說明 (200字內)",
    "primary_domain": "最主要的領域ID"
}}

注意：
1. 只返回分數 > 0 的領域
2. 一個問題可能涉及多個領域
3. 根據問題特性判斷，不要勉強配對
4. 如果數據是高維度 (變數數 > 樣本數*0.3)，考慮 high_dimensional 領域"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是統計領域分類專家，擅長識別研究問題涉及的統計領域。請精確評估每個領域的相關性。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 使用較低溫度以獲得穩定結果
            response_format={"type": "json_object"},
            timeout=30.0  # 設定 30 秒超時
        )

        result = json.loads(response.choices[0].message.content)

        # 驗證返回的領域ID是否有效
        valid_domains = {}
        for domain_id, score in result.get("domains", {}).items():
            if domain_id in domains and 0 <= score <= 1:
                valid_domains[domain_id] = float(score)
            else:
                print(f"警告：無效的領域 '{domain_id}' 或分數 '{score}'")

        result["domains"] = valid_domains

        print(f"[GPT] 識別到 {len(valid_domains)} 個相關領域")
        return result

    except Exception as e:
        print(f"GPT 領域識別失敗: {e}")
        return {
            "domains": {},
            "reasoning": f"識別失敗: {str(e)}",
            "primary_domain": None
        }
