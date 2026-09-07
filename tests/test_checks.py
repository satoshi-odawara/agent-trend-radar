from agent_trend_radar import checks


class FakeGitHubClient:
    def __init__(self, existing_paths=None, directory_names=None):
        self._existing_paths = existing_paths or set()
        self._directory_names = directory_names or set()

    def path_exists(self, repo, path):
        return path in self._existing_paths

    def get_directory_names(self, repo):
        return self._directory_names


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
