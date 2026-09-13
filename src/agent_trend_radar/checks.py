import json

from agent_trend_radar.github_client import GitHubClient

AGENT_INSTRUCTION_PATHS = ["CLAUDE.md", "AGENTS.md", ".cursorrules"]
TEST_DIR_NAMES = {"tests", "test"}
EVAL_PATHS = ["evals", "eval"]
CI_PATHS = [".github/workflows"]
SECURITY_POLICY_PATHS = ["SECURITY.md"]
SKILLS_DIR = ".claude/skills"
COMMANDS_DIR = ".claude/commands"
SETTINGS_PATH = ".claude/settings.json"
MCP_CONFIG_PATH = ".mcp.json"


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


def has_skills_dir(client: GitHubClient, repo: str) -> bool:
    return client.path_exists(repo, SKILLS_DIR)


def skills_count(client: GitHubClient, repo: str) -> int:
    """`.claude/skills/`直下の子要素数(Skill 1件 = 1エントリ)。

    Skillの実体は`<name>/SKILL.md`というサブディレクトリ形式だけでなく、
    共有先へのシンボリックリンク`<name>`として置かれる場合もあるため
    (例: cline/cline)、ファイル種別を問わず直下の子要素数を数える。
    """
    return len(client.list_immediate_children(repo, SKILLS_DIR))


def has_custom_commands(client: GitHubClient, repo: str) -> bool:
    return client.path_exists(repo, COMMANDS_DIR)


def custom_commands_count(client: GitHubClient, repo: str) -> int:
    """`.claude/commands/`配下(サブディレクトリによる名前空間分けを含む)の`.md`ファイル数。"""
    prefix = f"{COMMANDS_DIR}/"
    return sum(
        1
        for path in client.get_file_paths(repo)
        if path.startswith(prefix) and path.endswith(".md")
    )


def has_hooks_config(client: GitHubClient, repo: str) -> bool:
    """`.claude/settings.json`が存在し、かつ`hooks`キーが空でないか。"""
    data = _load_json(client, repo, SETTINGS_PATH)
    return bool(data.get("hooks")) if data is not None else False


def mcp_servers_count(client: GitHubClient, repo: str) -> int:
    """`.mcp.json`の`mcpServers`に定義されたMCPサーバー数。"""
    data = _load_json(client, repo, MCP_CONFIG_PATH)
    if data is None:
        return 0
    servers = data.get("mcpServers")
    return len(servers) if isinstance(servers, dict) else 0


def _load_json(client: GitHubClient, repo: str, path: str) -> dict | None:
    content = client.get_file_content(repo, path)
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None
