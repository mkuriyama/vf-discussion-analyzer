"""
画像生成モデルの定義
各プロバイダーの画像生成モデルの仕様とコスト情報を管理
"""

IMAGE_MODELS = {
    "OpenAI": {
        "gpt-image-1": {
            "name": "GPT-Image-1",
            "provider": "OpenAI",
            "description": "高品質な画像生成、詳細な指示に対応",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["auto", "low", "medium", "high"],
            "cost_per_image": {
                "1024x1024": {
                    "auto": 0.040,  # 1K output tokens換算: 40/1000 * 1
                    "low": 0.040,
                    "medium": 0.040,
                    "high": 0.040
                },
                "1024x1792": {
                    "auto": 0.072,  # 約1.8K tokens
                    "low": 0.072,
                    "medium": 0.072,
                    "high": 0.072
                },
                "1792x1024": {
                    "auto": 0.072,  # 約1.8K tokens
                    "low": 0.072,
                    "medium": 0.072,
                    "high": 0.072
                }
            },
            "cost_input_per_1m": 5.00,   # USD per 1M input tokens
            "cost_output_per_1m": 40.00,  # USD per 1M output tokens
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "auto"
        },
        "gpt-image-1-mini": {
            "name": "GPT-Image-1-Mini",
            "provider": "OpenAI",
            "description": "コストパフォーマンスに優れた画像生成",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["auto", "low", "medium", "high"],
            "cost_per_image": {
                "1024x1024": {
                    "auto": 0.008,  # 1K output tokens換算: 8/1000 * 1
                    "low": 0.008,
                    "medium": 0.008,
                    "high": 0.008
                },
                "1024x1792": {
                    "auto": 0.014,  # 約1.8K tokens
                    "low": 0.014,
                    "medium": 0.014,
                    "high": 0.014
                },
                "1792x1024": {
                    "auto": 0.014,  # 約1.8K tokens
                    "low": 0.014,
                    "medium": 0.014,
                    "high": 0.014
                }
            },
            "cost_input_per_1m": 2.50,   # USD per 1M input tokens
            "cost_output_per_1m": 8.00,   # USD per 1M output tokens
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "auto"
        }
    },
    "Google (Gemini)": {
        "gemini-3-pro-image-preview": {
            "name": "Gemini 3 Pro Image Preview",
            "provider": "Google (Gemini)",
            "description": "Nano Banana Pro。高品質な画像生成（プレビュー版）",
            "supported_sizes": ["1024x1024", "2048x2048", "4096x4096"],
            "supported_quality": ["1K", "2K", "4K"],
            "cost_per_image": {
                "1024x1024": {
                    "1K": 0.134  # $120/1M tokens * 1.115 tokens per 1K image
                },
                "2048x2048": {
                    "2K": 0.134  # Same as 1K
                },
                "4096x4096": {
                    "4K": 0.240  # $120/1M tokens * 2K tokens per 4K image
                }
            },
            "cost_input_per_1m": 2.00,    # USD per 1M input tokens (text/image)
            "cost_output_per_1m": 120.00,  # USD per 1M output tokens (images)
            "cost_output_text_per_1m": 12.00,  # USD per 1M output tokens (text)
            "max_prompt_length": 8192,
            "default_size": "1024x1024",
            "default_quality": "1K"
        },
        "gemini-2.5-flash-image": {
            "name": "Gemini 2.5 Flash Image",
            "provider": "Google (Gemini)",
            "description": "Nano Banana。高速・低コストな画像生成",
            "supported_sizes": ["1024x1024"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.039  # $0.039 per image
                }
            },
            "cost_input_per_1m": 0.30,   # USD per 1M input tokens
            "cost_output_per_1m": 39.00,  # USD per 1M tokens (calculated from $0.039 per image)
            "max_prompt_length": 8192,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "imagen-4.0-fast-generate-001": {
            "name": "Imagen 4 Fast",
            "provider": "Google (Gemini)",
            "description": "高速な画像生成、最もコスト効率的",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.020
                },
                "1536x1536": {
                    "standard": 0.020
                }
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "imagen-4.0-generate-001": {
            "name": "Imagen 4 Standard",
            "provider": "Google (Gemini)",
            "description": "標準品質の画像生成",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.040
                },
                "1536x1536": {
                    "standard": 0.040
                }
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "imagen-4.0-ultra-generate-001": {
            "name": "Imagen 4 Ultra",
            "provider": "Google (Gemini)",
            "description": "最高品質の画像生成",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["ultra"],
            "cost_per_image": {
                "1024x1024": {
                    "ultra": 0.060
                },
                "1536x1536": {
                    "ultra": 0.060
                }
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "ultra"
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
        'model_id': 'gpt-image-1-mini',
        'size': '1024x1024',
        'quality': 'standard'
    }

