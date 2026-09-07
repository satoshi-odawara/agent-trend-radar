from agent_trend_radar.github_client import GitHubClient

AGENT_INSTRUCTION_PATHS = ["CLAUDE.md", "AGENTS.md", ".cursorrules"]
TEST_DIR_NAMES = {"tests", "test"}
EVAL_PATHS = ["evals", "eval"]
CI_PATHS = [".github/workflows"]
SECURITY_POLICY_PATHS = ["SECURITY.md"]

MANIFEST_PATHS = ["pyproject.toml", "requirements.txt", "package.json"]

# SPEC.md「has_observability_depの判定対象パッケージ」と同期させること。
OBSERVABILITY_PACKAGES = [
    "langsmith",
    "langfuse",
    "traceloop-sdk",
    "traceloop",
    "arize-phoenix",
    "helicone",
    "promptlayer",
]


def _any_path_exists(client: GitHubClient, repo: str, paths: list[str]) -> bool:
    return any(client.path_exists(repo, path) for path in paths)


def has_agent_instructions(client: GitHubClient, repo: str) -> bool:
    return _any_path_exists(client, repo, AGENT_INSTRUCTION_PATHS)


def has_tests(client: GitHubClient, repo: str) -> bool:
    directory_names = client.get_directory_names(repo)
    return not TEST_DIR_NAMES.isdisjoint(directory_names)


def has_eval(client: GitHubClient, repo: str) -> bool:
    return _any_path_exists(client, repo, EVAL_PATHS)


def has_ci(client: GitHubClient, repo: str) -> bool:
    return _any_path_exists(client, repo, CI_PATHS)


def has_security_policy(client: GitHubClient, repo: str) -> bool:
    return _any_path_exists(client, repo, SECURITY_POLICY_PATHS)


def has_observability_dep(client: GitHubClient, repo: str) -> bool:
    for manifest_path in MANIFEST_PATHS:
        content = client.get_file_content(repo, manifest_path)
        if content is None:
            continue
        content_lower = content.lower()
        if any(package in content_lower for package in OBSERVABILITY_PACKAGES):
            return True
    return False
