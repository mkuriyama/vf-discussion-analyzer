"""
AIレポート生成モジュール
OpenAI APIを使用してMarkdownからレポートを生成
"""

import os
from openai import OpenAI


def generate_report(md_content, instruction, api_key, model="gpt-4o", max_tokens=8000):
    """
    Markdownコンテンツから指示に基づいてレポートを生成
    
    Parameters:
    -----------
    md_content : str
        元のMarkdownコンテンツ
    instruction : str
        レポート生成の指示
    api_key : str
        OpenAI APIキー
    model : str
        使用するモデル名
    max_tokens : int
        最大トークン数
    
    Returns:
    --------
    str : 生成されたレポート
    """
    
    # OpenAIクライアント初期化
    client = OpenAI(api_key=api_key)
    
    # コンテンツのサイズチェックと最適化
    # 非常に大きいファイルの場合は要約セクションのみを使用
    content_to_use = md_content
    if len(md_content) > 100000:  # 100KB超える場合
        # 統計情報と設問一覧、最初の数名の回答のみを抽出
        lines = md_content.split('\n')
        header_end = 0
        details_start = 0
        
        for i, line in enumerate(lines):
            if '## 議論内容詳細' in line:
                details_start = i
                break
            if i < 500:  # 最初の500行は必ず含める
                header_end = i
        
        # ヘッダー部分 + 詳細の最初の一部
        if details_start > 0:
            content_to_use = '\n'.join(lines[:details_start]) + '\n\n[... 以下、一部省略 ...]\n\n' + '\n'.join(lines[details_start:details_start+2000])
        else:
            content_to_use = '\n'.join(lines[:10000])
    
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
        # API呼び出し
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
        
    except Exception as e:
        raise Exception(f"OpenAI API エラー: {str(e)}")


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
