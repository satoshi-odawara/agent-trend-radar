import os
import sys

from agent_trend_radar import config, unknown_paths
from agent_trend_radar.github_client import GitHubClient

OUTPUT_PATH = "reports/unknown_agent_paths.md"


def build_report(client: GitHubClient, targets: list[dict]) -> str:
    header = "| repo | " + " | ".join(c["path"] for c in unknown_paths.CANDIDATE_PATHS) + " |"
    separator = "| --- | " + " | ".join("---" for _ in unknown_paths.CANDIDATE_PATHS) + " |"
    lines = [
        "# 未知のエージェント関連規約パスの検出(Issue #32)",
        "",
        "既知のチェック対象パス一覧(SPEC.md記載分)にない、エージェント関連と"
        "思われるパスをリポジトリごとに件数付きで一覧化したもの。ファイル型は"
        "存在すれば1・無ければ0、ディレクトリ型は配下の全ファイル数(再帰)。"
        "チェック項目に昇格させるかは人間が判断する。",
        "",
        header,
        separator,
    ]
    for target in targets:
        repo = target["repo"]
        counts = unknown_paths.detect_unknown_paths(client, repo)
        cells = [str(counts[c["path"]]) for c in unknown_paths.CANDIDATE_PATHS]
        lines.append(f"| {repo} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    targets = config.load_targets()
    client = GitHubClient()

    report = build_report(client, targets)

    dirname = os.path.dirname(OUTPUT_PATH)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"{OUTPUT_PATH} に出力しました({len(targets)}リポジトリ分)。")


if __name__ == "__main__":
    main()
