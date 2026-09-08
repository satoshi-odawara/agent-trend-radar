import os
import shutil
import sys

import report

from agent_trend_radar import agent_doc_analysis, config, storage
from agent_trend_radar.github_client import GitHubClient

OUTPUT_DIR = "data/latest"
AGENT_DOCS_DIR = os.path.join(OUTPUT_DIR, "agent_docs")


def repo_to_filename(repo: str) -> str:
    owner, name = repo.split("/", 1)
    return f"{owner}__{name}.md"


def write_text(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def publish_report() -> None:
    conn = storage.connect()
    storage.ensure_schema(conn)
    rows = report.fetch_latest_checks(conn)
    conn.close()

    write_text(os.path.join(OUTPUT_DIR, "report.md"), report.render_markdown(rows))
    write_text(os.path.join(OUTPUT_DIR, "stats.md"), report.render_stats(rows))


def publish_agent_docs() -> None:
    """CLAUDE.md/AGENTS.mdの生テキストをリポジトリごとに書き出す(Issue #22)。

    要約・解釈はせず原文のまま出力する(#12中止の理由と同じく、解釈は
    Claude Project側に委ねる)。既存ファイルは実行のたびに全消去してから
    書き直し、対象リポジトリから外れた/内容がなくなったファイルが古いまま
    残らないようにする。
    """
    shutil.rmtree(AGENT_DOCS_DIR, ignore_errors=True)

    targets = config.load_targets()
    client = GitHubClient()

    total = len(targets)
    for i, target in enumerate(targets, start=1):
        repo = target["repo"]
        print(f"[{i}/{total}] {repo} ...")
        try:
            content = agent_doc_analysis.fetch_agent_doc_content(client, repo)
        except Exception as exc:
            print(f"[{i}/{total}] {repo}: ERROR {exc}")
            continue
        if not content:
            print(f"[{i}/{total}] {repo}: skip (CLAUDE.md/AGENTS.mdなし)")
            continue
        path = os.path.join(AGENT_DOCS_DIR, repo_to_filename(repo))
        write_text(path, f"# {repo}\n\n{content}")
        print(f"[{i}/{total}] {repo}: done")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    publish_report()
    publish_agent_docs()
    print(f"公開データを{OUTPUT_DIR}/ に出力しました。")


if __name__ == "__main__":
    main()
