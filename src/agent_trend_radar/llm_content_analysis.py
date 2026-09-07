import json
import subprocess
from typing import Callable

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
) -> dict[str, bool]:
    """CLAUDE.md/AGENTS.mdの内容を、#5のキーワード一致では拾えない4テーマ
    (reports/agent_doc_analysis_validation.md 発見3参照)についてLLMで分類する。

    Claude Code CLIのヘッドレス実行(`claude -p`)を使う。Anthropic API課金
    ではなくClaude Codeのサブスクリプション認証で完結させるための選択
    (詳細はIssue.md #15参照)。
    """
    if not content:
        return {field: False for field in CLASSIFICATION_FIELDS}

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
        return {field: bool(structured[field]) for field in CLASSIFICATION_FIELDS}
    except KeyError as exc:
        raise LLMClassificationError(
            f"claude CLIの出力に必要なフィールドがありません: {exc}"
        ) from exc


def _run_claude_cli(content: str) -> str:
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
        ],
        input=content,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise LLMClassificationError(
            f"claude CLIがエラー終了しました(code={result.returncode}): {result.stderr}"
        )
    return result.stdout
