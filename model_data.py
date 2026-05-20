"""
AI モデル仕様データベース（コスト情報付き）
最新のモデル情報、コンテキストウィンドウ制限、価格情報を管理
"""

MODEL_SPECS = {
    # ==================== OpenAI ====================
    "OpenAI": {
        # GPT-5.5 シリーズ（2026-04 リリース）
        "gpt-5.5-pro": {
            "name": "GPT-5.5 Pro",
            "input_tokens": 1_000_000,
            "output_tokens": 128_000,
            "description": "最上位プレミアムモデル。最高インテリジェンス。272K超で2x/1.5x課金。",
            "released": "2026-04-24",
            "uses_completion_tokens": True,
            "note": "272Kトークン超で入力2x・出力1.5x。reasoning.effortサポート。",
            "cost_input": 30.00,
            "cost_output": 180.00
        },
        "gpt-5.4-pro": {
            "name": "GPT-5.4 Pro",
            "input_tokens": 1_000_000,
            "output_tokens": 128_000,
            "description": "GPT-5.4の最上位版。最高品質・高度な推論タスク向け。272K超で2x/1.5x課金。",
            "released": "2026-03-05",
            "uses_completion_tokens": True,
            "note": "272Kトークン超で入力2x・出力1.5x。temperatureサポートなし。",
            "cost_input": 30.00,
            "cost_output": 180.00
        },
        "gpt-5.5": {
            "name": "GPT-5.5",
            "input_tokens": 1_000_000,
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。Agentワークフロー・コーディング特化。ネイティブcomputer use対応。272K超で2x/1.5x課金。",
            "released": "2026-04-23",
            "uses_completion_tokens": True,
            "note": "272Kトークン超で入力2x・出力1.5x。reasoning.effortサポート。temperatureサポートなし。",
            "cost_input": 5.00,
            "cost_output": 30.00
        },
        # GPT-5.4 シリーズ（2026-03 リリース）
        "gpt-5.4": {
            "name": "GPT-5.4",
            "input_tokens": 1_000_000,
            "output_tokens": 128_000,
            "description": "本番ワークホース。ネイティブcomputer use対応。272K超で2x/1.5x課金。",
            "released": "2026-03-05",
            "uses_completion_tokens": True,
            "note": "272Kトークン超で入力2x・出力1.5x。temperatureサポートなし。",
            "cost_input": 2.50,
            "cost_output": 15.00
        },
        "gpt-5.4-mini": {
            "name": "GPT-5.4 Mini",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "コーディング・computer use・ツール呼び出し・画像推論に最適化。高コスパ。",
            "released": "2026-03-17",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし。",
            "cost_input": 0.75,
            "cost_output": 4.50
        },
        "gpt-5.4-nano": {
            "name": "GPT-5.4 Nano",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "高スループット・低レイテンシ向け。分類・データ抽出・サブエージェントに最適。",
            "released": "2026-03-17",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし。",
            "cost_input": 0.20,
            "cost_output": 1.25
        },
        # GPT-5.2 シリーズ（2025-12 リリース）
        "gpt-5.2-2025-12-11": {
            "name": "GPT-5.2",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "推論機能内蔵（xhigh effort対応）、コーディング・Agentタスクに特化。",
            "released": "2025-12-11",
            "uses_completion_tokens": True,
            "note": "reasoning.effortサポート（none/low/medium/high/xhigh）、temperatureサポートなし",
            "cost_input": 1.75,
            "cost_output": 14.00
        },
        # GPT-5 軽量シリーズ（2025-08 リリース）—— 最安価オプション
        "gpt-5-mini-2025-08-07": {
            "name": "GPT-5 Mini",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "5.4-miniより安価な軽量モデル。コストパフォーマンス重視。",
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
            "description": "最安価テキストモデル。オンデバイス連携や超高速処理向け。",
            "released": "2025-08-07",
            "uses_completion_tokens": True,
            "note": "temperatureサポートなし（1固定）",
            "cost_input": 0.05,
            "cost_output": 0.40
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
        # Gemini 3.5 シリーズ（2026-05 GA）
        "gemini-3.5-flash": {
            "name": "Gemini 3.5 Flash",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "最新Flashモデル。Gemini 3.1 Pro超えのコーディング・Agentベンチマーク。Dynamic Thinking対応。4x高速。",
            "released": "2026-05-19",
            "cost_input": 1.50,
            "cost_output": 9.00,
            "note": "Dynamic Thinking対応（minimal/low/medium/high）"
        },
        # Gemini 3.1 シリーズ（2026-03〜04）
        "gemini-3.1-pro-preview": {
            "name": "Gemini 3.1 Pro Preview",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "マルチモーダル・エージェント・コーディング最高峰。200K超で価格2倍。",
            "released": "2026-04",
            "cost_input": 2.00,
            "cost_output": 12.00,
            "cost_input_long": 4.00,
            "cost_output_long": 18.00,
            "note": "200Kトークン超で入力$4/出力$18。無料枠なし。"
        },
        "gemini-3.1-flash-lite": {
            "name": "Gemini 3.1 Flash Lite",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "最もコスト効率的なモデル。高ボリューム・低レイテンシ向け。Thinking対応。",
            "released": "2026-03-03",
            "cost_input": 0.25,
            "cost_output": 1.50,
            "note": "Thinking対応。2.5 Flash Liteより2.5x高速。"
        },
        # Gemini 2.5 シリーズ（コスト優位で継続）
        "gemini-2.5-pro": {
            "name": "Gemini 2.5 Pro",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "安定版ハイエンドモデル。3.1 Proより入力コスト優位（$1.25 vs $2.00）。",
            "released": "2025-06-17",
            "cost_input": 1.25,
            "cost_output": 10.00
        },
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "安定版Flashモデル。3.1 Flashより安価（$0.30 vs $0.50）。",
            "released": "2025-06",
            "cost_input": 0.30,
            "cost_output": 2.50
        },
        "gemini-2.5-flash-lite": {
            "name": "Gemini 2.5 Flash Lite",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "最安価Geminiモデル。3.1 Flash Liteより安価（$0.10 vs $0.25）。",
            "released": "2025-06",
            "cost_input": 0.10,
            "cost_output": 0.40
        },
    }
}
