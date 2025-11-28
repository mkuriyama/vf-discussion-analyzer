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


def generate_report(md_content, instruction, api_key, model, provider="OpenAI", max_tokens=8000):
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
    max_tokens : int
        最大出力トークン数
    
    Returns:
    --------
    str : 生成されたレポート
    """
    
    # モデル仕様を取得
    try:
        import model_specs
        model_info = model_specs.get_model_info(provider, model)
        
        if model_info:
            # 拡張トークンがあれば使用
            max_input_tokens = model_info.get('input_tokens_extended', model_info['input_tokens'])
        else:
            # デフォルト値（プロバイダー別）
            if "OpenAI" in provider:
                max_input_tokens = 100_000
            elif "Anthropic" in provider:
                max_input_tokens = 180_000
            elif "Google" in provider or "Gemini" in provider:
                max_input_tokens = 900_000
            else:
                max_input_tokens = 100_000
    except:
        # フォールバック
        max_input_tokens = 100_000
    
    # コンテンツのトークン数をチェック
    estimated_tokens = estimate_tokens(md_content)
    
    # 安全マージンを考慮（システムプロンプト + ユーザープロンプト）
    safe_limit = int(max_input_tokens * 0.8)  # 80%を上限とする
    
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
    
    try:
        if "OpenAI" in provider:
            return _generate_openai(system_prompt, user_prompt, api_key, model, max_tokens)
        elif "Anthropic" in provider:
            return _generate_anthropic(system_prompt, user_prompt, api_key, model, max_tokens)
        elif "Google" in provider or "Gemini" in provider:
            return _generate_google(system_prompt, user_prompt, api_key, model, max_tokens)
        else:
            raise ValueError(f"未対応のプロバイダー: {provider}")
            
    except Exception as e:
        raise Exception(f"{provider} API エラー: {str(e)}")


def _generate_openai(system_prompt, user_prompt, api_key, model, max_tokens):
    """OpenAI APIで生成"""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    
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
    
    # 2024年時点の料金（要確認）
    pricing = {
        'gpt-4o': {'input': 0.005, 'output': 0.015},  # per 1K tokens
        'gpt-4o-mini': {'input': 0.00015, 'output': 0.0006},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015}
    }
    
    if model not in pricing:
        return 0.0
    
    input_cost = (input_tokens / 1000) * pricing[model]['input']
    output_cost = (output_tokens / 1000) * pricing[model]['output']
    
    return input_cost + output_cost
