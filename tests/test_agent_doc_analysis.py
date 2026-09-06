from agent_trend_radar import agent_doc_analysis as doc_analysis


class FakeGitHubClient:
    def __init__(self, file_contents=None):
        self._file_contents = file_contents or {}

    def path_exists(self, repo, path):
        raise NotImplementedError

    def get_file_content(self, repo, path):
        return self._file_contents.get(path)


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
