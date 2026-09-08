import sys
from datetime import datetime, timezone

from agent_trend_radar import agent_doc_analysis, checks, config, llm_content_analysis, storage
from agent_trend_radar.github_client import GitHubClient


def run_checks_for_repo(client: GitHubClient, repo: str) -> dict:
    content = agent_doc_analysis.fetch_agent_doc_content(client, repo)
    llm_themes = llm_content_analysis.classify_agent_doc_themes(content)
    return {
        "has_agent_instructions": checks.has_agent_instructions(client, repo),
        "has_tests": checks.has_tests(client, repo),
        "has_eval": checks.has_eval(client, repo),
        "has_ci": checks.has_ci(client, repo),
        "has_security_policy": checks.has_security_policy(client, repo),
        "agent_doc_char_count": agent_doc_analysis.agent_doc_char_count(content),
        "agent_doc_heading_count": agent_doc_analysis.agent_doc_heading_count(content),
        "agent_doc_has_code_block": agent_doc_analysis.agent_doc_has_code_block(content),
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
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    targets = config.load_targets()
    client = GitHubClient()
    conn = storage.connect()
    storage.ensure_schema(conn)
    checked_at = datetime.now(timezone.utc).isoformat()

    total = len(targets)
    for i, target in enumerate(targets, start=1):
        repo = target["repo"]
        print(f"[{i}/{total}] {repo} ...")
        try:
            results = run_checks_for_repo(client, repo)
        except Exception as exc:
            print(f"[{i}/{total}] {repo}: ERROR {exc}")
            continue
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


if __name__ == "__main__":
    main()
