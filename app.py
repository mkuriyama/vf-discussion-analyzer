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

# OpenAI API設定
st.sidebar.subheader("🔑 APIキー設定")

# すべてのAPIキーを一度に表示
openai_api_key = st.sidebar.text_input(
    "OpenAI APIキー",
    type="password",
    help="OpenAI APIキーを入力してください",
    value=os.getenv("OPENAI_API_KEY", "")
)

anthropic_api_key = st.sidebar.text_input(
    "Anthropic APIキー",
    type="password",
    help="Anthropic APIキーを入力してください",
    value=os.getenv("ANTHROPIC_API_KEY", "")
)

google_api_key = st.sidebar.text_input(
    "Google APIキー",
    type="password",
    help="Google API キーを入力してください",
    value=os.getenv("GOOGLE_API_KEY", "")
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
        st.write(f"**プロバイダー**: {ai_provider}")
        st.write(f"**モデル名**: {selected_model_info['name']}")
        st.write(f"**説明**: {selected_model_info['description']}")
        st.write(f"**モデルID**: `{selected_model}`")
        st.write(f"**リリース**: {selected_model_info.get('released', 'N/A')}")
        
        # コスト情報の表示
        st.markdown("---")
        st.markdown("**💰 コスト情報（USD per 1M tokens）:**")
        cost_in = selected_model_info.get('cost_input', 0)
        cost_out = selected_model_info.get('cost_output', 0)
        st.write(f"• 入力: ${cost_in:.2f}")
        st.write(f"• 出力: ${cost_out:.2f}")
        
        # Gemini 3 Proの特別価格表示
        if selected_model == "gemini-3-pro-preview":
            cost_in_long = selected_model_info.get('cost_input_long', 0)
            cost_out_long = selected_model_info.get('cost_output_long', 0)
            st.write(f"• 入力 (>200K): ${cost_in_long:.2f}")
            st.write(f"• 出力 (>200K): ${cost_out_long:.2f}")
        
        # トークン制限情報
        st.markdown("---")
        st.markdown("**📏 トークン制限:**")
        input_tokens = selected_model_info['input_tokens']
        output_tokens = selected_model_info['output_tokens']
        
        st.write(f"• 入力: {input_tokens:,} tokens")
        if 'input_tokens_extended' in selected_model_info:
            st.write(f"  *(拡張: {selected_model_info['input_tokens_extended']:,} tokens)*")
        st.write(f"• 出力: {output_tokens:,} tokens")
        
        st.markdown("---")
        
        # コスト情報
        cost_input = selected_model_info.get('cost_input', 0)
        cost_output = selected_model_info.get('cost_output', 0)
        
        if cost_input > 0 or cost_output > 0:
            st.write("**💰 コスト（per 1M tokens）**:")
            st.write(f"  • 入力: **${cost_input:.2f}**")
            st.write(f"  • 出力: **${cost_output:.2f}**")
            
            # 長文コストがある場合（Gemini 3 Pro等）
            if 'cost_input_long' in selected_model_info:
                st.write(f"  • 入力（>200K）: **${selected_model_info['cost_input_long']:.2f}**")
                st.write(f"  • 出力（>200K）: **${selected_model_info['cost_output_long']:.2f}**")
        
        if 'note' in selected_model_info:
            st.info(selected_model_info['note'])
    
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 Markdown閲覧", "📝 レポート生成", "📚 出力結果一覧", "ℹ️ 使い方", "🔧 詳細設定"])

with tab1:
    st.subheader("📄 変換されたMarkdownファイル")
    
    if st.session_state.current_md_content is None:
        st.info("👈 サイドバーからZIPファイルをアップロードしてください")
    else:
        st.success(f"✅ ファイル: {st.session_state.uploaded_file_name}")
        
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
        
        # カスタム指示入力
        custom_instruction = None
        if "カスタム" in output_type:
            custom_instruction = st.text_area(
                "出力内容の指示を入力してください:",
                height=150,
                placeholder="例: 主要な意見を3つに絞り、それぞれについて賛成・反対の意見を対比させてください。全体で1500字程度でまとめてください。"
            )
        
        st.markdown("---")
        
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
                        
                        # デバッグ: result_dataの型を確認
                        if not isinstance(result_data, dict):
                            st.error(f"⚠️ 予期しない戻り値の型: {type(result_data)}")
                            st.write(f"値: {result_data}")
                            raise ValueError(f"generate_reportが辞書を返しませんでした: {type(result_data)}")
                        
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
                        
                        # 結果表示（整形済みMarkdown・横スクロール防止）
                        st.markdown("---")
                        st.subheader("📄 生成されたレポート")
                        st.markdown(
                            f'<div style="word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap;">{result}</div>',
                            unsafe_allow_html=True
                        )
                        
                        # 履歴に保存
                        output_record = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'zip_file': st.session_state.uploaded_file_name,
                            'output_type': output_type,
                            'custom_instruction': custom_instruction if custom_instruction else "-",
                            'provider': ai_provider,
                            'model': selected_model,
                            'content': result
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
        
        for idx, record in enumerate(st.session_state.output_history):
            # レポートの文字数を計算
            content_length = len(record['content'])
            
            # 改善されたタイトル: 日時 | 出力タイプ | モデル | ファイル | 文字数
            title = f"📄 {record['timestamp']} | {record['output_type']} | {record['model']} | {record['zip_file']} | {content_length:,}字"
            
            with st.expander(title, expanded=(idx == 0)):
                # メタデータ表示
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**生成日時**: {record['timestamp']}")
                    st.write(f"**元ファイル**: {record['zip_file']}")
                    st.write(f"**出力タイプ**: {record['output_type']}")
                    st.write(f"**文字数**: {content_length:,}字")
                with col2:
                    st.write(f"**AIプロバイダー**: {record['provider']}")
                    st.write(f"**モデル**: {record['model']}")
                    
                if record['custom_instruction'] != "-":
                    st.write(f"**カスタム指示**: {record['custom_instruction']}")
                
                st.markdown("---")
                
                # レポート内容表示（整形済み・横スクロール防止）
                st.markdown(
                    f'<div style="word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap;">{record["content"]}</div>',
                    unsafe_allow_html=True
                )
                
                # ダウンロードボタン
                st.download_button(
                    label="📥 このレポートをダウンロード",
                    data=record['content'],
                    file_name=f"report_{idx}_{record['timestamp'].replace(':', '-').replace(' ', '_')}.md",
                    mime="text/markdown",
                    key=f"download_{idx}"
                )

with tab4:
    st.markdown("""
    ## 📖 使い方
    
    ### 1. ファイルのアップロード
    サイドバーから議論データが含まれるZIPファイルをアップロードしてください。
    自動的にMarkdownに変換されます。
    
    ### 2. Markdownの確認
    「📄 Markdown閲覧」タブで変換されたMarkdownファイルを確認できます。
    
    ### 3. AIプロバイダーとモデルの選択
    サイドバーで使用するAIプロバイダー（OpenAI/Anthropic/Google）とモデルを選択します。
    対応するAPIキーを設定してください。
    
    ### 4. レポートの生成
    「📝 レポート生成」タブでレポートタイプを選択し、生成ボタンをクリックします。
    
    - **400字版**: 経営層向けの簡潔なサマリー
    - **2000字版**: バランスの取れた構造化レポート（推奨）
    - **5000字版**: 詳細な分析レポート
    - **カスタム**: 自由に指示を記述
    
    ### 5. 結果の確認と保存
    - 生成されたレポートはその場で確認できます
    - 「📚 出力結果一覧」タブで過去のレポートも閲覧可能
    - 各レポートは個別にダウンロードできます
    
    ## 💡 Tips
    
    ### トークン制限エラーが出た場合
    - より小さいモデルを選択（例: gpt-4o-mini）
    - 短いレポートタイプを選択（400字版）
    - カスタム指示で具体的な焦点を絞る
    
    ### 各AIプロバイダーの特徴
    - **OpenAI**: 最新のGPTモデル、高速で高品質
    - **Anthropic (Claude)**: 長文理解に優れる、詳細な分析
    - **Google (Gemini)**: コスト効率が良い、マルチモーダル対応
    
    ### コスト最適化
    - 小さいモデル（mini/nano）を優先的に使用
    - 必要な情報のみを含むカスタム指示を活用
    - 同じデータで複数試す場合は出力結果一覧を活用
    """)


with tab5:
    st.markdown("""
    ## 🔧 詳細設定
    
    ### Streamlit Secrets設定
    
    本番環境では、Streamlit Cloud の Secrets 機能を使用してAPIキーを安全に管理できます。
    
    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY = "your-openai-key"
    ANTHROPIC_API_KEY = "your-anthropic-key"
    GOOGLE_API_KEY = "your-google-key"
    ```
    """)
    
    st.markdown("---")
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
    
    st.markdown("---")
    st.markdown("""
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
    
    ### 💡 Tips
    
    - **トークン制限**: 各モデルの入力トークン数は上記の表を参照
    - **大きなファイル**: トークン制限の80%を超えると自動圧縮
    - **GPT-5 Pro**: TPM制限があるため、大きなファイルは自動的に20,000トークンに制限されます
    - **コスト最適化**: mini/flash/haiku モデルは経済的
    """)


# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Powered by OpenAI API | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
