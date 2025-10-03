def recommend_methods(task: str, y_type: str, roles: dict):
    recs = []
    if task == "causal" and roles.get("treatment") and roles.get("y"):
        recs.append({
            "method_id": "dr_ate_cbps",
            "name": "Doubly Robust ATE (with CBPS-like weights)",
            "why": "偵測到因果問題且存在 treatment/outcome 欄位；提供ATE與平衡診斷。",
            "assumptions": ["可觀測性(ignorability)或正確指定的任一模型", "overlap"],
            "inputs_required": ["treatment(0/1)", "outcome", "covariates"]
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
    return recs[:3]
