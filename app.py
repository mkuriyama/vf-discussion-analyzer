"""
議論データ分析Webアプリケーション
Streamlit Cloud対応版
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import zipfile
from io import BytesIO

# 静的コンテンツのインポート
import content_reference as ref
import content_settings as settings


def estimate_tokens_multilingual(text):
    """
    多言語対応のトークン推定
    日本語: 1.5文字 ≈ 1トークン（1文字 ≈ 0.67トークン）
    英語: 1単語 ≈ 1.3トークン (4文字 ≈ 1トークン)
    """
    # 日本語文字（ひらがな、カタカナ、漢字）をカウント
    japanese_chars = sum(1 for c in text if '\u3040' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff')
    # それ以外の文字
    other_chars = len(text) - japanese_chars
    
    # 推定トークン数
    # 日本語: 1.5文字 ≈ 1トークン
    # 英語など: 4文字 ≈ 1トークン
    estimated_tokens = int(japanese_chars / 1.5 + other_chars / 4)
    
    return estimated_tokens


def calculate_cost(input_tokens, output_tokens, model_info, exchange_rate=150.0):
    """
    コストを計算（USD → JPY）
    
    Parameters:
    -----------
    input_tokens : int
        入力トークン数
    output_tokens : int
        出力トークン数  
    model_info : dict
        モデル情報（cost_input, cost_outputを含む）
    exchange_rate : float
        USD/JPY為替レート
    
    Returns:
    --------
    dict : {
        'input_cost_usd': float,
        'output_cost_usd': float,
        'total_cost_usd': float,
        'input_cost_jpy': float,
        'output_cost_jpy': float,
        'total_cost_jpy': float
    }
    """
    cost_input_per_1m = model_info.get('cost_input', 0)
    cost_output_per_1m = model_info.get('cost_output', 0)
    
    # USD計算
    input_cost_usd = (input_tokens / 1_000_000) * cost_input_per_1m
    output_cost_usd = (output_tokens / 1_000_000) * cost_output_per_1m
    total_cost_usd = input_cost_usd + output_cost_usd
    
    # JPY計算
    input_cost_jpy = input_cost_usd * exchange_rate
    output_cost_jpy = output_cost_usd * exchange_rate
    total_cost_jpy = total_cost_usd * exchange_rate
    
    return {
        'input_cost_usd': input_cost_usd,
        'output_cost_usd': output_cost_usd,
        'total_cost_usd': total_cost_usd,
        'input_cost_jpy': input_cost_jpy,
        'output_cost_jpy': output_cost_jpy,
        'total_cost_jpy': total_cost_jpy
    }

# ページ設定
st.set_page_config(
    page_title="VFデータ変換・結果出力ツール",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
    }
    .output-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    /* Optimized spacing for Markdown rendered content */
    .compact-content p {
        margin-bottom: 0.5rem !important;
        margin-top: 0rem !important;
        line-height: 1.6 !important;
    }
    .compact-content h1 {
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
        font-size: 1.8rem !important;
    }
    .compact-content h2 {
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
        font-size: 1.5rem !important;
    }
    .compact-content h3 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1.2rem !important;
    }
    .compact-content ul, .compact-content ol {
        margin-bottom: 0.5rem !important;
        margin-top: 0.3rem !important;
        padding-left: 1.5rem !important;
    }
    .compact-content li {
        margin-bottom: 0.2rem !important;
        line-height: 1.5 !important;
    }
    .compact-content blockquote {
        margin: 0.5rem 0 !important;
        padding-left: 1rem !important;
        border-left: 3px solid #ccc !important;
    }
    .compact-content code {
        background-color: #f4f4f4 !important;
        padding: 0.1rem 0.3rem !important;
        border-radius: 3px !important;
    }
    .compact-content pre {
        margin: 0.5rem 0 !important;
        padding: 0.8rem !important;
        background-color: #f4f4f4 !important;
        border-radius: 5px !important;
    }
</style>
""", unsafe_allow_html=True)

# タイトル
st.markdown('<div class="main-header">📊 VFデータ変換・結果出力ツール（プロトタイプ検討用）</div>', unsafe_allow_html=True)
st.markdown("VFからダウンロードしたAIエージェント会議録データを加工し、目的に合わせたレポートを生成します")

# サイドバー設定
st.sidebar.header("⚙️ 設定")

# セッションステートの初期化（最初に実行）
if 'output_history' not in st.session_state:
    st.session_state.output_history = []
if 'current_md_content' not in st.session_state:
    st.session_state.current_md_content = None
if 'current_md_path' not in st.session_state:
    st.session_state.current_md_path = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# APIキー設定（折りたたみ可能）
with st.sidebar.expander("🔑 APIキー設定", expanded=False):
    st.info("""
    **APIキーの使用方法**:
    - 空欄の場合: システムに設定されたAPIキーを使用（設定されている場合）
    - 入力した場合: 入力したAPIキーを優先使用
    
    ⚠️ 自分のAPIキーを入力する場合は、使用後にブラウザを閉じることを推奨します。
    """)
    
    # ユーザー入力のAPIキー（デフォルトは空）
    user_openai_key = st.text_input(
        "OpenAI APIキー（任意）",
        type="password",
        help="自分のAPIキーを使用する場合のみ入力してください",
        placeholder="空欄の場合はシステム設定を使用"
    )
    
    user_anthropic_key = st.text_input(
        "Anthropic APIキー（任意）",
        type="password",
        help="自分のAPIキーを使用する場合のみ入力してください",
        placeholder="空欄の場合はシステム設定を使用"
    )
    
    user_google_key = st.text_input(
        "Google APIキー（任意）",
        type="password",
        help="自分のAPIキーを使用する場合のみ入力してください",
        placeholder="空欄の場合はシステム設定を使用"
    )
    
    # 実際に使用するAPIキーを決定（ユーザー入力 or システム設定）
    openai_api_key = user_openai_key if user_openai_key else os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key = user_anthropic_key if user_anthropic_key else os.getenv("ANTHROPIC_API_KEY", "")
    google_api_key = user_google_key if user_google_key else os.getenv("GOOGLE_API_KEY", "")
    
    # 使用中のキーの状態を表示（キー自体は表示しない）
    st.markdown("**現在の設定状態:**")
    col1, col2 = st.columns(2)
    with col1:
        st.write("OpenAI:", "🔑 ユーザー入力" if user_openai_key else ("✅ システム設定" if openai_api_key else "❌ 未設定"))
    with col2:
        st.write("Anthropic:", "🔑 ユーザー入力" if user_anthropic_key else ("✅ システム設定" if anthropic_api_key else "❌ 未設定"))
    st.write("Google:", "🔑 ユーザー入力" if user_google_key else ("✅ システム設定" if google_api_key else "❌ 未設定"))


st.sidebar.markdown("---")

# 為替レート設定
exchange_rate = st.sidebar.number_input(
    "💱 為替レート (USD/JPY)",
    min_value=100.0,
    max_value=200.0,
    value=150.0,
    step=0.1,
    help="コスト計算に使用する為替レート"
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 モデル選択")

# モデル仕様の読み込み
import model_specs
import importlib

# モジュールを強制的にリロード（開発時のみ、本番では不要）
importlib.reload(model_specs)

# すべてのプロバイダーのモデルを統合
all_models = []
for provider_name in ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"]:
    provider_models = model_specs.get_available_models(provider_name)
    for model_id, info in provider_models.items():
        all_models.append({
            'id': model_id,
            'name': info['name'],
            'provider': provider_name,
            'released': info.get('released', ''),
            'description': info['description'],
            'cost_input': info.get('cost_input', 0),
            'cost_output': info.get('cost_output', 0)
        })


# プロバイダー別にグループ化して表示（モデル名のみ - シンプル表示）
model_options = []
model_id_map = {}
for model in sorted(all_models, key=lambda x: (x['provider'], x['released']), reverse=True):
    # シンプルな表示名: モデル名のみ
    display_name = f"{model['name']}"
    model_options.append(display_name)
    model_id_map[display_name] = (model['id'], model['provider'])

# モデル選択
if model_options:
    selected_display_name = st.sidebar.selectbox(
        "使用するモデル",
        model_options,
        index=0,
        help="すべてのプロバイダーのモデルから選択"
    )
    
    # 選択されたモデルのIDとプロバイダーを取得
    selected_model, ai_provider = model_id_map[selected_display_name]
    
    # 選択されたプロバイダーに応じてAPIキーを設定
    if ai_provider == "OpenAI":
        api_key = openai_api_key
    elif ai_provider == "Anthropic (Claude)":
        api_key = anthropic_api_key
    else:  # Google (Gemini)
        api_key = google_api_key
    
    # モデル情報の表示（コスト情報を含む）
    selected_model_info = model_specs.get_model_info(ai_provider, selected_model)
    
    with st.sidebar.expander("📊 選択中のモデル情報", expanded=False):
        # CSSでコンパクト表示
        st.markdown("""
        <style>
        .compact-info p { margin-bottom: 0.3rem !important; }
        </style>
        <div class="compact-info">
        """, unsafe_allow_html=True)
        
        st.write(f"**プロバイダー**: {ai_provider}")
        st.write(f"**モデル名**: {selected_model_info['name']}")
        st.write(f"**説明**: {selected_model_info['description']}")
        st.write(f"**モデルID**: `{selected_model}`")
        st.write(f"**リリース**: {selected_model_info.get('released', 'N/A')}")
        
        # トークン制限情報
        st.markdown("**📏 トークン制限:**")
        input_tokens = selected_model_info['input_tokens']
        output_tokens = selected_model_info['output_tokens']
        
        st.write(f"• 入力: {input_tokens:,} tokens")
        if 'input_tokens_extended' in selected_model_info:
            st.write(f"  *(拡張: {selected_model_info['input_tokens_extended']:,} tokens)*")
        st.write(f"• 出力: {output_tokens:,} tokens")
        
        # コスト情報（統合版）
        cost_input = selected_model_info.get('cost_input', 0)
        cost_output = selected_model_info.get('cost_output', 0)
        
        if cost_input > 0 or cost_output > 0:
            st.markdown("**💰 コスト (USD per 1M tokens):**")
            st.write(f"• 入力: ${cost_input:.2f}")
            st.write(f"• 出力: ${cost_output:.2f}")
            
            # 長文コストがある場合（Gemini 3 Pro等）
            if 'cost_input_long' in selected_model_info:
                st.write(f"• 入力 (>200K): ${selected_model_info['cost_input_long']:.2f}")
                st.write(f"• 出力 (>200K): ${selected_model_info['cost_output_long']:.2f}")
        
        if 'note' in selected_model_info:
            st.info(selected_model_info['note'])
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ファイルサイズとの比較表示
    if 'current_md_content' in st.session_state and st.session_state.current_md_content:
        compatibility = model_specs.check_token_compatibility(
            ai_provider,
            selected_model,
            st.session_state.current_md_content
        )
        
        with st.sidebar.expander("⚖️ ファイル互換性チェック", expanded=True):
            # ステータス表示
            if compatibility['status'] == 'safe':
                st.success("✅ 余裕あり - データは圧縮せずに処理可能")
                status_color = "green"
            elif compatibility['status'] == 'warning':
                st.warning("⚠️ 注意 - データ量が多め")
                status_color = "orange"
            else:
                st.error("🔴 制限近い - データを自動圧縮します")
                status_color = "red"
            
            # プログレスバー
            st.progress(
                min(compatibility['usage_percentage'] / 100, 1.0),
                text=f"トークン使用率: {compatibility['usage_percentage']:.1f}%"
            )
            
            st.write(f"**推定トークン数**: {compatibility['estimated_tokens']:,}")
            st.write(f"**モデル上限**: {compatibility['max_tokens']:,}")
            
            # 推奨モデル表示
            if compatibility['compression_needed']:
                st.markdown("---")
                st.write("**💡 より大きいモデルを推奨:**")
                
                recommendations = model_specs.get_optimal_models(
                    ai_provider,
                    st.session_state.current_md_content
                )
                
                for rec in recommendations[:3]:  # 上位3つを表示
                    if rec['is_safe']:
                        st.write(f"✅ {rec['model_name']} ({rec['usage_percentage']:.1f}%)")
else:
    st.sidebar.error("モデル情報の読み込みに失敗しました")

st.sidebar.markdown("---")

# ファイルアップロード
st.sidebar.subheader("📁 ファイルアップロード")
uploaded_file = st.sidebar.file_uploader(
    "ZIPファイルを選択",
    type=['zip'],
    help="議論データが含まれるZIPファイルをアップロード"
)

# ファイルがアップロードされたら、Markdown変換を実行
if uploaded_file is not None:
    # 新しいファイルがアップロードされた場合のみ処理
    if 'uploaded_file_name' not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.uploaded_file_name = uploaded_file.name
        
        with st.sidebar:
            with st.spinner("📄 Markdownに変換中..."):
                import processor
                import tempfile
                
                try:
                    # 一時ファイルに保存
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Markdown変換
                    md_path = processor.convert_zip_to_markdown(tmp_path)
                    
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                        st.session_state.current_md_content = md_content
                        st.session_state.current_md_path = md_path
                    
                    # 元のZIPファイルとMarkdownファイルのデータ量を計算
                    zip_size_bytes = len(uploaded_file.getvalue())
                    md_size_bytes = len(md_content.encode('utf-8'))
                    md_char_count = len(md_content)
                    
                    st.session_state.conversion_stats = {
                        'zip_size_bytes': zip_size_bytes,
                        'md_size_bytes': md_size_bytes,
                        'md_char_count': md_char_count
                    }
                    
                    # クリーンアップ
                    os.unlink(tmp_path)
                    
                    st.success(f"✅ 変換完了: {uploaded_file.name}")
                    
                    # データ量の表示
                    st.write("**📊 データ量:**")
                    st.write(f"  • 元ZIP: {zip_size_bytes:,} bytes ({zip_size_bytes/1024:.1f} KB)")
                    st.write(f"  • Markdown: {md_size_bytes:,} bytes ({md_size_bytes/1024:.1f} KB)")
                    st.write(f"  • 文字数: {md_char_count:,}字")
                    
                except Exception as e:
                    st.error(f"❌ 変換エラー: {str(e)}")
                    st.session_state.current_md_content = None
                    st.session_state.current_md_path = None

# メインエリア
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Markdown閲覧", "📝 レポート生成", "📚 出力結果一覧", "📖 参考情報", "🔧 詳細設定"])

with tab1:
    st.subheader("📄 変換されたMarkdownファイル")
    
    if st.session_state.current_md_content is None:
        st.info("👈 サイドバーからZIPファイルをアップロードしてください")
    else:
        st.success(f"✅ ファイル: {st.session_state.uploaded_file_name}")
        
        # データ量情報を表示（永続化）
        if 'conversion_stats' in st.session_state:
            conv_stats = st.session_state.conversion_stats
            st.markdown("**📊 データ量:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("元ZIP", f"{conv_stats['zip_size_bytes']/1024:.1f} KB")
            with col2:
                st.metric("Markdown", f"{conv_stats['md_size_bytes']/1024:.1f} KB")
            with col3:
                st.metric("文字数", f"{conv_stats['md_char_count']:,}字")
        
        # Markdownの表示（整形済み）
        st.markdown("---")
        st.markdown(st.session_state.current_md_content)
        
        # ダウンロードボタン
        st.markdown("---")
        st.download_button(
            label="📥 Markdownファイルをダウンロード",
            data=st.session_state.current_md_content,
            file_name=f"{Path(st.session_state.uploaded_file_name).stem}_converted.md",
            mime="text/markdown",
            use_container_width=True
        )

with tab2:
    st.subheader("📝 AIレポート生成")
    
    if st.session_state.current_md_content is None:
        st.info("👈 まずサイドバーからZIPファイルをアップロードしてください")
    else:
        st.success(f"✅ ファイル: {st.session_state.uploaded_file_name}")
        
        # 出力タイプ選択
        st.subheader("📝 出力タイプ選択")
        
        output_type = st.radio(
            "レポートの種類を選択してください:",
            [
                "400字版 - エグゼクティブサマリー",
                "2000字版 - 構造化レポート（推奨）",
                "5000字版 - 詳細分析レポート",
                "カスタム - 自由記述で指示"
            ],
            index=1,
            help="デフォルトは2000字版がおすすめです"
        )
        
        # 選択された出力タイプの指示文を表示
        with st.expander("💡 選択中の出力タイプの指示文（参考）"):
            if "400字" in output_type:
                st.code("""以下の議論データから、最も重要なポイントのみを抽出し、400字以内のエグゼクティブサマリーを作成してください。""", language="text")
            elif "2000字" in output_type:
                st.code("""以下の議論データを分析し、2000字程度の構造化レポートを作成してください。

レポート構成:
1. 全体サマリー（200字）
2. 主要な意見の整理（頻出意見と高評価意見の対比を含む）
3. 特筆すべき少数意見
4. 結論と示唆""", language="text")
            elif "5000字" in output_type:
                st.code("""以下の議論データを詳細に分析し、5000字程度の包括的レポートを作成してください。

レポート構成:
1. エグゼクティブサマリー（300字）
2. 議論の背景と目的
3. 主要トピックごとの詳細分析
   - 各トピックについて、賛成意見・反対意見・中立意見を整理
   - 高評価を得た意見の詳細な分析
4. 頻出キーワードと傾向分析
5. 特筆すべき少数意見・独創的な提案
6. 総合的な結論と今後の検討課題""", language="text")
            else:
                st.info("カスタム指示を下記に入力してください。上記の指示文を参考に、自由に改変できます。")
        
        # カスタム指示入力
        custom_instruction = None
        if "カスタム" in output_type:
            custom_instruction = st.text_area(
                "出力内容の指示を入力してください:",
                height=200,
                placeholder="例: 主要な意見を3つに絞り、それぞれについて賛成・反対の意見を対比させてください。全体で1500字程度でまとめてください。"
            )
        
        st.markdown("---")
        
        # コスト推定を表示
        if st.session_state.current_md_content:
            input_tokens_est = estimate_tokens_multilingual(st.session_state.current_md_content)
            
            # 出力トークン推定（出力タイプに基づく）
            if "400字" in output_type:
                output_tokens_est = int(400 / 1.5)  # 日本語: 1.5文字≈1トークン
            elif "2000字" in output_type:
                output_tokens_est = int(2000 / 1.5)
            elif "5000字" in output_type:
                output_tokens_est = int(5000 / 1.5)
            else:
                output_tokens_est = int(2000 / 1.5)  # デフォルト
            
            # コスト計算
            cost_estimate = calculate_cost(
                input_tokens_est,
                output_tokens_est,
                selected_model_info,
                exchange_rate
            )
            
            st.info(f"""
            💰 **推定コスト** (為替: {exchange_rate:.1f}円/USD)  
            • 入力: {input_tokens_est:,} tokens → ¥{cost_estimate['input_cost_jpy']:.2f}  
            • 出力: {output_tokens_est:,} tokens → ¥{cost_estimate['output_cost_jpy']:.2f}  
            • **合計: ¥{cost_estimate['total_cost_jpy']:.2f}** (${cost_estimate['total_cost_usd']:.4f})
            
            ※実際のコストは出力内容により変動します
            """)
        
        # 生成ボタン
        if st.button("🚀 レポート生成", type="primary", use_container_width=True):
            if not api_key:
                st.error(f"❌ {ai_provider} のAPIキーを設定してください")
            elif "カスタム" in output_type and not custom_instruction:
                st.error("❌ カスタム指示を入力してください")
            else:
                with st.spinner("🔄 AIでレポート生成中..."):
                    import ai_generator
                    from datetime import datetime
                    
                    try:
                        # 指示文の準備
                        if "400字" in output_type:
                            instruction = "以下の議論データから、最も重要なポイントのみを抽出し、400字以内のエグゼクティブサマリーを作成してください。"
                        elif "2000字" in output_type:
                            instruction = """以下の議論データを分析し、2000字程度の構造化レポートを作成してください。
                            
レポート構成:
1. 全体サマリー（200字）
2. 主要な意見の整理（頻出意見と高評価意見の対比を含む）
3. 特筆すべき少数意見
4. 結論と示唆
"""
                        elif "5000字" in output_type:
                            instruction = """以下の議論データの詳細分析レポートを5000字程度で作成してください。

レポート構成:
1. エグゼクティブサマリー
2. データ概要（参加者数、設問数など）
3. 設問別の詳細分析
   - 回答分布
   - 高評価意見の分析
   - 多数意見と少数意見の対比
4. 横断的な分析
   - 共通テーマの抽出
   - 意見の対立軸の可視化
5. 結論と提言
"""
                        else:
                            instruction = custom_instruction
                        
                        # AI生成（プロバイダー対応）
                        result_data = ai_generator.generate_report(
                            md_content=st.session_state.current_md_content,
                            instruction=instruction,
                            api_key=api_key,
                            model=selected_model,
                            provider=ai_provider
                        )
                        
                        result = result_data['content']
                        stats = result_data['stats']
                        
                        st.success("✅ レポート生成完了")
                        
                        # 統計情報の表示
                        st.write("**📊 生成統計:**")
                        
                        # 入力データ量の表示
                        if 'conversion_stats' in st.session_state:
                            conv_stats = st.session_state.conversion_stats
                            st.write("**入力データ:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("元ZIP", f"{conv_stats['zip_size_bytes']/1024:.1f} KB")
                            with col2:
                                st.metric("Markdown", f"{conv_stats['md_size_bytes']/1024:.1f} KB")
                            with col3:
                                st.metric("文字数", f"{conv_stats['md_char_count']:,}字")
                        
                        # 出力データ量と処理時間の表示
                        st.write("**出力データ:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            # 処理時間を分と秒で表示
                            if stats['processing_time'] >= 60:
                                minutes = int(stats['processing_time'] // 60)
                                seconds = stats['processing_time'] % 60
                                st.metric("処理時間", f"{minutes}分{seconds:.0f}秒")
                            else:
                                st.metric("処理時間", f"{stats['processing_time']:.1f}秒")
                        with col2:
                            st.metric("出力文字数", f"{stats['output_chars']:,}字")
                        with col3:
                            st.metric("出力サイズ", f"{stats['output_bytes']/1024:.1f} KB")
                        
                        st.write(f"**使用モデル**: {stats['model']}")
                        if stats['compressed']:
                            st.info("ℹ️ 入力データが圧縮されました")
                        
                        # 使用量に基づくコスト推定
                        actual_input_tokens = estimate_tokens_multilingual(st.session_state.current_md_content)
                        actual_output_tokens = estimate_tokens_multilingual(result)
                        actual_cost = calculate_cost(
                            actual_input_tokens,
                            actual_output_tokens,
                            selected_model_info,
                            exchange_rate
                        )
                        
                        st.write("**💰 使用量ベースのコスト推定:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "入力コスト",
                                f"¥{actual_cost['input_cost_jpy']:.2f}",
                                f"{actual_input_tokens:,} tokens"
                            )
                        with col2:
                            st.metric(
                                "出力コスト",
                                f"¥{actual_cost['output_cost_jpy']:.2f}",
                                f"{actual_output_tokens:,} tokens"
                            )
                        with col3:
                            st.metric(
                                "合計推定",
                                f"¥{actual_cost['total_cost_jpy']:.2f}",
                                f"${actual_cost['total_cost_usd']:.4f}"
                            )
                        
                        st.caption(f"為替レート: {exchange_rate:.1f}円/USD | ※思考トークン等は含まれません")
                        
                        # 結果表示（Markdownレンダリング）
                        st.markdown("---")
                        st.subheader("📄 生成されたレポート")
                        
                        # CSSクラスを適用したコンテナ内でMarkdownをレンダリング
                        st.markdown('<div class="compact-content">', unsafe_allow_html=True)
                        st.markdown(result, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 履歴に保存
                        output_record = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'zip_file': st.session_state.uploaded_file_name,
                            'output_type': output_type,
                            'custom_instruction': custom_instruction if custom_instruction else "-",
                            'provider': ai_provider,
                            'model': selected_model,
                            'model_name': selected_model_info['name'],
                            'content': result,
                            'stats': stats,
                            'cost': {
                                'input_tokens': actual_input_tokens,
                                'output_tokens': actual_output_tokens,
                                'total_jpy': actual_cost['total_cost_jpy'],
                                'total_usd': actual_cost['total_cost_usd'],
                                'exchange_rate': exchange_rate
                            }
                        }
                        st.session_state.output_history.insert(0, output_record)
                        
                        # ダウンロード
                        st.markdown("---")
                        st.download_button(
                            label="📥 レポートをダウンロード",
                            data=result,
                            file_name=f"report_{Path(st.session_state.uploaded_file_name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        
                    except Exception as e:
                        st.error(f"❌ エラーが発生しました: {str(e)}")
                        import traceback
                        with st.expander("詳細なエラー情報"):
                            st.code(traceback.format_exc())

with tab3:
    st.subheader("📚 出力結果一覧")
    
    if len(st.session_state.output_history) == 0:
        st.info("まだレポートが生成されていません")
    else:
        st.write(f"**保存されているレポート数**: {len(st.session_state.output_history)}")
        
        # 一括ダウンロード機能
        if st.button("📦 全レポートを一括ダウンロード (ZIP)", use_container_width=True):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for idx, record in enumerate(st.session_state.output_history):
                    # レポート本文
                    report_filename = f"{idx+1:02d}_{record['timestamp'].replace(':', '-')}_{record['output_type'].split(' ')[0]}.md"
                    zip_file.writestr(report_filename, record['content'])
                    
                    # メタデータ（Markdown形式）
                    stats = record.get('stats', {})
                    cost = record.get('cost', {})
                    
                    # コスト内訳を計算
                    input_tokens = cost.get('input_tokens', 0)
                    output_tokens = cost.get('output_tokens', 0)
                    total_jpy = cost.get('total_jpy', 0)
                    total_tokens = input_tokens + output_tokens
                    
                    if total_tokens > 0:
                        input_cost_jpy = total_jpy * input_tokens / total_tokens
                        output_cost_jpy = total_jpy * output_tokens / total_tokens
                    else:
                        input_cost_jpy = 0
                        output_cost_jpy = 0
                    
                    metadata_md = f"""# レポートメタデータ

## 基本情報
- **生成日時**: {record['timestamp']}
- **元ファイル**: {record['zip_file']}
- **出力タイプ**: {record['output_type']}
- **カスタム指示**: {record.get('custom_instruction', '-')}

## モデル情報
- **AIプロバイダー**: {record['provider']}
- **モデル名**: {record.get('model_name', record['model'])}
- **モデルID**: `{record['model']}`

## 処理統計
- **処理時間**: {stats.get('processing_time', 0):.1f}秒
- **出力サイズ**: {stats.get('output_bytes', 0):,} bytes ({stats.get('output_bytes', 0)/1024:.1f} KB)
- **出力文字数**: {stats.get('output_chars', 0):,}字
- **データ圧縮**: {'あり' if stats.get('compressed', False) else 'なし'}

## コスト情報
- **入力トークン**: {input_tokens:,} tokens
- **出力トークン**: {output_tokens:,} tokens
- **入力コスト**: ¥{input_cost_jpy:.2f}
- **出力コスト**: ¥{output_cost_jpy:.2f}
- **合計コスト**: ¥{total_jpy:.2f} (${cost.get('total_usd', 0):.4f})
- **為替レート**: {cost.get('exchange_rate', 150):.1f}円/USD

---
*生成: VFデータ変換・結果出力ツール*
"""
                    metadata_filename = f"{idx+1:02d}_{record['timestamp'].replace(':', '-')}_info.md"
                    zip_file.writestr(metadata_filename, metadata_md)
            
            zip_buffer.seek(0)
            st.download_button(
                label="💾 ZIPファイルをダウンロード",
                data=zip_buffer.getvalue(),
                file_name=f"all_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        st.markdown("---")
        
        for idx, record in enumerate(st.session_state.output_history):
            # レポートの文字数を計算
            content_length = len(record['content'])
            
            # コスト情報を取得
            cost_info = record.get('cost', {})
            cost_display = f"¥{cost_info.get('total_jpy', 0):.2f}" if cost_info else "N/A"
            
            # 改善されたタイトル: 日時 | 出力タイプ | モデル名 | コスト | 文字数
            model_name = record.get('model_name', record['model'])
            title = f"📄 {record['timestamp']} | {record['output_type']} | {model_name} | {cost_display} | {content_length:,}字"
            
            with st.expander(title, expanded=(idx == 0)):
                # メタデータ表示
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**生成日時**: {record['timestamp']}")
                    st.write(f"**元ファイル**: {record['zip_file']}")
                    st.write(f"**出力タイプ**: {record['output_type']}")
                with col2:
                    st.write(f"**AIプロバイダー**: {record['provider']}")
                    st.write(f"**モデル**: {model_name}")
                    st.write(f"**モデルID**: `{record['model']}`")
                with col3:
                    st.write(f"**文字数**: {content_length:,}字")
                    if cost_info:
                        st.write(f"**コスト推定**: ¥{cost_info.get('total_jpy', 0):.2f}")
                        st.write(f"  (${cost_info.get('total_usd', 0):.4f})")
                    
                if record.get('custom_instruction', '-') != "-":
                    st.write(f"**カスタム指示**: {record['custom_instruction']}")
                
                # 処理統計とコスト詳細
                if 'stats' in record or 'cost' in record:
                    st.markdown("**📊 詳細情報:**")
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        if 'stats' in record:
                            stats = record['stats']
                            st.write(f"• 処理時間: {stats.get('processing_time', 0):.1f}秒")
                            st.write(f"• 出力サイズ: {stats.get('output_bytes', 0)/1024:.1f} KB")
                    
                    with detail_col2:
                        if cost_info:
                            st.write(f"• 入力: {cost_info.get('input_tokens', 0):,} tokens")
                            st.write(f"• 出力: {cost_info.get('output_tokens', 0):,} tokens")
                
                st.markdown("---")
                
                # レポート内容表示（Markdownレンダリング）
                st.markdown("---")
                
                # CSSクラスを適用したコンテナ内でMarkdownをレンダリング
                st.markdown('<div class="compact-content">', unsafe_allow_html=True)
                st.markdown(record["content"], unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ダウンロードボタン
                st.download_button(
                    label="📥 このレポートをダウンロード",
                    data=record['content'],
                    file_name=f"report_{idx}_{record['timestamp'].replace(':', '-').replace(' ', '_')}.md",
                    mime="text/markdown",
                    key=f"download_{idx}"
                )

with tab4:
    st.markdown("## 📖 参考情報")
    
    # 使い方セクション
    st.markdown("### 📚 基本的な使い方")
    st.markdown(ref.USAGE_GUIDE)
    
    # トークン推定ロジック
    st.markdown("---")
    st.markdown("### 💡 トークン数推定のロジック")
    st.markdown(ref.TOKEN_ESTIMATION_INTRO)
    
    col1, col2 = st.columns(2)
    with col1:
        st.code(ref.TOKEN_ESTIMATION_EXAMPLE_1, language="text")
    with col2:
        st.code(ref.TOKEN_ESTIMATION_EXAMPLE_2, language="text")
    
    st.info(ref.TOKEN_ESTIMATION_NOTE)
    
    # コスト計算のロジック
    st.markdown("---")
    st.markdown("### 💰 コスト計算のロジック")
    st.markdown("**基本計算式**:")
    st.code(ref.COST_CALCULATION_FORMULA, language="text")
    
    st.markdown("**計算例** (Gemini 2.5 Flash-Lite、為替150円/USD):")
    st.code(ref.COST_CALCULATION_EXAMPLE, language="text")
    
    st.warning(ref.COST_CALCULATION_WARNING)
    
    # 各出力タイプの指示文
    st.markdown("---")
    st.markdown("### 📝 各出力タイプの指示文")
    
    tab_400, tab_2000, tab_5000 = st.tabs(["400字版", "2000字版", "5000字版"])
    
    with tab_400:
        st.markdown("**400字版 - エグゼクティブサマリー**")
        st.code(ref.OUTPUT_INSTRUCTIONS["400字版"], language="text")
    
    with tab_2000:
        st.markdown("**2000字版 - 構造化レポート（推奨）**")
        st.code(ref.OUTPUT_INSTRUCTIONS["2000字版"], language="text")
    
    with tab_5000:
        st.markdown("**5000字版 - 詳細分析レポート**")
        st.code(ref.OUTPUT_INSTRUCTIONS["5000字版"], language="text")
    
    st.info(ref.OUTPUT_INSTRUCTIONS_NOTE)
    
    # 暗黙の前提条件
    st.markdown("---")
    st.markdown("### ⚠️ 暗黙の前提と制限事項")
    st.markdown(ref.ASSUMPTIONS_AND_LIMITATIONS)
    
    # Tips
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown(ref.TIPS_CONTENT)


with tab5:
    st.markdown("## 🔧 詳細設定")
    
    # 対応モデル一覧
    st.markdown("### 📋 対応モデル一覧")
    
    # 動的にモデル情報を表示
    for provider_name in ["OpenAI", "Anthropic (Claude)", "Google (Gemini)"]:
        st.markdown(f"#### {provider_name}")
        
        provider_models = model_specs.get_available_models(provider_name)
        
        # モデル情報をテーブル形式で表示
        model_data = []
        for model_id, info in provider_models.items():
            input_tokens = info.get('input_tokens', 0)
            output_tokens = info.get('output_tokens', 0)
            
            # 拡張トークンがあれば表示
            if 'input_tokens_extended' in info:
                input_str = f"{input_tokens:,} ({info['input_tokens_extended']:,}拡張)"
            else:
                input_str = f"{input_tokens:,}"
            
            model_data.append({
                'モデル': info['name'],
                'モデルID': f"`{model_id}`",
                '入力トークン': input_str,
                '出力トークン': f"{output_tokens:,}",
                'コスト ($/1M)': f"${info.get('cost_input', 0):.2f} / ${info.get('cost_output', 0):.2f}",
                '説明': info['description']
            })
        
        # DataFrameで表示
        import pandas as pd
        df = pd.DataFrame(model_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("")
    
    # APIキーの取得、Tips、Secrets設定
    st.markdown("---")
    st.markdown(settings.API_KEY_GUIDE)
    
    st.markdown("---")
    st.markdown(settings.SETTINGS_TIPS)
    
    st.markdown("---")
    st.markdown(settings.STREAMLIT_SECRETS_GUIDE)
    
    # モデル設定編集（上級者向け - 現在無効） - 一番下に移動
    st.markdown("---")
    st.markdown("### 🔧 モデル設定編集（上級者向け）")
    
    if st.checkbox("モデル設定を編集する（上級者向け）", disabled=True):
        st.warning(settings.MODEL_EDITING_WARNING)
        st.info("この機能は現在開発中です。次のバージョンで有効化予定です。")
        
        # モデルデータ表示（読み取り専用として）
        model_data_path = Path(__file__).parent / 'model_data.py'
        try:
            with open(model_data_path, 'r', encoding='utf-8') as f:
                model_data_content = f.read()
            
            st.text_area(
                "現在のモデル設定（読み取り専用）:",
                value=model_data_content,
                height=300,
                disabled=True,
                help="この機能は開発中のため、現在は閲覧のみ可能です"
            )
        except FileNotFoundError:
            st.error(f"model_data.pyが見つかりません: {model_data_path}")


# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Powered by OpenAI API | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
