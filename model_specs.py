"""
AI モデル仕様管理モジュール
モデルデータの取得と操作を行う関数群
"""

from model_data import MODEL_SPECS


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
    """
    入力テキストのトークン数を概算
    多言語対応の推定式:
    - 日本語: 1.5文字 ≈ 1トークン
    - その他: 4文字 ≈ 1トークン
    """
    # 日本語文字（ひらがな、カタカナ、漢字）をカウント
    japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff')
    # それ以外の文字
    other_chars = len(text) - japanese_chars
    
    # 推定トークン数
    # 日本語: 1.5文字 ≈ 1トークン
    # 英語など: 4文字 ≈ 1トークン
    estimated_tokens = int(japanese_chars / 1.5 + other_chars / 4)
    
    return estimated_tokens


def check_token_compatibility(provider, model_id, text_content):
    """
    テキストコンテンツがモデルの制限内かチェック
    
    Returns:
    --------
    dict : {
        'status': str,  # 'safe', 'warning', 'danger'
        'estimated_tokens': int,
        'max_tokens': int,
        'usage_percentage': float,
        'compression_needed': bool
    }
    """
    model_info = get_model_info(provider, model_id)
    if not model_info:
        return {
            'status': 'danger',
            'estimated_tokens': 0,
            'max_tokens': 0,
            'usage_percentage': 100.0,
            'compression_needed': True
        }
    
    # トークン数を推定
    estimated_tokens = estimate_input_tokens(text_content)
    max_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
    
    # 使用率を計算
    usage_percentage = (estimated_tokens / max_tokens) * 100
    
    # ステータスを決定
    if usage_percentage < 60:
        status = 'safe'
        compression_needed = False
    elif usage_percentage < 80:
        status = 'warning'
        compression_needed = False
    else:
        status = 'danger'
        compression_needed = True
    
    return {
        'status': status,
        'estimated_tokens': estimated_tokens,
        'max_tokens': max_tokens,
        'usage_percentage': usage_percentage,
        'compression_needed': compression_needed
    }


def get_optimal_models(provider, text_content, budget_per_1m_tokens=None):
    """
    テキストコンテンツに適したモデルを提案
    
    Parameters:
    -----------
    provider : str
        現在のプロバイダー
    text_content : str
        テキストコンテンツ
    budget_per_1m_tokens : float, optional
        予算上限（USD per 1M tokens）
    
    Returns:
    --------
    list of dict : [{
        'model_name': str,
        'model_id': str,
        'provider': str,
        'is_safe': bool,
        'usage_percentage': float,
        'max_tokens': int,
        'cost_input': float,
        'cost_output': float
    }]
    """
    estimated_tokens = estimate_input_tokens(text_content)
    suitable_models = []
    
    # 同じプロバイダーのモデルのみを対象
    if provider in MODEL_SPECS:
        for model_id, info in MODEL_SPECS[provider].items():
            max_tokens = info.get('input_tokens_extended', info['input_tokens'])
            usage_percentage = (estimated_tokens / max_tokens) * 100
            is_safe = usage_percentage < 80
            
            cost_input = info.get('cost_input', 0)
            
            # 予算チェック
            if budget_per_1m_tokens is None or cost_input <= budget_per_1m_tokens:
                suitable_models.append({
                    'model_name': info['name'],
                    'model_id': model_id,
                    'provider': provider,
                    'is_safe': is_safe,
                    'usage_percentage': usage_percentage,
                    'max_tokens': max_tokens,
                    'cost_input': cost_input,
                    'cost_output': info.get('cost_output', 0)
                })
    
    # 安全性とコスト順にソート（安全なモデルを優先、次にコスト）
    suitable_models.sort(key=lambda x: (not x['is_safe'], x['cost_input']))
    
    return suitable_models
