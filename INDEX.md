# 議論データ分析Webアプリ - プロジェクトインデックス

## 📂 ドキュメント一覧

### 🚀 すぐに始めたい方
**[QUICKSTART.md](QUICKSTART.md)** - 5分でデプロイできるクイックスタートガイド

### 📖 詳しく知りたい方
1. **[README.md](README.md)** - プロジェクト概要、機能説明、使い方
2. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Streamlit Cloudへの詳細なデプロイ手順
3. **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - コード構造とカスタマイズ方法

## 📁 ファイル構成

### コアファイル
- `app.py` - Streamlit UIメインアプリケーション
- `processor.py` - CSV処理とMarkdown変換モジュール
- `ai_generator.py` - OpenAI API連携モジュール

### 設定ファイル
- `requirements.txt` - Python依存関係
- `.streamlit/config.toml` - Streamlit設定
- `.streamlit/secrets.toml.example` - API設定テンプレート
- `.gitignore` - Git除外設定

### テスト
- `test_setup.py` - セットアップ検証スクリプト

## 🎯 このアプリでできること

### 入力
専門家AIによる会議録（CSV形式をZIPで圧縮）

### 処理
1. CSV → Markdownに自動変換
2. OpenAI APIで分析
3. 目的に合わせたレポート生成

### 出力オプション
- **400字版**: エグゼクティブサマリー
- **2000字版**: 構造化レポート（推奨）
- **5000字版**: 詳細分析レポート
- **カスタム**: 自由な指示でカスタマイズ

### 配信方法
- ブラウザ上で即座に確認
- Markdownファイルとしてダウンロード
- メールで送信（オプション）

## 🛠️ 技術スタック

- **フロントエンド**: Streamlit
- **データ処理**: Pandas
- **AI**: OpenAI API (GPT-4o, GPT-4o-mini等)
- **デプロイ**: Streamlit Cloud
- **言語**: Python 3.11+

## 📊 使用フロー

```
ZIPアップロード → CSV解析 → Markdown生成 → AI分析 → レポート出力
     ↓              ↓           ↓            ↓          ↓
  (app.py)    (processor.py) (processor.py) (ai_gen)  (app.py)
```

## 🚀 デプロイまでの3ステップ

### 1. GitHubにプッシュ
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Streamlit Cloudでデプロイ
https://streamlit.io/cloud → New app → リポジトリ選択

### 3. APIキー設定
Settings → Secrets → `OPENAI_API_KEY = "sk-..."`

**完了！あなたのアプリが公開されます 🎉**

## 💡 推奨される最初の手順

1. ✅ [QUICKSTART.md](QUICKSTART.md) を読む（5分）
2. ✅ OpenAI APIキーを取得
3. ✅ GitHubリポジトリを作成
4. ✅ Streamlit Cloudにデプロイ
5. ✅ サンプルデータでテスト

## 🆘 ヘルプ

### 問題が発生した場合
1. README.mdのトラブルシューティングを確認
2. DEPLOYMENT.mdの詳細ガイドを確認
3. GitHubのIssuesで質問

### よくある質問
- 無料で使える？ → はい（Streamlit Cloud無料プラン + OpenAI無料クレジット）
- セキュリティは？ → データは処理後自動削除、APIキーはSecretsで管理
- カスタマイズ可能？ → はい、すべてのコードが編集可能

## 🎓 学習リソース

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [OpenAI API ガイド](https://platform.openai.com/docs)
- [Pandas ドキュメント](https://pandas.pydata.org/docs/)

## 📝 ライセンス

MIT License - 自由に使用・改変できます

## 🙏 謝辞

- Streamlit - 素晴らしいWebフレームワーク
- OpenAI - 強力なAI API
- Pandas - 高速なデータ処理

---

**Version**: 1.0.0  
**Last Updated**: 2024-11  
**Status**: ✅ Production Ready

**始めましょう！→ [QUICKSTART.md](QUICKSTART.md)**
