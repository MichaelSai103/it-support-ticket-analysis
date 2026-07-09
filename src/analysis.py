"""Analyse synthetic IT support ticket data.

The goal is to produce simple operational insights that would be useful to an
IT support or service desk team: volume, SLA compliance, resolution time and
common issue categories.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("data/synthetic_it_tickets.csv")
DEFAULT_OUTPUT_DIR = Path("output")


def load_tickets(path: Path = DEFAULT_INPUT) -> pd.DataFrame:
    """Load ticket data and apply basic type conversions."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run `python src/generate_tickets.py` first."
        )

    tickets = pd.read_csv(path)
    tickets["created_at"] = pd.to_datetime(tickets["created_at"], errors="coerce")
    tickets["resolved_at"] = pd.to_datetime(tickets["resolved_at"], errors="coerce")
    tickets["sla_met"] = tickets["sla_met"].astype("boolean")
    return tickets


def build_summary(tickets: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build summary tables for IT support reporting."""
    resolved = tickets[tickets["resolved_at"].notna()].copy()
    resolved["resolution_hours"] = resolved["resolution_minutes"] / 60

    category_volume = (
        tickets.groupby("category")
        .size()
        .reset_index(name="ticket_count")
        .sort_values("ticket_count", ascending=False)
    )

    priority_summary = (
        resolved.groupby("priority")
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
            median_resolution_hours=("resolution_hours", "median"),
            sla_met_rate=("sla_met", "mean"),
        )
        .reset_index()
    )

    category_resolution = (
        resolved.groupby("category")
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
            sla_met_rate=("sla_met", "mean"),
            avg_customer_satisfaction=("customer_satisfaction", "mean"),
        )
        .reset_index()
        .sort_values("avg_resolution_hours", ascending=False)
    )

    site_volume = (
        tickets.groupby("site")
        .size()
        .reset_index(name="ticket_count")
        .sort_values("ticket_count", ascending=False)
    )

    channel_volume = (
        tickets.groupby("channel")
        .size()
        .reset_index(name="ticket_count")
        .sort_values("ticket_count", ascending=False)
    )

    monthly_volume = (
        tickets.assign(month=tickets["created_at"].dt.to_period("M").astype(str))
        .groupby("month")
        .size()
        .reset_index(name="ticket_count")
    )

    return {
        "category_volume": category_volume,
        "priority_summary": priority_summary,
        "category_resolution": category_resolution,
        "site_volume": site_volume,
        "channel_volume": channel_volume,
        "monthly_volume": monthly_volume,
    }


def save_summary_tables(summary: dict[str, pd.DataFrame], output_dir: Path = DEFAULT_OUTPUT_DIR) -> None:
    """Save analysis tables to CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in summary.items():
        table.to_csv(output_dir / f"{name}.csv", index=False)


def print_key_findings(tickets: pd.DataFrame, summary: dict[str, pd.DataFrame]) -> None:
    """Print a short human-readable report."""
    resolved = tickets[tickets["resolved_at"].notna()].copy()
    sla_rate = resolved["sla_met"].mean() if len(resolved) else 0
    avg_resolution_hours = resolved["resolution_minutes"].mean() / 60 if len(resolved) else 0
    top_category = summary["category_volume"].iloc[0]

    print("IT Support Ticket Analysis")
    print("=" * 30)
    print(f"Total tickets: {len(tickets)}")
    print(f"Resolved/closed tickets: {len(resolved)}")
    print(f"Overall SLA met rate: {sla_rate:.1%}")
    print(f"Average resolution time: {avg_resolution_hours:.2f} hours")
    print(f"Top issue category: {top_category['category']} ({top_category['ticket_count']} tickets)")
    print("\nSummary tables saved to output/.")


def main() -> None:
    tickets = load_tickets()
    summary = build_summary(tickets)
    save_summary_tables(summary)
    print_key_findings(tickets, summary)


if __name__ == "__main__":
    main()
