from backend.services.ai_service import get_method_recommendation_with_gpt

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
