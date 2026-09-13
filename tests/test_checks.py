import json

from agent_trend_radar import checks


class FakeGitHubClient:
    def __init__(
        self,
        existing_paths=None,
        directory_names=None,
        file_paths=None,
        file_contents=None,
        immediate_children=None,
    ):
        self._existing_paths = existing_paths or set()
        self._directory_names = directory_names or set()
        self._file_paths = file_paths or set()
        self._file_contents = file_contents or {}
        self._immediate_children = immediate_children or {}

    def path_exists(self, repo, path):
        return path in self._existing_paths

    def get_directory_names(self, repo):
        return self._directory_names

    def get_file_paths(self, repo):
        return self._file_paths

    def get_file_content(self, repo, path):
        return self._file_contents.get(path)

    def list_immediate_children(self, repo, dir_path):
        return self._immediate_children.get(dir_path, set())


def test_has_agent_instructions_true_for_claude_md():
    client = FakeGitHubClient(existing_paths={"CLAUDE.md"})
    assert checks.has_agent_instructions(client, "owner/repo") is True


def test_has_agent_instructions_true_for_agents_md():
    client = FakeGitHubClient(existing_paths={"AGENTS.md"})
    assert checks.has_agent_instructions(client, "owner/repo") is True


def test_has_agent_instructions_false_when_none_exist():
    client = FakeGitHubClient()
    assert checks.has_agent_instructions(client, "owner/repo") is False


def test_has_tests_true_when_tests_dir_exists():
    client = FakeGitHubClient(directory_names={"tests"})
    assert checks.has_tests(client, "owner/repo") is True


def test_has_tests_true_when_test_dir_exists():
    client = FakeGitHubClient(directory_names={"test"})
    assert checks.has_tests(client, "owner/repo") is True


def test_has_tests_true_when_nested_in_monorepo():
    client = FakeGitHubClient(directory_names={"libs", "core", "tests"})
    assert checks.has_tests(client, "owner/repo") is True


def test_has_tests_false_when_missing():
    client = FakeGitHubClient(directory_names={"src", "docs"})
    assert checks.has_tests(client, "owner/repo") is False


def test_has_eval_true_for_evals_or_eval():
    assert checks.has_eval(FakeGitHubClient(existing_paths={"evals"}), "o/r") is True
    assert checks.has_eval(FakeGitHubClient(existing_paths={"eval"}), "o/r") is True


def test_has_eval_false_when_missing():
    assert checks.has_eval(FakeGitHubClient(), "o/r") is False


def test_has_ci_true_when_workflows_dir_exists():
    client = FakeGitHubClient(existing_paths={".github/workflows"})
    assert checks.has_ci(client, "owner/repo") is True


def test_has_ci_false_when_missing():
    client = FakeGitHubClient()
    assert checks.has_ci(client, "owner/repo") is False


def test_has_security_policy_true_when_security_md_exists():
    client = FakeGitHubClient(existing_paths={"SECURITY.md"})
    assert checks.has_security_policy(client, "owner/repo") is True


def test_has_security_policy_false_when_missing():
    client = FakeGitHubClient()
    assert checks.has_security_policy(client, "owner/repo") is False


def test_has_skills_dir_true_when_exists():
    client = FakeGitHubClient(existing_paths={".claude/skills"})
    assert checks.has_skills_dir(client, "owner/repo") is True


def test_has_skills_dir_false_when_missing():
    assert checks.has_skills_dir(FakeGitHubClient(), "owner/repo") is False


def test_skills_count_counts_immediate_children_of_skills_dir():
    client = FakeGitHubClient(
        immediate_children={".claude/skills": {"foo", "bar"}},
    )
    assert checks.skills_count(client, "owner/repo") == 2


def test_skills_count_counts_symlinked_skills():
    """Skillがサブディレクトリ(SKILL.md)ではなくシンボリックリンクとして
    置かれている場合(例: cline/cline)でも数える。"""
    client = FakeGitHubClient(
        immediate_children={".claude/skills": {"cline-sdk", "opentui"}},
    )
    assert checks.skills_count(client, "owner/repo") == 2


def test_skills_count_zero_when_no_skills_dir():
    assert checks.skills_count(FakeGitHubClient(), "owner/repo") == 0


def test_has_custom_commands_true_when_exists():
    client = FakeGitHubClient(existing_paths={".claude/commands"})
    assert checks.has_custom_commands(client, "owner/repo") is True


def test_has_custom_commands_false_when_missing():
    assert checks.has_custom_commands(FakeGitHubClient(), "owner/repo") is False


def test_custom_commands_count_counts_md_files_including_nested():
    client = FakeGitHubClient(
        file_paths={
            ".claude/commands/deploy.md",
            ".claude/commands/frontend/component.md",
            ".claude/commands/README.txt",
        }
    )
    assert checks.custom_commands_count(client, "owner/repo") == 2


def test_has_hooks_config_true_when_hooks_key_present():
    client = FakeGitHubClient(
        file_contents={".claude/settings.json": json.dumps({"hooks": {"PreToolUse": []}})}
    )
    assert checks.has_hooks_config(client, "owner/repo") is True


def test_has_hooks_config_false_when_hooks_key_empty():
    client = FakeGitHubClient(file_contents={".claude/settings.json": json.dumps({"hooks": {}})})
    assert checks.has_hooks_config(client, "owner/repo") is False


def test_has_hooks_config_false_when_settings_missing():
    assert checks.has_hooks_config(FakeGitHubClient(), "owner/repo") is False


def test_has_hooks_config_false_when_settings_invalid_json():
    client = FakeGitHubClient(file_contents={".claude/settings.json": "{not valid json"})
    assert checks.has_hooks_config(client, "owner/repo") is False


def test_mcp_servers_count_counts_entries():
    client = FakeGitHubClient(
        file_contents={".mcp.json": json.dumps({"mcpServers": {"a": {}, "b": {}}})}
    )
    assert checks.mcp_servers_count(client, "owner/repo") == 2


def test_mcp_servers_count_zero_when_missing():
    assert checks.mcp_servers_count(FakeGitHubClient(), "owner/repo") == 0
