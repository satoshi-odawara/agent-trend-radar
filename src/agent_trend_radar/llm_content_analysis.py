import hashlib
import json
import os
import subprocess
import tempfile
from typing import Callable

DEFAULT_RUN_METADATA_PATH = "data/llm_run_metadata.json"

CLASSIFICATION_FIELDS = [
    "agent_doc_mentions_repo_structure",
    "agent_doc_mentions_boundaries",
    "agent_doc_mentions_pr_review",
    "agent_doc_mentions_release_process",
]

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {field: {"type": "boolean"} for field in CLASSIFICATION_FIELDS},
    "required": CLASSIFICATION_FIELDS,
}

CLASSIFICATION_PROMPT = """\
標準入力で渡されるCLAUDE.md/AGENTS.mdの内容を読み、以下4つのテーマについて
それぞれ本文中で言及されているかを判定してください。曖昧な場合は本文に
具体的な記述があるかどうかで判断し、根拠となる記述が本文になければfalse
としてください。

1. agent_doc_mentions_repo_structure: リポジトリの構成・モノレポにおける
   各ディレクトリの役割の説明(例: "Repository Map", "Monorepo structure",
   "Codebase structure"のような見出しでファイル/ディレクトリ構成を説明)
2. agent_doc_mentions_boundaries: エージェントが自律的にやってはいけない
   こと・変更してはいけない範囲の説明(例: "Cross-Repository Boundaries",
   "No Magic Strings", "Architecture Boundaries", "Security Model"のような、
   エージェントの自律性を制限する記述)
3. agent_doc_mentions_pr_review: PRの作成・レビューに関する基準や、人間に
   よる確認が必要なポイントの説明(例: "PR Description Human Check",
   "Landing PRs: What Reviewers Catch", "when a fix is imminent, open the
   PR, not an issue"のような記述)
4. agent_doc_mentions_release_process: リリース・デプロイの手順の説明
   (例: "Cutting a release", "Release Workflow", "Release Notes"のような
   記述)

指定されたJSON Schemaに従い、4つの真偽値のみを返してください。
"""


class LLMClassificationError(Exception):
    pass


def classify_agent_doc_themes(
    content: str,
    runner: Callable[[str], str] | None = None,
) -> tuple[dict[str, bool], str | None]:
    """CLAUDE.md/AGENTS.mdの内容を、#5のキーワード一致では拾えない4テーマ
    (reports/agent_doc_analysis_validation.md 発見3参照)についてLLMで分類する。

    Claude Code CLIのヘッドレス実行(`claude -p`)を使う。Anthropic API課金
    ではなくClaude Codeのサブスクリプション認証で完結させるための選択
    (詳細はIssue.md #15参照)。

    戻り値は(4項目の分類結果, 使用されたモデル名)のタプル。`_run_claude_cli`
    は`--model`を指定していないためモデル名はCLIバージョンからは分からず、
    JSON出力の`modelUsage`キーから取り出す(#35)。contentが空の場合は
    claude -pを呼ばないためモデル名はNone。
    """
    if not content:
        return {field: False for field in CLASSIFICATION_FIELDS}, None

    run = runner or _run_claude_cli
    stdout = run(content)

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise LLMClassificationError(
            f"claude CLIの出力をJSONとして解釈できませんでした: {exc}"
        ) from exc

    structured = data.get("structured_output")
    if not isinstance(structured, dict):
        raise LLMClassificationError(
            "claude CLIの出力にstructured_outputが含まれていません"
        )

    try:
        themes = {field: bool(structured[field]) for field in CLASSIFICATION_FIELDS}
    except KeyError as exc:
        raise LLMClassificationError(
            f"claude CLIの出力に必要なフィールドがありません: {exc}"
        ) from exc

    return themes, extract_model_name(data)


def extract_model_name(data: dict) -> str | None:
    """claude -pのJSON出力の`modelUsage`キーから使用されたモデル名を
    取り出す(#35)。複数のモデルが使われていた場合は`", "`区切りで連結
    する。キーが無い/空の場合はNone。
    """
    model_usage = data.get("modelUsage")
    if not isinstance(model_usage, dict) or not model_usage:
        return None
    return ", ".join(sorted(model_usage.keys()))


def _run_claude_cli(content: str) -> str:
    """第三者リポジトリのCLAUDE.md/AGENTS.md(信頼できない入力)を渡すため、
    空の一時ディレクトリをcwdにしツールを全て無効化する(`--tools ""`)。
    これにより、radar自身のCLAUDE.md/SPEC.mdが分類コンテキストに混入する
    ことと、プロンプト注入によるツール実行の両方を防ぐ(#30、R2)。
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = subprocess.run(
            [
                "claude",
                "-p",
                CLASSIFICATION_PROMPT,
                "--output-format",
                "json",
                "--json-schema",
                json.dumps(CLASSIFICATION_SCHEMA),
                "--permission-prompts",
                "none",
                "--tools",
                "",
            ],
            input=content,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=tmp_dir,
        )
    if result.returncode != 0:
        raise LLMClassificationError(
            f"claude CLIがエラー終了しました(code={result.returncode}): {result.stderr}"
        )
    return result.stdout


def classification_prompt_hash() -> str:
    """分類プロンプトのSHA256ハッシュ。プロンプト変更を追跡するためのもの
    (#30)。プロンプト自体は本モジュール内の定数のため常に決定的。
    """
    return hashlib.sha256(CLASSIFICATION_PROMPT.encode("utf-8")).hexdigest()


def get_claude_cli_version() -> str:
    """使用しているclaude CLIのバージョン文字列(`claude --version`の出力)。"""
    result = subprocess.run(["claude", "--version"], capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()


def collect_run_metadata(model_name: str | None = None) -> dict:
    """1回の収集実行につき1回だけ記録すればよい、LLM分類のトレーサビリティ
    用メタデータ(CLIバージョン・プロンプトハッシュ・モデル名)。28リポジトリ
    全件で同一の値になるため、`repo_checks`(リポジトリ単位)ではなくこの
    関数の戻り値をhubスナップショットのトップレベルに1回だけ記録する
    (#30)。`model_name`は呼び出し側(`collect.py`)が各リポジトリの分類
    呼び出しで観測した値を渡す(#35、複数観測された場合は連結済みの文字列)。
    1件もLLM分類が発生しなかった場合(全リポジトリで指示文書が無い等)は
    Noneのままでよく、その場合はキー自体を含めない。
    """
    metadata = {
        "claude_cli_version": get_claude_cli_version(),
        "classification_prompt_hash": classification_prompt_hash(),
    }
    if model_name:
        metadata["model_name"] = model_name
    return metadata


def write_run_metadata(metadata: dict, path: str = DEFAULT_RUN_METADATA_PATH) -> None:
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def read_run_metadata(path: str = DEFAULT_RUN_METADATA_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)
