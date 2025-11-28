"""
AI モデル仕様データベース
最新のモデル情報とコンテキストウィンドウ制限を管理
"""

MODEL_SPECS = {
    # ==================== OpenAI ====================
    "OpenAI": {
        # 【Update】 2025-11-13 リリースの最新系列
        "gpt-5.1-2025-11-13": {
            "name": "GPT-5.1",
            "input_tokens": 400_000,        # GPT-5 Proと同等だが制御性向上
            "output_tokens": 128_000,
            "description": "最新フラッグシップ。Agenticワークフローに特化。",
            "released": "2025-11-13"
        },
        # 最上位モデル (DevDay発表版)
        "gpt-5-pro-2025-10-06": {
            "name": "GPT-5 Pro",
            "input_tokens": 400_000,
            "output_tokens": 272_000,       # Reasoning強化により出力枠が大きい
            "description": "DevDay 2025発表の重量級モデル。Deep Research等はこれがベース。",
            "released": "2025-10-06"
        },
        "gpt-5-2025-08-07": {
            "name": "GPT-5",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "汎用GPT-5。基本モデル。",
            "released": "2025-08-07"
        },
        # 軽量モデル群
        "gpt-5-mini-2025-08-07": {
            "name": "GPT-5 Mini",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "コストパフォーマンス重視。",
            "released": "2025-08-07"
        },
        "gpt-5-nano-2025-08-07": {
            "name": "GPT-5 Nano",
            "input_tokens": 400_000,
            "output_tokens": 128_000,
            "description": "オンデバイス連携や超高速処理向け。",
            "released": "2025-08-07"
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
            "released": "2025-11-24"        # API IDの日付とリリース日はズレることがあるためID優先
        },
        "claude-sonnet-4-5-20250929": {
            "name": "Claude Sonnet 4.5",
            "input_tokens": 200_000,
            "output_tokens": 64_000,
            "description": "バランス型ハイエンド。New Sonnet。",
            "released": "2025-09-29"
        },
        "claude-haiku-4-5-20251001": {
            "name": "Claude Haiku 4.5",
            "input_tokens": 200_000,
            "output_tokens": 32_000,
            "description": "最速・低コストモデル。",
            "released": "2025-10-01"
        },
    },

    # ==================== Google (Gemini) ====================
    "Google (Gemini)": {
        # 11月20日発表のGemini 3系列
        "gemini-3-pro-preview": {
            "name": "Gemini 3 Pro Preview",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "次世代Gemini 3。マルチモーダル推論強化。",
            "released": "2025-11-20"
        },
        "gemini-2.5-pro": {
            "name": "Gemini 2.5 Pro",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "安定版ハイエンド。長いコンテキストに強い。",
            "released": "2025-06-17"
        },
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "高速・低レイテンシモデル。",
            "released": "2025-06"
        },
        "gemini-2.5-flash-lite": {
            "name": "Gemini 2.5 Flash Lite",
            "input_tokens": 1_048_576,
            "output_tokens": 65_536,
            "description": "最軽量レイテンシモデル。",
            "released": "2025-06"
        },
    }
}


def get_model_info(provider, model_id):
    """
    モデル情報を取得
    
    Returns:
    --------
    dict or None : モデル情報の辞書
    """
    return MODEL_SPECS.get(provider, {}).get(model_id)


def get_available_models(provider):
    """
    プロバイダーの利用可能モデル一覧を取得
    
    Returns:
    --------
    dict : {model_id: model_info}
    """
    return MODEL_SPECS.get(provider, {})


def estimate_input_tokens(text):
    """
    入力テキストのトークン数を概算
    日本語: 約2文字/トークン
    英語: 約4文字/トークン
    
    Returns:
    --------
    int : 推定トークン数
    """
    import re
    
    # 英数字と日本語を分離
    english_chars = len(re.findall(r'[a-zA-Z0-9]', text))
    other_chars = len(text) - english_chars
    
    # 概算計算
    return (english_chars // 4) + (other_chars // 2)


def check_token_compatibility(provider, model_id, input_text):
    """
    入力テキストがモデルのトークン制限に収まるかチェック
    
    Returns:
    --------
    dict : {
        'compatible': bool,
        'estimated_tokens': int,
        'max_tokens': int,
        'usage_percentage': float,
        'compression_needed': bool,
        'status': str  # 'safe', 'warning', 'critical'
    }
    """
    model_info = get_model_info(provider, model_id)
    
    if not model_info:
        return {
            'compatible': False,
            'error': 'Model not found'
        }
    
    estimated_tokens = estimate_input_tokens(input_text)
    
    # 拡張トークン数を優先的に使用
    max_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
    
    usage_percentage = (estimated_tokens / max_tokens) * 100
    
    # ステータス判定
    if usage_percentage < 50:
        status = 'safe'
        compression_needed = False
    elif usage_percentage < 80:
        status = 'warning'
        compression_needed = False
    else:
        status = 'critical'
        compression_needed = True
    
    return {
        'compatible': estimated_tokens < max_tokens,
        'estimated_tokens': estimated_tokens,
        'max_tokens': max_tokens,
        'usage_percentage': usage_percentage,
        'compression_needed': compression_needed,
        'status': status,
        'model_name': model_info['name']
    }


def get_optimal_models(provider, input_text, min_safe_percentage=50):
    """
    入力テキストに最適なモデルを推奨
    
    Parameters:
    -----------
    provider : str
        AIプロバイダー名
    input_text : str
        入力テキスト
    min_safe_percentage : float
        安全とみなす最小使用率（%）
    
    Returns:
    --------
    list : 推奨モデルのリスト（使用率の昇順）
    """
    models = get_available_models(provider)
    estimated_tokens = estimate_input_tokens(input_text)
    
    recommendations = []
    
    for model_id, model_info in models.items():
        max_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
        usage_percentage = (estimated_tokens / max_tokens) * 100
        
        if usage_percentage < 100:  # 使用可能なモデルのみ
            recommendations.append({
                'model_id': model_id,
                'model_name': model_info['name'],
                'usage_percentage': usage_percentage,
                'max_tokens': max_tokens,
                'is_safe': usage_percentage < min_safe_percentage,
                'description': model_info['description']
            })
    
    # 使用率の昇順でソート
    recommendations.sort(key=lambda x: x['usage_percentage'])
    
    return recommendations
