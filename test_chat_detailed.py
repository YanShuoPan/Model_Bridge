#!/usr/bin/env python
"""測試對話式 API 的完整功能"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_chat_detailed():
    """測試完整的聊天功能"""

    questions = [
        "我想預測員工是否會離職",
        "政府想評估補助政策的效果",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"測試 {i}: {question}")
        print('='*70)

        response = requests.post(
            f"{API_BASE}/chat",
            json={"question": question}
        )

        if response.status_code == 200:
            data = response.json()

            print(f"\n[任務類型] {data['analysis']['task_type']}")
            print(f"[推薦信心] {data['analysis']['confidence']}")
            print(f"\n[分析理由]")
            print(f"{data['analysis']['reasoning']}")

            if data['recommended_methods']:
                method = data['recommended_methods'][0]
                print(f"\n[推薦方法] {method['name']}")
                print(f"{method['description']}")

                # 範例資料
                if 'example_data' in method:
                    ex_data = method['example_data']
                    print(f"\n[範例資料] {ex_data['name']}")
                    print(f"說明: {ex_data['description']}")
                    print(f"樣本數: {ex_data['sample_size']}")
                    print(f"預期結果: {ex_data['what_to_expect']}")

            # 後續問題
            if 'follow_up_questions' in data['analysis']:
                print(f"\n[可以接著問]")
                for q in data['analysis']['follow_up_questions']:
                    print(f"  - {q}")

            print(f"\n[下一步] {data['analysis']['next_steps']}")
        else:
            print(f"錯誤: {response.status_code}")

if __name__ == "__main__":
    print("\n[開始測試] 對話式 API 詳細功能\n")
    test_chat_detailed()
    print("\n\n[測試完成]")
