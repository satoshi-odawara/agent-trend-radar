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


def find_agent_doc_paths(client: GitHubClient, repo: str) -> list[str]:
    """リポジトリ内の任意の深さにあるCLAUDE.md/AGENTS.mdのパス一覧を返す(パス文字列の辞書順)。"""
    return sorted(p for p in client.get_file_paths(repo) if p.rsplit("/", 1)[-1] in AGENT_DOC_PATHS)


def agent_doc_count(client: GitHubClient, repo: str) -> int:
    """CLAUDE.md/AGENTS.mdが見つかったディレクトリの数(重複排除、モノレポ傾向の代理指標)。

    ファイル数ではなくディレクトリ数を数える。ルートにCLAUDE.md/AGENTS.md
    両方を置く運用(colinhacks/zod等)が一般的にあり、ファイル数で数えると
    モノレポでなくても2以上になってしまうため(#29で実データにより判明)。
    """
    paths = find_agent_doc_paths(client, repo)
    directories = {p.rsplit("/", 1)[0] if "/" in p else "" for p in paths}
    return len(directories)


def fetch_agent_doc_content(client: GitHubClient, repo: str) -> str:
    """CLAUDE.md/AGENTS.mdの内容を取得し連結する。見つからなければ空文字列。

    リポジトリルートにCLAUDE.md/AGENTS.mdがあればそれを分析対象とする
    (従来通り)。ルートに無ければ、見つかった文書のうち最も浅い
    (同じ深さならパス文字列の辞書順で先頭の)ディレクトリを代表として
    分析する。これはモノレポでルート直下に指示文書が無く
    `has_agent_instructions`が誤ってfalseになっていた問題(#29、例:
    continuedev/continueの`extensions/cli/AGENTS.md`)の修正に伴う対応。

    CLAUDE.mdをAGENTS.mdへのシンボリックリンクとして運用しているリポジトリ
    (apache/airflow, colinhacks/zodで実際に確認)では両パスが同一内容を
    返すため、重複カウントを避けるために同一内容は1回のみ含める。
    """
    paths = find_agent_doc_paths(client, repo)
    if not paths:
        return ""
    directory = _representative_directory(paths)

    parts = []
    seen = set()
    for filename in AGENT_DOC_PATHS:
        path = f"{directory}/{filename}" if directory else filename
        content = client.get_file_content(repo, path)
        if content and content not in seen:
            parts.append(content)
            seen.add(content)
    return "\n".join(parts)


def representative_doc_cache_key(client: GitHubClient, repo: str) -> str:
    """`fetch_agent_doc_content`が読み込む代表文書の入力が前回から変わったかを
    検知するためのキー(パス+blob SHAの組を連結した文字列)。

    LLM分類(#15)は同一入力でも実行のたびに結果が変わりうる(#25の2b)ため、
    このキーが前回と同じなのに分類結果が変わっていれば、それは文書の変更
    ではなくLLMの非決定性によるものと判別できる(#30)。blob SHAは
    `GitHubClient`が既にキャッシュ済みのTreeから取り出すため、新規API
    呼び出しは発生しない。文書が見つからない場合は空文字列を返す。
    """
    paths = find_agent_doc_paths(client, repo)
    if not paths:
        return ""
    directory = _representative_directory(paths)
    file_paths = client.get_file_paths(repo)

    entries = []
    for filename in AGENT_DOC_PATHS:
        path = f"{directory}/{filename}" if directory else filename
        if path in file_paths:
            entries.append(f"{path}:{client.get_file_sha(repo, path)}")
    return "|".join(entries)


def _representative_directory(paths: list[str]) -> str:
    root_paths = [p for p in paths if "/" not in p]
    if root_paths:
        return ""
    shallowest = min(paths, key=lambda p: (p.count("/"), p))
    return shallowest.rsplit("/", 1)[0]


def agent_doc_char_count(content: str) -> int:
    return len(content)


def agent_doc_heading_count(content: str) -> int:
    return sum(1 for line in content.splitlines() if line.lstrip().startswith("#"))


def agent_doc_has_code_block(content: str) -> bool:
    return agent_doc_code_block_count(content) > 0


def agent_doc_code_block_count(content: str) -> int:
    """```で囲まれたコードブロックの数(開き・閉じの組数)。

    `agent_doc_has_code_block`はtool67%・adopter70%(#20)とセグメント間の
    弁別力が無い。実データで検証したところ0件〜44件(browser-use/browser-use)
    まで分散があり、指示文書の具体性を示す量的指標として使える。
    """
    return content.count("```") // 2


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
