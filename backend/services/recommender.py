from backend.services.ai_service import get_method_recommendation_with_gpt, identify_question_domains
from backend.services.domain_service import load_all_methods_metadata, get_domain_info
from typing import Dict, List, Optional

def recommend_methods(task: str, y_type: str, roles: dict, question: str = "", df_info: dict = None, use_gpt: bool = True):
    """
    推薦統計方法，優先使用 GPT 提供詳細建議

    Args:
        task: 任務類型
        y_type: 結果變數類型
        roles: 變數角色
        question: 使用者問題（用於 GPT）
        df_info: 數據資訊（用於 GPT）
        use_gpt: 是否使用 GPT

    Returns:
        推薦方法列表
    """
    recs = []

    # 基於規則的方法推薦
    if task == "causal" and roles.get("treatment") and roles.get("y"):
        recs.append({
            "method_id": "dr_ate_cbps",
            "name": "Doubly Robust ATE (with CBPS-like weights)",
            "why": "偵測到因果問題且存在 treatment/outcome 欄位；提供ATE與平衡診斷。",
            "assumptions": ["可觀測性(ignorability)或正確指定的任一模型", "overlap"],
            "inputs_required": ["treatment(0/1)", "outcome", "covariates"]
        })

    # 高維度變數選擇 (OGA-HDIC)
    if y_type == "continuous" and roles.get("y") and df_info:
        n_samples = df_info.get("n_rows", 0)
        n_features = df_info.get("n_cols", 0) - 1  # 扣除結果變數
        # 當變數數量相對於樣本數較多時，推薦高維度方法
        if n_features > n_samples * 0.3:  # p > n * 0.3 視為高維度情境
            recs.append({
                "method_id": "oga_hdic",
                "name": "OGA-HDIC (高維度變數選擇)",
                "why": f"偵測到高維度問題（{n_features} 個變數 vs {n_samples} 筆樣本），適合使用變數選擇方法進行特徵篩選。",
                "assumptions": ["真實模型是稀疏的（只有少數變數真正重要）", "線性關係", "樣本獨立"],
                "inputs_required": ["y(連續)", "多個預測變數X"]
            })

    if y_type == "binary" and roles.get("y"):
        recs.append({
            "method_id": "logistic_regression",
            "name": "Logistic Regression (sklearn)",
            "why": "因變數為二元；建立機率模型並輸出ROC等診斷。",
            "assumptions": ["對數勝算線性", "樣本獨立"],
            "inputs_required": ["y(0/1)", "X"]
        })
    if not recs:
        recs.append({
            "method_id": "logistic_regression",
            "name": "Logistic Regression (sklearn)",
            "why": "預設範例與報告。",
            "assumptions": ["對數勝算線性", "樣本獨立"],
            "inputs_required": ["y(0/1)", "X"]
        })

    # 使用 GPT 增強推薦說明
    if use_gpt and question and df_info and recs:
        try:
            gpt_advice = get_method_recommendation_with_gpt(
                question=question,
                task_type=task,
                df_info=df_info,
                available_methods=recs
            )

            # 將 GPT 的建議加入到推薦方法中
            for rec in recs:
                if rec["method_id"] == gpt_advice.get("recommended_method"):
                    rec["gpt_reasoning"] = gpt_advice.get("reasoning", "")
                    rec["considerations"] = gpt_advice.get("considerations", [])
                    rec["interpretation_tips"] = gpt_advice.get("interpretation_tips", "")
                    break

            print(f"[GPT] 方法推薦增強完成")
        except Exception as e:
            print(f"[GPT] 推薦增強失敗: {e}")

    return recs[:3]


def recommend_methods_by_domains(
    question: str,
    df_info: dict = None,
    top_n: int = 5,
    use_gpt_identification: bool = True
) -> Dict[str, any]:
    """
    基於多領域匹配推薦統計方法

    Args:
        question: 使用者研究問題
        df_info: 數據資訊 (包含 n_rows, n_cols, columns 等)
        top_n: 返回前 N 個推薦方法
        use_gpt_identification: 是否使用 GPT 識別領域

    Returns:
        dict: {
            "question_domains": {...},  # 問題涉及的領域及分數
            "recommended_methods": [...],  # 推薦的方法列表
            "reasoning": "...",  # 推薦理由
            "total_methods_evaluated": int  # 評估的方法總數
        }
    """
    # Step 1: 識別問題涉及的領域
    if use_gpt_identification:
        domain_result = identify_question_domains(question, df_info)
        question_domains = domain_result.get("domains", {})
        reasoning = domain_result.get("reasoning", "")
        primary_domain = domain_result.get("primary_domain")
    else:
        # 如果不使用 GPT，返回空結果（未來可加入規則式識別）
        return {
            "question_domains": {},
            "recommended_methods": [],
            "reasoning": "未使用 GPT 領域識別且無規則式識別",
            "total_methods_evaluated": 0
        }

    if not question_domains:
        print("[推薦] 警告：未識別到任何相關領域")
        return {
            "question_domains": {},
            "recommended_methods": [],
            "reasoning": "無法識別問題涉及的領域",
            "total_methods_evaluated": 0
        }

    print(f"[推薦] 識別到 {len(question_domains)} 個領域: {list(question_domains.keys())}")

    # Step 2: 載入所有方法的 metadata
    all_methods_metadata = load_all_methods_metadata()

    if not all_methods_metadata:
        print("[推薦] 警告：沒有可用的方法")
        return {
            "question_domains": question_domains,
            "recommended_methods": [],
            "reasoning": reasoning,
            "total_methods_evaluated": 0
        }

    # Step 3: 計算每個方法的匹配分數
    scored_methods = []

    for method_id, metadata in all_methods_metadata.items():
        method_domains = metadata.get("domains", [])

        if not method_domains:
            # 如果方法沒有標記領域，跳過
            continue

        # 計算匹配分數
        match_score = 0.0
        matched_domains_detail = []

        for method_domain_info in method_domains:
            domain_id = method_domain_info.get("domain_id")
            domain_weight = method_domain_info.get("weight", 1.0)

            if domain_id in question_domains:
                question_score = question_domains[domain_id]
                contribution = question_score * domain_weight
                match_score += contribution

                matched_domains_detail.append({
                    "domain_id": domain_id,
                    "domain_name": get_domain_info(domain_id).get("name", domain_id) if get_domain_info(domain_id) else domain_id,
                    "question_score": round(question_score, 2),
                    "method_weight": round(domain_weight, 2),
                    "contribution": round(contribution, 2),
                    "relevance": method_domain_info.get("relevance", "unknown")
                })

        # 只保留有匹配的方法
        if match_score > 0:
            scored_methods.append({
                "method_id": method_id,
                "name": metadata.get("name", method_id),
                "name_zh": metadata.get("name_zh", ""),
                "match_score": round(match_score, 3),
                "matched_domains": matched_domains_detail,
                "difficulty": metadata.get("difficulty", "unknown"),
                "category": metadata.get("category", "unknown"),
                "tags": metadata.get("tags", []),
                "assumptions": metadata.get("assumptions", []),
                "when_to_use": metadata.get("when_to_use", {}),
                "limitations": metadata.get("limitations", [])
            })

    # Step 4: 排序並返回前 N 個
    scored_methods.sort(key=lambda x: x["match_score"], reverse=True)
    top_methods = scored_methods[:top_n]

    print(f"[推薦] 評估了 {len(all_methods_metadata)} 個方法，匹配到 {len(scored_methods)} 個，返回前 {len(top_methods)} 個")

    return {
        "question_domains": {
            domain_id: {
                "score": round(score, 2),
                "name": get_domain_info(domain_id).get("name", domain_id) if get_domain_info(domain_id) else domain_id,
                "name_en": get_domain_info(domain_id).get("name_en", "") if get_domain_info(domain_id) else ""
            }
            for domain_id, score in question_domains.items()
        },
        "recommended_methods": top_methods,
        "reasoning": reasoning,
        "primary_domain": primary_domain,
        "total_methods_evaluated": len(all_methods_metadata),
        "total_matched": len(scored_methods)
    }
