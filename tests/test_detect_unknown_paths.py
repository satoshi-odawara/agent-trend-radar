import detect_unknown_paths

from agent_trend_radar import unknown_paths


class FakeGitHubClient:
    def __init__(self, repo_file_paths):
        self._repo_file_paths = repo_file_paths

    def get_file_paths(self, repo):
        return self._repo_file_paths.get(repo, set())


def test_build_report_includes_header_row_for_all_candidates():
    client = FakeGitHubClient({})
    report = detect_unknown_paths.build_report(client, [])

    for candidate in unknown_paths.CANDIDATE_PATHS:
        assert candidate["path"] in report


def test_build_report_includes_one_row_per_target_with_counts():
    client = FakeGitHubClient(
        {
            "owner/repo-a": {"GEMINI.md"},
            "owner/repo-b": set(),
        }
    )
    targets = [
        {"repo": "owner/repo-a", "segment": "tool", "monetization_model": "individual_community"},
        {"repo": "owner/repo-b", "segment": "adopter", "monetization_model": "individual_community"},
    ]

    report = detect_unknown_paths.build_report(client, targets)

    assert "owner/repo-a" in report
    assert "owner/repo-b" in report
    lines = report.splitlines()
    row_a = next(line for line in lines if line.startswith("| owner/repo-a"))
    row_b = next(line for line in lines if line.startswith("| owner/repo-b"))
    gemini_col = unknown_paths.CANDIDATE_PATHS.index({"path": "GEMINI.md", "kind": "file"})
    assert row_a.split(" | ")[gemini_col + 1] == "1"
    assert row_b.split(" | ")[gemini_col + 1] == "0"
