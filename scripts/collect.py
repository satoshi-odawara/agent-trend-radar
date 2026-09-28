import logging
import os
import sys
from datetime import datetime, timezone

from agent_trend_radar import agent_doc_analysis, checks, config, llm_content_analysis, storage
from agent_trend_radar.github_client import GitHubClient

LOG_PATH = "data/collect.log"

logger = logging.getLogger(__name__)


def configure_logging(log_path: str = LOG_PATH) -> None:
    """エラー・リトライの発生をファイルに残す(#11)。

    週次自動実行(#10)で失敗が起きても標準出力はCIログにしか残らないため、
    `github_client`のリトライ警告・収集失敗を`log_path`に追記する。
    """
    dirname = os.path.dirname(log_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
    )


def run_checks_for_repo(client: GitHubClient, repo: str) -> tuple[dict, str | None]:
    content = agent_doc_analysis.fetch_agent_doc_content(client, repo)
    llm_themes, model_name = llm_content_analysis.classify_agent_doc_themes(content)
    checks_result = {
        "has_agent_instructions": checks.has_agent_instructions(client, repo),
        "has_tests": checks.has_tests(client, repo),
        "has_eval": checks.has_eval(client, repo),
        "has_ci": checks.has_ci(client, repo),
        "ci_workflow_count": checks.ci_workflow_count(client, repo),
        "has_security_policy": checks.has_security_policy(client, repo),
        "agent_doc_count": agent_doc_analysis.agent_doc_count(client, repo),
        "agent_doc_char_count": agent_doc_analysis.agent_doc_char_count(content),
        "agent_doc_heading_count": agent_doc_analysis.agent_doc_heading_count(content),
        "agent_doc_has_code_block": agent_doc_analysis.agent_doc_has_code_block(content),
        "agent_doc_code_block_count": agent_doc_analysis.agent_doc_code_block_count(content),
        "agent_doc_mentions_test": agent_doc_analysis.agent_doc_mentions_test(content),
        "agent_doc_mentions_lint": agent_doc_analysis.agent_doc_mentions_lint(content),
        "agent_doc_mentions_security": agent_doc_analysis.agent_doc_mentions_security(content),
        "agent_doc_mentions_commit_convention": (
            agent_doc_analysis.agent_doc_mentions_commit_convention(content)
        ),
        "agent_doc_mentions_tool_usage": agent_doc_analysis.agent_doc_mentions_tool_usage(content),
        "agent_doc_mentions_repo_structure": llm_themes["agent_doc_mentions_repo_structure"],
        "agent_doc_mentions_boundaries": llm_themes["agent_doc_mentions_boundaries"],
        "agent_doc_mentions_pr_review": llm_themes["agent_doc_mentions_pr_review"],
        "agent_doc_mentions_release_process": llm_themes["agent_doc_mentions_release_process"],
        "has_skills_dir": checks.has_skills_dir(client, repo),
        "skills_count": checks.skills_count(client, repo),
        "has_custom_commands": checks.has_custom_commands(client, repo),
        "custom_commands_count": checks.custom_commands_count(client, repo),
        "has_hooks_config": checks.has_hooks_config(client, repo),
        "mcp_servers_count": checks.mcp_servers_count(client, repo),
        "agent_doc_llm_cache_key": agent_doc_analysis.representative_doc_cache_key(client, repo),
    }
    return checks_result, model_name


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    configure_logging()
    targets = config.load_targets()
    client = GitHubClient()
    conn = storage.connect()
    storage.ensure_schema(conn)
    checked_at = datetime.now(timezone.utc).isoformat()

    total = len(targets)
    observed_models: set[str] = set()
    for i, target in enumerate(targets, start=1):
        repo = target["repo"]
        print(f"[{i}/{total}] {repo} ...")
        try:
            results, model_name = run_checks_for_repo(client, repo)
        except Exception as exc:
            print(f"[{i}/{total}] {repo}: ERROR {exc}")
            logger.error("%s: %s", repo, exc)
            continue
        if model_name:
            observed_models.add(model_name)
        storage.insert_repo_check(
            conn,
            repo=repo,
            segment=target["segment"],
            monetization_model=target["monetization_model"],
            checks=results,
            checked_at=checked_at,
        )
        print(f"[{i}/{total}] {repo}: done")

    conn.close()
    model_name = ", ".join(sorted(observed_models)) if observed_models else None
    llm_content_analysis.write_run_metadata(
        llm_content_analysis.collect_run_metadata(model_name=model_name)
    )


if __name__ == "__main__":
    main()
