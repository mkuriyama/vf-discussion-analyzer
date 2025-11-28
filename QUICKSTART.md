# 🚀 クイックスタートガイド

## 5分でデプロイ！

### ステップ1: GitHubリポジトリを作成 (2分)

```bash
# 1. このフォルダをGitリポジトリとして初期化
git init

# 2. すべてのファイルをステージング
git add .

# 3. 初回コミット
git commit -m "Initial commit: Discussion analyzer app"

# 4. GitHubで新しいリポジトリを作成してから、URLを設定
git remote add origin https://github.com/YOUR_USERNAME/discussion-analyzer.git

# 5. プッシュ
git branch -M main
git push -u origin main
```

### ステップ2: Streamlit Cloudでデプロイ (3分)

1. **アクセス**: https://streamlit.io/cloud
2. **ログイン**: GitHubアカウントでログイン
3. **新規アプリ**: "New app" をクリック
4. **設定**:
   - Repository: `YOUR_USERNAME/discussion-analyzer`
   - Branch: `main`
   - Main file: `app.py`
5. **デプロイ**: "Deploy!" をクリック

### ステップ3: APIキーを設定 (1分)

1. デプロイ中のアプリの設定に移動
2. "Secrets" セクションを開く
3. 以下を入力:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

4. "Save" をクリック

### 完了！ 🎉

あなたのアプリが公開されました！
URL: `https://your-app-name.streamlit.app`

---

## OpenAI APIキーの取得方法

1. https://platform.openai.com/ にアクセス
2. アカウント作成/ログイン
3. 右上のメニュー → "API keys"
4. "Create new secret key" をクリック
5. キーをコピー（再表示不可なので注意！）

💡 **ヒント**: まずは無料クレジットで試せます

---

## ローカルで試す場合

```bash
# 1. 依存関係をインストール
pip install -r requirements.txt

# 2. Secrets設定
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml を編集してAPIキーを追加

# 3. アプリを起動
streamlit run app.py
```

ブラウザで http://localhost:8501 が自動的に開きます

---

## よくある質問

### Q: 無料で使えますか？
**A**: はい！
- Streamlit Cloud: 無料プラン（1アプリ）
- OpenAI: 新規アカウントに無料クレジット付与

### Q: どのくらいコストがかかりますか？
**A**: モデル別の目安（2000字レポート）:
- gpt-4o-mini: $0.001-0.003
- gpt-4o: $0.01-0.03
- gpt-4-turbo: $0.02-0.06

### Q: ZIPファイルのサイズ制限は？
**A**: 最大200MB（設定変更可能）

### Q: プライベートなデータは安全ですか？
**A**: はい
- 処理後は自動削除
- データは保存されません
- Streamlit Cloudは SOC 2 Type II 認証取得

### Q: カスタマイズできますか？
**A**: もちろん！
- `app.py`: UI変更
- `processor.py`: データ処理ロジック
- `ai_generator.py`: AIプロンプト調整

---

## トラブルシューティング

### エラー: "APIキーが無効です"
→ Secretsの設定を確認してください

### エラー: "ZIPファイルの処理に失敗"
→ 必要なCSVファイルが含まれているか確認

### アプリが遅い
→ gpt-4o-miniに変更してみてください

---

## 次のステップ

✅ デプロイ完了後:
1. 実際のデータでテスト
2. チームメンバーとURLを共有
3. フィードバックを収集
4. 必要に応じてカスタマイズ

📚 さらに詳しく:
- [README.md](README.md) - 完全なドキュメント
- [DEPLOYMENT.md](DEPLOYMENT.md) - 詳細なデプロイガイド
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - コード構造の解説

---

**問題が発生した場合**: GitHubのIssuesで質問してください

**Happy analyzing! 📊✨**
