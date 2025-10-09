# AI Agent 統計平台 - 架構設計文檔

## 專案目標

打造一個 AI 驅動的統計方法推薦與執行平台，具備以下核心功能：

### 1. 智能問題解析與方法推薦
- 使用者上傳數據並提出研究問題
- AI 自動解析問題類型、數據特徵並標籤化
- 推薦適合的統計方法並說明理由

### 2. 統計方法知識庫
- 提供各種統計方法的詳細說明文檔
- 展示實際範例與執行結果
- 包含方法的假設、適用情境、解釋指南

### 3. 研究者貢獻系統
- 研究者可提交新的統計方法
- 包含方法說明文檔、範例數據、執行程式
- 平台自動整合並提供給使用者

---

## 現有架構分析

### 後端 (FastAPI)
```
backend/
├── main.py                    # FastAPI 主應用
├── methods/                   # 統計方法實作
│   ├── base.py               # BaseMethod 類別與註冊機制
│   ├── logistic_regression.py
│   └── dr_ate_cbps.py
├── routers/                   # API 端點
│   ├── parse.py              # 解析 CSV 與問題
│   ├── recommend.py          # 推薦統計方法
│   └── run.py                # 執行統計方法
├── services/                  # 核心服務
│   ├── parser.py             # 問題與數據解析
│   ├── recommender.py        # 方法推薦邏輯
│   ├── runner.py             # 方法執行引擎
│   └── reports.py            # 報告生成
└── storage/                   # 數據存儲
    ├── uploads/              # 上傳的 CSV
    ├── runs/                 # 執行結果
    └── demo/                 # 示範數據
```

### 前端 (Next.js)
- 單頁應用，三欄式設計
- 上傳 CSV → 查看推薦 → 執行並查看結果

---

## 擴展架構設計

### 1. 統計方法知識庫系統

#### 1.1 知識庫數據結構
```
backend/knowledge_base/
├── methods/                   # 方法詳細資訊
│   ├── logistic_regression/
│   │   ├── metadata.json     # 方法元數據
│   │   ├── description.md    # 詳細說明文檔
│   │   ├── examples/         # 範例集合
│   │   │   ├── basic/
│   │   │   │   ├── data.csv
│   │   │   │   ├── config.json
│   │   │   │   └── expected_output/
│   │   │   └── advanced/
│   │   └── tutorial.md       # 教學文檔
│   └── dr_ate_cbps/
│       └── ...
└── tags/                      # 標籤與分類
    └── taxonomy.json
```

#### 1.2 方法元數據格式 (metadata.json)
```json
{
  "method_id": "logistic_regression",
  "name": "Logistic Regression",
  "name_zh": "邏輯迴歸",
  "category": "classification",
  "tags": ["supervised", "binary", "interpretable"],
  "difficulty": "beginner",
  "requires": {
    "task": ["classification"],
    "y_type": ["binary"],
    "min_samples": 30
  },
  "assumptions": [
    "對數勝算線性關係",
    "樣本獨立性",
    "無嚴重共線性"
  ],
  "when_to_use": "當結果變數為二元且想了解各因素的影響時",
  "limitations": [
    "無法捕捉非線性關係",
    "對離群值敏感"
  ],
  "interpretation_guide": {
    "coefficients": "係數的指數為勝算比 (Odds Ratio)",
    "metrics": {
      "AUC": "模型區分能力，0.5為隨機，1.0為完美",
      "accuracy": "整體預測準確率"
    }
  },
  "related_methods": ["probit_regression", "random_forest"],
  "references": [
    {
      "title": "Applied Logistic Regression",
      "authors": "Hosmer & Lemeshow",
      "year": 2013
    }
  ],
  "author": {
    "name": "Platform Team",
    "email": "team@example.com",
    "institution": "Example University"
  },
  "version": "1.0.0",
  "last_updated": "2024-10-09"
}
```

#### 1.3 範例配置格式 (config.json)
```json
{
  "example_name": "Customer Churn Prediction",
  "example_name_zh": "客戶流失預測",
  "description": "預測客戶是否會流失",
  "data_source": "data.csv",
  "roles": {
    "y": "churned",
    "X": ["age", "tenure", "monthly_charges"]
  },
  "parameters": {
    "test_size": 0.3,
    "random_state": 42
  },
  "learning_objectives": [
    "理解邏輯迴歸的基本概念",
    "學會解釋係數與勝算比",
    "評估模型預測能力"
  ],
  "expected_insights": [
    "合約長度對流失率的影響",
    "費用與流失的關係"
  ]
}
```

### 2. 研究者貢獻系統

#### 2.1 貢獻流程
```
研究者提交 → 格式驗證 → 自動測試 → 審核 → 上線
```

#### 2.2 貢獻包結構
```
contribution_package/
├── manifest.json              # 貢獻清單
├── method/
│   ├── implementation.py      # 方法實作 (繼承 BaseMethod)
│   ├── requirements.txt       # Python 依賴
│   └── tests.py              # 單元測試
├── documentation/
│   ├── description.md         # 說明文檔
│   ├── tutorial.md           # 教學
│   └── metadata.json         # 元數據
└── examples/
    └── example_1/
        ├── data.csv
        └── config.json
```

#### 2.3 貢獻清單格式 (manifest.json)
```json
{
  "contribution_type": "new_method",
  "method_id": "new_method_name",
  "version": "1.0.0",
  "author": {
    "name": "Dr. Jane Smith",
    "email": "jane@university.edu",
    "institution": "Example University",
    "orcid": "0000-0000-0000-0000"
  },
  "license": "MIT",
  "dependencies": {
    "python": ">=3.8",
    "packages": ["numpy>=1.20", "scipy>=1.7"]
  },
  "submission_date": "2024-10-09",
  "checklist": {
    "implementation_complete": true,
    "tests_passing": true,
    "documentation_complete": true,
    "examples_provided": true
  }
}
```

#### 2.4 BaseMethod 規範強化
```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class MethodMetadata:
    """方法元數據"""
    id: str
    name: str
    category: str
    tags: List[str]
    assumptions: List[str]
    requires: Dict[str, Any]

class BaseMethod:
    """所有統計方法的基礎類別"""

    # 必填屬性
    metadata: MethodMetadata

    def validate_input(self, df, roles: dict) -> tuple[bool, str]:
        """驗證輸入數據是否符合方法需求"""
        raise NotImplementedError

    def run(self, df, roles: dict, params: dict, out_dir: str) -> Dict[str, Any]:
        """執行統計方法"""
        raise NotImplementedError

    def interpret_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """提供結果的解釋說明"""
        raise NotImplementedError

    def get_documentation(self) -> str:
        """返回方法說明文檔"""
        raise NotImplementedError
```

### 3. 新增 API 端點

#### 3.1 知識庫 API
```
GET  /api/methods                    # 列出所有方法
GET  /api/methods/{method_id}        # 取得方法詳細資訊
GET  /api/methods/{method_id}/examples # 取得方法範例列表
GET  /api/methods/{method_id}/examples/{example_id} # 取得特定範例
POST /api/methods/{method_id}/examples/{example_id}/run # 執行範例
GET  /api/search?q=...&tags=...     # 搜尋方法
```

#### 3.2 貢獻系統 API
```
POST /api/contributions              # 提交新貢獻
GET  /api/contributions/{id}         # 查看貢獻狀態
POST /api/contributions/{id}/validate # 驗證貢獻包
GET  /api/my-contributions          # 查看我的貢獻
```

### 4. 前端擴展

#### 4.1 新增頁面結構
```
frontend/app/
├── page.tsx                   # 首頁（現有）
├── methods/                   # 方法知識庫
│   ├── page.tsx              # 方法列表頁
│   └── [methodId]/
│       ├── page.tsx          # 方法詳情頁
│       └── examples/
│           └── [exampleId]/page.tsx # 範例詳情頁
├── contribute/                # 貢獻頁面
│   ├── page.tsx              # 貢獻指南
│   └── submit/page.tsx       # 提交表單
└── learn/                     # 學習中心
    └── page.tsx              # 教學資源
```

#### 4.2 方法詳情頁組件
```typescript
// 展示方法的完整資訊
<MethodDetailPage>
  <MethodHeader />           {/* 名稱、類別、難度 */}
  <MethodDescription />      {/* 詳細說明 */}
  <Assumptions />           {/* 假設與限制 */}
  <WhenToUse />            {/* 使用時機 */}
  <InterpretationGuide />  {/* 結果解釋指南 */}
  <Examples />             {/* 範例列表 */}
  <RelatedMethods />       {/* 相關方法 */}
  <References />           {/* 參考文獻 */}
</MethodDetailPage>
```

### 5. 智能推薦系統增強

#### 5.1 LLM 整合
```python
# backend/services/ai_recommender.py
from openai import OpenAI

class AIRecommender:
    """使用 LLM 進行智能推薦"""

    def analyze_question(self, question: str, df_summary: dict) -> dict:
        """
        分析使用者問題並提供詳細建議

        Returns:
            {
                "task_type": "causal",
                "research_goal": "估計政策效果",
                "suggested_methods": [...],
                "considerations": [...],
                "alternative_approaches": [...]
            }
        """
        prompt = self._build_analysis_prompt(question, df_summary)
        response = self.llm.complete(prompt)
        return self._parse_response(response)

    def explain_recommendation(self, method_id: str, context: dict) -> str:
        """解釋為何推薦此方法"""
        pass
```

#### 5.2 多層推薦策略
```
1. 基於規則的快速篩選 (現有)
2. 基於數據特徵的匹配
3. LLM 語義理解與推薦
4. 使用者反饋學習
```

### 6. 數據庫設計（未來擴展）

當需要多使用者、歷史記錄等功能時：

```sql
-- 使用者表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    institution VARCHAR(255),
    created_at TIMESTAMP
);

-- 分析歷史
CREATE TABLE analysis_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    question TEXT,
    task_type VARCHAR(50),
    method_id VARCHAR(100),
    file_path VARCHAR(500),
    results JSONB,
    created_at TIMESTAMP
);

-- 方法貢獻
CREATE TABLE method_contributions (
    id UUID PRIMARY KEY,
    author_id UUID REFERENCES users(id),
    method_id VARCHAR(100),
    status VARCHAR(50), -- pending, approved, rejected
    manifest JSONB,
    submitted_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewer_notes TEXT
);

-- 使用統計
CREATE TABLE method_usage_stats (
    method_id VARCHAR(100),
    date DATE,
    usage_count INT,
    success_count INT,
    avg_runtime FLOAT,
    PRIMARY KEY (method_id, date)
);
```

---

## 實施路線圖

### Phase 1: 知識庫基礎建設（Week 1-2）
- [ ] 設計並實作知識庫數據結構
- [ ] 為現有方法創建完整文檔
- [ ] 建立範例庫
- [ ] 新增知識庫 API 端點

### Phase 2: 前端知識庫介面（Week 3-4）
- [ ] 創建方法列表頁
- [ ] 創建方法詳情頁
- [ ] 實作範例瀏覽與執行
- [ ] 添加搜尋與篩選功能

### Phase 3: 研究者貢獻系統（Week 5-6）
- [ ] 設計貢獻包格式
- [ ] 實作貢獻提交 API
- [ ] 建立自動驗證系統
- [ ] 創建貢獻者介面

### Phase 4: AI 推薦增強（Week 7-8）
- [ ] 整合 LLM API
- [ ] 實作智能問題分析
- [ ] 增強推薦解釋
- [ ] 添加互動式問答

### Phase 5: 優化與擴展（Week 9-10）
- [ ] 使用者系統（登入、歷史記錄）
- [ ] 分析結果分享功能
- [ ] 方法評分與評論
- [ ] 效能優化與監控

---

## 技術棧建議

### 後端擴展
- **知識庫**: JSON 文件 + 文件系統（初期）→ PostgreSQL + Vector DB（長期）
- **AI/LLM**: OpenAI API / Anthropic Claude API
- **搜尋**: Elasticsearch（可選）
- **任務隊列**: Celery + Redis（處理長時間運算）

### 前端擴展
- **UI 組件庫**: shadcn/ui, Tailwind CSS
- **狀態管理**: Zustand / React Query
- **Markdown 渲染**: react-markdown
- **程式碼高亮**: Prism.js / highlight.js
- **圖表**: Recharts / Plotly

### 部署
- **後端**: Render (現有) → 可考慮 Railway / Fly.io
- **前端**: Vercel (現有)
- **數據庫**: Render PostgreSQL / Supabase
- **文件存儲**: S3 / Cloudflare R2

---

## 安全性考量

### 貢獻系統安全
1. **程式碼沙箱執行**: Docker 容器隔離
2. **依賴掃描**: 檢查惡意套件
3. **程式碼審查**: 人工 + 自動化檢查
4. **資源限制**: CPU、記憶體、執行時間限制

### 數據安全
1. **數據加密**: 上傳文件加密存儲
2. **隱私保護**: 自動移除敏感資訊
3. **存取控制**: 使用者只能存取自己的數據

---

## 成功指標

### 使用者端
- 每月活躍使用者數
- 方法執行成功率
- 使用者滿意度評分

### 知識庫
- 方法覆蓋數量（目標: 50+ 方法）
- 範例品質評分
- 文檔完整度

### 貢獻者
- 貢獻者數量
- 貢獻方法數
- 貢獻通過率

---

## 下一步行動

1. **確認優先級**: 與團隊討論 Phase 1-5 的優先順序
2. **建立第一個完整範例**: 為一個現有方法建立完整的知識庫條目
3. **設計貢獻者指南**: 撰寫詳細的貢獻文檔
4. **原型開發**: 先實作一個簡化版本驗證可行性
