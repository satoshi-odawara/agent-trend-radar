import argparse
import csv
import statistics
import sys

from agent_trend_radar import storage

NUMERIC_COLUMNS = {
    "agent_doc_count",
    "agent_doc_char_count",
    "agent_doc_heading_count",
    "skills_count",
    "custom_commands_count",
    "mcp_servers_count",
    "ci_workflow_count",
    "agent_doc_code_block_count",
}

META_COLUMNS = ["repo", "segment", "monetization_model"]
ALL_COLUMNS = META_COLUMNS + storage.CHECK_COLUMNS

# フィードフォワード(事前に指示するもの)/フィードバック(事後に検証する
# もの)の分類(#34)。「指示文書の中身を一段深く見るため」という#5の追加
# 理由から、指示文書の内容を見るagent_doc_*系もフィードフォワード側に
# 含めた。has_mcp_serversはCHECK_COLUMNSに対応する真偽値列が無い
# (mcp_servers_countのみ)ため、`render_mcp_derived_stats`で
# `mcp_servers_count > 0`から派生させる。has_security_policy(想定読者が
# 人間の研究者・報告者でエージェント向けではない)とagent_doc_count
# (#29でモノレポ傾向の代理指標として追加、この軸とは無関係)は対象外。
# agent_doc_char_count/heading_count/agent_doc_code_block_countは「量」を
# 測る数値指標で0/1化できないため対象外。
FEEDFORWARD_COLUMNS = [
    "has_agent_instructions",
    "has_skills_dir",
    "has_custom_commands",
    "has_mcp_servers",
    "agent_doc_has_code_block",
    "agent_doc_mentions_test",
    "agent_doc_mentions_lint",
    "agent_doc_mentions_security",
    "agent_doc_mentions_commit_convention",
    "agent_doc_mentions_tool_usage",
    "agent_doc_mentions_repo_structure",
    "agent_doc_mentions_boundaries",
    "agent_doc_mentions_pr_review",
    "agent_doc_mentions_release_process",
]

FEEDBACK_COLUMNS = [
    "has_tests",
    "has_eval",
    "has_ci",
    "has_hooks_config",
]


def fetch_latest_checks(conn) -> list[tuple]:
    columns_sql = ", ".join(ALL_COLUMNS)
    cursor = conn.execute(
        f"""
        SELECT {columns_sql}
        FROM repo_checks r
        WHERE checked_at = (
            SELECT MAX(checked_at) FROM repo_checks r2 WHERE r2.repo = r.repo
        )
        ORDER BY segment, monetization_model, repo
        """
    )
    return cursor.fetchall()


def format_cell(column: str, value) -> str:
    if column in NUMERIC_COLUMNS:
        return str(value)
    if column in META_COLUMNS:
        return str(value)
    if column in storage.TEXT_COLUMNS:
        return str(value) if value else ""
    return "✓" if value else ""


def render_markdown(rows: list[tuple]) -> str:
    header = "| " + " | ".join(ALL_COLUMNS) + " |"
    separator = "| " + " | ".join("---" for _ in ALL_COLUMNS) + " |"
    lines = [header, separator]
    for row in rows:
        cells = [format_cell(col, value) for col, value in zip(ALL_COLUMNS, row)]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_numeric_stats(rows: list[tuple]) -> str:
    """segment x monetization_modelでグループ化したn/min/中央値/平均/maxを出力する。

    平均値だけでは外れ値に強く引っ張られるため(#17参照)、中央値・分布も
    併記する。
    """
    segment_idx = ALL_COLUMNS.index("segment")
    monetization_idx = ALL_COLUMNS.index("monetization_model")

    sections = []
    for column in sorted(NUMERIC_COLUMNS):
        col_idx = ALL_COLUMNS.index(column)
        groups: dict[tuple[str, str], list[int]] = {}
        for row in rows:
            key = (row[segment_idx], row[monetization_idx])
            groups.setdefault(key, []).append(row[col_idx])

        lines = [
            f"## {column}",
            "| segment | monetization_model | n | min | median | mean | max |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for (segment, monetization_model), values in sorted(groups.items()):
            lines.append(
                "| {segment} | {monetization_model} | {n} | {min} | {median:.0f} | {mean:.0f} | {max} |".format(
                    segment=segment,
                    monetization_model=monetization_model,
                    n=len(values),
                    min=min(values),
                    median=statistics.median(values),
                    mean=statistics.mean(values),
                    max=max(values),
                )
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _render_boolean_section(rows: list[tuple], label: str, values: list[bool]) -> str:
    """rowsと同じ並び順のbool値のリストから、segment x monetization_model
    別のtrue件数/true率テーブルを1セクション分組み立てる。
    """
    segment_idx = ALL_COLUMNS.index("segment")
    monetization_idx = ALL_COLUMNS.index("monetization_model")
    groups: dict[tuple[str, str], list[bool]] = {}
    for row, value in zip(rows, values):
        key = (row[segment_idx], row[monetization_idx])
        groups.setdefault(key, []).append(value)

    lines = [
        f"## {label}",
        "| segment | monetization_model | n | true | true率 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for (segment, monetization_model), group_values in sorted(groups.items()):
        n = len(group_values)
        true_n = sum(group_values)
        lines.append(
            "| {segment} | {monetization_model} | {n} | {true_n} | {rate:.0%} |".format(
                segment=segment,
                monetization_model=monetization_model,
                n=n,
                true_n=true_n,
                rate=(true_n / n) if n else 0,
            )
        )
    return "\n".join(lines)


def render_boolean_stats(rows: list[tuple]) -> str:
    """真偽値項目をsegment x monetization_modelでグループ化したtrue件数/true率を出力する。

    「分散がなく比較材料として機能していない」項目(天井/床効果、#16・#20
    参照)を機械的に検出するための評価方法(#15の有効性確認を兼ねる)。
    """
    boolean_columns = [
        col
        for col in storage.CHECK_COLUMNS
        if col not in NUMERIC_COLUMNS and col not in storage.TEXT_COLUMNS
    ]

    sections = []
    for column in boolean_columns:
        col_idx = ALL_COLUMNS.index(column)
        values = [bool(row[col_idx]) for row in rows]
        sections.append(_render_boolean_section(rows, column, values))
    return "\n\n".join(sections)


def render_mcp_derived_stats(rows: list[tuple]) -> str:
    """`mcp_servers_count > 0`から`has_mcp_servers`を派生させて出力する。

    `mcp_servers_count`にはCHECK_COLUMNS上に対応する真偽値列が無いが、
    フィードフォワード分類(#34)にMCPを含めるため、この関数で個別に
    render_boolean_statsと同じ形式のセクションを1つだけ追加する。
    """
    count_idx = ALL_COLUMNS.index("mcp_servers_count")
    values = [row[count_idx] > 0 for row in rows]
    return _render_boolean_section(rows, "has_mcp_servers(mcp_servers_countの派生)", values)


def render_ff_fb_classification() -> str:
    """フィードフォワード/フィードバックの分類対応表(agent-trend-playbook
    調査案R6、Issue #34)。

    各項目自体のtrue率は上記の項目別セクション(`render_boolean_stats`/
    `render_mcp_derived_stats`)を参照する。ここでは分類のみを示し、群
    ごとの平均等には集約しない。ツール導入の有無(has_skills_dir等)と
    指示文書内のキーワード言及(agent_doc_mentions_*)は性質が異なる
    シグナルであり、1つの数値に混ぜると実際のツール投資と文書の饒舌さを
    見分けられなくなり解釈を誤らせるため。
    """
    lines = [
        "## フィードフォワード/フィードバックの分類",
        "",
        "各項目のtrue率は上記の項目別セクションを参照。性質の異なる項目を",
        "1つの数値に集約すると解釈を誤らせるため、ここでは分類のみ示す。",
        "",
        "### フィードフォワード(事前に指示するもの)",
        "",
    ]
    lines += [f"- {column}" for column in FEEDFORWARD_COLUMNS]
    lines += ["", "### フィードバック(事後に検証するもの)", ""]
    lines += [f"- {column}" for column in FEEDBACK_COLUMNS]
    return "\n".join(lines)


def render_stats(rows: list[tuple]) -> str:
    return (
        render_numeric_stats(rows)
        + "\n\n"
        + render_boolean_stats(rows)
        + "\n\n"
        + render_mcp_derived_stats(rows)
        + "\n\n"
        + render_ff_fb_classification()
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="repo_checksの結果をレポート出力する")
    parser.add_argument(
        "--format",
        choices=["markdown", "csv", "stats"],
        default="markdown",
        help="出力形式(既定: markdown)",
    )
    args = parser.parse_args()

    conn = storage.connect()
    storage.ensure_schema(conn)
    rows = fetch_latest_checks(conn)
    conn.close()

    if args.format == "csv":
        writer = csv.writer(sys.stdout, lineterminator="\n")
        writer.writerow(ALL_COLUMNS)
        writer.writerows(rows)
    elif args.format == "stats":
        print(render_stats(rows))
    else:
        print(render_markdown(rows))


if __name__ == "__main__":
    main()
