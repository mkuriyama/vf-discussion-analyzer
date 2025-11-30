"""
詳細設定タブの静的コンテンツ
API情報、Tips、Secrets設定などの情報を管理
"""

# APIキーの取得方法
API_KEY_GUIDE = """
### APIキーの取得

#### OpenAI
1. https://platform.openai.com/ にアクセス
2. API Keysセクションで新規作成

#### Anthropic
1. https://console.anthropic.com/ にアクセス
2. API Keysで新規作成

#### Google
1. https://aistudio.google.com/app/apikey にアクセス
2. Create API keyをクリック
"""

# Tips
SETTINGS_TIPS = """
### 💡 Tips

- **トークン制限**: 各モデルの入力トークン数は上記の表を参照
- **大きなファイル**: トークン制限の80%を超えると自動圧縮
- **GPT-5 Pro**: TPM制限があるため、大きなファイルは自動的に20,000トークンに制限されます
- **コスト最適化**: mini/flash/haiku モデルは経済的
"""

# Streamlit Secrets設定
STREAMLIT_SECRETS_GUIDE = """
### Streamlit Secrets設定

本番環境では、Streamlit Cloud の Secrets 機能を使用してAPIキーを安全に管理できます。

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-key"
ANTHROPIC_API_KEY = "your-anthropic-key"
GOOGLE_API_KEY = "your-google-key"
```
"""

# モデル設定編集の注意事項
MODEL_EDITING_WARNING = """
**注意**: この機能は上級者向けです。設定を誤るとアプリが動作しなくなる可能性があります。
- 変更はセッション中のみ有効（リロードでリセット）
- Pythonの辞書形式を理解している必要があります
- 万一、設定エラーでアプリが動作しなくなった場合は、ページをリロードしてください
- ただし、リロードすると出力履歴も消えますので、重要なレポートは事前にダウンロードしておいてください
"""
