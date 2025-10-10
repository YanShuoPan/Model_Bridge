#!/usr/bin/env python
"""測試不同類型的問題"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_all_question_types():
    """測試四種問題類型"""

    test_cases = [
        {
            "type": "方法推薦",
            "questions": [
                "我想預測客戶是否會流失",
                "如何評估政策的因果效應"
            ]
        },
        {
            "type": "解釋性問題",
            "questions": [
                "什麼是勝算比？",
                "如何解讀邏輯迴歸的結果？",
                "AUC 是什麼意思？"
            ]
        },
        {
            "type": "操作問題",
            "questions": [
                "如何檢查共線性？",
                "怎麼處理缺失值？"
            ]
        },
        {
            "type": "一般問答",
            "questions": [
                "什麼是統計學？",
                "你可以做什麼？"
            ]
        }
    ]

    for case in test_cases:
        print(f"\n{'='*70}")
        print(f"測試類型: {case['type']}")
        print('='*70)

        for q in case['questions']:
            print(f"\n問題: {q}")
            print("-" * 70)

            try:
                response = requests.post(
                    f"{API_BASE}/chat",
                    json={"question": q},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    # 判斷回覆類型
                    if data.get("is_direct_answer"):
                        print(f"[回覆類型] 直接回答")
                        print(f"[問題分類] {data.get('question_type', 'unknown')}")
                        print(f"\n{data.get('answer', '')[:200]}...")
                    else:
                        print(f"[回覆類型] 方法推薦")
                        print(f"[任務類型] {data.get('analysis', {}).get('task_type', 'unknown')}")
                        if data.get('recommended_methods'):
                            method = data['recommended_methods'][0]
                            print(f"[推薦方法] {method.get('name', 'unknown')}")
                        else:
                            print(f"[推薦方法] 無")
                else:
                    print(f"[錯誤] HTTP {response.status_code}")

            except Exception as e:
                print(f"[錯誤] {e}")

if __name__ == "__main__":
    print("\n開始測試不同問題類型\n")
    test_all_question_types()
    print("\n\n測試完成")
