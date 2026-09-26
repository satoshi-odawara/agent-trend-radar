from agent_trend_radar.github_client import GitHubClient

CANDIDATE_PATHS = [
    {"path": ".cursor/rules", "kind": "dir"},
    {"path": ".github/copilot-instructions.md", "kind": "file"},
    {"path": ".github/instructions", "kind": "dir"},
    {"path": ".clinerules", "kind": "dir"},
    {"path": ".windsurfrules", "kind": "file"},
    {"path": ".windsurf/rules", "kind": "dir"},
    {"path": "GEMINI.md", "kind": "file"},
    {"path": ".openhands", "kind": "dir"},
    {"path": ".claude/agents", "kind": "dir"},
]


def count_candidate(client: GitHubClient, repo: str, candidate: dict) -> int:
    """候補パスの件数を返す。

    ファイル型は存在すれば1・無ければ0。ディレクトリ型は配下の全ファイル数を
    再帰的にカウントする(各ツールのサブディレクトリ規約を個別に調べ込む
    価値は薄い探索的な検出のため、`skills_count`のような「直下の子要素数」
    ではなくシンプルな再帰カウントを採用、#32)。既存のTreeキャッシュ
    (`GitHubClient.get_file_paths`)を再利用するため、候補パス数を増やしても
    リポジトリごとの追加API呼び出しは発生しない。
    """
    path = candidate["path"]
    file_paths = client.get_file_paths(repo)
    if candidate["kind"] == "file":
        return 1 if path in file_paths else 0
    prefix = f"{path}/"
    return sum(1 for p in file_paths if p.startswith(prefix))


def detect_unknown_paths(client: GitHubClient, repo: str) -> dict[str, int]:
    """候補パスごとの件数を`{パス: 件数}`で返す。"""
    return {candidate["path"]: count_candidate(client, repo, candidate) for candidate in CANDIDATE_PATHS}
