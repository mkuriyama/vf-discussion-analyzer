"""
AI モデル仕様データベース（コスト情報付き）
最新のモデル情報、コンテキストウィンドウ制限、価格情報を管理
"""

MODEL_SPECS = {
    # ==================== OpenAI ====================
    "OpenAI": {
        # 【Update】 2025-11-13 リリースの最新系列
        "gpt-5.1-2025-11-13": {
            "name": "GPT-5.1",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。Agenticワークフローに特化。",
            "released": "2025-11-13",
            "uses_completion_tokens": True,
            "note": "アクセスには登録が必要",
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
    },

    # ==================== Anthropic (Claude) ====================
    # ID形式修正: バージョンのドット→ハイフン、日付→YYYYMMDD
    "Anthropic (Claude)": {
        "claude-opus-4-5-20251101": {
            "name": "Claude Opus 4.5",
            "input_tokens": 200_000,
            "output_tokens": 64_000,        # コーディング・エージェント特化
            "description": "2025年11月リリースの最上位モデル。エージェント性能最高峰。",
            "released": "2025-11-01",
            "cost_input": 5.00,
            "cost_output": 25.00
        },
        "claude-sonnet-4-5-20250929": {
            "name": "Claude Sonnet 4.5",
            "input_tokens": 200_000,
            "output_tokens": 64_000,
            "description": "バランス型・コーディング最適",
            "released": "2025-09-29",
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
        # 11月20日発表のGemini 3系列
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


def get_available_models(provider=None):
    """利用可能なモデル一覧を取得"""
    if provider:
        return MODEL_SPECS.get(provider, {})
    return MODEL_SPECS


def get_model_info(provider, model_id):
    """特定のモデル情報を取得"""
    if provider in MODEL_SPECS and model_id in MODEL_SPECS[provider]:
        return MODEL_SPECS[provider][model_id]
    return None


def estimate_input_tokens(text):
    """入力テキストのトークン数を概算（1トークン≈4文字）"""
    return len(text) // 4


def check_token_compatibility(provider, model_id, estimated_tokens):
    """トークン数がモデルの制限内かチェック"""
    model_info = get_model_info(provider, model_id)
    if not model_info:
        return False, "モデル情報が見つかりません"
    
    max_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
    
    if estimated_tokens > max_tokens:
        return False, f"トークン数が制限を超えています（推定: {estimated_tokens:,}、上限: {max_tokens:,}）"
    
    return True, "OK"


def get_optimal_models(estimated_tokens, budget_per_1m_tokens=None):
    """推定トークン数と予算に基づいて最適なモデルを提案"""
    suitable_models = []
    
    for provider, models in MODEL_SPECS.items():
        for model_id, info in models.items():
            max_tokens = info.get('input_tokens_extended', info['input_tokens'])
            
            if estimated_tokens <= max_tokens:
                cost_input = info.get('cost_input', 0)
                
                if budget_per_1m_tokens is None or cost_input <= budget_per_1m_tokens:
                    suitable_models.append({
                        'provider': provider,
                        'model_id': model_id,
                        'name': info['name'],
                        'max_tokens': max_tokens,
                        'cost_input': cost_input,
                        'cost_output': info.get('cost_output', 0)
                    })
    
    # コスト順にソート
    suitable_models.sort(key=lambda x: x['cost_input'])
    
    return suitable_models
