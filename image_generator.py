"""
画像生成機能
テキストから画像を生成するための機能を提供
"""

import os
import base64
from io import BytesIO
from PIL import Image
import requests

def generate_image_openai(prompt, api_key, model="dall-e-3", size="1024x1024", quality="standard"):
    """
    OpenAI DALL-Eで画像を生成
    
    Parameters:
    -----------
    prompt : str
        画像生成プロンプト（英語）
    api_key : str
        OpenAI APIキー
    model : str
        モデル名（"dall-e-3" or "dall-e-2"）
    size : str
        画像サイズ
    quality : str
        品質（"standard" or "hd"）
    
    Returns:
    --------
    dict : {
        'image_url': str,  # 画像URL（一時的）
        'image_data': bytes,  # 画像データ
        'revised_prompt': str,  # 改善されたプロンプト（DALL-E 3のみ）
        'size': str,
        'model': str
    }
    """
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # DALL-E 3の場合
        if model == "dall-e-3":
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else prompt
            
        # DALL-E 2の場合
        else:
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = prompt
        
        # 画像をダウンロード
        image_response = requests.get(image_url)
        image_data = image_response.content
        
        return {
            'image_url': image_url,
            'image_data': image_data,
            'revised_prompt': revised_prompt,
            'size': size,
            'model': model,
            'quality': quality
        }
        
    except Exception as e:
        raise Exception(f"OpenAI画像生成エラー: {str(e)}")

def generate_image_google(prompt, api_key, model="imagen-4.0-generate-001", size="1024x1024", quality="standard"):
    """
    Google Imagenで画像を生成
    
    Parameters:
    -----------
    prompt : str
        画像生成プロンプト
    api_key : str
        Google APIキー
    model : str
        モデル名
    size : str
        画像サイズ
    quality : str
        品質（Imagen 4では使用されないが、インターフェース統一のため）
    
    Returns:
    --------
    dict : 画像生成結果
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # モデル名からImagenのバージョンを判定
        if "imagen-4" in model:
            # Imagen 4シリーズ
            imagen_model = genai.ImageGenerationModel(model)
            
            # 画像生成
            response = imagen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1" if size == "1024x1024" else "4:3",
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )
            
            # 生成された画像を取得
            image = response.images[0]
            
            # 画像データを取得（PIL ImageまたはBytes）
            if hasattr(image, '_pil_image'):
                # PIL Imageの場合
                from io import BytesIO
                img_byte_arr = BytesIO()
                image._pil_image.save(img_byte_arr, format='PNG')
                image_data = img_byte_arr.getvalue()
            elif hasattr(image, '_image_bytes'):
                # Bytesの場合
                image_data = image._image_bytes
            else:
                # その他の場合は画像URLからダウンロード
                import requests
                if hasattr(image, 'url'):
                    img_response = requests.get(image.url)
                    image_data = img_response.content
                else:
                    raise Exception("画像データの取得に失敗しました")
            
            return {
                'image_url': None,
                'image_data': image_data,
                'revised_prompt': prompt,  # Imagenはプロンプトを変更しない
                'size': size,
                'model': model,
                'quality': quality
            }
            
        elif "gemini" in model.lower():
            # Gemini画像生成モデル
            # Gemini 2.5 Flash Image または Gemini 3 Pro Image
            gen_model = genai.GenerativeModel(model)
            
            # 画像生成プロンプトを構築
            generation_config = {
                "temperature": 0.4,
                "max_output_tokens": 8192,
            }
            
            # 画像生成を指示
            response = gen_model.generate_content(
                f"Generate an image: {prompt}",
                generation_config=generation_config
            )
            
            # 生成された画像を取得
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # 画像パーツを探す
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Base64デコード
                        import base64
                        image_data = base64.b64decode(part.inline_data.data)
                        
                        return {
                            'image_url': None,
                            'image_data': image_data,
                            'revised_prompt': prompt,
                            'size': size,
                            'model': model,
                            'quality': quality
                        }
            
            raise Exception("画像生成レスポンスに画像データが含まれていません")
        
        else:
            raise Exception(f"サポートされていないモデル: {model}")
        
    except Exception as e:
        raise Exception(f"Google画像生成エラー: {str(e)}")

def generate_image_stability(prompt, api_key, model="stable-diffusion-xl-1024-v1-0", size="1024x1024"):
    """
    Stability AI Stable Diffusionで画像を生成
    
    Parameters:
    -----------
    prompt : str
        画像生成プロンプト
    api_key : str
        Stability AI APIキー
    model : str
        モデル名
    size : str
        画像サイズ
    
    Returns:
    --------
    dict : 画像生成結果
    """
    try:
        # Stability AI APIの呼び出し
        width, height = map(int, size.split('x'))
        
        url = f"https://api.stability.ai/v1/generation/{model}/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Base64デコード
        image_data = base64.b64decode(data['artifacts'][0]['base64'])
        
        return {
            'image_url': None,
            'image_data': image_data,
            'revised_prompt': prompt,
            'size': size,
            'model': model,
            'quality': 'standard'
        }
        
    except Exception as e:
        raise Exception(f"Stability AI画像生成エラー: {str(e)}")

def generate_image(prompt, provider, model, api_key, size="1024x1024", quality="standard"):
    """
    プロバイダーに応じて画像を生成
    
    Parameters:
    -----------
    prompt : str
        画像生成プロンプト
    provider : str
        プロバイダー名
    model : str
        モデル名
    api_key : str
        APIキー
    size : str
        画像サイズ
    quality : str
        品質
    
    Returns:
    --------
    dict : 画像生成結果
    """
    if provider == "OpenAI":
        return generate_image_openai(prompt, api_key, model, size, quality)
    elif provider == "Google (Gemini)":
        return generate_image_google(prompt, api_key, model, size, quality)
    elif provider == "Stability AI":
        return generate_image_stability(prompt, api_key, model, size)
    else:
        raise ValueError(f"サポートされていないプロバイダー: {provider}")

def save_image_to_bytes(image_data):
    """
    画像データをBytesIOオブジェクトに変換
    
    Parameters:
    -----------
    image_data : bytes
        画像データ
    
    Returns:
    --------
    BytesIO : 画像のBytesIOオブジェクト
    """
    return BytesIO(image_data)

def get_image_base64(image_data):
    """
    画像データをBase64エンコード
    
    Parameters:
    -----------
    image_data : bytes
        画像データ
    
    Returns:
    --------
    str : Base64エンコードされた画像
    """
    return base64.b64encode(image_data).decode('utf-8')
