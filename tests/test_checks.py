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
        symlink_targets=None,
    ):
        self._existing_paths = existing_paths or set()
        self._directory_names = directory_names or set()
        self._file_paths = file_paths or set()
        self._file_contents = file_contents or {}
        self._immediate_children = immediate_children or {}
        self._symlink_targets = symlink_targets or {}

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

    def get_symlink_target(self, repo, path):
        return self._symlink_targets.get(path)


def test_has_agent_instructions_true_for_claude_md():
    client = FakeGitHubClient(file_paths={"CLAUDE.md"})
    assert checks.has_agent_instructions(client, "owner/repo") is True


def test_has_agent_instructions_true_for_agents_md():
    client = FakeGitHubClient(file_paths={"AGENTS.md"})
    assert checks.has_agent_instructions(client, "owner/repo") is True


def test_has_agent_instructions_false_when_none_exist():
    client = FakeGitHubClient()
    assert checks.has_agent_instructions(client, "owner/repo") is False


def test_has_agent_instructions_true_for_nested_monorepo_doc():
    """ルート直下に指示文書が無いモノレポでの検知漏れ対応(#29)。
    例: continuedev/continueの`extensions/cli/AGENTS.md`。"""
    client = FakeGitHubClient(file_paths={"extensions/cli/AGENTS.md"})
    assert checks.has_agent_instructions(client, "owner/repo") is True


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
    assert checks.has_eval(FakeGitHubClient(file_paths={"evals/test.py"}), "o/r") is True
    assert checks.has_eval(FakeGitHubClient(file_paths={"eval/test.py"}), "o/r") is True


def test_has_eval_false_when_missing():
    assert checks.has_eval(FakeGitHubClient(), "o/r") is False


def test_has_eval_false_for_nested_only():
    """ルート直下限定の判定を維持している(#39でTreeキャッシュ経由に
    変更したが、ネストした場所のevalsは対象外のまま)。"""
    client = FakeGitHubClient(file_paths={"some/nested/evals/test.py"})
    assert checks.has_eval(client, "o/r") is False


def test_has_ci_true_when_workflow_file_exists():
    client = FakeGitHubClient(file_paths={".github/workflows/ci.yml"})
    assert checks.has_ci(client, "owner/repo") is True


def test_has_ci_false_when_missing():
    client = FakeGitHubClient()
    assert checks.has_ci(client, "owner/repo") is False


def test_ci_workflow_count_counts_files_under_workflows_dir():
    client = FakeGitHubClient(
        file_paths={".github/workflows/ci.yml", ".github/workflows/release.yml"}
    )
    assert checks.ci_workflow_count(client, "owner/repo") == 2


def test_ci_workflow_count_zero_when_missing():
    assert checks.ci_workflow_count(FakeGitHubClient(), "owner/repo") == 0


def test_ci_workflow_count_ignores_unrelated_prefix_match():
    client = FakeGitHubClient(file_paths={".github/workflows-old/ci.yml"})
    assert checks.ci_workflow_count(client, "owner/repo") == 0


def test_has_security_policy_true_when_security_md_exists():
    client = FakeGitHubClient(file_paths={"SECURITY.md"})
    assert checks.has_security_policy(client, "owner/repo") is True


def test_has_security_policy_false_when_missing():
    client = FakeGitHubClient()
    assert checks.has_security_policy(client, "owner/repo") is False


def test_has_skills_dir_true_when_exists():
    client = FakeGitHubClient(immediate_children={".claude/skills": {"foo"}})
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


def test_skills_count_resolves_symlinked_skills_dir():
    """`.claude/skills`自体が共有ディレクトリへのシンボリックリンクに
    なっている場合(例: getsentry/sentry, supabase/supabase, vercel/next.js
    が`../.agents/skills`を指す)、リンク先を解決してから数える。"""
    client = FakeGitHubClient(
        symlink_targets={".claude/skills": "../.agents/skills"},
        immediate_children={".agents/skills": {"foo", "bar", "baz"}},
    )
    assert checks.skills_count(client, "owner/repo") == 3


def test_has_skills_dir_true_when_only_agents_skills_exists():
    """`.claude/skills`が存在せず`.agents/skills`のみのケース
    (例: OpenHands/OpenHands, sveltejs/svelte, astral-sh/ruff,
    remix-run/remix)。"""
    client = FakeGitHubClient(immediate_children={".agents/skills": {"foo"}})
    assert checks.has_skills_dir(client, "owner/repo") is True


def test_skills_count_counts_agents_skills_when_claude_skills_missing():
    client = FakeGitHubClient(
        immediate_children={".agents/skills": {"custom-codereview-guide.md", "pr-design-doc", "release.md"}},
    )
    assert checks.skills_count(client, "owner/repo") == 3


def test_skills_count_unions_both_paths_without_double_counting_overlap():
    """`.claude/skills`が`.agents/skills`の一部だけを個別シンボリック
    リンクしている(不完全な)ケース(例: apache/airflow, cline/cline)。
    和集合を取り、重複エントリは二重カウントしない。"""
    client = FakeGitHubClient(
        immediate_children={
            ".claude/skills": {"foo", "bar"},
            ".agents/skills": {"foo", "bar", "baz"},
        },
    )
    assert checks.skills_count(client, "owner/repo") == 3


def test_has_custom_commands_true_when_exists():
    client = FakeGitHubClient(file_paths={".claude/commands/deploy.md"})
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


def test_custom_commands_count_resolves_symlinked_commands_dir():
    client = FakeGitHubClient(
        symlink_targets={".claude/commands": "../.agents/commands"},
        file_paths={".agents/commands/deploy.md", ".agents/commands/README.txt"},
    )
    assert checks.custom_commands_count(client, "owner/repo") == 1


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
