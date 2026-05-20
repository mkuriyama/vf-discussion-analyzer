"""
画像生成モデルの定義
各プロバイダーの画像生成モデルの仕様とコスト情報を管理
"""

IMAGE_MODELS = {
    "OpenAI": {
        "gpt-image-2": {
            "name": "GPT-Image-2",
            "provider": "OpenAI",
            "description": "最新フラッグシップ画像生成。詳細な指示・編集対応。2026-04-21リリース。",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["auto", "low", "medium", "high"],
            "cost_per_image": {
                "1024x1024": {
                    "auto":   0.053,
                    "low":    0.006,
                    "medium": 0.053,
                    "high":   0.211
                },
                "1024x1792": {
                    "auto":   0.093,
                    "low":    0.011,
                    "medium": 0.093,
                    "high":   0.370
                },
                "1792x1024": {
                    "auto":   0.093,
                    "low":    0.011,
                    "medium": 0.093,
                    "high":   0.370
                }
            },
            "cost_input_per_1m": 5.00,    # USD per 1M text input tokens
            "cost_image_input_per_1m": 8.00,   # USD per 1M image input tokens
            "cost_output_per_1m": 30.00,   # USD per 1M image output tokens
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "medium"
        },
        "gpt-image-1.5": {
            "name": "GPT-Image-1.5",
            "provider": "OpenAI",
            "description": "gpt-image-2より安価な画像生成。テキスト出力も対応。2025-12リリース。",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["auto", "low", "medium", "high"],
            "cost_per_image": {
                "1024x1024": {
                    "auto":   0.057,
                    "low":    0.006,
                    "medium": 0.057,
                    "high":   0.225
                },
                "1024x1792": {
                    "auto":   0.100,
                    "low":    0.011,
                    "medium": 0.100,
                    "high":   0.394
                },
                "1792x1024": {
                    "auto":   0.100,
                    "low":    0.011,
                    "medium": 0.100,
                    "high":   0.394
                }
            },
            "cost_input_per_1m": 5.00,
            "cost_image_input_per_1m": 8.00,
            "cost_output_per_1m": 32.00,
            "cost_output_text_per_1m": 10.00,
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "medium"
        },
        "gpt-image-1-mini": {
            "name": "GPT-Image-1 Mini",
            "provider": "OpenAI",
            "description": "コストパフォーマンスに優れた画像生成。gpt-image-2より安価。",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["auto", "low", "medium", "high"],
            "cost_per_image": {
                "1024x1024": {
                    "auto":   0.008,
                    "low":    0.008,
                    "medium": 0.008,
                    "high":   0.008
                },
                "1024x1792": {
                    "auto":   0.014,
                    "low":    0.014,
                    "medium": 0.014,
                    "high":   0.014
                },
                "1792x1024": {
                    "auto":   0.014,
                    "low":    0.014,
                    "medium": 0.014,
                    "high":   0.014
                }
            },
            "cost_input_per_1m": 2.50,
            "cost_output_per_1m": 8.00,
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "auto"
        }
    },
    "Google (Gemini)": {
        "gemini-3.1-flash-image-preview": {
            "name": "Gemini 3.1 Flash Image Preview",
            "provider": "Google (Gemini)",
            "description": "最新Flash画像生成モデル。0.5K〜4K解像度対応。2026-02-26リリース。",
            "supported_sizes": ["512x512", "1024x1024", "2048x2048", "4096x4096"],
            "supported_quality": ["0.5K", "1K", "2K", "4K"],
            "cost_per_image": {
                "512x512":   {"0.5K": 0.045},
                "1024x1024": {"1K":   0.067},
                "2048x2048": {"2K":   0.101},
                "4096x4096": {"4K":   0.151}
            },
            "cost_input_per_1m": 0.50,     # USD per 1M text/image input tokens
            "cost_output_per_1m": 60.00,   # USD per 1M image output tokens
            "cost_output_text_per_1m": 3.00,  # USD per 1M text/thinking output tokens
            "max_prompt_length": 8192,
            "default_size": "1024x1024",
            "default_quality": "1K"
        },
        "gemini-2.5-flash-image": {
            "name": "Gemini 2.5 Flash Image",
            "provider": "Google (Gemini)",
            "description": "2.5 Flashベースの画像生成。$0.039/枚と最安価。1024x1024まで対応。",
            "supported_sizes": ["1024x1024"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {"standard": 0.039}  # $30/1M * 1,290 tokens
            },
            "cost_input_per_1m": 0.30,    # USD per 1M text/image input tokens
            "cost_output_per_1m": 30.00,  # USD per 1M image output tokens (1,290 tokens per image)
            "max_prompt_length": 8192,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "gemini-3-pro-image-preview": {
            "name": "Gemini 3 Pro Image Preview",
            "provider": "Google (Gemini)",
            "description": "高品質な画像生成。最高品質オプション。",
            "supported_sizes": ["1024x1024", "2048x2048", "4096x4096"],
            "supported_quality": ["1K", "2K", "4K"],
            "cost_per_image": {
                "1024x1024": {"1K": 0.134},
                "2048x2048": {"2K": 0.134},
                "4096x4096": {"4K": 0.240}
            },
            "cost_input_per_1m": 2.00,
            "cost_output_per_1m": 120.00,
            "cost_output_text_per_1m": 12.00,
            "max_prompt_length": 8192,
            "default_size": "1024x1024",
            "default_quality": "1K"
        },
        "imagen-4.0-ultra-generate-001": {
            "name": "Imagen 4 Ultra",
            "provider": "Google (Gemini)",
            "description": "Imagen 4最高品質。フォトリアリスティック・アート表現に最適。",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["ultra"],
            "cost_per_image": {
                "1024x1024": {"ultra": 0.060},
                "1536x1536": {"ultra": 0.060}
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "ultra"
        },
        "imagen-4.0-generate-001": {
            "name": "Imagen 4 Standard",
            "provider": "Google (Gemini)",
            "description": "Imagen 4標準品質。バランスの取れた画像生成。",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {"standard": 0.040},
                "1536x1536": {"standard": 0.040}
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "imagen-4.0-fast-generate-001": {
            "name": "Imagen 4 Fast",
            "provider": "Google (Gemini)",
            "description": "Imagen 4最速・最安価。高ボリューム・コスト効率重視。",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {"standard": 0.020},
                "1536x1536": {"standard": 0.020}
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        }
    }
}


def get_image_providers():
    """画像生成プロバイダーの一覧を取得"""
    return list(IMAGE_MODELS.keys())

def get_image_models_by_provider(provider):
    """指定プロバイダーの画像生成モデル一覧を取得"""
    return IMAGE_MODELS.get(provider, {})

def get_image_model_info(provider, model_id):
    """画像生成モデルの詳細情報を取得"""
    provider_models = IMAGE_MODELS.get(provider, {})
    return provider_models.get(model_id)

def calculate_image_cost(provider, model_id, size, quality, num_images=1):
    """
    画像生成のコストを計算

    Parameters:
    -----------
    provider : str
        プロバイダー名
    model_id : str
        モデルID
    size : str
        画像サイズ（例: "1024x1024"）
    quality : str
        品質（"standard", "1K", "2K", "4K", "ultra"など）
    num_images : int
        生成枚数

    Returns:
    --------
    float : コスト（USD）
    """
    model_info = get_image_model_info(provider, model_id)
    if not model_info:
        return 0.0

    cost_structure = model_info.get("cost_per_image", {})
    size_costs = cost_structure.get(size, {})
    cost_per_image = size_costs.get(quality, 0.0)

    return cost_per_image * num_images

def get_all_image_models():
    """すべての画像生成モデルを取得（プロバイダー別）"""
    all_models = []
    for provider, models in IMAGE_MODELS.items():
        for model_id, info in models.items():
            all_models.append({
                'provider': provider,
                'model_id': model_id,
                'name': info['name'],
                'description': info['description']
            })
    return all_models

def get_default_image_model():
    """デフォルトの画像生成モデルを取得"""
    return {
        'provider': 'OpenAI',
        'model_id': 'gpt-image-2',
        'size': '1024x1024',
        'quality': 'medium'
    }
