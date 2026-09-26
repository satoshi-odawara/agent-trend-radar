from agent_trend_radar import agent_doc_analysis as doc_analysis


class FakeGitHubClient:
    def __init__(self, file_contents=None, file_paths=None, file_shas=None):
        self._file_contents = file_contents or {}
        # file_pathsを省略した場合、file_contentsのキー(=内容が存在するパス)を
        # そのままリポジトリ内の全ファイルパスとして扱う(既存テストとの互換用)。
        self._file_paths = file_paths if file_paths is not None else set(self._file_contents.keys())
        self._file_shas = file_shas or {}

    def path_exists(self, repo, path):
        raise NotImplementedError

    def get_file_content(self, repo, path):
        return self._file_contents.get(path)

    def get_file_paths(self, repo):
        return self._file_paths

    def get_file_sha(self, repo, path):
        return self._file_shas.get(path)


def test_fetch_agent_doc_content_concatenates_both_files():
    client = FakeGitHubClient(
        file_contents={"CLAUDE.md": "claude part", "AGENTS.md": "agents part"}
    )
    content = doc_analysis.fetch_agent_doc_content(client, "owner/repo")
    assert "claude part" in content
    assert "agents part" in content


def test_fetch_agent_doc_content_empty_when_neither_exists():
    client = FakeGitHubClient()
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == ""


def test_fetch_agent_doc_content_uses_whichever_exists():
    client = FakeGitHubClient(file_contents={"CLAUDE.md": "only claude"})
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == "only claude"


def test_fetch_agent_doc_content_dedupes_identical_content():
    # CLAUDE.mdがAGENTS.mdへのシンボリックリンクの場合、両パスが同一内容を
    # 返す(apache/airflow, colinhacks/zodで実際に確認したパターン)。
    same_content = "shared instructions"
    client = FakeGitHubClient(
        file_contents={"CLAUDE.md": same_content, "AGENTS.md": same_content}
    )
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == same_content


def test_fetch_agent_doc_content_falls_back_to_shallowest_nested_dir():
    """ルート直下に指示文書が無いモノレポでの検知漏れ対応(#29)。
    例: continuedev/continueの`extensions/cli/AGENTS.md`。"""
    client = FakeGitHubClient(
        file_contents={"extensions/cli/AGENTS.md": "nested instructions"},
        file_paths={"extensions/cli/AGENTS.md", "extensions/cli/README.md"},
    )
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == "nested instructions"


def test_fetch_agent_doc_content_prefers_root_over_nested():
    client = FakeGitHubClient(
        file_contents={"AGENTS.md": "root doc", "sub/AGENTS.md": "nested doc"},
        file_paths={"AGENTS.md", "sub/AGENTS.md"},
    )
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == "root doc"


def test_fetch_agent_doc_content_picks_shallowest_when_multiple_nested():
    client = FakeGitHubClient(
        file_contents={"a/b/AGENTS.md": "deep doc", "a/AGENTS.md": "shallow doc"},
        file_paths={"a/b/AGENTS.md", "a/AGENTS.md"},
    )
    assert doc_analysis.fetch_agent_doc_content(client, "owner/repo") == "shallow doc"


def test_find_agent_doc_paths_filters_by_basename_and_sorts():
    client = FakeGitHubClient(
        file_paths={"z/AGENTS.md", "a/CLAUDE.md", "a/README.md", "AGENTS.md"},
    )
    assert doc_analysis.find_agent_doc_paths(client, "owner/repo") == [
        "AGENTS.md",
        "a/CLAUDE.md",
        "z/AGENTS.md",
    ]


def test_agent_doc_count_counts_distinct_directories_not_files():
    """CLAUDE.mdとAGENTS.mdが同じディレクトリ(ルート)に揃っているだけの
    リポジトリ(例: colinhacks/zod)をモノレポと誤検知しないための仕様。"""
    client = FakeGitHubClient(file_paths={"CLAUDE.md", "AGENTS.md"})
    assert doc_analysis.agent_doc_count(client, "owner/repo") == 1


def test_agent_doc_count_counts_multiple_directories():
    client = FakeGitHubClient(
        file_paths={"AGENTS.md", "packages/a/AGENTS.md", "packages/b/CLAUDE.md"},
    )
    assert doc_analysis.agent_doc_count(client, "owner/repo") == 3


def test_agent_doc_count_zero_when_none_found():
    assert doc_analysis.agent_doc_count(FakeGitHubClient(), "owner/repo") == 0


def test_agent_doc_char_count():
    assert doc_analysis.agent_doc_char_count("hello") == 5
    assert doc_analysis.agent_doc_char_count("") == 0


def test_agent_doc_heading_count():
    content = "# Title\n\nSome text\n## Subheading\nMore text\n### Sub-sub"
    assert doc_analysis.agent_doc_heading_count(content) == 3


def test_agent_doc_heading_count_zero_when_no_headings():
    assert doc_analysis.agent_doc_heading_count("just plain text") == 0


def test_agent_doc_has_code_block():
    assert doc_analysis.agent_doc_has_code_block("some ```code``` here") is True
    assert doc_analysis.agent_doc_has_code_block("no code block here") is False


def test_agent_doc_mentions_test():
    assert doc_analysis.agent_doc_mentions_test("Run `pytest` before committing") is True
    assert doc_analysis.agent_doc_mentions_test("Run `vitest run`") is True
    assert doc_analysis.agent_doc_mentions_test("nothing relevant here") is False


def test_agent_doc_mentions_lint():
    assert doc_analysis.agent_doc_mentions_lint("Run ruff check") is True
    assert doc_analysis.agent_doc_mentions_lint("nothing relevant here") is False


def test_agent_doc_mentions_security():
    assert doc_analysis.agent_doc_mentions_security("Never commit secrets") is True
    assert doc_analysis.agent_doc_mentions_security("nothing relevant here") is False


def test_agent_doc_mentions_commit_convention():
    assert doc_analysis.agent_doc_mentions_commit_convention("Follow Conventional Commit") is True
    assert doc_analysis.agent_doc_mentions_commit_convention("nothing relevant here") is False


def test_agent_doc_mentions_tool_usage():
    assert doc_analysis.agent_doc_mentions_tool_usage("Use the MCP server for X") is True
    assert doc_analysis.agent_doc_mentions_tool_usage("Invoke a Skill when Y") is True
    assert doc_analysis.agent_doc_mentions_tool_usage("nothing relevant here") is False


def test_keyword_matching_is_case_insensitive():
    assert doc_analysis.agent_doc_mentions_test("PYTEST") is True
    assert doc_analysis.agent_doc_mentions_tool_usage("SUBAGENT") is True


def test_representative_doc_cache_key_empty_when_no_doc():
    client = FakeGitHubClient()
    assert doc_analysis.representative_doc_cache_key(client, "owner/repo") == ""


def test_representative_doc_cache_key_single_file():
    client = FakeGitHubClient(
        file_paths={"CLAUDE.md"}, file_shas={"CLAUDE.md": "sha-claude"}
    )
    assert doc_analysis.representative_doc_cache_key(client, "owner/repo") == "CLAUDE.md:sha-claude"


def test_representative_doc_cache_key_combines_both_files_in_fixed_order():
    client = FakeGitHubClient(
        file_paths={"CLAUDE.md", "AGENTS.md"},
        file_shas={"CLAUDE.md": "sha-claude", "AGENTS.md": "sha-agents"},
    )
    assert (
        doc_analysis.representative_doc_cache_key(client, "owner/repo")
        == "CLAUDE.md:sha-claude|AGENTS.md:sha-agents"
    )


def test_representative_doc_cache_key_uses_representative_directory():
    """ルート直下に無いモノレポでは代表ディレクトリ配下のパス+SHAを使う(#29と同じ選定ロジック)。"""
    client = FakeGitHubClient(
        file_paths={"extensions/cli/AGENTS.md", "extensions/cli/README.md"},
        file_shas={"extensions/cli/AGENTS.md": "sha-nested"},
    )
    assert (
        doc_analysis.representative_doc_cache_key(client, "owner/repo")
        == "extensions/cli/AGENTS.md:sha-nested"
    )


def test_representative_doc_cache_key_changes_when_sha_changes():
    client_v1 = FakeGitHubClient(file_paths={"CLAUDE.md"}, file_shas={"CLAUDE.md": "sha-v1"})
    client_v2 = FakeGitHubClient(file_paths={"CLAUDE.md"}, file_shas={"CLAUDE.md": "sha-v2"})
    key_v1 = doc_analysis.representative_doc_cache_key(client_v1, "owner/repo")
    key_v2 = doc_analysis.representative_doc_cache_key(client_v2, "owner/repo")
    assert key_v1 != key_v2
