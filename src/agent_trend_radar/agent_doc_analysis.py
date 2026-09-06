from agent_trend_radar.github_client import GitHubClient

AGENT_DOC_PATHS = ["CLAUDE.md", "AGENTS.md"]

TEST_KEYWORDS = ["test", "pytest", "jest", "vitest"]
LINT_KEYWORDS = ["lint", "ruff", "eslint", "prettier"]
SECURITY_KEYWORDS = ["security", "secret", "credential", "vulnerability"]
COMMIT_CONVENTION_KEYWORDS = ["commit message", "conventional commit"]
TOOL_USAGE_KEYWORDS = [
    "mcp",
    "skill",
    "subagent",
    "slash command",
    "hook",
    "tool use",
    "function calling",
]


def fetch_agent_doc_content(client: GitHubClient, repo: str) -> str:
    """CLAUDE.md/AGENTS.mdの内容を取得し連結する。どちらもなければ空文字列。

    CLAUDE.mdをAGENTS.mdへのシンボリックリンクとして運用しているリポジトリ
    (apache/airflow, colinhacks/zodで実際に確認)では両パスが同一内容を
    返すため、重複カウントを避けるために同一内容は1回のみ含める。
    """
    parts = []
    seen = set()
    for path in AGENT_DOC_PATHS:
        content = client.get_file_content(repo, path)
        if content and content not in seen:
            parts.append(content)
            seen.add(content)
    return "\n".join(parts)


def agent_doc_char_count(content: str) -> int:
    return len(content)


def agent_doc_heading_count(content: str) -> int:
    return sum(1 for line in content.splitlines() if line.lstrip().startswith("#"))


def agent_doc_has_code_block(content: str) -> bool:
    return "```" in content


def agent_doc_mentions_test(content: str) -> bool:
    return _any_keyword_in(content, TEST_KEYWORDS)


def agent_doc_mentions_lint(content: str) -> bool:
    return _any_keyword_in(content, LINT_KEYWORDS)


def agent_doc_mentions_security(content: str) -> bool:
    return _any_keyword_in(content, SECURITY_KEYWORDS)


def agent_doc_mentions_commit_convention(content: str) -> bool:
    return _any_keyword_in(content, COMMIT_CONVENTION_KEYWORDS)


def agent_doc_mentions_tool_usage(content: str) -> bool:
    return _any_keyword_in(content, TOOL_USAGE_KEYWORDS)


def _any_keyword_in(content: str, keywords: list[str]) -> bool:
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in keywords)
