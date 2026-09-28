import json
import os

from agent_trend_radar import agent_doc_analysis
from agent_trend_radar.github_client import GitHubClient

DEFAULT_CACHE_PATH = "data/adoption_dates.json"

# #33で確定した対象パス。代表指示文書のパス(リポジトリごとに異なる、
# target_pathsで動的に解決)と合わせて計測する。
FIXED_PATHS = {
    "skills_claude": ".claude/skills",
    "skills_agents": ".agents/skills",
    "commands": ".claude/commands",
    "settings": ".claude/settings.json",
    "mcp_config": ".mcp.json",
}


def target_paths(client: GitHubClient, repo: str) -> list[str]:
    """このリポジトリで初出コミット日を計測する対象パスの一覧を返す。

    5つの固定パスに加え、代表指示文書のパス(#30と同じ選定ロジックで
    解決、複数存在する場合はCLAUDE.mdを優先)を含める。指示文書が
    見つからないリポジトリでは、その分を含めない(#40)。
    """
    paths = list(FIXED_PATHS.values())
    doc_paths = agent_doc_analysis.representative_doc_paths(client, repo)
    if doc_paths:
        paths.append(doc_paths[0])
    return paths


def update_cache_for_repo(client: GitHubClient, repo: str, cache: dict) -> dict:
    """指定リポジトリの対象パスについてキャッシュを更新し、同じcacheを返す。

    初出コミット日が既に確定している(値がnon-null)組は不変の事実なので
    再確認しない。未採用(値がnull)または未確認(キー自体が無い)の組は、
    将来の採用を検知できるよう毎回1コールで軽く確認し直す(#33で確定した
    差分キャッシュ方針: 日付は永続キャッシュ、不在は毎回再チェック)。
    """
    repo_cache = cache.setdefault(repo, {})
    for path in target_paths(client, repo):
        if repo_cache.get(path) is not None:
            continue
        repo_cache[path] = client.get_first_commit_date(repo, path)
    return cache


def load_cache(path: str = DEFAULT_CACHE_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache: dict, path: str = DEFAULT_CACHE_PATH) -> None:
    dirname = os.path.dirname(path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def build_report(targets: list[dict], cache: dict) -> str:
    """人間が読めるMarkdown一覧を組み立てる。"""
    lines = [
        "# 規約ファイル初出コミット日(Issue #40)",
        "",
        "各リポジトリで規約ファイルが最初にコミットされた日付。",
        "「(未採用)」は対象パスがまだ一度もコミットされていないことを示す",
        "(直近の再計算時点の状態。未採用は次回実行時に再確認される)。",
        "",
        "| repo | パス | 初出コミット日 |",
        "| --- | --- | --- |",
    ]
    for target in targets:
        repo = target["repo"]
        repo_cache = cache.get(repo, {})
        for path in sorted(repo_cache):
            date = repo_cache[path]
            lines.append(f"| {repo} | {path} | {date if date else '(未採用)'} |")
    return "\n".join(lines) + "\n"
