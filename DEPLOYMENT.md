# Streamlit Cloudデプロイメントガイド

## 📦 事前準備

### 1. GitHubリポジトリの作成

```bash
# プロジェクトディレクトリで実行
git init
git add .
git commit -m "Initial commit: Discussion analyzer app"

# GitHubで新しいリポジトリを作成してから
git remote add origin https://github.com/your-username/discussion-analyzer.git
git branch -M main
git push -u origin main
```

### 2. 必要なファイルの確認

以下のファイルがリポジトリに含まれていることを確認:

- ✅ `app.py` - メインアプリケーション
- ✅ `processor.py` - データ処理モジュール
- ✅ `ai_generator.py` - AI生成モジュール
- ✅ `requirements.txt` - 依存関係
- ✅ `README.md` - ドキュメント
- ✅ `.streamlit/config.toml` - Streamlit設定

## 🚀 Streamlit Cloudへのデプロイ

### Step 1: Streamlit Cloudにアクセス

1. https://streamlit.io/cloud にアクセス
2. "Sign up with GitHub" または "Sign in with GitHub" をクリック
3. GitHubアカウントで認証

### Step 2: 新しいアプリをデプロイ

1. ダッシュボードで "New app" ボタンをクリック
2. 以下の情報を入力:
   - **Repository**: `your-username/discussion-analyzer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. "Advanced settings" をクリック（オプション）
   - Python version: 3.11 (推奨)
4. "Deploy!" をクリック

### Step 3: Secretsの設定

⚠️ **重要**: APIキーは必ずSecretsで管理してください

1. デプロイ中のアプリの設定画面に移動
2. 左サイドバーの "⚙️ Settings" をクリック
3. "Secrets" セクションを見つける
4. 以下の内容を入力:

```toml
# OpenAI API設定（必須）
OPENAI_API_KEY = "sk-your-actual-api-key-here"

# メール送信設定（オプション - 使用しない場合は不要）
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"
```

5. "Save" をクリック
6. アプリが自動的に再起動されます

### Step 4: デプロイ完了

アプリが正常にデプロイされると:
- 自動的にURLが生成されます（例: `https://your-app-name.streamlit.app`）
- このURLを共有してアプリにアクセスできます

## 🔐 セキュリティのベストプラクティス

### OpenAI APIキーの取得

1. https://platform.openai.com/ にアクセス
2. アカウントを作成/ログイン
3. "API Keys" セクションに移動
4. "Create new secret key" をクリック
5. キーをコピー（再表示できないので注意）

### Gmailアプリパスワードの取得（メール送信機能を使う場合）

1. Googleアカウントで2段階認証を有効化
2. https://myaccount.google.com/apppasswords にアクセス
3. アプリ名を入力（例: "Discussion Analyzer"）
4. "生成" をクリック
5. 16文字のパスワードをコピー
6. このパスワードを `SMTP_PASSWORD` に設定

## 🔄 アプリの更新

コードを更新してGitHubにプッシュすると、Streamlit Cloudが自動的に再デプロイします:

```bash
git add .
git commit -m "Update: feature description"
git push origin main
```

手動で再起動する場合:
1. Streamlit Cloudダッシュボードに移動
2. アプリの "⋮" メニューをクリック
3. "Reboot" を選択

## 📊 使用量の監視

### Streamlit Cloud

- 無料プラン: 1アプリ、リソース制限あり
- 有料プラン: 複数アプリ、より多くのリソース

ダッシュボードで以下を確認できます:
- アクティブユーザー数
- リソース使用状況
- アプリの稼働時間

### OpenAI API

https://platform.openai.com/usage でAPI使用量とコストを確認:
- トークン使用量
- API呼び出し回数
- 推定コスト

コストを抑える方法:
- `gpt-4o-mini` を使用（10分の1のコスト）
- 不要に長い入力を避ける
- エラーハンドリングを実装して無駄な再試行を防ぐ

## 🐛 トラブルシューティング

### エラー: "ModuleNotFoundError"

**原因**: requirements.txtに依存関係が不足
**解決**: requirements.txtを確認して必要なパッケージを追加

```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### エラー: "Secrets not found"

**原因**: Secretsが正しく設定されていない
**解決**: 
1. Streamlit Cloudの設定で Secrets を確認
2. TOMLフォーマットが正しいか確認
3. アプリを再起動

### アプリが遅い

**原因**: 大容量ファイル処理、APIレスポンス待ち
**解決**:
- プログレスバーを追加してユーザー体験を改善
- キャッシュを活用（`@st.cache_data`）
- ファイルサイズ制限を設定

### デプロイが失敗する

**解決手順**:
1. ログを確認（Streamlit Cloudダッシュボード）
2. ローカルで `streamlit run app.py` が動作するか確認
3. requirements.txtのバージョンを確認
4. Pythonバージョンの互換性を確認

## 📞 サポート

- **Streamlit**: https://docs.streamlit.io/
- **Streamlit Community**: https://discuss.streamlit.io/
- **OpenAI**: https://help.openai.com/

## 🎉 完了

これでアプリが公開され、誰でもアクセスできるようになりました！

URLを共有してユーザーに使ってもらいましょう 🚀
