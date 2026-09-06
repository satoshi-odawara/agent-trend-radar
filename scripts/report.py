import argparse
import csv
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


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="repo_checksの結果をレポート出力する")
    parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
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
    else:
        print(render_markdown(rows))


if __name__ == "__main__":
    main()
