import argparse
import csv
import statistics
import sys

from agent_trend_radar import storage

NUMERIC_COLUMNS = {"agent_doc_char_count", "agent_doc_heading_count"}

META_COLUMNS = ["repo", "segment", "monetization_model"]
ALL_COLUMNS = META_COLUMNS + storage.CHECK_COLUMNS


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


def render_boolean_stats(rows: list[tuple]) -> str:
    """真偽値項目をsegment x monetization_modelでグループ化したtrue件数/true率を出力する。

    「分散がなく比較材料として機能していない」項目(天井/床効果、#16・#20
    参照)を機械的に検出するための評価方法(#15の有効性確認を兼ねる)。
    """
    segment_idx = ALL_COLUMNS.index("segment")
    monetization_idx = ALL_COLUMNS.index("monetization_model")
    boolean_columns = [col for col in storage.CHECK_COLUMNS if col not in NUMERIC_COLUMNS]

    sections = []
    for column in boolean_columns:
        col_idx = ALL_COLUMNS.index(column)
        groups: dict[tuple[str, str], list[bool]] = {}
        for row in rows:
            key = (row[segment_idx], row[monetization_idx])
            groups.setdefault(key, []).append(bool(row[col_idx]))

        lines = [
            f"## {column}",
            "| segment | monetization_model | n | true | true率 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for (segment, monetization_model), values in sorted(groups.items()):
            n = len(values)
            true_n = sum(values)
            lines.append(
                "| {segment} | {monetization_model} | {n} | {true_n} | {rate:.0%} |".format(
                    segment=segment,
                    monetization_model=monetization_model,
                    n=n,
                    true_n=true_n,
                    rate=(true_n / n) if n else 0,
                )
            )
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def render_stats(rows: list[tuple]) -> str:
    return render_numeric_stats(rows) + "\n\n" + render_boolean_stats(rows)


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
