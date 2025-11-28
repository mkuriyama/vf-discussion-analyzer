# プロジェクト構造

```
discussion_analyzer/
│
├── app.py                          # メインアプリケーション（Streamlit UI）
├── processor.py                    # データ処理モジュール（ZIP → Markdown変換）
├── ai_generator.py                 # AI生成モジュール（OpenAI API連携）
├── test_setup.py                   # セットアップテストスクリプト
│
├── requirements.txt                # Python依存関係
├── README.md                       # プロジェクト概要とドキュメント
├── DEPLOYMENT.md                   # デプロイメントガイド
├── .gitignore                      # Git除外設定
│
└── .streamlit/
    ├── config.toml                 # Streamlit設定
    └── secrets.toml.example        # Secrets設定例
```

## 各ファイルの役割

### コアファイル

#### `app.py`
- **目的**: Streamlitベースのウェブインターフェース
- **機能**:
  - ファイルアップロード（ZIP）
  - 出力タイプ選択（400字/2000字/5000字/カスタム）
  - OpenAI API設定
  - レポート生成と表示
  - ダウンロード・メール送信機能
- **起動**: `streamlit run app.py`

#### `processor.py`
- **目的**: 議論データCSVの処理とMarkdown変換
- **主要クラス**:
  - `DataAnalyzer`: CSVデータ構造の解析
  - `OptimizedMarkdownGenerator`: 最適化されたMarkdown生成
- **主要関数**:
  - `convert_zip_to_markdown()`: メイン変換関数
  - `find_csv_files()`: CSV検索
  - `safe_read_csv()`: エンコーディング対応CSV読み込み

#### `ai_generator.py`
- **目的**: OpenAI APIを使用したレポート生成
- **主要関数**:
  - `generate_report()`: AIレポート生成
  - `send_email()`: メール送信（オプション）
  - `estimate_cost()`: API利用コスト概算
- **対応モデル**:
  - gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo

### 設定ファイル

#### `requirements.txt`
```
streamlit>=1.32.0      # Webフレームワーク
pandas>=2.0.0          # データ処理
openai>=1.12.0         # OpenAI API
python-dotenv>=1.0.0   # 環境変数管理
```

#### `.streamlit/config.toml`
- Streamlitのテーマとサーバー設定
- アップロードサイズ制限: 200MB
- セキュリティ設定

#### `.streamlit/secrets.toml` (作成が必要)
```toml
OPENAI_API_KEY = "your-api-key"
SMTP_SERVER = "smtp.gmail.com"  # オプション
SMTP_PORT = "587"                # オプション
SMTP_USER = "your-email"         # オプション
SMTP_PASSWORD = "your-password"  # オプション
```

### ドキュメント

#### `README.md`
- プロジェクト概要
- 機能説明
- クイックスタート
- デプロイ手順
- トラブルシューティング

#### `DEPLOYMENT.md`
- Streamlit Cloudデプロイの詳細ガイド
- GitHub設定
- Secrets設定
- セキュリティベストプラクティス
- トラブルシューティング

### テストファイル

#### `test_setup.py`
- セットアップの検証
- モジュールインポートテスト
- ファイル構成チェック
- 基本機能テスト
- 実行: `python test_setup.py`

## データフロー

```
1. ユーザー入力
   ├── ZIPファイルアップロード
   ├── 出力タイプ選択
   └── OpenAI設定

2. データ処理 (processor.py)
   ├── ZIPファイル展開
   ├── CSV検索・読み込み
   ├── データ構造解析
   └── Markdown生成

3. AI処理 (ai_generator.py)
   ├── Markdownコンテンツ読み込み
   ├── 指示文準備
   ├── OpenAI API呼び出し
   └── レポート生成

4. 出力
   ├── ブラウザ表示
   ├── ダウンロード（Markdown）
   └── メール送信（オプション）
```

## カスタマイズポイント

### レポートテンプレートの追加
`app.py` の `tab1` セクションで出力タイプを追加:
```python
output_type = st.radio(
    "レポートの種類を選択してください:",
    [
        "400字版 - エグゼクティブサマリー",
        "2000字版 - 構造化レポート（推奨）",
        "5000字版 - 詳細分析レポート",
        "新しいタイプ - カスタム説明",  # ← 追加
        "カスタム - 自由記述で指示"
    ]
)
```

### データ処理ロジックの変更
`processor.py` の `DataAnalyzer` クラスで解析ロジックをカスタマイズ

### AIプロンプトの調整
`ai_generator.py` の `generate_report()` 関数でシステムプロンプトを変更

### UI/UXの改善
`app.py` でStreamlitコンポーネントを追加・変更

## 環境変数

### 必須
- `OPENAI_API_KEY`: OpenAI APIキー

### オプション
- `SMTP_SERVER`: メールサーバー
- `SMTP_PORT`: SMTPポート
- `SMTP_USER`: メールアカウント
- `SMTP_PASSWORD`: メールパスワード

## セキュリティ

### APIキー管理
- ✅ Streamlit Secretsを使用
- ✅ 環境変数から読み込み
- ❌ コードにハードコードしない
- ❌ GitHubにコミットしない

### データプライバシー
- アップロードされたファイルは一時的に処理
- 処理後は自動削除
- ローカルストレージに保存しない

## パフォーマンス

### 最適化ポイント
1. **大容量ファイル対応**
   - 10MB超のMarkdownは自動要約
   - 段階的な処理表示

2. **API効率化**
   - モデル選択によるコスト最適化
   - トークン数の事前チェック

3. **キャッシング**
   - Streamlitの `@st.cache_data` 活用可能
   - 同じファイルの再処理を回避

## 今後の拡張案

### 機能追加
- [ ] 複数ファイルの一括処理
- [ ] レポートのPDF出力
- [ ] グラフ・チャートの自動生成
- [ ] 履歴管理機能
- [ ] ユーザー認証

### 技術改善
- [ ] 非同期処理による高速化
- [ ] データベース連携
- [ ] より詳細なエラーハンドリング
- [ ] ユニットテストの追加
- [ ] CI/CDパイプライン

## サポート

質問や問題がある場合:
1. README.mdのトラブルシューティングを確認
2. DEPLOYMENT.mdのトラブルシューティングを確認
3. GitHubのIssuesで報告

---

**最終更新**: 2024年
**バージョン**: 1.0.0
