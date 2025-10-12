"use client";
import React, { useState, useRef, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API || "http://localhost:8000/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  data?: any; // 額外的結構化數據
}

interface ExampleQuestion {
  category: string;
  question: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "你好！我是統計方法諮詢助手。\n\n我可以幫助你：\n• 理解統計問題\n• 推薦適合的統計方法\n• 說明方法的使用時機與注意事項\n\n⏱️ 提示：首次訪問時，後端需要約 30 秒啟動，請稍候片刻。\n\n請告訴我你的研究問題，或點擊下方的範例問題開始。"
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [examples, setExamples] = useState<ExampleQuestion[]>([]);
  const [loadingExamples, setLoadingExamples] = useState(true);
  const [apiReady, setApiReady] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 載入範例問題（帶超時和重試）
  useEffect(() => {
    const loadExamples = async () => {
      try {
        setLoadingExamples(true);

        // 設置 30 秒超時
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch(`${API_BASE}/chat/examples`, {
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          const data = await response.json();
          setExamples(data.examples || []);
          setApiReady(true);
        }
      } catch (err) {
        console.error("載入範例失敗:", err);
        // 即使失敗也設為 ready，讓用戶可以手動輸入
        setApiReady(true);
      } finally {
        setLoadingExamples(false);
      }
    };

    loadExamples();
  }, []);

  // 自動滾動到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // 發送訊息
  const sendMessage = async (question: string) => {
    if (!question.trim() || loading) return;

    // 添加使用者訊息
    const userMessage: Message = { role: "user", content: question };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // 呼叫 GPT 分析 API
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await response.json();

      // 生成助手回覆
      let assistantContent = "";

      // 如果是直接回答模式
      if (data.is_direct_answer) {
        assistantContent = data.answer;
      } else {
        // 原本的方法推薦模式
        // 分析結果
        const analysis = data.analysis;
      if (analysis) {
        assistantContent += `### 📊 問題分析\n\n`;
        assistantContent += `**任務類型：** ${getTaskTypeLabel(analysis.task_type)}\n\n`;
        assistantContent += `**分析：** ${analysis.reasoning}\n\n`;

        // 如果有推薦方法
        if (data.recommended_methods && data.recommended_methods.length > 0) {
          const method = data.recommended_methods[0];
          assistantContent += `---\n\n### ✅ 推薦方法\n\n`;
          assistantContent += `**${method.name}**\n\n`;
          assistantContent += `${method.description}\n\n`;

          assistantContent += `**📋 適用情境：**\n`;
          method.suitable_for.forEach((s: string) => {
            assistantContent += `• ${s}\n`;
          });

          assistantContent += `\n**📦 需要的資料：**\n`;
          if (analysis.data_requirements && analysis.data_requirements.length > 0) {
            analysis.data_requirements.forEach((req: string) => {
              assistantContent += `• ${req}\n`;
            });
          }

          assistantContent += `\n**🎯 能回答的問題：**\n${analysis.what_you_can_learn}\n\n`;

          assistantContent += `**⚠️ 重要假設：**\n`;
          method.assumptions.forEach((a: string) => {
            assistantContent += `• ${a}\n`;
          });

          assistantContent += `\n**📈 輸出結果：**\n`;
          method.outputs.forEach((o: string) => {
            assistantContent += `• ${o}\n`;
          });

          // 範例資料展示
          if (method.example_data && analysis.show_example) {
            const exData = method.example_data;
            assistantContent += `\n---\n\n### 📂 範例資料\n\n`;
            assistantContent += `我們提供了 **${exData.name}** 供你測試：\n\n`;
            assistantContent += `**資料說明：** ${exData.description}\n\n`;
            assistantContent += `**資料欄位：**\n`;
            Object.entries(exData.columns).forEach(([key, val]) => {
              assistantContent += `• ${key}: ${val}\n`;
            });
            assistantContent += `\n**樣本數：** ${exData.sample_size}\n\n`;
            assistantContent += `**預期結果：** ${exData.what_to_expect}\n\n`;
          }

          assistantContent += `---\n\n`;
          assistantContent += `💡 **下一步：** ${analysis.next_steps}\n\n`;

          // 後續問題建議
          if (analysis.follow_up_questions && analysis.follow_up_questions.length > 0) {
            assistantContent += `**💬 你也可以問：**\n`;
            analysis.follow_up_questions.forEach((q: string) => {
              assistantContent += `• ${q}\n`;
            });
          }

        } else {
          assistantContent += `---\n\n`;
          assistantContent += `😕 ${analysis.reasoning}\n\n`;
          assistantContent += `**建議：** ${analysis.next_steps}\n\n`;

          // 後續問題建議
          if (analysis.follow_up_questions && analysis.follow_up_questions.length > 0) {
            assistantContent += `**💬 你可以這樣問：**\n`;
            analysis.follow_up_questions.forEach((q: string) => {
              assistantContent += `• ${q}\n`;
            });
          }
        }
      }
      } // 結束方法推薦模式

      const assistantMessage: Message = {
        role: "assistant",
        content: assistantContent,
        data: data
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("發送失敗:", error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "抱歉，系統發生錯誤。請稍後再試。"
      }]);
    } finally {
      setLoading(false);
    }
  };

  const getTaskTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      "classification": "分類預測",
      "causal": "因果推論",
      "prediction": "預測分析",
      "survival": "存活分析",
      "unknown": "未知"
    };
    return labels[type] || type;
  };

  return (
    <main style={{
      display: "flex",
      flexDirection: "column",
      height: "100vh",
      maxWidth: "1000px",
      margin: "0 auto",
      fontFamily: "ui-sans-serif, system-ui, sans-serif"
    }}>
      {/* 標題欄 */}
      <header style={{
        padding: "16px 24px",
        borderBottom: "1px solid #e5e7eb",
        backgroundColor: "#f9fafb"
      }}>
        <h1 style={{ margin: 0, fontSize: "24px", fontWeight: 600 }}>
          統計方法諮詢助手
        </h1>
        <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "4px" }}>
          <p style={{ margin: 0, fontSize: "14px", color: "#6b7280" }}>
            AI 驅動的統計方法推薦系統
          </p>
          {loadingExamples && (
            <span style={{
              fontSize: "12px",
              color: "#f59e0b",
              fontWeight: 500,
              padding: "2px 8px",
              backgroundColor: "#fef3c7",
              borderRadius: "4px"
            }}>
              🔄 正在連接後端...
            </span>
          )}
          {!loadingExamples && apiReady && (
            <span style={{
              fontSize: "12px",
              color: "#10b981",
              fontWeight: 500,
              padding: "2px 8px",
              backgroundColor: "#d1fae5",
              borderRadius: "4px"
            }}>
              ✓ 已就緒
            </span>
          )}
        </div>
      </header>

      {/* 對話區域 */}
      <div style={{
        flex: 1,
        overflowY: "auto",
        padding: "24px",
        backgroundColor: "#ffffff"
      }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            marginBottom: "20px",
            display: "flex",
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start"
          }}>
            <div style={{
              maxWidth: "80%",
              padding: "12px 16px",
              borderRadius: "12px",
              backgroundColor: msg.role === "user" ? "#3b82f6" : "#f3f4f6",
              color: msg.role === "user" ? "#ffffff" : "#1f2937",
              whiteSpace: "pre-wrap",
              lineHeight: 1.6
            }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: "20px" }}>
            <div style={{
              padding: "12px 16px",
              borderRadius: "12px",
              backgroundColor: "#f3f4f6",
              color: "#6b7280"
            }}>
              正在思考...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 範例問題區域 */}
      {messages.length <= 1 && (
        <div style={{
          padding: "16px 24px",
          borderTop: "1px solid #e5e7eb",
          backgroundColor: "#f9fafb"
        }}>
          {loadingExamples ? (
            <div style={{ fontSize: "14px", color: "#6b7280", textAlign: "center" }}>
              🔄 正在載入範例問題...（後端啟動中，請稍候）
            </div>
          ) : examples.length > 0 ? (
            <>
              <div style={{ fontSize: "14px", color: "#6b7280", marginBottom: "12px" }}>
                💡 範例問題（點擊試試）：
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {examples.map((ex, idx) => (
                  <button
                    key={idx}
                    onClick={() => sendMessage(ex.question)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: "8px",
                      border: "1px solid #d1d5db",
                      backgroundColor: "#ffffff",
                      fontSize: "13px",
                      cursor: "pointer",
                      transition: "all 0.2s"
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.backgroundColor = "#f3f4f6";
                      e.currentTarget.style.borderColor = "#3b82f6";
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.backgroundColor = "#ffffff";
                      e.currentTarget.style.borderColor = "#d1d5db";
                    }}
                  >
                    {ex.question}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <div style={{ fontSize: "14px", color: "#6b7280", textAlign: "center" }}>
              範例問題載入失敗，但你仍可以直接輸入問題 👇
            </div>
          )}
        </div>
      )}

      {/* 輸入區域 */}
      <div style={{
        padding: "16px 24px",
        borderTop: "1px solid #e5e7eb",
        backgroundColor: "#ffffff"
      }}>
        <div style={{ display: "flex", gap: "12px" }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && !loadingExamples && sendMessage(input)}
            placeholder={loadingExamples ? "後端啟動中，請稍候..." : "輸入你的統計問題..."}
            disabled={loading || loadingExamples}
            style={{
              flex: 1,
              padding: "12px 16px",
              border: "1px solid #d1d5db",
              borderRadius: "8px",
              fontSize: "14px",
              outline: "none",
              backgroundColor: loadingExamples ? "#f9fafb" : "#ffffff",
              cursor: loadingExamples ? "not-allowed" : "text"
            }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={loading || loadingExamples || !input.trim()}
            style={{
              padding: "12px 24px",
              backgroundColor: loading || loadingExamples || !input.trim() ? "#d1d5db" : "#3b82f6",
              color: "#ffffff",
              border: "none",
              borderRadius: "8px",
              fontSize: "14px",
              fontWeight: 600,
              cursor: loading || loadingExamples || !input.trim() ? "not-allowed" : "pointer",
              transition: "background-color 0.2s"
            }}
          >
            {loadingExamples ? "啟動中..." : loading ? "發送中..." : "發送"}
          </button>
        </div>
      </div>
    </main>
  );
}
