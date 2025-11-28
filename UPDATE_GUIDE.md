# 🔄 アップデート手順（v1.0.0 → v1.1.0）

## ⚡ クイックアップデート（5分）

### ステップ1: ファイルを更新
GitHubリポジトリの以下のファイルを新しいバージョンで置き換えてください:

- ✅ `app.py` （更新）
- ✅ `ai_generator.py` （更新）
- ✅ `requirements.txt` （更新）
- ✅ `CHANGELOG.md` （新規）

### ステップ2: GitHubにプッシュ
```bash
git add .
git commit -m "Update to v1.1.0: Multi-provider support and history tracking"
git push origin main
```

Streamlit Cloudが自動的に再デプロイします（約2-3分）。

### ステップ3: Secrets設定（オプション）
Anthropic やGoogle を使用する場合、Streamlit CloudのSecretsに追加:

```toml
# 既存（OpenAIのみ使う場合はこれだけでOK）
OPENAI_API_KEY = "sk-..."

# 新規（Anthropicを使う場合）
ANTHROPIC_API_KEY = "sk-ant-..."

# 新規（Googleを使う場合）
GOOGLE_API_KEY = "..."
```

**完了！** アプリが再起動したら新機能が使えます🎉

---

## 📋 主な新機能

### 1. Markdown閲覧タブ
- ZIPアップロード後、すぐにMarkdown全文が閲覧可能
- レポート生成前にデータを確認できる

### 2. マルチAIプロバイダー
サイドバーで以下から選択可能:
- **OpenAI** (gpt-4o, gpt-4o-mini 等)
- **Anthropic** (Claude Sonnet 4, Haiku 等)
- **Google** (Gemini 2.0 Flash 等)

### 3. 出力結果一覧
- 「📚 出力結果一覧」タブで過去のレポートを管理
- 生成条件（モデル、タイプ等）も記録
- 後からでもダウンロード可能

### 4. トークン制限エラー解消
- 大きなファイルでも自動圧縮
- gpt-4o-miniでも安定動作

---

## 🆕 UIの変化

### タブ構成
**旧版**: 📄 レポート生成 | ℹ️ 使い方 | 🔧 詳細設定

**新版**: 📄 Markdown閲覧 | 📝 レポート生成 | 📚 出力結果一覧 | ℹ️ 使い方 | 🔧 詳細設定

### サイドバー
- プロバイダー選択が追加
- 選択したプロバイダーに応じてAPIキー入力欄が変化
- モデル選択肢も動的に変更

---

## 💡 使い方のヒント

### 推奨ワークフロー
1. ZIPファイルをアップロード
2. 「📄 Markdown閲覧」でデータ確認
3. 「📝 レポート生成」で分析
4. 「📚 出力結果一覧」で過去のレポートと比較

### コスト最適化
- **低コスト**: gpt-4o-mini, claude-3-5-haiku, gemini-2.0-flash
- **高品質**: claude-sonnet-4, gpt-4o-2024-11-20
- **バランス**: claude-3-5-sonnet, gpt-4o-mini

### トークンエラーが出たら
1. モデルを変更（miniやhaiku）
2. 短いレポート（400字版）を選択
3. カスタム指示で焦点を絞る

---

## 🔒 セキュリティ注意事項

### APIキーの管理
複数のAPIキーを使う場合も、必ずStreamlit Secretsで管理:

```toml
# .streamlit/secrets.toml （ローカル開発用）
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_API_KEY = "..."
```

**重要**: `.gitignore`に`secrets.toml`が含まれていることを確認！

---

## ⚠️ 既知の制限事項

### セッション履歴
- 出力結果一覧はブラウザセッション中のみ保持
- リフレッシュすると履歴はクリア
- 重要なレポートは個別にダウンロード推奨

### APIキー要件
- 各プロバイダーを使うには対応するAPIキーが必要
- OpenAIのキーだけでも従来通り使用可能

---

## 🐛 トラブルシューティング

### エラー: "No module named 'anthropic'"
**原因**: 依存関係が更新されていない  
**解決**: Streamlit Cloudが自動インストール。ローカルなら `pip install -r requirements.txt`

### エラー: APIキーが無効
**原因**: プロバイダーとキーが一致していない  
**解決**: 正しいプロバイダーを選択しているか確認

### 出力履歴が表示されない
**原因**: セッションがリセットされた  
**解決**: ブラウザリフレッシュ後は新規セッションとして開始

---

## 📞 サポート

問題が解決しない場合:
1. [CHANGELOG.md](CHANGELOG.md) の詳細を確認
2. [README.md](README.md) のトラブルシューティング
3. GitHubのIssuesで報告

---

## 🎓 参考リンク

### APIキーの取得
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google**: https://aistudio.google.com/app/apikey

### 各プロバイダーのドキュメント
- **OpenAI**: https://platform.openai.com/docs
- **Anthropic**: https://docs.anthropic.com/
- **Google**: https://ai.google.dev/docs

---

**アップデート完了後、動作確認をお忘れなく！** 🚀

問題なく動作すれば、より柔軟で強力なツールになっています✨
