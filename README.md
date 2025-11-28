# 議論データ分析Webアプリケーション

専門家AIによる会議録（CSV形式）を分析し、目的に合わせたレポートを生成するWebアプリケーションです。

## 🌟 特徴

- **簡単操作**: ZIPファイルをアップロードするだけ
- **柔軟な出力**: 400字/2000字/5000字版、またはカスタム指示
- **AI駆動**: OpenAI APIによる高品質な分析レポート
- **即座にデプロイ**: Streamlit Cloudで簡単にホスティング

## 📋 機能

### レポートタイプ

1. **400字版 - エグゼクティブサマリー**
   - 経営層向けの簡潔な要約
   - 主要ポイントのみを抽出

2. **2000字版 - 構造化レポート（推奨）**
   - バランスの取れた詳細度
   - 主要意見の整理と対比
   - 構造化された読みやすい形式

3. **5000字版 - 詳細分析レポート**
   - 包括的な分析
   - 設問別の詳細分析
   - 横断的な分析と提言

4. **カスタム - 自由記述指示**
   - 独自の要件に対応
   - 柔軟な出力フォーマット

### 出力オプション

- **ダウンロード**: Markdownファイルとして保存
- **メール送信**: 指定したアドレスに直接送信（要設定）

## 🚀 クイックスタート

### ローカル実行

```bash
# リポジトリをクローン
git clone <repository-url>
cd discussion_analyzer

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
streamlit run app.py
```

### 環境変数

`.env` ファイルを作成:

```env
OPENAI_API_KEY=your-api-key-here

# メール送信機能（オプション）
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🌐 Streamlit Cloudへのデプロイ

### 1. GitHubリポジトリの準備

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントでログイン
3. "New app" をクリック
4. リポジトリ、ブランチ、ファイル（`app.py`）を選択
5. "Deploy!" をクリック

### 3. Secrets設定

Streamlit Cloudのダッシュボードで:

1. デプロイしたアプリの設定に移動
2. "Secrets" セクションを開く
3. 以下の形式で追加:

```toml
OPENAI_API_KEY = "your-api-key-here"

# メール送信機能（オプション）
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
```

## 📊 入力データ形式

アップロードするZIPファイルには、以下のCSVファイルが含まれている必要があります:

- `project_idea_scores_*.csv`: 回答スコア
- `project_user_scores_*.csv`: ユーザースコア（オプション）
- `project_review_comments_*.csv`: コメント（オプション）

## 🔧 カスタマイズ

### モデル選択

以下のOpenAIモデルに対応:

- **gpt-4o**: 最新・最高性能（推奨）
- **gpt-4o-mini**: コストパフォーマンス重視
- **gpt-4-turbo**: 高性能・大容量
- **gpt-3.5-turbo**: 高速・低コスト

### カスタム指示の例

```
主要な意見を3つに絞り、それぞれについて賛成・反対の意見を対比させてください。
全体で1500字程度でまとめてください。
```

```
設問ごとに最高評価の回答を抽出し、なぜ高評価だったのかを分析してください。
共通する成功パターンがあれば指摘してください。
```

## 💡 Tips

- **処理時間**: 400字版（約10秒）< 2000字版（約30秒）< 5000字版（約60秒）
- **APIコスト**: gpt-4o-miniを使用すると大幅にコスト削減可能
- **大容量データ**: 10MB以上のMarkdownは自動的に要約されます
- **セキュリティ**: APIキーは必ずSecretsで管理してください

## 🛠️ トラブルシューティング

### エラー: "OpenAI API エラー"

- APIキーが正しく設定されているか確認
- API使用量の上限に達していないか確認
- モデル名が正しいか確認

### エラー: "CSVファイルの読み込みに失敗"

- ZIPファイルに必要なCSVが含まれているか確認
- ファイル名が正規表現パターンに一致しているか確認

### メール送信が機能しない

- SMTP設定がすべて正しく設定されているか確認
- Gmailの場合は「アプリパスワード」を使用
- ファイアウォールでポートがブロックされていないか確認

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 コントリビューション

プルリクエストを歓迎します！大きな変更の場合は、まずissueで議論してください。

## 📞 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

---

**Powered by OpenAI API | Built with Streamlit**
