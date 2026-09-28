from agent_trend_radar import adoption_dates


class FakeGitHubClient:
    def __init__(self, file_paths=None, first_commit_dates=None):
        self._file_paths = file_paths or set()
        self._first_commit_dates = first_commit_dates or {}
        self.calls = []

    def get_file_paths(self, repo):
        return self._file_paths

    def get_first_commit_date(self, repo, path):
        self.calls.append((repo, path))
        return self._first_commit_dates.get(path)


def test_target_paths_includes_fixed_paths_and_representative_doc():
    client = FakeGitHubClient(file_paths={"CLAUDE.md"})
    paths = adoption_dates.target_paths(client, "owner/repo")

    assert "CLAUDE.md" in paths
    assert ".claude/skills" in paths
    assert ".agents/skills" in paths
    assert ".claude/commands" in paths
    assert ".claude/settings.json" in paths
    assert ".mcp.json" in paths
    assert len(paths) == 6


def test_target_paths_excludes_doc_path_when_none_exists():
    client = FakeGitHubClient()
    paths = adoption_dates.target_paths(client, "owner/repo")

    assert len(paths) == 5
    assert "CLAUDE.md" not in paths
    assert "AGENTS.md" not in paths


def test_update_cache_for_repo_calls_api_for_new_paths():
    client = FakeGitHubClient(first_commit_dates={".mcp.json": "2026-01-01T00:00:00Z"})
    cache = {}

    adoption_dates.update_cache_for_repo(client, "owner/repo", cache)

    assert cache["owner/repo"][".mcp.json"] == "2026-01-01T00:00:00Z"
    assert cache["owner/repo"][".claude/skills"] is None


def test_update_cache_for_repo_skips_already_confirmed_dates():
    client = FakeGitHubClient()
    cache = {"owner/repo": {".mcp.json": "2026-01-01T00:00:00Z"}}

    adoption_dates.update_cache_for_repo(client, "owner/repo", cache)

    assert ("owner/repo", ".mcp.json") not in client.calls
    assert cache["owner/repo"][".mcp.json"] == "2026-01-01T00:00:00Z"


def test_update_cache_for_repo_rechecks_null_entries():
    """未採用(null)は将来の採用を検知するため毎回再確認する(#40、#33で
    確定した差分キャッシュ方針)。"""
    client = FakeGitHubClient()
    cache = {"owner/repo": {".mcp.json": None}}

    adoption_dates.update_cache_for_repo(client, "owner/repo", cache)

    assert ("owner/repo", ".mcp.json") in client.calls


def test_build_report_lists_dates_and_marks_unadopted():
    targets = [
        {"repo": "owner/repo", "segment": "tool", "monetization_model": "individual_community"}
    ]
    cache = {
        "owner/repo": {
            ".mcp.json": "2026-01-01T00:00:00Z",
            ".claude/commands": None,
        }
    }

    report = adoption_dates.build_report(targets, cache)

    assert "| owner/repo | .mcp.json | 2026-01-01T00:00:00Z |" in report
    assert "| owner/repo | .claude/commands | (未採用) |" in report


def test_cache_roundtrip(tmp_path):
    path = str(tmp_path / "cache.json")
    cache = {
        "owner/repo": {
            ".mcp.json": "2026-01-01T00:00:00Z",
            ".claude/commands": None,
        }
    }

    adoption_dates.save_cache(cache, path=path)
    loaded = adoption_dates.load_cache(path=path)

    assert loaded == cache


def test_load_cache_returns_empty_dict_when_missing(tmp_path):
    path = str(tmp_path / "does_not_exist.json")
    assert adoption_dates.load_cache(path=path) == {}
