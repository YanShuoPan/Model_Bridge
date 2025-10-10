#!/usr/bin/env python
"""測試 GPT 整合功能"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_parse_with_gpt():
    """測試使用 GPT 解析問題"""

    # 測試 1: 因果推論問題
    print("=" * 60)
    print("測試 1: 因果推論問題")
    print("=" * 60)

    with open("backend/storage/demo/causal_demo.csv", "rb") as f:
        files = {"file": ("causal_demo.csv", f, "text/csv")}
        data = {"question": "我想估計這個政策介入的平均因果效應 (ATE)"}

        response = requests.post(f"{API_BASE}/parse", files=files, data=data)
        result = response.json()

        print(f"問題: {data['question']}")
        print(f"識別的任務類型: {result.get('task')}")
        print(f"結果變數類型: {result.get('y_type')}")
        print(f"識別的變數角色: {json.dumps(result.get('roles'), ensure_ascii=False, indent=2)}")
        print()

    # 測試 2: 分類問題
    print("=" * 60)
    print("測試 2: 二元分類問題")
    print("=" * 60)

    with open("backend/storage/demo/binary_demo.csv", "rb") as f:
        files = {"file": ("binary_demo.csv", f, "text/csv")}
        data = {"question": "我想預測客戶是否會流失，並了解哪些因素影響流失率"}

        response = requests.post(f"{API_BASE}/parse", files=files, data=data)
        result = response.json()

        print(f"問題: {data['question']}")
        print(f"識別的任務類型: {result.get('task')}")
        print(f"結果變數類型: {result.get('y_type')}")
        print()

def test_recommend_with_gpt():
    """測試使用 GPT 增強方法推薦"""

    print("=" * 60)
    print("測試 3: GPT 增強方法推薦")
    print("=" * 60)

    # 先解析數據
    with open("backend/storage/demo/binary_demo.csv", "rb") as f:
        files = {"file": ("binary_demo.csv", f, "text/csv")}
        data = {"question": "預測客戶流失"}

        parse_response = requests.post(f"{API_BASE}/parse", files=files, data=data)
        parse_result = parse_response.json()

    # 獲取推薦（帶 GPT 增強）
    recommend_payload = {
        "task": parse_result["task"],
        "y_type": parse_result["y_type"],
        "roles": parse_result["roles"],
        "question": data["question"],
        "df_info": {
            "columns": list(parse_result["preview"]["schema"].keys()),
            "n_rows": parse_result["preview"]["n_rows"]
        }
    }

    rec_response = requests.post(f"{API_BASE}/recommend", json=recommend_payload)
    recommendations = rec_response.json()["recommendations"]

    for i, rec in enumerate(recommendations, 1):
        print(f"\n推薦方法 {i}: {rec['name']}")
        print(f"  - 基本理由: {rec['why']}")
        if 'gpt_reasoning' in rec and rec['gpt_reasoning']:
            print(f"  - GPT 分析: {rec['gpt_reasoning']}")
        if 'considerations' in rec and rec['considerations']:
            print(f"  - 注意事項: {', '.join(rec['considerations'])}")
        if 'interpretation_tips' in rec and rec['interpretation_tips']:
            print(f"  - 解讀建議: {rec['interpretation_tips']}")

if __name__ == "__main__":
    try:
        print("\n>>> 開始測試 ChatGPT API 整合\n")

        test_parse_with_gpt()
        print("\n")
        test_recommend_with_gpt()

        print("\n" + "=" * 60)
        print("[成功] 測試完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n[錯誤] 測試失敗: {e}")
        import traceback
        traceback.print_exc()
