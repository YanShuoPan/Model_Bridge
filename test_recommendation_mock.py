"""
測試多領域推薦匹配邏輯（不使用 GPT）

模擬 GPT 返回的領域分數，測試推薦匹配算法
"""

import sys
from pathlib import Path

# 添加 backend 到路徑
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from services.domain_service import load_all_methods_metadata, get_domain_info

def mock_recommend(question_domains: dict, top_n: int = 5):
    """
    模擬推薦邏輯（不調用 GPT）

    Args:
        question_domains: 模擬的問題領域分數 {"domain_id": score, ...}
        top_n: 返回前 N 個方法
    """
    print(f"\n【問題領域分數】")
    for domain_id, score in question_domains.items():
        domain_info = get_domain_info(domain_id)
        name = domain_info.get("name", domain_id) if domain_info else domain_id
        print(f"  - {name} ({domain_id}): {score}")

    # 載入所有方法的 metadata
    all_methods_metadata = load_all_methods_metadata()
    print(f"\n【載入的方法】共 {len(all_methods_metadata)} 個")

    # 計算每個方法的匹配分數
    scored_methods = []

    for method_id, metadata in all_methods_metadata.items():
        method_domains = metadata.get("domains", [])

        if not method_domains:
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
                "matched_domains": matched_domains_detail
            })

    # 排序並返回前 N 個
    scored_methods.sort(key=lambda x: x["match_score"], reverse=True)
    top_methods = scored_methods[:top_n]

    print(f"\n【匹配結果】共匹配 {len(scored_methods)} 個方法，返回前 {len(top_methods)} 個\n")

    for i, method in enumerate(top_methods, 1):
        print(f"{i}. {method['name']} ({method['name_zh']})")
        print(f"   方法ID: {method['method_id']}")
        print(f"   總匹配分數: {method['match_score']}")
        print(f"   匹配領域:")
        for domain in method["matched_domains"]:
            print(f"     - {domain['domain_name']}: 問題={domain['question_score']} × 權重={domain['method_weight']} = {domain['contribution']} ({domain['relevance']})")
        print()

    return top_methods


if __name__ == "__main__":
    print("=" * 80)
    print("   Multi-Domain Recommendation Logic Test (Mock)")
    print("=" * 80)

    # 測試 1: 高維度問題
    print("\n" + "=" * 80)
    print("測試 1: 高維度變數選擇問題")
    print("=" * 80)
    mock_recommend({
        "high_dimensional": 0.9,
        "regression": 0.7,
        "machine_learning": 0.4
    })

    # 測試 2: 因果推論問題
    print("\n" + "=" * 80)
    print("測試 2: 因果推論問題")
    print("=" * 80)
    mock_recommend({
        "causal_inference": 1.0,
        "regression": 0.5
    })

    # 測試 3: 分類問題
    print("\n" + "=" * 80)
    print("測試 3: 二元分類問題")
    print("=" * 80)
    mock_recommend({
        "classification": 0.9,
        "machine_learning": 0.7,
        "regression": 0.3
    })

    # 測試 4: 多領域混合問題
    print("\n" + "=" * 80)
    print("測試 4: 高維度 + 因果推論混合問題")
    print("=" * 80)
    mock_recommend({
        "high_dimensional": 0.8,
        "causal_inference": 0.6,
        "regression": 0.7
    })

    # 測試 5: 只有一個領域
    print("\n" + "=" * 80)
    print("測試 5: 單一領域（只有分類）")
    print("=" * 80)
    mock_recommend({
        "classification": 1.0
    })

    print("\n" + "=" * 80)
    print("✅ 所有測試完成")
    print("=" * 80)
    print("\n【結論】")
    print("如果只推薦一個方法，原因可能是：")
    print("1. GPT 只識別到一個領域，且只有一個方法匹配該領域")
    print("2. 其他方法的匹配分數太低")
    print("3. top_n 參數設置為 1")
    print("\n檢查方式：查看後端日誌中的 [GPT] 和 [推薦] 訊息")
