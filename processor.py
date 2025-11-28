"""
議論データCSV → Markdown変換モジュール
元のColabスクリプトをStreamlit用に最適化
"""

import pandas as pd
import zipfile
import os
import re
import tempfile
import shutil
from datetime import datetime
from pathlib import Path


class Config:
    """設定クラス"""
    CSV_PATTERNS = {
        'idea_scores': r'project_idea_scores_\d+\.csv',
        'user_scores': r'project_user_scores_\d+\.csv',
        'review_comments': r'project_review_comments_\d+\.csv'
    }


def find_csv_files(directory, patterns):
    """ディレクトリ内からパターンに一致するCSVファイルを検索"""
    found_files = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            for key, pattern in patterns.items():
                if re.match(pattern, filename):
                    found_files[key] = os.path.join(root, filename)
    return found_files


def safe_read_csv(filepath):
    """CSVファイルを安全に読み込む（複数エンコーディング対応）"""
    encodings = ['utf-8-sig', 'utf-8', 'cp932', 'shift_jis']
    for enc in encodings:
        try:
            return pd.read_csv(filepath, encoding=enc)
        except:
            continue
    raise ValueError(f"CSVファイルの読み込みに失敗: {filepath}")


def escape_markdown(text):
    """Markdown特殊文字をエスケープ"""
    if pd.isna(text):
        return ""
    return str(text).replace('|', '\\|')


def format_value(val):
    """値を表示用にフォーマット"""
    if pd.isna(val):
        return "-"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return f"{val:.2f}"
    return str(val)


class DataAnalyzer:
    """CSVデータを解析するクラス"""

    def __init__(self, df_scores, df_user_scores, df_comments):
        self.df_scores = df_scores
        self.df_user_scores = df_user_scores
        self.df_comments = df_comments
        self._parse_structure()

    def _parse_structure(self):
        """データ構造を解析"""
        self.questions = {}
        self.question_cols = {}
        self.eval_types = {}

        for col in self.df_scores.columns:
            match = re.match(r'(Q\d+-\d+)([_:])(.+)', col)
            if match:
                q_id = match.group(1)
                separator = match.group(2)
                suffix = match.group(3)

                if q_id not in self.question_cols:
                    self.question_cols[q_id] = {
                        'response': None,
                        'summary': None,
                        'category': None,
                        'evals': []
                    }

                if separator == ':' and suffix.startswith('評価'):
                    self.question_cols[q_id]['evals'].append(col)
                    if '共感性' in col:
                        self.eval_types[col] = '共感性'
                    elif '新規性' in col:
                        self.eval_types[col] = '新規性'
                elif suffix.endswith('_要約') or col.endswith('_要約'):
                    self.question_cols[q_id]['summary'] = col
                elif suffix.endswith('_分類') or col.endswith('_分類'):
                    self.question_cols[q_id]['category'] = col
                elif separator == '_':
                    if self.question_cols[q_id]['response'] is None:
                        self.question_cols[q_id]['response'] = col
                    if q_id not in self.questions or self.questions[q_id] is None:
                        self.questions[q_id] = suffix

        self.respondents = self.df_scores['回答者名'].tolist()

        self.user_score_mapping = {}
        if self.df_user_scores is not None:
            for col in self.df_user_scores.columns:
                if col.startswith('回答力_') or col.startswith('目利き力_'):
                    score_type = '回答力' if col.startswith('回答力_') else '目利き力'
                    rest = col[len(score_type)+1:]

                    matched_qid = None
                    for q_id, q_text in self.questions.items():
                        if q_text and rest.startswith(q_text[:30]):
                            matched_qid = q_id
                            break

                    eval_type = '共感性' if '共感性' in col else ('新規性' if '新規性' in col else '不明')

                    if matched_qid:
                        self.user_score_mapping[col] = (matched_qid, score_type, eval_type)

    def get_comments_for_response(self, respondent, q_id):
        """特定の回答へのコメントを取得"""
        if self.df_comments is None:
            return []

        q_text = self.questions.get(q_id, '')
        if not q_text:
            return []

        search_text = str(q_text)[:40]
        mask = (
            (self.df_comments['回答者名'] == respondent) &
            (self.df_comments['設問'].str.contains(search_text, regex=False, na=False))
        )

        comments = self.df_comments[mask]
        return [
            {'commenter': row.get('コメントしたユーザー名', '不明'), 'comment': row.get('コメント', '')}
            for _, row in comments.iterrows()
        ]


class OptimizedMarkdownGenerator:
    """最適化Markdownを生成するクラス"""

    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.lines = []

    def add(self, text=""):
        self.lines.append(text)

    def add_header(self, text, level=1):
        self.add("#" * level + " " + text)
        self.add()

    def generate(self):
        """最適化されたMarkdownを生成"""
        self._generate_header()
        self._generate_respondent_summary()
        self._generate_statistics()
        self._generate_question_list()
        self._generate_user_scores()
        self._generate_discussion_details()
        self._generate_appendix()

        return "\n".join(self.lines)

    def _generate_header(self):
        self.add_header("議論データ分析レポート（最適化版）", 1)
        self.add(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.add("> このファイルは重複情報を省いた最適化版です。設問の全文は「設問一覧」セクションを参照してください。\n")

        self.add_header("ドキュメント情報", 2)
        self.add("| 項目 | 値 |")
        self.add("| --- | --- |")
        self.add(f"| 回答者数 | {len(self.analyzer.respondents)} |")
        self.add(f"| 設問数 | {len(self.analyzer.questions)} |")
        if self.analyzer.df_comments is not None:
            self.add(f"| コメント総数 | {len(self.analyzer.df_comments)} |")
        self.add("| 元CSVファイル | idea_scores, user_scores, review_comments |")
        self.add()

    def _generate_respondent_summary(self):
        self.add_header("回答者一覧", 2)
        self.add("| 順位 | 回答者名 | 総合スコア | 回答ID | 提出日時 |")
        self.add("| --- | --- | --- | --- | --- |")

        df_sorted = self.analyzer.df_scores.sort_values('総合スコア', ascending=False)
        for i, (_, row) in enumerate(df_sorted.iterrows(), 1):
            vals = [
                str(i),
                escape_markdown(row.get('回答者名', '')),
                format_value(row.get('総合スコア')),
                format_value(row.get('回答ID')),
                format_value(row.get('提出日時'))
            ]
            self.add("| " + " | ".join(vals) + " |")
        self.add()

    def _generate_statistics(self):
        self.add_header("統計情報", 2)
        scores = self.analyzer.df_scores['総合スコア']
        self.add("| 指標 | 値 |")
        self.add("| --- | --- |")
        self.add(f"| 平均 | {scores.mean():.2f} |")
        self.add(f"| 最高 | {scores.max():.2f} |")
        self.add(f"| 最低 | {scores.min():.2f} |")
        self.add(f"| 中央値 | {scores.median():.2f} |")
        self.add(f"| 標準偏差 | {scores.std():.2f} |")
        self.add()

    def _generate_question_list(self):
        self.add_header("設問一覧", 2)
        self.add("以下の設問IDは本文書全体で参照されます。\n")

        for q_id in sorted(self.analyzer.questions.keys()):
            q_text = self.analyzer.questions[q_id]
            self.add_header(q_id, 3)
            self.add(f"{q_text}\n")

    def _generate_user_scores(self):
        if self.analyzer.df_user_scores is None:
            return

        self.add_header("ユーザー評価スコア", 2)
        self.add("※設問の全文は「設問一覧」を参照\n")

        for respondent in self.analyzer.respondents:
            row = self.analyzer.df_user_scores[
                self.analyzer.df_user_scores['回答者名'] == respondent
            ]
            if row.empty:
                continue
            row = row.iloc[0]

            self.add_header(respondent, 3)
            self.add(f"回答数: {row.get('回答数', '-')}\n")

            qid_scores = {}
            for col, (qid, score_type, eval_type) in self.analyzer.user_score_mapping.items():
                val = row.get(col)
                if pd.isna(val):
                    continue
                if qid not in qid_scores:
                    qid_scores[qid] = {}
                qid_scores[qid][f"{score_type}_{eval_type}"] = val

            if qid_scores:
                self.add("| 設問 | 回答力(共感性) | 回答力(新規性) | 目利き力(共感性) | 目利き力(新規性) |")
                self.add("| --- | --- | --- | --- | --- |")

                for qid in sorted(qid_scores.keys()):
                    s = qid_scores[qid]
                    vals = [
                        qid,
                        format_value(s.get('回答力_共感性')),
                        format_value(s.get('回答力_新規性')),
                        format_value(s.get('目利き力_共感性')),
                        format_value(s.get('目利き力_新規性'))
                    ]
                    self.add("| " + " | ".join(vals) + " |")
                self.add()

    def _generate_discussion_details(self):
        self.add_header("議論内容詳細", 2)

        for q_id in sorted(self.analyzer.questions.keys()):
            cols = self.analyzer.question_cols.get(q_id, {})

            self.add_header(q_id, 3)
            self.add("※設問全文は「設問一覧」参照\n")

            for _, row in self.analyzer.df_scores.iterrows():
                respondent = row['回答者名']

                self.add_header(respondent, 4)
                self.add(f"*総合スコア: {format_value(row.get('総合スコア'))} / 回答ID: {format_value(row.get('回答ID'))}*\n")

                if cols.get('category') and pd.notna(row.get(cols['category'])):
                    self.add(f"**分類**: {row[cols['category']]}\n")

                if cols.get('summary') and pd.notna(row.get(cols['summary'])):
                    self.add(f"**要約**: {row[cols['summary']]}\n")

                if cols.get('response'):
                    response_val = row.get(cols['response'])
                    if pd.notna(response_val):
                        if isinstance(response_val, (int, float)):
                            self.add(f"**回答（数値）**: {format_value(response_val)}\n")
                        else:
                            self.add(f"**回答**:\n{response_val}\n")

                if cols.get('evals'):
                    eval_parts = []
                    for ec in cols['evals']:
                        if pd.notna(row.get(ec)):
                            short_name = self.analyzer.eval_types.get(ec, '評価')
                            eval_parts.append(f"{short_name}: {format_value(row[ec])}")
                    if eval_parts:
                        self.add(f"**評価**: {' / '.join(eval_parts)}\n")

                comments = self.analyzer.get_comments_for_response(respondent, q_id)
                if comments:
                    self.add("**コメント**:")
                    for c in comments:
                        self.add(f"- **{c['commenter']}**: {escape_markdown(c['comment'])}")
                    self.add()

                self.add("---\n")

    def _generate_appendix(self):
        self.add_header("付録: データ構造リファレンス", 2)
        self.add("元CSVファイルの完全な列名一覧です。\n")

        self.add_header("idea_scores.csv", 3)
        self.add("```")
        for i, col in enumerate(self.analyzer.df_scores.columns):
            self.add(f"{i+1}. {col}")
        self.add("```\n")

        if self.analyzer.df_user_scores is not None:
            self.add_header("user_scores.csv", 3)
            self.add("```")
            for i, col in enumerate(self.analyzer.df_user_scores.columns):
                self.add(f"{i+1}. {col}")
            self.add("```\n")

        if self.analyzer.df_comments is not None:
            self.add_header("review_comments.csv", 3)
            self.add("```")
            for i, col in enumerate(self.analyzer.df_comments.columns):
                self.add(f"{i+1}. {col}")
            self.add("```\n")


def convert_zip_to_markdown(zip_path, output_path=None):
    """
    ZIPファイルをMarkdownに変換するメイン関数
    
    Parameters:
    -----------
    zip_path : str
        入力ZIPファイルのパス
    output_path : str, optional
        出力ファイルのパス（Noneの場合は一時ファイルを使用）
    
    Returns:
    --------
    str : 生成されたMarkdownファイルのパス
    """
    
    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    
    try:
        # ZIP展開
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # CSVファイル検索
        csv_files = find_csv_files(temp_dir, Config.CSV_PATTERNS)
        
        if 'idea_scores' not in csv_files:
            raise ValueError("idea_scoresファイルが見つかりません")
        
        # CSVファイル読み込み
        df_scores = safe_read_csv(csv_files['idea_scores'])
        df_user_scores = safe_read_csv(csv_files['user_scores']) if 'user_scores' in csv_files else None
        df_comments = safe_read_csv(csv_files['review_comments']) if 'review_comments' in csv_files else None
        
        # データ解析
        analyzer = DataAnalyzer(df_scores, df_user_scores, df_comments)
        
        # Markdown生成
        generator = OptimizedMarkdownGenerator(analyzer)
        markdown_content = generator.generate()
        
        # 出力ファイル名決定
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.md', text=True)
            os.close(fd)
        
        # ファイル出力
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return output_path
        
    finally:
        # クリーンアップ
        shutil.rmtree(temp_dir, ignore_errors=True)
