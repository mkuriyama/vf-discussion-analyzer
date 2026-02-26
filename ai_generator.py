"""
AIレポート生成モジュール
複数のAIプロバイダー（OpenAI、Anthropic、Google）をサポート
"""

import os
import re


def estimate_tokens(text):
    """テキストのトークン数を概算（英語: 4文字/トークン、日本語: 2文字/トークン）"""
    # 簡易的な推定
    english_chars = len(re.findall(r'[a-zA-Z0-9]', text))
    other_chars = len(text) - english_chars
    return (english_chars // 4) + (other_chars // 2)


def compress_markdown_for_model(md_content, max_tokens=30000):
    """
    Markdownコンテンツをモデルのトークン制限内に圧縮
    
    Parameters:
    -----------
    md_content : str
        元のMarkdownコンテンツ
    max_tokens : int
        最大トークン数
    
    Returns:
    --------
    str : 圧縮されたコンテンツ
    """
    current_tokens = estimate_tokens(md_content)
    
    if current_tokens <= max_tokens:
        return md_content
    
    # セクション分割
    lines = md_content.split('\n')
    
    # 重要なセクションを特定
    important_sections = []
    current_section = []
    in_important = False
    
    for line in lines:
        # 重要なヘッダー（統計、設問一覧、回答者一覧）
        if any(keyword in line for keyword in ['## 統計情報', '## 設問一覧', '## 回答者一覧', '## ドキュメント情報']):
            if current_section:
                if in_important:
                    important_sections.append('\n'.join(current_section))
                current_section = []
            in_important = True
            current_section.append(line)
        # 詳細セクションの開始
        elif '## 議論内容詳細' in line:
            if current_section and in_important:
                important_sections.append('\n'.join(current_section))
            in_important = False
            current_section = []
        else:
            current_section.append(line)
    
    if current_section and in_important:
        important_sections.append('\n'.join(current_section))
    
    # 重要セクションのみで構成
    compressed = '\n\n'.join(important_sections)
    
    # まだ大きい場合はさらに削減
    if estimate_tokens(compressed) > max_tokens:
        # 最初の部分のみ
        compressed_lines = compressed.split('\n')
        target_lines = int(len(compressed_lines) * (max_tokens / estimate_tokens(compressed)))
        compressed = '\n'.join(compressed_lines[:target_lines])
        compressed += '\n\n[... 残りのデータは省略されました ...]'
    
    return compressed


def generate_report(md_content, instruction, api_key, model, provider="OpenAI", max_tokens=None):
    """
    Markdownコンテンツから指示に基づいてレポートを生成
    
    Parameters:
    -----------
    md_content : str
        元のMarkdownコンテンツ
    instruction : str
        レポート生成の指示
    api_key : str
        APIキー
    model : str
        使用するモデル名
    provider : str
        AIプロバイダー（"OpenAI", "Anthropic (Claude)", "Google (Gemini)"）
    max_tokens : int, optional
        最大出力トークン数（Noneの場合は自動設定）
    
    Returns:
    --------
    dict : {
        'content': str,  # 生成されたレポート
        'stats': {
            'processing_time': float,  # 処理時間（秒）
            'output_bytes': int,  # 出力バイト数
            'output_chars': int,  # 出力文字数
            'model': str,  # 使用モデル
            'compressed': bool  # 圧縮されたか
        }
    }
    """
    import time
    start_time = time.time()
    
    # モデル仕様を取得
    try:
        import model_specs
        model_info = model_specs.get_model_info(provider, model)
        
        if model_info:
            # 拡張トークンがあれば使用
            max_input_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
            model_output_tokens = model_info.get('output_tokens', 4096)
            
            # max_tokensが指定されていない場合は、モデルの出力制限の50%を使用
            if max_tokens is None:
                max_tokens = min(8000, int(model_output_tokens * 0.5))
        else:
            # デフォルト値（プロバイダー別）
            if "OpenAI" in provider:
                max_input_tokens = 100_000
                max_tokens = max_tokens or 4096
            elif "Anthropic" in provider:
                max_input_tokens = 180_000
                max_tokens = max_tokens or 4096
            elif "Google" in provider or "Gemini" in provider:
                max_input_tokens = 900_000
                max_tokens = max_tokens or 8000
            else:
                max_input_tokens = 100_000
                max_tokens = max_tokens or 4096
    except Exception as e:
        # フォールバック
        max_input_tokens = 100_000
        max_tokens = max_tokens or 4096
    
    # コンテンツのトークン数をチェック
    estimated_tokens = estimate_tokens(md_content)
    
    # GPT-5 Proは特別なTPM制限があるため、より厳しい制限を適用
    if "gpt-5-pro" in model.lower():
        # TPM制限: 30,000 tokens/min
        # 出力トークンも考慮して、入力は最大20,000トークンに制限
        safe_limit = min(20_000, int(max_input_tokens * 0.5))
        print(f"⚠️ GPT-5 Pro使用: TPM制限のため入力を{safe_limit:,}トークンに制限")
    else:
        # 通常のモデル: 80%を上限とする
        safe_limit = int(max_input_tokens * 0.8)
    
    # トークンウィンドウに余裕がある場合は圧縮しない
    if estimated_tokens <= safe_limit:
        content_to_use = md_content
        print(f"✓ トークンウィンドウに余裕あり ({estimated_tokens:,} / {max_input_tokens:,} tokens) - 圧縮なし")
    else:
        # 圧縮が必要な場合のみ実行
        print(f"⚠ トークン制限により圧縮実行 ({estimated_tokens:,} → {safe_limit:,} tokens)")
        content_to_use = compress_markdown_for_model(md_content, safe_limit)
    
    # システムプロンプト
    system_prompt = """あなたは議論データの分析専門家です。
提供されたMarkdown形式の議論データを詳細に分析し、指示に従って有益なレポートを作成してください。

レポート作成時の注意点:
1. データに基づいた客観的な分析を行う
2. 重要な意見や傾向を適切に抽出する
3. 定量的なデータ（スコア、人数など）を効果的に活用する
4. 多数意見と少数意見のバランスを考慮する
5. 読みやすく構造化された文章で記述する
6. Markdown形式で出力する
"""
    
    # ユーザープロンプト
    user_prompt = f"""{instruction}

# 議論データ

{content_to_use}
"""
    
    # 圧縮されたかどうかを記録
    was_compressed = (estimated_tokens > safe_limit)
    
    try:
        if "OpenAI" in provider:
            result = _generate_openai(system_prompt, user_prompt, api_key, model, max_tokens)
        elif "Anthropic" in provider:
            result = _generate_anthropic(system_prompt, user_prompt, api_key, model, max_tokens)
        elif "Google" in provider or "Gemini" in provider:
            result = _generate_google(system_prompt, user_prompt, api_key, model, max_tokens)
        else:
            raise ValueError(f"未対応のプロバイダー: {provider}")
        
        # 処理時間と統計情報を計算
        processing_time = time.time() - start_time
        output_bytes = len(result.encode('utf-8'))
        output_chars = len(result)
        
        return {
            'content': result,
            'stats': {
                'processing_time': processing_time,
                'output_bytes': output_bytes,
                'output_chars': output_chars,
                'model': model,
                'compressed': was_compressed
            }
        }
            
    except Exception as e:
        raise Exception(f"{provider} API エラー: {str(e)}")


def _generate_openai(system_prompt, user_prompt, api_key, model, max_tokens):
    """OpenAI APIで生成"""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    # GPT-5 Proは専用のresponsesエンドポイントを使用
    if "gpt-5-pro" in model.lower():
        # responsesエンドポイントはsystem promptとuser promptを統合
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            # Responses APIは max_output_tokens を使用
            response = client.responses.create(
                model=model,
                input=combined_prompt,
                max_output_tokens=max_tokens
            )
            
            # レスポンスからテキストを抽出（複数の方法を試行）
            output_text = ""
            
            # 方法1: output属性から抽出（最も標準的な方法）
            if hasattr(response, 'output') and response.output is not None:
                try:
                    for item in response.output:
                        if hasattr(item, "content") and item.content is not None:
                            for content in item.content:
                                if hasattr(content, "text"):
                                    output_text += content.text
                except (TypeError, AttributeError):
                    pass  # 次の方法を試す
            
            # 方法2: output_text属性を直接取得
            if not output_text and hasattr(response, 'output_text') and response.output_text:
                output_text = response.output_text
            
            # 方法3: model_dumpで辞書形式から抽出（フォールバック）
            if not output_text and hasattr(response, 'model_dump'):
                try:
                    response_dict = response.model_dump()
                    if 'output' in response_dict and response_dict['output']:
                        for item in response_dict['output']:
                            if isinstance(item, dict) and 'content' in item and item['content']:
                                for content in item['content']:
                                    if isinstance(content, dict) and 'text' in content:
                                        output_text += content['text']
                except Exception:
                    pass  # 最終的にエラーとして処理
            
            if output_text:
                return output_text
            else:
                # デバッグ情報を含むエラーメッセージ
                import json
                debug_info = ""
                try:
                    if hasattr(response, 'model_dump'):
                        response_dict = response.model_dump()
                        debug_info = f"\nレスポンス構造: {json.dumps(response_dict, indent=2, ensure_ascii=False)[:500]}"
                except Exception:
                    pass
                
                raise ValueError(
                    f"GPT-5 Proのレスポンスからテキストを抽出できませんでした。\n"
                    f"レスポンスタイプ: {type(response)}{debug_info}"
                )
                
        except Exception as e:
            # より詳細なエラー情報を提供
            error_msg = f"GPT-5 Pro API エラー: {str(e)}"
            raise Exception(error_msg)
    
    # 通常のchat/completionsエンドポイント
    api_params = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    # GPT-5, o1シリーズは max_completion_tokens
    if model.startswith(('gpt-5', 'o1')):
        api_params["max_completion_tokens"] = max_tokens
    else:
        api_params["max_tokens"] = max_tokens
    
    # GPT-5とo1シリーズはtemperatureをサポートしない（デフォルト1のみ）
    if not model.startswith(('gpt-5', 'o1')):
        api_params["temperature"] = 0.7
    
    response = client.chat.completions.create(**api_params)
    
    return response.choices[0].message.content


def _generate_anthropic(system_prompt, user_prompt, api_key, model, max_tokens):
    """Anthropic (Claude) APIで生成"""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise ImportError("anthropicパッケージが必要です: pip install anthropic")
    
    client = Anthropic(api_key=api_key)
    
    # Claudeはsystem promptを別パラメータで指定
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7
    )
    
    return response.content[0].text


def _generate_google(system_prompt, user_prompt, api_key, model, max_tokens):
    """Google (Gemini) APIで生成"""
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("google-generativeaiパッケージが必要です: pip install google-generativeai")
    
    genai.configure(api_key=api_key)
    
    # Geminiはシステムプロンプトをユーザープロンプトに統合
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    model_instance = genai.GenerativeModel(model)
    
    response = model_instance.generate_content(
        combined_prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7
        )
    )
    
    return response.text


def send_email(recipient, subject, body, smtp_config=None):
    """
    メール送信機能（オプション）
    
    Parameters:
    -----------
    recipient : str
        受信者メールアドレス
    subject : str
        件名
    body : str
        本文
    smtp_config : dict, optional
        SMTP設定 {'server': '', 'port': 587, 'user': '', 'password': ''}
    
    Returns:
    --------
    bool : 送信成功/失敗
    """
    
    # 簡易版: 実装はオプション
    # 実際の実装ではSMTPサーバー設定が必要
    
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # デフォルト設定を環境変数から取得
    if smtp_config is None:
        smtp_config = {
            'server': os.getenv('SMTP_SERVER', ''),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'user': os.getenv('SMTP_USER', ''),
            'password': os.getenv('SMTP_PASSWORD', '')
        }
    
    # 設定が不完全な場合はスキップ
    if not all([smtp_config['server'], smtp_config['user'], smtp_config['password']]):
        return False
    
    try:
        # メッセージ作成
        msg = MIMEMultipart()
        msg['From'] = smtp_config['user']
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # SMTP接続
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['user'], smtp_config['password'])
        
        # 送信
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"メール送信エラー: {str(e)}")
        return False


def estimate_cost(model, input_tokens, output_tokens):
    """
    API利用コストの概算

    Parameters:
    -----------
    model : str
        モデル名
    input_tokens : int
        入力トークン数
    output_tokens : int
        出力トークン数

    Returns:
    --------
    float : コスト（USD）
    """

    # model_data.py の MODEL_SPECS から料金を取得（優先）
    try:
        import model_specs
        for provider in ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"]:
            model_info = model_specs.get_model_info(provider, model)
            if model_info:
                cost_input_per_1m = model_info.get('cost_input', 0)
                cost_output_per_1m = model_info.get('cost_output', 0)
                input_cost = (input_tokens / 1_000_000) * cost_input_per_1m
                output_cost = (output_tokens / 1_000_000) * cost_output_per_1m
                return input_cost + output_cost
    except Exception:
        pass

    # フォールバック: 代表的なモデルのハードコード料金（USD per 1M tokens）
    pricing_per_1m = {
        # OpenAI
        'gpt-5.2': {'input': 1.75, 'output': 14.00},
        'gpt-5.1': {'input': 1.25, 'output': 10.00},
        'gpt-5': {'input': 1.25, 'output': 10.00},
        'gpt-5-mini': {'input': 0.25, 'output': 2.00},
        'gpt-5-nano': {'input': 0.05, 'output': 0.40},
        'gpt-4.1': {'input': 2.00, 'output': 8.00},
        'gpt-4.1-mini': {'input': 0.40, 'output': 1.60},
        'gpt-4.1-nano': {'input': 0.10, 'output': 0.40},
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        # Anthropic
        'claude-opus-4-6': {'input': 5.00, 'output': 25.00},
        'claude-sonnet-4-6': {'input': 3.00, 'output': 15.00},
        'claude-opus-4-5': {'input': 5.00, 'output': 25.00},
        'claude-sonnet-4-5': {'input': 3.00, 'output': 15.00},
        'claude-haiku-4-5': {'input': 1.00, 'output': 5.00},
        # Google
        'gemini-3-flash-preview': {'input': 0.50, 'output': 3.00},
        'gemini-3-pro-preview': {'input': 2.00, 'output': 12.00},
        'gemini-2.5-pro': {'input': 1.25, 'output': 10.00},
        'gemini-2.5-flash': {'input': 0.30, 'output': 2.50},
        'gemini-2.5-flash-lite': {'input': 0.10, 'output': 0.40},
    }

    # モデルIDの前方一致で検索
    for key, prices in pricing_per_1m.items():
        if model.startswith(key) or key in model:
            input_cost = (input_tokens / 1_000_000) * prices['input']
            output_cost = (output_tokens / 1_000_000) * prices['output']
            return input_cost + output_cost

    return 0.0
