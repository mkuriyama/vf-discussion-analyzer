"""
AI モデル仕様データベース（コスト情報付き）
最新のモデル情報、コンテキストウィンドウ制限、価格情報を管理
"""

MODEL_SPECS = {
    # ==================== OpenAI ====================
    "OpenAI": {
        # 【Update】 2025-12-11 リリースの最新フラッグシップ
        "gpt-5.2-2025-12-11": {
            "name": "GPT-5.2",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。推論機能内蔵（xhigh effort対応）、コーディング・Agentタスクに特化。",
            "released": "2025-12-11",
            "uses_completion_tokens": True,
            "note": "reasoning.effortサポート（none/low/medium/high/xhigh）、temperatureサポートなし",
            "cost_input": 1.75,  # USD per 1M tokens
            "cost_output": 14.00
        },
        # 2025-11-13 リリースの系列
        "gpt-5.1-2025-11-13": {
            "name": "GPT-5.1",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。Agenticワークフローに特化。",
            "released": "2025-11-13",
            "uses_completion_tokens": True,
            "cost_input": 1.25,  # USD per 1M tokens
            "cost_output": 10.00
        },
        "gpt-5-pro-2025-10-06": {
            "name": "GPT-5 Pro",
            "input_tokens": 400_000,
            "output_tokens": 272_000,
            "description": "Deep Research等はこれがベース。TPM: 30,000 tokens/minの制限に注意",
            "released": "2025-10-06",
            "uses_completion_tokens": True,
            "note": "TPM: 30,000 tokens/min",
            "cost_input": 1.25,
            "cost_output": 10.00
        },
        "gpt-5-2025-08-07": {
            "name": "GPT-5",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "汎用GPT-5。基本モデル。",
            "released": "2025-08-07",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし（1固定）",
            "cost_input": 1.25,
            "cost_output": 10.00
        },
        # 軽量モデル群
        "gpt-5-mini-2025-08-07": {
            "name": "GPT-5 Mini",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "コストパフォーマンス重視。",
            "released": "2025-08-07",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし（1固定）",
            "cost_input": 0.25,
            "cost_output": 2.00
        },
        "gpt-5-nano-2025-08-07": {
            "name": "GPT-5 Nano",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "オンデバイス連携や超高速処理向け。",
            "released": "2025-08-07",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし（1固定）",
            "cost_input": 0.05,
            "cost_output": 0.40
        },
        # GPT-4以前
        "gpt-4.1-2025-04-14": {
            "name": "GPT-4.1",
            "input_tokens": 1_047_576,
            "output_tokens": 32_768,
            "description": "高速レスポンス、長文脈処理（最大100万トークン）、コーディング・指示追従能力に特化。",
            "released": "2025-04-14",
            "uses_completion_tokens": False,
            "cost_input": 2.00,
            "cost_output": 8.00
        },
        "gpt-4.1-mini-2025-04-14": {
            "name": "GPT-4.1 mini",
            "input_tokens": 1_047_576,
            "output_tokens": 32_768,
            "description": "GPT-4.1の小型版。速度とコスト効率を重視しつつ、高い推論力を維持。",
            "released": "2025-04-14",
            "uses_completion_tokens": False,
            "cost_input": 0.40,
            "cost_output": 0.10
        },
        "gpt-4.1-nano-2025-04-14": {
            "name": "GPT-4.1 nano",
            "input_tokens": 1_047_576,
            "output_tokens": 32_768,
            "description": "GPT-4.1シリーズで最速・最安価なモデル。軽量タスクや高頻度利用に最適。",
            "released": "2025-04-14",
            "uses_completion_tokens": False,
            "cost_input": 0.10,
            "cost_output": 0.025
        },
    },
    
    # ==================== Anthropic (Claude) ====================
    "Anthropic (Claude)": {
        # Claude 4.7 シリーズ（最新）
        "claude-opus-4-7": {
            "name": "Claude Opus 4.7",
            "input_tokens": 1_000_000,
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。最高インテリジェンス。Adaptive Thinking対応。temperatureサポートなし。",
            "released": "2026-04",
            "cost_input": 5.00,
            "cost_output": 25.00,
            "note": "Adaptive Thinkingのみ対応。temperature/top_p/top_k不可。"
        },
        # Claude 4.6 シリーズ（安定版）
        "claude-opus-4-6": {
            "name": "Claude Opus 4.6",
            "input_tokens": 200_000,
            "output_tokens": 128_000,
            "description": "高インテリジェンス。コーディングと推論に最適化。Adaptive Thinking対応。",
            "released": "2025-12",
            "cost_input": 5.00,
            "cost_output": 25.00
        },
        "claude-sonnet-4-6": {
            "name": "Claude Sonnet 4.6",
            "input_tokens": 200_000,
            "output_tokens": 64_000,
            "description": "速度とインテリジェンスのバランス最良。Adaptive Thinking対応。",
            "released": "2025-12",
            "cost_input": 3.00,
            "cost_output": 15.00
        },
        "claude-haiku-4-5-20251001": {
            "name": "Claude Haiku 4.5",
            "input_tokens": 200_000,
            "output_tokens": 32_000,
            "description": "最速・低コストモデル。",
            "released": "2025-10-01",
            "cost_input": 1.00,
            "cost_output": 5.00
        },
    },
    
    # ==================== Google (Gemini) ====================
    "Google (Gemini)": {
        # 2025-12-17 リリースのGemini 3 Flash
        "gemini-3-flash-preview": {
            "name": "Gemini 3 Flash Preview",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "高速・高性能。Gemini 3 Proレベルの推論をFlashスピードで提供。Thinkingトークン対応。",
            "released": "2025-12-17",
            "cost_input": 0.50,  # ≤200K tokens
            "cost_output": 3.00,
            "note": "Thinkingトークンあり（reasoning levels: minimal/low/medium/high）"
        },
        # 11月20日発表のGemini 3 Pro系列
        "gemini-3-pro-preview": {
            "name": "Gemini 3 Pro Preview",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "次世代最上位モデル",
            "released": "2025-11-20",
            "cost_input": 2.00,  # ≤200K tokens
            "cost_output": 12.00,
            "cost_input_long": 4.00,  # >200K tokens
            "cost_output_long": 18.00,
            "note": "200Kトークン超で価格2倍"
        },
        "gemini-2.5-pro": {
            "name": "Gemini 2.5 Pro",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "安定版ハイエンドモデル",
            "released": "2025-06-17",
            "cost_input": 1.25,
            "cost_output": 10.00
        },
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "高速・低レイテンシモデル。",
            "released": "2025-06",
            "cost_input": 0.30,
            "cost_output": 2.50
        },
        "gemini-2.5-flash-lite": {
            "name": "Gemini 2.5 Flash Lite",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "最軽量レイテンシモデル。",
            "released": "2025-06",
            "cost_input": 0.10,
            "cost_output": 0.40
        },
    }
}

