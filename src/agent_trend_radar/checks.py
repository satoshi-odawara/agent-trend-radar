import json
import posixpath

from agent_trend_radar.github_client import GitHubClient

AGENT_INSTRUCTION_PATHS = ["CLAUDE.md", "AGENTS.md", ".cursorrules"]
TEST_DIR_NAMES = {"tests", "test"}
EVAL_PATHS = ["evals", "eval"]
CI_PATHS = [".github/workflows"]
SECURITY_POLICY_PATHS = ["SECURITY.md"]
SKILLS_DIRS = [".claude/skills", ".agents/skills"]
COMMANDS_DIR = ".claude/commands"
SETTINGS_PATH = ".claude/settings.json"
MCP_CONFIG_PATH = ".mcp.json"


def _any_path_exists(client: GitHubClient, repo: str, paths: list[str]) -> bool:
    return any(client.path_exists(repo, path) for path in paths)


def has_agent_instructions(client: GitHubClient, repo: str) -> bool:
    """CLAUDE.md/AGENTS.md/.cursorrulesがリポジトリ内の任意の深さに存在するか。

    モノレポでルート直下に指示文書が無いケース(#29、例:
    continuedev/continueの`extensions/cli/AGENTS.md`)を検知するため、
    ルート直下だけでなく全深度を探索する(`has_tests`の#14対応と同型)。
    """
    basenames = {path.rsplit("/", 1)[-1] for path in client.get_file_paths(repo)}
    return not set(AGENT_INSTRUCTION_PATHS).isdisjoint(basenames)


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
    return _any_path_exists(client, repo, SKILLS_DIRS)


def skills_count(client: GitHubClient, repo: str) -> int:
    """`.claude/skills/`・`.agents/skills/`直下の子要素の和集合の数
    (Skill 1件 = 1エントリ)。

    `.agents/skills/`はAgentSkills.io等が推進するツール非依存の標準で、
    `.claude/skills`はそのClaude Code向け互換レイヤ(ディレクトリ単位・
    個別スキル単位いずれかのシンボリックリンク、または逆にこちらが実体で
    `.agents/skills`側がリンクの場合もある)として運用されているケースが
    多い(#28、実データで確認)。どちらか一方だけを見ると検知漏れ・過小
    カウントが起きるため、両パスを(自身がシンボリックリンクの場合は
    解決した上で)調べ、名前の和集合を数える(同一エントリの二重カウント
    を避ける)。
    """
    children: set[str] = set()
    for candidate in SKILLS_DIRS:
        resolved = _resolve_dir_path(client, repo, candidate)
        children |= client.list_immediate_children(repo, resolved)
    return len(children)


def has_custom_commands(client: GitHubClient, repo: str) -> bool:
    return client.path_exists(repo, COMMANDS_DIR)


def custom_commands_count(client: GitHubClient, repo: str) -> int:
    """`.claude/commands/`配下(サブディレクトリによる名前空間分けを含む)の`.md`ファイル数。

    `.claude/commands`自体がシンボリックリンクの場合はリンク先を解決する
    (skills_countと同様の理由)。
    """
    resolved = _resolve_dir_path(client, repo, COMMANDS_DIR)
    prefix = f"{resolved}/"
    return sum(
        1
        for path in client.get_file_paths(repo)
        if path.startswith(prefix) and path.endswith(".md")
    )


def _resolve_dir_path(client: GitHubClient, repo: str, dir_path: str) -> str:
    """dir_path自体がシンボリックリンクの場合、リンク先の実パスに解決する。

    シンボリックリンクでなければdir_pathをそのまま返す。
    """
    target = client.get_symlink_target(repo, dir_path)
    if target is None:
        return dir_path
    return posixpath.normpath(posixpath.join(posixpath.dirname(dir_path), target))


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
