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
from datetime import datetime, timezone, timedelta
import json
import zipfile
from io import BytesIO

# 静的コンテンツのインポート
import content_reference as ref
import content_settings as settings
import output_templates as templates

# 機能モジュールのインポート
import ai_generator
import model_specs
import processor
import image_model_data
import image_generator


# JST (Japan Standard Time) タイムゾーン
JST = timezone(timedelta(hours=9))

def get_jst_now():
    """現在のJST時刻を取得"""
    return datetime.now(JST)

def format_jst_datetime(dt_str=None):
    """JSTでフォーマットされた日時文字列を返す"""
    if dt_str is None:
        return get_jst_now().strftime('%Y-%m-%d %H:%M:%S JST')
    return dt_str  # 既存のタイムスタンプはそのまま表示


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

# 画像生成モデル選択
st.sidebar.subheader("🎨 画像生成モデル選択")

import image_model_data

# 画像生成プロバイダーとモデルの取得
image_providers = image_model_data.get_image_providers()

# すべての画像モデルを統合
all_image_models = []
for provider_name in image_providers:
    provider_models = image_model_data.get_image_models_by_provider(provider_name)
    for model_id, info in provider_models.items():
        all_image_models.append({
            'id': model_id,
            'name': info['name'],
            'provider': provider_name,
            'description': info['description'],
            'default_size': info['default_size'],
            'default_quality': info['default_quality']
        })

# 画像モデル選択
image_model_options = []
image_model_id_map = {}
for model in all_image_models:
    display_name = f"{model['name']}"
    image_model_options.append(display_name)
    image_model_id_map[display_name] = (model['id'], model['provider'])

if image_model_options:
    selected_image_display_name = st.sidebar.selectbox(
        "画像生成モデル",
        image_model_options,
        index=0,  # デフォルトは最初のモデル
        help="画像生成に使用するモデルを選択"
    )
    
    # 選択されたモデルのIDとプロバイダーを取得
    selected_image_model, image_provider = image_model_id_map[selected_image_display_name]
    
    # 選択されたプロバイダーに応じてAPIキーを設定
    if image_provider == "OpenAI":
        image_api_key = openai_api_key
    else:  # Google (Gemini)
        image_api_key = google_api_key
    
    # 画像モデル情報の取得
    selected_image_model_info = image_model_data.get_image_model_info(image_provider, selected_image_model)
    
    # サイズと品質の選択
    col1, col2 = st.sidebar.columns(2)
    with col1:
        available_sizes = selected_image_model_info['supported_sizes']
        selected_image_size = st.selectbox(
            "サイズ",
            available_sizes,
            index=available_sizes.index(selected_image_model_info['default_size']),
            help="生成する画像のサイズ"
        )
    
    with col2:
        available_qualities = selected_image_model_info['supported_quality']
        selected_image_quality = st.selectbox(
            "品質",
            available_qualities,
            index=available_qualities.index(selected_image_model_info['default_quality']),
            help="画像の品質設定"
        )
    
    # 画像モデル情報の表示
    with st.sidebar.expander("📊 選択中の画像モデル情報", expanded=False):
        st.write(f"**プロバイダー**: {image_provider}")
        st.write(f"**モデル名**: {selected_image_model_info['name']}")
        st.write(f"**説明**: {selected_image_model_info['description']}")
        st.write(f"**モデルID**: `{selected_image_model}`")
        
        # コスト情報
        st.markdown("**💰 コスト:**")
        image_cost = image_model_data.calculate_image_cost(
            image_provider,
            selected_image_model,
            selected_image_size,
            selected_image_quality,
            num_images=1
        )
        image_cost_jpy = image_cost * exchange_rate
        st.write(f"• 1枚あたり: ${image_cost:.4f} (¥{image_cost_jpy:.2f})")

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
        
        # 出力テンプレート選択
        st.subheader("📝 出力形式選択")
        
        # カテゴリ別の選択肢を作成
        categorized = templates.get_categorized_template_names()
        
        # 選択肢をフラット化（カテゴリプレフィックス付き）
        template_options = []
        template_map = {}  # 表示名 -> テンプレートオブジェクト
        
        for category, template_names in categorized.items():
            for name in template_names:
                template_obj = templates.get_template_by_name(name)
                if template_obj:
                    # 表示形式: "カテゴリ > テンプレート名"
                    display_name = f"{category} > {name}"
                    template_options.append(display_name)
                    template_map[display_name] = template_obj
        
        # セッション状態で選択を保持
        if 'selected_template_display' not in st.session_state:
            # デフォルトは2000字版
            default_name = "要約・サマリー > 2000字版 - 構造化レポート"
            st.session_state.selected_template_display = default_name if default_name in template_options else template_options[0]
        
        # ドロップダウンで選択
        selected_display = st.selectbox(
            "出力形式を選択してください:",
            options=template_options,
            index=template_options.index(st.session_state.selected_template_display) if st.session_state.selected_template_display in template_options else 0,
            help="カテゴリ別に整理された出力形式から選択できます"
        )
        
        # 選択を保存
        st.session_state.selected_template_display = selected_display
        
        # 選択されたテンプレートを取得
        selected_template = template_map[selected_display]
        
        # テンプレートの説明を表示
        st.info(f"📄 **{selected_template['description']}**")
        
        # 日本語対応テンプレートの場合は注意書きを表示
        if selected_template.get('requires_japanese', False):
            # 現在のモデルが推奨かどうか判定
            is_gemini_3_pro = 'gemini-3-pro' in selected_image_model.lower()
            is_gpt_image = 'gpt-image' in selected_image_model.lower()
            
            if is_gemini_3_pro:
                model_status = "✅ 最適"
            elif is_gpt_image:
                model_status = "✅ 推奨"
            else:
                model_status = "⚠️ 品質が低い可能性"
            
            st.warning(f"""
            ℹ️ **日本語テキスト対応テンプレート**
            
            このテンプレートは画像内に日本語テキストを含みます。
            
            **推奨モデル（最新モデル推奨）**:
            - 🌟 Gemini 3 Pro Image Preview（最高品質）
            - ✅ GPT-Image-1シリーズ（高品質）
            - △ Gemini 2.5 Flash Image（日本語テキストが崩れる場合あり）
            
            **非推奨モデル**:
            - ❌ Imagen 4シリーズ（日本語テキストの品質が低い）
            
            現在選択中: **{selected_image_model_info['name']}** ({model_status})
            """)
        
        # 指示文の表示と編集
        st.subheader("✏️ 指示文")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**現在の指示文:**")
        with col2:
            edit_mode = st.checkbox("編集する", value=False, key="edit_instruction")
        
        if edit_mode or selected_template['name'] == 'カスタム指示':
            # 編集可能モード
            if 'edited_instruction' not in st.session_state or st.session_state.get('last_template') != selected_template['name']:
                st.session_state.edited_instruction = selected_template['instruction']
                st.session_state.last_template = selected_template['name']
            
            edited_instruction = st.text_area(
                "指示文を編集:",
                value=st.session_state.edited_instruction,
                height=300,
                help="この指示文を編集して、カスタマイズしたレポートを生成できます",
                label_visibility="collapsed"
            )
            
            st.session_state.edited_instruction = edited_instruction
            
            # 編集している場合の注意
            if edited_instruction != selected_template['instruction']:
                st.warning("⚠️ 指示文が編集されています。元に戻す場合は「編集する」のチェックを外してください。")
            
            final_instruction = edited_instruction
        else:
            # 表示のみモード
            if selected_template['instruction']:
                st.code(selected_template['instruction'], language="text")
            else:
                st.info("カスタム指示を使用する場合は、「編集する」にチェックを入れて指示文を入力してください。")
            
            final_instruction = selected_template['instruction']
        
        st.markdown("---")
        
        # コスト推定を表示
        if st.session_state.current_md_content and final_instruction:
            input_tokens_est = estimate_tokens_multilingual(st.session_state.current_md_content)
            output_tokens_est = selected_template['estimated_tokens']
            
            # コスト計算
            cost_estimate = calculate_cost(
                input_tokens_est,
                output_tokens_est,
                selected_model_info,
                exchange_rate
            )
            
            # 画像生成の場合は画像コストも含める
            is_image_template = selected_template.get('output_type') == 'image'
            
            if is_image_template:
                # 画像生成コストを計算
                image_cost_usd = image_model_data.calculate_image_cost(
                    image_provider,
                    selected_image_model,
                    selected_image_size,
                    selected_image_quality,
                    num_images=1
                )
                image_cost_jpy = image_cost_usd * exchange_rate
                
                # 合計コスト（言語モデル + 画像モデル）
                total_cost_usd = cost_estimate['total_cost_usd'] + image_cost_usd
                total_cost_jpy = cost_estimate['total_cost_jpy'] + image_cost_jpy
                
                st.info(f"""
                💰 **推定コスト** (為替: {exchange_rate:.1f}円/USD)
                
                **フェーズ1: プロンプト生成**（言語モデル: {selected_model_info['name']}）
                • 入力: {input_tokens_est:,} tokens → ¥{cost_estimate['input_cost_jpy']:.2f}  
                • 出力: {output_tokens_est:,} tokens → ¥{cost_estimate['output_cost_jpy']:.2f}  
                • 小計: ¥{cost_estimate['total_cost_jpy']:.2f} (${cost_estimate['total_cost_usd']:.4f})
                
                **フェーズ2: 画像生成**（画像モデル: {selected_image_model_info['name']}）
                • サイズ: {selected_image_size}
                • 品質: {selected_image_quality}
                • 小計: ¥{image_cost_jpy:.2f} (${image_cost_usd:.4f})
                
                **合計: ¥{total_cost_jpy:.2f}** (${total_cost_usd:.4f})
                
                ※実際のコストは出力内容により変動します
                """)
            else:
                st.info(f"""
                💰 **推定コスト** (為替: {exchange_rate:.1f}円/USD)  
                • 入力: {input_tokens_est:,} tokens → ¥{cost_estimate['input_cost_jpy']:.2f}  
                • 出力: {output_tokens_est:,} tokens → ¥{cost_estimate['output_cost_jpy']:.2f}  
                • **合計: ¥{cost_estimate['total_cost_jpy']:.2f}** (${cost_estimate['total_cost_usd']:.4f})
                
                ※実際のコストは出力内容により変動します
                """)
        
        # 生成ボタン
        button_text = "🎨 画像生成" if is_image_template else "🚀 レポート生成"
        
        if st.button(button_text, type="primary", use_container_width=True, disabled=not final_instruction):
            if not final_instruction:
                st.error("指示文が入力されていません")
            else:
                # プロバイダーに応じたAPIキーを選択
                if ai_provider == "OpenAI":
                    api_key = openai_api_key
                elif ai_provider == "Anthropic (Claude)":
                    api_key = anthropic_api_key
                elif ai_provider == "Google (Gemini)":
                    api_key = google_api_key
                else:
                    api_key = None
                
                if is_image_template:
                    # ========================================
                    # 画像生成の2段階プロセス
                    # ========================================
                    
                    # フェーズ1: 画像生成プロンプトの生成
                    with st.spinner('🔤 画像生成プロンプトを作成中...'):
                        try:
                            import time
                            phase1_start = time.time()
                            
                            result = ai_generator.generate_report(
                                st.session_state.current_md_content,
                                final_instruction,
                                api_key,
                                selected_model,
                                provider=ai_provider
                            )
                            
                            image_prompt = result['content'].strip()
                            phase1_time = time.time() - phase1_start
                            phase1_stats = result['stats']
                            
                            # プロンプト表示
                            st.markdown("---")
                            st.subheader("🔤 生成された画像プロンプト")
                            st.code(image_prompt, language="text")
                            
                            st.info(f"✅ プロンプト生成完了（{phase1_time:.1f}秒）")
                            
                        except Exception as e:
                            st.error(f"プロンプト生成エラー: {str(e)}")
                            st.stop()
                    
                    # フェーズ2: 画像生成
                    with st.spinner('🎨 画像を生成中...'):
                        try:
                            phase2_start = time.time()
                            
                            image_result = image_generator.generate_image(
                                image_prompt,
                                image_provider,
                                selected_image_model,
                                image_api_key,
                                selected_image_size,
                                selected_image_quality
                            )
                            
                            phase2_time = time.time() - phase2_start
                            total_time = phase1_time + phase2_time
                            
                            # 画像表示
                            st.markdown("---")
                            st.subheader("🖼️ 生成された画像")
                            st.image(image_result['image_data'], use_column_width=True)
                            
                            # 改善されたプロンプト表示（DALL-Eの場合）
                            if 'revised_prompt' in image_result and image_result['revised_prompt'] != image_prompt:
                                with st.expander("📝 改善されたプロンプト（DALL-Eによる）"):
                                    st.code(image_result['revised_prompt'], language="text")
                            
                            # 統計情報
                            st.success(f"""
                            ✅ **画像生成完了！**  
                            • プロンプト生成: {phase1_time:.1f}秒  
                            • 画像生成: {phase2_time:.1f}秒  
                            • **合計処理時間**: {total_time:.1f}秒
                            """)
                            
                            # コスト計算
                            # フェーズ1（テキスト生成）のコスト
                            phase1_input_tokens = input_tokens_est
                            phase1_output_tokens = estimate_tokens_multilingual(image_prompt)
                            phase1_cost = calculate_cost(
                                phase1_input_tokens,
                                phase1_output_tokens,
                                selected_model_info,
                                exchange_rate
                            )
                            
                            # フェーズ2（画像生成）のコスト
                            phase2_cost_usd = image_model_data.calculate_image_cost(
                                image_provider,
                                selected_image_model,
                                selected_image_size,
                                selected_image_quality,
                                num_images=1
                            )
                            phase2_cost_jpy = phase2_cost_usd * exchange_rate
                            
                            # 合計コスト
                            total_cost_usd = phase1_cost['total_cost_usd'] + phase2_cost_usd
                            total_cost_jpy = phase1_cost['total_cost_jpy'] + phase2_cost_jpy
                            
                            st.info(f"""
                            💰 **コスト内訳**  
                            **フェーズ1（プロンプト生成）:**  
                            • 言語モデル: {selected_model_info['name']}  
                            • 入力: {phase1_input_tokens:,} tokens → ¥{phase1_cost['input_cost_jpy']:.2f}  
                            • 出力: {phase1_output_tokens:,} tokens → ¥{phase1_cost['output_cost_jpy']:.2f}  
                            • 小計: ¥{phase1_cost['total_cost_jpy']:.2f} (${phase1_cost['total_cost_usd']:.4f})
                            
                            **フェーズ2（画像生成）:**  
                            • 画像モデル: {selected_image_model_info['name']}  
                            • サイズ: {selected_image_size}  
                            • 品質: {selected_image_quality}  
                            • 小計: ¥{phase2_cost_jpy:.2f} (${phase2_cost_usd:.4f})
                            
                            **合計: ¥{total_cost_jpy:.2f}** (${total_cost_usd:.4f})
                            """)
                            
                            # 履歴に保存
                            output_record = {
                                'timestamp': get_jst_now().strftime('%Y-%m-%d %H:%M:%S JST'),
                                'zip_file': st.session_state.uploaded_file_name,
                                'output_type': selected_template['name'],
                                'output_format': 'image',
                                'provider': ai_provider,
                                'model': selected_model,
                                'model_name': selected_model_info['name'],
                                'image_provider': image_provider,
                                'image_model': selected_image_model,
                                'image_model_name': selected_image_model_info['name'],
                                'image_size': selected_image_size,
                                'image_quality': selected_image_quality,
                                'prompt': image_prompt,
                                'revised_prompt': image_result.get('revised_prompt', image_prompt),
                                'image_data': image_result['image_data'],
                                'custom_instruction': final_instruction if edit_mode or selected_template['name'] == 'カスタム指示' else None,
                                'stats': {
                                    'phase1_time': phase1_time,
                                    'phase2_time': phase2_time,
                                    'total_time': total_time,
                                    'prompt_chars': len(image_prompt),
                                    'prompt_tokens': phase1_output_tokens
                                },
                                'cost': {
                                    'phase1_input_tokens': phase1_input_tokens,
                                    'phase1_output_tokens': phase1_output_tokens,
                                    'phase1_cost_usd': phase1_cost['total_cost_usd'],
                                    'phase1_cost_jpy': phase1_cost['total_cost_jpy'],
                                    'phase2_cost_usd': phase2_cost_usd,
                                    'phase2_cost_jpy': phase2_cost_jpy,
                                    'total_usd': total_cost_usd,
                                    'total_jpy': total_cost_jpy,
                                    'exchange_rate': exchange_rate
                                }
                            }
                            
                            st.session_state.output_history.append(output_record)
                            
                            # ダウンロードボタン
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📥 画像をダウンロード",
                                    data=image_result['image_data'],
                                    file_name=f"image_{get_jst_now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png"
                                )
                            with col2:
                                st.download_button(
                                    label="📝 プロンプトをダウンロード",
                                    data=image_prompt,
                                    file_name=f"prompt_{get_jst_now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                            
                        except Exception as e:
                            st.error(f"画像生成エラー: {str(e)}")
                            st.info("画像モデルのAPIキーが正しく設定されているか確認してください。")
                
                else:
                    # ========================================
                    # テキストレポート生成（従来の処理）
                    # ========================================
                    with st.spinner('レポートを生成中...'):
                        try:
                            import time
                            start_time = time.time()
                            
                            # プロバイダーに応じたAPIキーを選択
                            if ai_provider == "OpenAI":
                                api_key = openai_api_key
                            elif ai_provider == "Anthropic (Claude)":
                                api_key = anthropic_api_key
                            elif ai_provider == "Google (Gemini)":
                                api_key = google_api_key
                            else:
                                api_key = None
                            
                            # レポート生成
                            result = ai_generator.generate_report(
                                st.session_state.current_md_content,
                                final_instruction,
                                api_key,
                                selected_model,
                                provider=ai_provider
                            )
                            
                            # generate_reportは辞書を返す
                            report_content = result['content']
                            report_stats = result['stats']
                            processing_time = report_stats['processing_time']
                            
                            # 結果表示（Markdownレンダリング）
                            st.markdown("---")
                            st.subheader("📄 生成されたレポート")
                            
                            # CSSクラスを適用したコンテナ内でMarkdownをレンダリング
                            st.markdown('<div class="compact-content">', unsafe_allow_html=True)
                            st.markdown(report_content, unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 履歴に保存
                            output_record = {
                                'timestamp': get_jst_now().strftime('%Y-%m-%d %H:%M:%S JST'),
                                'zip_file': st.session_state.uploaded_file_name,
                                'output_type': selected_template['name'],
                                'output_format': 'text',
                                'provider': ai_provider,
                                'model': selected_model,
                                'model_name': selected_model_info['name'],
                                'custom_instruction': final_instruction if edit_mode or selected_template['name'] == 'カスタム指示' else None,
                                'content': report_content,
                                'stats': {
                                    'processing_time': processing_time,
                                    'output_bytes': report_stats['output_bytes'],
                                    'output_chars': report_stats['output_chars'],
                                    'compressed': report_stats['compressed']
                                },
                                'cost': {
                                    'input_tokens': input_tokens_est,
                                    'output_tokens': estimate_tokens_multilingual(report_content),
                                    'total_usd': cost_estimate['total_cost_usd'],
                                    'total_jpy': cost_estimate['total_cost_jpy'],
                                    'exchange_rate': exchange_rate
                                }
                            }
                            
                            st.session_state.output_history.append(output_record)
                            
                            # 統計情報
                            st.success(f"""
                            ✅ **生成完了！**  
                            • 処理時間: {processing_time:.1f}秒  
                            • 出力: {report_stats['output_bytes']:,} bytes ({report_stats['output_bytes']//1024:.1f} KB)  
                            • 文字数: {report_stats['output_chars']:,}字
                            """)
                            
                            # 使用量ベースのコスト推定
                            actual_output_tokens = estimate_tokens_multilingual(report_content)
                            actual_cost = calculate_cost(
                                input_tokens_est,
                                actual_output_tokens,
                                selected_model_info,
                                exchange_rate
                            )
                            
                            st.info(f"""
                            💰 **使用量ベースのコスト推定**  
                            • 入力: {input_tokens_est:,} tokens → ¥{actual_cost['input_cost_jpy']:.2f}  
                            • 出力: {actual_output_tokens:,} tokens → ¥{actual_cost['output_cost_jpy']:.2f}  
                            • **合計: ¥{actual_cost['total_cost_jpy']:.2f}** (${actual_cost['total_cost_usd']:.4f})
                            """)
                            
                            # ダウンロードボタン
                            st.download_button(
                                label="📥 レポートをダウンロード",
                                data=report_content,
                                file_name=f"report_{get_jst_now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                            
                        except Exception as e:
                            st.error(f"エラーが発生しました: {str(e)}")
                            st.info("APIキーが正しく設定されているか、モデルが選択されているか確認してください。")


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
                    output_format = record.get('output_format', 'text')
                    
                    if output_format == 'image':
                        # 画像の場合
                        # 画像ファイル
                        image_filename = f"{idx+1:02d}_{record['timestamp'].replace(':', '-')}_{record['output_type'].replace('/', '_')}.png"
                        zip_file.writestr(image_filename, record['image_data'])
                        
                        # プロンプトファイル
                        prompt_filename = f"{idx+1:02d}_{record['timestamp'].replace(':', '-')}_prompt.txt"
                        zip_file.writestr(prompt_filename, record['prompt'])
                        
                        # メタデータ
                        stats = record.get('stats', {})
                        cost = record.get('cost', {})
                        
                        metadata_md = f"""# 画像生成メタデータ

## 基本情報
- **生成日時**: {record['timestamp']}
- **元ファイル**: {record['zip_file']}
- **出力タイプ**: {record['output_type']}
- **画像サイズ**: {record.get('image_size', 'N/A')}
- **画像品質**: {record.get('image_quality', 'N/A')}

## モデル情報
### フェーズ1: プロンプト生成
- **AIプロバイダー**: {record['provider']}
- **モデル名**: {record.get('model_name', record['model'])}
- **モデルID**: `{record['model']}`

### フェーズ2: 画像生成
- **AIプロバイダー**: {record.get('image_provider', 'N/A')}
- **モデル名**: {record.get('image_model_name', 'N/A')}
- **モデルID**: `{record.get('image_model', 'N/A')}`

## 処理統計
- **フェーズ1 処理時間**: {stats.get('phase1_time', 0):.1f}秒
- **フェーズ2 処理時間**: {stats.get('phase2_time', 0):.1f}秒
- **合計処理時間**: {stats.get('total_time', 0):.1f}秒
- **プロンプト文字数**: {stats.get('prompt_chars', 0):,}字

## コスト情報
### フェーズ1（プロンプト生成）
- **入力トークン**: {cost.get('phase1_input_tokens', 0):,} tokens
- **出力トークン**: {cost.get('phase1_output_tokens', 0):,} tokens
- **コスト**: ¥{cost.get('phase1_cost_jpy', 0):.2f} (${cost.get('phase1_cost_usd', 0):.4f})

### フェーズ2（画像生成）
- **コスト**: ¥{cost.get('phase2_cost_jpy', 0):.2f} (${cost.get('phase2_cost_usd', 0):.4f})

### 合計
- **合計コスト**: ¥{cost.get('total_jpy', 0):.2f} (${cost.get('total_usd', 0):.4f})
- **為替レート**: {cost.get('exchange_rate', 150):.1f}円/USD

---
*生成: VFデータ変換・結果出力ツール*
"""
                        metadata_filename = f"{idx+1:02d}_{record['timestamp'].replace(':', '-')}_info.md"
                        zip_file.writestr(metadata_filename, metadata_md)
                        
                    else:
                        # テキストの場合（従来の処理）
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
                file_name=f"all_reports_{get_jst_now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        st.markdown("---")
        
        for idx, record in enumerate(st.session_state.output_history):
            output_format = record.get('output_format', 'text')
            
            # コスト情報を取得
            cost_info = record.get('cost', {})
            cost_display = f"¥{cost_info.get('total_jpy', 0):.2f}" if cost_info else "N/A"
            
            # タイトルの作成（形式に応じて）
            model_name = record.get('model_name', record['model'])
            zip_file = record.get('zip_file', 'N/A')
            
            if output_format == 'image':
                # 画像の場合のタイトル
                icon = "🖼️"
                size_info = record.get('image_size', 'N/A')
                image_model_name = record.get('image_model_name', 'N/A')
                title = f"{icon} {record['timestamp']} | {zip_file} | {record['output_type']} | 言語:{model_name} 画像:{image_model_name} | {cost_display} | {size_info}"
            else:
                # テキストの場合のタイトル
                icon = "📄"
                content_length = len(record.get('content', ''))
                title = f"{icon} {record['timestamp']} | {zip_file} | {record['output_type']} | {model_name} | {cost_display} | {content_length:,}字"
            
            with st.expander(title, expanded=(idx == 0)):
                # メタデータ表示（形式に応じて）
                if output_format == 'image':
                    # 画像の場合のメタデータ
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**生成日時**: {record['timestamp']}")
                        st.write(f"**元ファイル**: {record['zip_file']}")
                        st.write(f"**出力タイプ**: {record['output_type']}")
                    with col2:
                        st.write(f"**言語モデル**: {model_name}")
                        st.write(f"**画像モデル**: {record.get('image_model_name', 'N/A')}")
                        st.write(f"**画像サイズ**: {record.get('image_size', 'N/A')}")
                    with col3:
                        st.write(f"**画像品質**: {record.get('image_quality', 'N/A')}")
                        if cost_info:
                            st.write(f"**コスト推定**: ¥{cost_info.get('total_jpy', 0):.2f}")
                            st.write(f"  (${cost_info.get('total_usd', 0):.4f})")
                    
                    # コスト詳細（expanderで）
                    with st.expander("💰 詳細なコスト内訳"):
                        st.markdown("**フェーズ1（プロンプト生成）:**")
                        st.write(f"• 入力トークン: {cost_info.get('phase1_input_tokens', 0):,}")
                        st.write(f"• 出力トークン: {cost_info.get('phase1_output_tokens', 0):,}")
                        st.write(f"• コスト: ¥{cost_info.get('phase1_cost_jpy', 0):.2f} (${cost_info.get('phase1_cost_usd', 0):.4f})")
                        
                        st.markdown("**フェーズ2（画像生成）:**")
                        st.write(f"• コスト: ¥{cost_info.get('phase2_cost_jpy', 0):.2f} (${cost_info.get('phase2_cost_usd', 0):.4f})")
                        
                        st.markdown("**合計:**")
                        st.write(f"• **¥{cost_info.get('total_jpy', 0):.2f}** (${cost_info.get('total_usd', 0):.4f})")
                    
                    # 処理統計（expanderで）
                    stats = record.get('stats', {})
                    with st.expander("📊 処理統計"):
                        st.write(f"**フェーズ1 処理時間**: {stats.get('phase1_time', 0):.1f}秒")
                        st.write(f"**フェーズ2 処理時間**: {stats.get('phase2_time', 0):.1f}秒")
                        st.write(f"**合計処理時間**: {stats.get('total_time', 0):.1f}秒")
                        st.write(f"**プロンプト文字数**: {stats.get('prompt_chars', 0):,}字")
                        st.write(f"**プロンプトトークン数**: {stats.get('prompt_tokens', 0):,} tokens")
                
                else:
                    # テキストの場合のメタデータ（従来の処理）
                    content_length = len(record.get('content', ''))
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
                
                # 出力形式に応じた内容表示
                output_format = record.get('output_format', 'text')
                
                if output_format == 'image':
                    # 画像の場合
                    st.markdown("---")
                    
                    # プロンプト表示
                    st.markdown("**🔤 生成されたプロンプト:**")
                    st.code(record['prompt'], language="text")
                    
                    # 画像表示
                    st.markdown("**🖼️ 生成された画像:**")
                    st.image(record['image_data'], use_column_width=True)
                    
                    # ダウンロードボタン
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 画像をダウンロード",
                            data=record['image_data'],
                            file_name=f"image_{idx}_{record['timestamp'].replace(':', '-').replace(' ', '_')}.png",
                            mime="image/png",
                            key=f"download_img_{idx}"
                        )
                    with col2:
                        st.download_button(
                            label="📝 プロンプトをダウンロード",
                            data=record['prompt'],
                            file_name=f"prompt_{idx}_{record['timestamp'].replace(':', '-').replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"download_prompt_{idx}"
                        )
                else:
                    # テキストレポートの場合（従来の処理）
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
    
    # 画像生成モデル情報
    st.markdown("---")
    st.markdown("### 🎨 画像生成モデル一覧")
    
    # プロバイダー別に画像モデルを表示
    for provider_name, provider_key in [("OpenAI", "OpenAI"), ("Google (Gemini)", "Google")]:
        if provider_key not in image_model_data.IMAGE_MODELS:
            continue
            
        with st.expander(f"**{provider_name}** 画像生成モデル", expanded=False):
            provider_models = image_model_data.IMAGE_MODELS[provider_key]
            
            if not provider_models:
                st.info(f"{provider_name}の画像モデルは現在登録されていません")
                continue
            
            image_model_list = []
            for model_id, info in provider_models.items():
                # 基本情報
                name = info['name']
                description = info['description']
                
                # サイズと品質
                sizes = ', '.join(info.get('supported_sizes', info.get('available_sizes', ['N/A'])))
                qualities = ', '.join(info.get('supported_quality', info.get('available_qualities', ['N/A'])))
                
                # コスト（デフォルトサイズで計算）
                default_size = info.get('default_size', info.get('supported_sizes', info.get('available_sizes', ['1024x1024']))[0])
                default_quality = info.get('default_quality', info.get('supported_quality', info.get('available_qualities', ['standard']))[0])
                
                # プロバイダーキーを小文字に変換（関数が期待する形式）
                provider_key_lower = "openai" if provider_key == "OpenAI" else "google"
                
                cost_usd = image_model_data.calculate_image_cost(
                    provider_key_lower,
                    model_id,
                    default_size,
                    default_quality,
                    num_images=1
                )
                cost_jpy = cost_usd * 150  # 為替150円で計算
                
                image_model_list.append({
                    'モデル': name,
                    'モデルID': f"`{model_id}`",
                    'サイズ': sizes,
                    '品質': qualities,
                    'コスト (1枚)': f"${cost_usd:.4f} (¥{cost_jpy:.2f})",
                    '説明': description
                })
            
            # DataFrameで表示
            df_image = pd.DataFrame(image_model_list)
            st.dataframe(df_image, use_container_width=True, hide_index=True)
            
            # 追加の注意事項
            if provider_key == "Google":
                st.info("""
                **Google画像モデルの特徴:**
                - Gemini 3 Pro: 日本語テキスト対応（最高品質）
                - Gemini 2.5 Flash: 日本語プロンプト対応（テキストは崩れる場合あり）
                - Imagen 4: 英語テキストのみ推奨
                """)
            elif provider_key == "OpenAI":
                st.info("""
                **OpenAI画像モデルの特徴:**
                - GPT-Image-1-Mini: 最安値・高速
                - GPT-Image-1: 高品質
                - 日本語テキスト対応
                - 認証が必要な場合があります
                """)
    
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
