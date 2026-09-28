import compute_adoption_dates


class FakeGitHubClient:
    def __init__(self, first_commit_dates=None):
        self._first_commit_dates = first_commit_dates or {}
        self.calls = []

    def get_file_paths(self, repo):
        return set()

    def get_first_commit_date(self, repo, path):
        self.calls.append((repo, path))
        return self._first_commit_dates.get((repo, path))


def test_run_updates_cache_for_all_targets():
    client = FakeGitHubClient(
        first_commit_dates={("owner/a", ".mcp.json"): "2026-01-01T00:00:00Z"}
    )
    targets = [
        {"repo": "owner/a", "segment": "tool", "monetization_model": "individual_community"},
        {"repo": "owner/b", "segment": "tool", "monetization_model": "individual_community"},
    ]

    cache = compute_adoption_dates.run(client, targets, {})

    assert cache["owner/a"][".mcp.json"] == "2026-01-01T00:00:00Z"
    assert "owner/b" in cache


def test_run_does_not_call_api_for_already_confirmed_paths():
    client = FakeGitHubClient()
    targets = [{"repo": "owner/a", "segment": "tool", "monetization_model": "individual_community"}]
    cache = {
        "owner/a": {
            ".claude/skills": "2026-01-01T00:00:00Z",
            ".agents/skills": "2026-01-01T00:00:00Z",
            ".claude/commands": "2026-01-01T00:00:00Z",
            ".claude/settings.json": "2026-01-01T00:00:00Z",
            ".mcp.json": "2026-01-01T00:00:00Z",
        }
    }

    compute_adoption_dates.run(client, targets, cache)

    assert client.calls == []
