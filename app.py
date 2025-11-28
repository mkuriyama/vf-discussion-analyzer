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
    page_title="議論データ分析アプリ",
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
st.markdown('<div class="main-header">📊 議論データ分析アプリ</div>', unsafe_allow_html=True)
st.markdown("専門家AIによる会議録を分析し、目的に合わせたレポートを生成します")

# サイドバー設定
st.sidebar.header("⚙️ 設定")

# OpenAI API設定
st.sidebar.subheader("OpenAI API設定")
api_key = st.sidebar.text_input(
    "APIキー",
    type="password",
    help="OpenAI APIキーを入力してください",
    value=os.getenv("OPENAI_API_KEY", "")
)

model_options = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-3.5-turbo"
]
selected_model = st.sidebar.selectbox(
    "モデル選択",
    model_options,
    index=0,
    help="使用するOpenAIモデルを選択"
)

st.sidebar.markdown("---")

# ファイルアップロード
st.sidebar.subheader("📁 ファイルアップロード")
uploaded_file = st.sidebar.file_uploader(
    "ZIPファイルを選択",
    type=['zip'],
    help="議論データが含まれるZIPファイルをアップロード"
)

# メインエリア
tab1, tab2, tab3 = st.tabs(["📄 レポート生成", "ℹ️ 使い方", "🔧 詳細設定"])

with tab1:
    if uploaded_file is None:
        st.info("👈 サイドバーからZIPファイルをアップロードしてください")
    else:
        st.success(f"✅ ファイルアップロード完了: {uploaded_file.name}")
        
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
        
        # 出力オプション
        st.subheader("📤 出力オプション")
        col1, col2 = st.columns(2)
        
        with col1:
            enable_download = st.checkbox("ダウンロード機能を有効化", value=True)
        
        with col2:
            enable_email = st.checkbox("メール送信機能を有効化", value=False)
        
        # メール設定
        email_address = None
        if enable_email:
            email_address = st.text_input(
                "送信先メールアドレス",
                placeholder="example@example.com"
            )
        
        st.markdown("---")
        
        # 生成ボタン
        if st.button("🚀 レポート生成", type="primary", use_container_width=True):
            if not api_key:
                st.error("❌ OpenAI APIキーを設定してください")
            elif "カスタム" in output_type and not custom_instruction:
                st.error("❌ カスタム指示を入力してください")
            else:
                # プレースホルダー（実装は次のステップ）
                with st.spinner("🔄 データを処理中..."):
                    import time
                    import processor
                    import ai_generator
                    
                    try:
                        # 一時ファイルに保存
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Step 1: ZIP → Markdown変換
                        st.info("📄 Step 1/3: ZIPファイルをMarkdownに変換中...")
                        md_path = processor.convert_zip_to_markdown(tmp_path)
                        
                        with open(md_path, 'r', encoding='utf-8') as f:
                            md_content = f.read()
                        
                        st.success("✅ Markdown変換完了")
                        
                        # Step 2: AI処理
                        st.info("🤖 Step 2/3: AIでレポート生成中...")
                        
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
                        
                        # AI生成
                        result = ai_generator.generate_report(
                            md_content=md_content,
                            instruction=instruction,
                            api_key=api_key,
                            model=selected_model
                        )
                        
                        st.success("✅ レポート生成完了")
                        
                        # Step 3: 結果表示
                        st.info("📊 Step 3/3: 結果を表示中...")
                        
                        # 結果表示
                        st.markdown("---")
                        st.subheader("📄 生成されたレポート")
                        st.markdown('<div class="output-box">', unsafe_allow_html=True)
                        st.markdown(result)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # ダウンロード
                        if enable_download:
                            st.download_button(
                                label="📥 レポートをダウンロード",
                                data=result,
                                file_name=f"discussion_report_{Path(uploaded_file.name).stem}.md",
                                mime="text/markdown"
                            )
                        
                        # メール送信
                        if enable_email and email_address:
                            if st.button("📧 メールで送信"):
                                with st.spinner("送信中..."):
                                    success = ai_generator.send_email(
                                        recipient=email_address,
                                        subject="議論データ分析レポート",
                                        body=result
                                    )
                                    if success:
                                        st.success(f"✅ {email_address} に送信しました")
                                    else:
                                        st.error("❌ メール送信に失敗しました")
                        
                        # クリーンアップ
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"❌ エラーが発生しました: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

with tab2:
    st.markdown("""
    ## 📖 使い方
    
    ### 1. APIキーの設定
    サイドバーからOpenAI APIキーを入力してください。環境変数 `OPENAI_API_KEY` が設定されている場合は自動で読み込まれます。
    
    ### 2. ファイルのアップロード
    サイドバーから議論データが含まれるZIPファイルをアップロードしてください。
    
    ### 3. レポートタイプの選択
    - **400字版**: 経営層向けの簡潔なサマリー
    - **2000字版**: バランスの取れた構造化レポート（推奨）
    - **5000字版**: 詳細な分析レポート
    - **カスタム**: 自由に指示を記述
    
    ### 4. 生成と出力
    「レポート生成」ボタンをクリックすると、AIが分析を開始します。
    結果はブラウザ上で確認でき、必要に応じてダウンロードやメール送信が可能です。
    
    ## 💡 Tips
    - カスタム指示では、具体的な要件を記述するほど精度が上がります
    - 長いレポートほど処理時間がかかります（目安: 400字版 10秒、5000字版 60秒）
    - APIキーは安全に管理してください（Streamlit Secretsの使用を推奨）
    """)

with tab3:
    st.markdown("""
    ## 🔧 詳細設定
    
    ### Streamlit Secrets設定
    
    本番環境では、Streamlit Cloud の Secrets 機能を使用してAPIキーを安全に管理できます。
    
    ```toml
    # .streamlit/secrets.toml
    OPENAI_API_KEY = "your-api-key-here"
    ```
    
    ### 環境変数
    
    以下の環境変数が利用可能です:
    - `OPENAI_API_KEY`: OpenAI APIキー
    - `SMTP_SERVER`: メール送信用SMTPサーバー（オプション）
    - `SMTP_PORT`: SMTPポート（オプション）
    - `SMTP_USER`: SMTP認証ユーザー（オプション）
    - `SMTP_PASSWORD`: SMTP認証パスワード（オプション）
    
    ### モデル選択について
    
    - **gpt-4o**: 最新・最高性能（推奨）
    - **gpt-4o-mini**: コストパフォーマンス重視
    - **gpt-4-turbo**: 高性能・大容量
    - **gpt-3.5-turbo**: 高速・低コスト
    
    ### ファイルサイズ制限
    
    - アップロード可能なZIPファイルサイズ: 最大200MB
    - 処理可能なMarkdownサイズ: 最大10MB
    """)

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>Powered by OpenAI API | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
