"""
テストスクリプト - 基本機能の動作確認
"""

import sys
import os

def test_imports():
    """必要なモジュールがインポートできるかテスト"""
    print("📦 モジュールのインポートをテスト中...")
    
    try:
        import streamlit
        print("✅ streamlit")
    except ImportError as e:
        print(f"❌ streamlit: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError as e:
        print(f"❌ pandas: {e}")
        return False
    
    try:
        import openai
        print("✅ openai")
    except ImportError as e:
        print(f"❌ openai: {e}")
        return False
    
    try:
        import processor
        print("✅ processor (カスタムモジュール)")
    except ImportError as e:
        print(f"❌ processor: {e}")
        return False
    
    try:
        import ai_generator
        print("✅ ai_generator (カスタムモジュール)")
    except ImportError as e:
        print(f"❌ ai_generator: {e}")
        return False
    
    return True


def test_file_structure():
    """必要なファイルが存在するかテスト"""
    print("\n📁 ファイル構成をテスト中...")
    
    required_files = [
        'app.py',
        'processor.py',
        'ai_generator.py',
        'requirements.txt',
        'README.md',
        '.streamlit/config.toml'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} が見つかりません")
            all_exist = False
    
    return all_exist


def test_processor_module():
    """processorモジュールの基本機能をテスト"""
    print("\n🔧 processorモジュールをテスト中...")
    
    try:
        from processor import DataAnalyzer, OptimizedMarkdownGenerator
        print("✅ DataAnalyzer クラスをインポート")
        print("✅ OptimizedMarkdownGenerator クラスをインポート")
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def test_ai_generator_module():
    """ai_generatorモジュールの基本機能をテスト"""
    print("\n🤖 ai_generatorモジュールをテスト中...")
    
    try:
        from ai_generator import generate_report, estimate_cost
        print("✅ generate_report 関数をインポート")
        print("✅ estimate_cost 関数をインポート")
        
        # コスト計算のテスト
        cost = estimate_cost('gpt-4o', 1000, 500)
        print(f"✅ コスト計算テスト: 1000入力トークン + 500出力トークン = ${cost:.4f}")
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def main():
    """すべてのテストを実行"""
    print("=" * 60)
    print("議論データ分析アプリ - セットアップテスト")
    print("=" * 60)
    
    results = []
    
    # テスト実行
    results.append(("モジュールインポート", test_imports()))
    results.append(("ファイル構成", test_file_structure()))
    results.append(("processorモジュール", test_processor_module()))
    results.append(("ai_generatorモジュール", test_ai_generator_module()))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ 成功" if passed else "❌ 失敗"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 すべてのテストが成功しました！")
        print("\n次のステップ:")
        print("1. OpenAI APIキーを取得")
        print("2. .streamlit/secrets.toml を作成（secrets.toml.example を参考に）")
        print("3. streamlit run app.py でアプリを起動")
        print("4. GitHubにプッシュしてStreamlit Cloudにデプロイ")
    else:
        print("⚠️  一部のテストが失敗しました。上記のエラーを確認してください。")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
