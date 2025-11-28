"""
AI モデル仕様データベース
最新のモデル情報とコンテキストウィンドウ制限を管理
"""

MODEL_SPECS = {
    # ==================== OpenAI ====================
    "OpenAI": {
        # GPT-5 シリーズ
        "gpt-5-2025-08-07": {
            "name": "GPT-5",
            "input_tokens": 272_000,
            "output_tokens": 128_000,
            "description": "最新の統合モデル。自動的に推論を調整",
            "released": "2025-08"
        },
        "gpt-5-mini-2025-08-07": {
            "name": "GPT-5 Mini",
            "input_tokens": 272_000,
            "output_tokens": 128_000,
            "description": "高速で経済的なバージョン",
            "released": "2025-08"
        },
        "gpt-5-nano-2025-08-07": {
            "name": "GPT-5 Nano",
            "input_tokens": 272_000,
            "output_tokens": 128_000,
            "description": "最も軽量で高速なバージョン",
            "released": "2025-08"
        },
        
        # GPT-5.1 シリーズ
        "gpt-5.1-2025": {
            "name": "GPT-5.1",
            "input_tokens": 272_000,
            "output_tokens": 128_000,
            "description": "GPT-5の改良版。より会話的で高速",
            "released": "2025-11"
        },
        
        # GPT-4.1 シリーズ
        "gpt-4.1-2025-01-15": {
            "name": "GPT-4.1",
            "input_tokens": 1_000_000,
            "output_tokens": 32_768,
            "description": "100万トークン対応。長文処理に最適",
            "released": "2025-01"
        },
        "gpt-4.1-mini-2025-01-15": {
            "name": "GPT-4.1 Mini",
            "input_tokens": 1_000_000,
            "output_tokens": 32_768,
            "description": "GPT-4.1の経済版",
            "released": "2025-01"
        },
        "gpt-4.1-nano-2025-01-15": {
            "name": "GPT-4.1 Nano",
            "input_tokens": 1_000_000,
            "output_tokens": 32_768,
            "description": "最高速・最低コスト版",
            "released": "2025-01"
        },
        
        # GPT-4o シリーズ
        "gpt-4o-2024-11-20": {
            "name": "GPT-4o (2024-11-20)",
            "input_tokens": 128_000,
            "output_tokens": 16_384,
            "description": "マルチモーダル対応の高性能版",
            "released": "2024-11"
        },
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "input_tokens": 128_000,
            "output_tokens": 16_384,
            "description": "コスト効率重視版",
            "released": "2024-07"
        },
        
        # o1 シリーズ（推論特化）
        "o1-preview": {
            "name": "o1 Preview",
            "input_tokens": 128_000,
            "output_tokens": 32_768,
            "description": "高度な推論タスクに特化",
            "released": "2024-09"
        },
        "o1-mini": {
            "name": "o1 Mini",
            "input_tokens": 128_000,
            "output_tokens": 65_536,
            "description": "効率的な推論モデル",
            "released": "2024-09"
        },
    },
    
    # ==================== Anthropic (Claude) ====================
    "Anthropic (Claude)": {
        # Claude Sonnet 4 シリーズ
        "claude-sonnet-4-20250514": {
            "name": "Claude Sonnet 4",
            "input_tokens": 200_000,
            "input_tokens_extended": 1_000_000,  # Beta機能
            "output_tokens": 16_384,
            "description": "最新Claude。100万トークン対応（Beta）",
            "released": "2025-05",
            "note": "1M tokens requires beta header: context-1m-2025-08-07"
        },
        "claude-sonnet-4.5-20250929": {
            "name": "Claude Sonnet 4.5",
            "input_tokens": 200_000,
            "input_tokens_extended": 1_000_000,  # Beta機能
            "output_tokens": 16_384,
            "description": "エージェントタスクに最適化",
            "released": "2025-09",
            "note": "1M tokens requires beta header"
        },
        
        # Claude 3.5 シリーズ
        "claude-3-5-sonnet-20241022": {
            "name": "Claude 3.5 Sonnet",
            "input_tokens": 200_000,
            "output_tokens": 8_192,
            "description": "バランスの取れた高性能版",
            "released": "2024-10"
        },
        "claude-3-5-haiku-20241022": {
            "name": "Claude 3.5 Haiku",
            "input_tokens": 200_000,
            "output_tokens": 8_192,
            "description": "高速・低コスト版",
            "released": "2024-10"
        },
        
        # Claude 3 シリーズ
        "claude-3-opus-20240229": {
            "name": "Claude 3 Opus",
            "input_tokens": 200_000,
            "output_tokens": 4_096,
            "description": "最高性能（旧世代）",
            "released": "2024-02"
        },
        "claude-3-sonnet-20240229": {
            "name": "Claude 3 Sonnet",
            "input_tokens": 200_000,
            "output_tokens": 4_096,
            "description": "バランス型（旧世代）",
            "released": "2024-02"
        },
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku",
            "input_tokens": 200_000,
            "output_tokens": 4_096,
            "description": "高速版（旧世代）",
            "released": "2024-03"
        },
    },
    
    # ==================== Google (Gemini) ====================
    "Google (Gemini)": {
        # Gemini 3 シリーズ
        "gemini-3-pro-preview-11-2025": {
            "name": "Gemini 3 Pro (Preview)",
            "input_tokens": 1_048_576,  # 1M tokens
            "output_tokens": 65_535,
            "description": "最新Preview版。100万トークン対応",
            "released": "2025-11",
            "note": "Preview版 - 変更の可能性あり"
        },
        
        # Gemini 2.5 シリーズ
        "gemini-2.5-pro": {
            "name": "Gemini 2.5 Pro",
            "input_tokens": 1_048_576,  # 1M tokens
            "output_tokens": 65_535,
            "description": "高性能版。超長文処理対応",
            "released": "2025-05"
        },
        "gemini-2.5-flash": {
            "name": "Gemini 2.5 Flash",
            "input_tokens": 1_048_576,  # 1M tokens
            "output_tokens": 65_535,
            "description": "高速・経済版",
            "released": "2025-05"
        },
        "gemini-2.0-flash-exp": {
            "name": "Gemini 2.0 Flash (Experimental)",
            "input_tokens": 1_048_576,  # 1M tokens
            "output_tokens": 65_535,
            "description": "実験版。最新機能をテスト",
            "released": "2024-12"
        },
        
        # Gemini 1.5 シリーズ
        "gemini-1.5-pro": {
            "name": "Gemini 1.5 Pro",
            "input_tokens": 2_097_152,  # 2M tokens
            "output_tokens": 65_535,
            "description": "200万トークン対応の超長文版",
            "released": "2024-05",
            "note": "2M tokens available to all developers"
        },
        "gemini-1.5-flash": {
            "name": "Gemini 1.5 Flash",
            "input_tokens": 1_048_576,  # 1M tokens
            "output_tokens": 65_535,
            "description": "高速処理版",
            "released": "2024-05"
        },
        
        # Gemini 1.0 シリーズ
        "gemini-1.0-pro": {
            "name": "Gemini 1.0 Pro",
            "input_tokens": 32_768,
            "output_tokens": 8_192,
            "description": "初期版（レガシー）",
            "released": "2023-12"
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
