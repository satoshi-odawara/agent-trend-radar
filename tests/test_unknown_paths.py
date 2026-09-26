from agent_trend_radar import unknown_paths


class FakeGitHubClient:
    def __init__(self, file_paths=None):
        self._file_paths = file_paths or set()

    def get_file_paths(self, repo):
        return self._file_paths


def test_count_candidate_file_type_present():
    client = FakeGitHubClient(file_paths={"GEMINI.md"})
    candidate = {"path": "GEMINI.md", "kind": "file"}
    assert unknown_paths.count_candidate(client, "owner/repo", candidate) == 1


def test_count_candidate_file_type_absent():
    client = FakeGitHubClient(file_paths=set())
    candidate = {"path": "GEMINI.md", "kind": "file"}
    assert unknown_paths.count_candidate(client, "owner/repo", candidate) == 0


def test_count_candidate_dir_type_counts_files_recursively():
    client = FakeGitHubClient(
        file_paths={
            ".claude/agents/a.md",
            ".claude/agents/sub/b.md",
            ".claude/agents-other/c.md",  # プレフィックス一致に見えるが別ディレクトリ
            "unrelated.md",
        }
    )
    candidate = {"path": ".claude/agents", "kind": "dir"}
    assert unknown_paths.count_candidate(client, "owner/repo", candidate) == 2


def test_count_candidate_dir_type_zero_when_absent():
    client = FakeGitHubClient(file_paths={"unrelated.md"})
    candidate = {"path": ".openhands", "kind": "dir"}
    assert unknown_paths.count_candidate(client, "owner/repo", candidate) == 0


def test_detect_unknown_paths_returns_all_candidates():
    client = FakeGitHubClient(file_paths={"GEMINI.md", ".clinerules/a.md"})
    result = unknown_paths.detect_unknown_paths(client, "owner/repo")

    assert result["GEMINI.md"] == 1
    assert result[".clinerules"] == 1
    assert result[".openhands"] == 0
    assert set(result.keys()) == {c["path"] for c in unknown_paths.CANDIDATE_PATHS}


def test_candidate_paths_do_not_overlap_known_check_paths():
    """既存のチェック対象パス(SPEC.md記載分)が候補に混ざっていないこと(完了条件)。"""
    known_paths = {
        "CLAUDE.md",
        "AGENTS.md",
        ".cursorrules",
        "tests",
        "test",
        "evals",
        "eval",
        ".github/workflows",
        "SECURITY.md",
        ".claude/skills",
        ".agents/skills",
        ".claude/commands",
        ".claude/settings.json",
        ".mcp.json",
    }
    candidate_paths = {c["path"] for c in unknown_paths.CANDIDATE_PATHS}
    assert known_paths.isdisjoint(candidate_paths)


def test_candidate_paths_have_no_duplicates():
    paths = [c["path"] for c in unknown_paths.CANDIDATE_PATHS]
    assert len(paths) == len(set(paths))
