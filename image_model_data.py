"""
画像生成モデルの定義
各プロバイダーの画像生成モデルの仕様とコスト情報を管理
"""

IMAGE_MODELS = {
    "OpenAI": {
        "dall-e-3": {
            "name": "DALL-E 3",
            "provider": "OpenAI",
            "description": "高品質な画像生成、詳細な指示に対応",
            "supported_sizes": ["1024x1024", "1024x1792", "1792x1024"],
            "supported_quality": ["standard", "hd"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.040,  # USD
                    "hd": 0.080
                },
                "1024x1792": {
                    "standard": 0.080,
                    "hd": 0.120
                },
                "1792x1024": {
                    "standard": 0.080,
                    "hd": 0.120
                }
            },
            "max_prompt_length": 4000,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "dall-e-2": {
            "name": "DALL-E 2",
            "provider": "OpenAI",
            "description": "コストパフォーマンスに優れた画像生成",
            "supported_sizes": ["256x256", "512x512", "1024x1024"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "256x256": {
                    "standard": 0.016
                },
                "512x512": {
                    "standard": 0.018
                },
                "1024x1024": {
                    "standard": 0.020
                }
            },
            "max_prompt_length": 1000,
            "default_size": "1024x1024",
            "default_quality": "standard"
        }
    },
    "Google (Gemini)": {
        "imagen-3.0-generate-001": {
            "name": "Imagen 3",
            "provider": "Google (Gemini)",
            "description": "Googleの最新画像生成モデル、高品質",
            "supported_sizes": ["1024x1024", "1536x1536"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.040
                },
                "1536x1536": {
                    "standard": 0.080
                }
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        },
        "imagen-2.0-generate-001": {
            "name": "Imagen 2",
            "provider": "Google (Gemini)",
            "description": "前世代モデル、コスト効率的",
            "supported_sizes": ["1024x1024"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.020
                }
            },
            "max_prompt_length": 2048,
            "default_size": "1024x1024",
            "default_quality": "standard"
        }
    },
    "Stability AI": {
        "stable-diffusion-xl-1024-v1-0": {
            "name": "Stable Diffusion XL",
            "provider": "Stability AI",
            "description": "オープンソース、高品質な画像生成",
            "supported_sizes": ["1024x1024", "1152x896", "896x1152", "1216x832", "832x1216"],
            "supported_quality": ["standard"],
            "cost_per_image": {
                "1024x1024": {
                    "standard": 0.020
                },
                "1152x896": {
                    "standard": 0.020
                },
                "896x1152": {
                    "standard": 0.020
                },
                "1216x832": {
                    "standard": 0.020
                },
                "832x1216": {
                    "standard": 0.020
                }
            },
            "max_prompt_length": 2000,
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
        品質（"standard" or "hd"）
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
        'model_id': 'dall-e-3',
        'size': '1024x1024',
        'quality': 'standard'
    }
