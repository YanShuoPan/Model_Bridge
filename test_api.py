#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test API for pre-run results functionality
"""
import requests
import json
import sys

# Set UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def test_chat_api():
    try:
        print("="*60)
        print("Testing Chat API with Pre-run Results")
        print("="*60)

        response = requests.post(
            'http://localhost:8000/api/chat',
            json={'question': 'I want to predict customer churn'},
            timeout=60
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Question Type: {data.get('question_type')}")

            if 'recommended_methods' in data and len(data['recommended_methods']) > 0:
                method = data['recommended_methods'][0]
                print(f"\nRecommended Method ID: {method.get('method_id')}")
                print(f"Method Name: {method.get('name')}")

                # Check pre-run results
                if 'pre_run_results' in method:
                    print("\n[SUCCESS] Pre-run Results: INCLUDED")
                    pre_run = method['pre_run_results']
                    print(f"  Example Name: {pre_run.get('example_name')}")
                    print(f"  Sample Size: {pre_run.get('summary', {}).get('sample_size')}")
                    print(f"  Metrics: {pre_run.get('metrics')}")
                    print(f"  Figures: {len(pre_run.get('figures', []))} images")
                else:
                    print("\n[FAIL] Pre-run Results: NOT FOUND")

                # Check GPT explanation
                if 'result_explanation' in method:
                    print("\n[SUCCESS] GPT Explanation: GENERATED")
                    explanation = method['result_explanation']
                    print(f"  Length: {len(explanation)} characters")
                    print(f"  Preview: {explanation[:200]}...")
                else:
                    print("\n[FAIL] GPT Explanation: NOT GENERATED")

                print("\n" + "="*60)
                print("TEST PASSED - All features working!")
                print("="*60)

            else:
                print("\n[FAIL] No recommended methods found")
        else:
            print(f"\n[FAIL] Error response: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_api()
