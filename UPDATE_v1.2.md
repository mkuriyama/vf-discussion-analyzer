# アップデート v1.2.0 - 最新モデル対応＆トークンウィンドウ最適化

## 🎯 実装内容

### 1. 最新モデルの完全対応

#### OpenAI
- **GPT-5シリーズ** (272K tokens): GPT-5, GPT-5 Mini, GPT-5 Nano, GPT-5.1
- **GPT-4.1シリーズ** (1M tokens) ⭐️: GPT-4.1, GPT-4.1 Mini, GPT-4.1 Nano
- **GPT-4oシリーズ** (128K tokens): GPT-4o, GPT-4o Mini
- **o1シリーズ**: o1 Preview, o1 Mini

#### Anthropic (Claude)
- **Claude Sonnet 4シリーズ** (200K → 1M tokens) ⭐️: Claude Sonnet 4, 4.5
- **Claude 3.5シリーズ** (200K tokens): Claude 3.5 Sonnet, Haiku
- **Claude 3シリーズ** (200K tokens): Claude 3 Opus, Sonnet, Haiku

#### Google (Gemini)
- **Gemini 3** (1M tokens) ⭐️: Gemini 3 Pro Preview
- **Gemini 2.5シリーズ** (1M tokens) ⭐️: Gemini 2.5 Pro, Flash, 2.0 Flash Experimental
- **Gemini 1.5シリーズ** (2M tokens) ⭐️⭐️: Gemini 1.5 Pro (最大200万トークン!)
- **Gemini 1.0** (32K tokens): Gemini 1.0 Pro

### 2. インテリジェントな圧縮制御

**従来**: 常に圧縮 → 情報欠損  
**新版**: トークンウィンドウに余裕があれば圧縮しない → 情報完全保持

### 3. リアルタイム互換性チェック

サイドバーに新機能「⚖️ ファイル互換性チェック」:
- 🟢 安全（< 50%）: 圧縮不要
- 🟡 注意（50-80%）: 問題なし
- 🔴 制限近い（> 80%）: 自動圧縮 + より大きいモデルを推奨

### 4. 詳細なモデル情報表示

各モデルの入力/出力トークン制限を表示し、ファイルサイズとの比較を可視化

## 📊 トークンウィンドウ比較

| モデル | 入力トークン | ランク |
|--------|------------|--------|
| Gemini 1.5 Pro | 2,097,152 | 🥇 |
| Claude Sonnet 4 (Beta) | 1,000,000 | 🥈 |
| GPT-4.1 | 1,000,000 | 🥈 |
| Gemini 2.5 Pro | 1,048,576 | 🥉 |
| GPT-5 | 272,000 | - |
| Claude 3.5/4 | 200,000 | - |
| GPT-4o | 128,000 | - |

## 🚀 使い方

1. モデルを選択（最新順にソート）
2. 「📊 選択中のモデル情報」でトークン制限確認
3. ZIPアップロード後、「⚖️ ファイル互換性チェック」を確認
4. 🔴が出たらより大きいモデルを推奨に従って選択

## 🔄 アップデート手順

```bash
git add model_specs.py app.py ai_generator.py
git commit -m "Update to v1.2.0: Latest models and optimization"
git push origin main
```

Streamlit Cloudが自動再デプロイ（2-3分）

## 📞 主な変更ファイル

- `model_specs.py` (新規): モデル仕様データベース
- `app.py` (更新): モデル選択UIと互換性チェック
- `ai_generator.py` (更新): インテリジェント圧縮

---

**Version**: 1.2.0 | **Status**: ✅ Production Ready
