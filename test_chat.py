#!/usr/bin/env python
"""測試對話式 API"""

import requests
import json

API_BASE = "http://localhost:8000/api"

def test_chat():
    """測試聊天功能"""

    questions = [
        "我想預測客戶是否會流失",
        "我們公司推行了員工培訓計畫，想知道對績效的影響",
        "如何分析股票價格的趨勢"  # 這個應該無法匹配
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"測試 {i}: {question}")
        print('='*60)

        response = requests.post(
            f"{API_BASE}/chat",
            json={"question": question}
        )

        if response.status_code == 200:
            data = response.json()

            print(f"\n任務類型: {data['analysis']['task_type']}")
            print(f"推薦信心: {data['analysis']['confidence']}")
            print(f"\n分析:")
            print(f"  {data['analysis']['reasoning']}")

            if data['recommended_methods']:
                method = data['recommended_methods'][0]
                print(f"\n推薦方法: {method['name']}")
                print(f"說明: {method['description']}")
                print(f"\n適用情境:")
                for s in method['suitable_for']:
                    print(f"  • {s}")
            else:
                print("\n沒有匹配的方法")

            print(f"\n下一步: {data['analysis']['next_steps']}")
        else:
            print(f"錯誤: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    print("\n>>> 測試對話式 API\n")
    test_chat()
    print("\n\n[完成] 測試完成")
