"""Streamlit dashboard for synthetic IT support ticket analysis.

This app is designed as a portfolio-style service desk dashboard.
It uses synthetic ticket data only and does not contain any real company,
customer, or employee information.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/synthetic_it_tickets.csv")
CHART_COLORS = ["#0C66E4", "#22A06B", "#8270DB", "#F97316", "#36B37E", "#579DFF", "#FFAB00"]


@st.cache_data
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load ticket data and prepare common reporting fields."""
    tickets = pd.read_csv(path)
    tickets["created_at"] = pd.to_datetime(tickets["created_at"], errors="coerce")
    tickets["resolved_at"] = pd.to_datetime(tickets["resolved_at"], errors="coerce")
    tickets["sla_met"] = tickets["sla_met"].astype("boolean")
    tickets["resolution_hours"] = tickets["resolution_minutes"] / 60
    tickets["month"] = tickets["created_at"].dt.to_period("M").astype(str)
    return tickets


def badge(text: str, class_name: str) -> str:
    """Return a small escaped HTML badge."""
    return f'<span class="badge {class_name}">{escape(str(text))}</span>'


def priority_badge(priority: str) -> str:
    class_name = {
        "P1 - Critical": "priority-critical",
        "P2 - High": "priority-high",
        "P3 - Medium": "priority-medium",
        "P4 - Low": "priority-low",
    }.get(priority, "priority-low")
    return badge(priority, class_name)


def status_badge(status: str) -> str:
    class_name = {
        "Closed": "status-closed",
        "Resolved": "status-resolved",
        "Open": "status-open",
        "Pending Vendor": "status-pending",
        "Pending User": "status-pending",
    }.get(status, "status-pending")
    return badge(status, class_name)


def kpi_card(label: str, value: str, helper: str, accent: str = "blue") -> str:
    return (
        f'<div class="kpi-card {accent}">'
        f'<div class="kpi-label">{escape(label)}</div>'
        f'<div class="kpi-value">{escape(value)}</div>'
        f'<div class="kpi-helper">{escape(helper)}</div>'
        "</div>"
    )


def build_ticket_rows(tickets: pd.DataFrame, max_rows: int = 8) -> str:
    """Return rendered HTML rows without leading indentation."""
    if tickets.empty:
        return '<div class="empty-state">No high-priority or pending tickets in the current filter.</div>'

    rows: list[str] = []
    for _, row in tickets.head(max_rows).iterrows():
        created = row["created_at"].strftime("%d %b %Y %H:%M") if pd.notna(row["created_at"]) else "Unknown"
        rows.append(
            '<div class="ticket-row">'
            '<div class="ticket-main">'
            f'<div class="ticket-title">{escape(str(row["subcategory"]))}</div>'
            f'<div class="ticket-meta">{escape(str(row["ticket_id"]))} · {escape(str(row["category"]))} · '
            f'{escape(str(row["site"]))} · {escape(created)}</div>'
            '</div>'
            f'<div class="ticket-assignee">{escape(str(row["assigned_group"]))}</div>'
            f'<div class="ticket-badges">{priority_badge(str(row["priority"]))}{status_badge(str(row["status"]))}</div>'
            '</div>'
        )
    return "".join(rows)


def build_ticket_table(tickets: pd.DataFrame, max_rows: int = 18) -> str:
    """Return a light-themed HTML table for portfolio display."""
    columns = [
        ("ticket_id", "Ticket"),
        ("created_at", "Created"),
        ("status", "Status"),
        ("priority", "Priority"),
        ("category", "Category"),
        ("subcategory", "Issue"),
        ("channel", "Channel"),
        ("site", "Site"),
        ("assigned_group", "Group"),
        ("resolution_minutes", "Resolution"),
        ("sla_met", "SLA"),
    ]

    header_cells = "".join(f"<th>{escape(label)}</th>" for _, label in columns)
    body_rows: list[str] = []

    for _, row in tickets.head(max_rows).iterrows():
        cells: list[str] = []
        for key, _ in columns:
            value = row.get(key, "")
            if key == "created_at" and pd.notna(value):
                rendered = escape(value.strftime("%d %b %Y %H:%M"))
            elif key == "status":
                rendered = status_badge(str(value))
            elif key == "priority":
                rendered = priority_badge(str(value))
            elif key == "resolution_minutes":
                rendered = "—" if pd.isna(value) else f"{int(value):,} min"
            elif key == "sla_met":
                rendered = badge("Met", "status-closed") if value is True else badge("Risk", "status-open")
            else:
                rendered = escape(str(value))
            cells.append(f"<td>{rendered}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return (
        '<div class="table-card">'
        '<div class="table-scroll">'
        '<table class="ticket-table">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</div>"
        "</div>"
    )


def chart_layout(fig):
    """Apply a clean dashboard look to Plotly charts."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        margin=dict(l=18, r=18, t=58, b=30),
        font=dict(
            family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            size=12,
            color="#253858",
        ),
        title=dict(font=dict(size=16, color="#172B4D")),
        showlegend=False,
    )
    fig.update_xaxes(
        title_font=dict(color="#44546F", size=12),
        tickfont=dict(color="#626F86", size=11),
        showline=True,
        linecolor="#B6C2CF",
        showgrid=False,
    )
    fig.update_yaxes(
        title_font=dict(color="#44546F", size=12),
        tickfont=dict(color="#626F86", size=11),
        showline=True,
        linecolor="#B6C2CF",
        gridcolor="#EBECF0",
        zerolinecolor="#B6C2CF",
    )
    return fig


PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}

st.set_page_config(page_title="IT Support Ticket Analysis", page_icon="🎧", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --page-bg: #F7F8FA;
    --card-bg: #FFFFFF;
    --text-main: #172B4D;
    --text-muted: #626F86;
    --border: #DFE1E6;
    --border-soft: #EBECF0;
    --blue: #0C66E4;
    --green: #22A06B;
    --orange: #F97316;
    --red: #C9372C;
    --purple: #8270DB;
}

.stApp {
    background: var(--page-bg);
    color: var(--text-main);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stSidebar"] {
    background: #0F172A;
    border-right: 1px solid #1E293B;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #F8FAFC !important;
}

.block-container {
    padding-top: 2.1rem;
    padding-bottom: 2.4rem;
    max-width: 1380px;
}

h1, h2, h3 {
    color: var(--text-main);
    letter-spacing: -0.03em;
}

.hero {
    background: linear-gradient(135deg, #172B4D 0%, #0C66E4 100%);
    color: white;
    padding: 28px 32px;
    border-radius: 28px;
    box-shadow: 0 18px 40px rgba(12, 102, 228, 0.20);
    margin-bottom: 22px;
}

.hero-title {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 15px;
    line-height: 1.6;
    max-width: 900px;
    color: #DEEBFF;
}

.section-title {
    font-size: 19px;
    font-weight: 750;
    margin: 4px 0 14px 0;
    color: var(--text-main);
}

.panel, .ticket-panel, .table-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 24px;
    box-shadow: 0 10px 28px rgba(9, 30, 66, 0.06);
    margin-bottom: 20px;
}

.panel {
    padding: 22px;
}

.ticket-panel {
    padding: 10px 16px;
}

.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 20px 22px;
    box-shadow: 0 10px 24px rgba(9, 30, 66, 0.05);
    border-top: 4px solid var(--blue);
    min-height: 135px;
}

.kpi-card.green { border-top-color: var(--green); }
.kpi-card.orange { border-top-color: var(--orange); }
.kpi-card.red { border-top-color: var(--red); }
.kpi-card.purple { border-top-color: var(--purple); }

.kpi-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

.kpi-value {
    font-size: 34px;
    color: var(--text-main);
    font-weight: 800;
    margin-bottom: 8px;
}

.kpi-helper {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.45;
}

.update-card {
    border: 1px solid var(--border-soft);
    border-radius: 18px;
    padding: 14px 15px;
    margin-bottom: 12px;
    background: #FFFFFF;
}

.update-title {
    font-weight: 750;
    font-size: 14px;
    color: var(--text-main);
    margin-bottom: 5px;
}

.update-text {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.45;
}

.ticket-row {
    display: grid;
    grid-template-columns: minmax(300px, 1.4fr) 170px 240px;
    gap: 16px;
    align-items: center;
    padding: 14px 6px;
    border-bottom: 1px solid var(--border-soft);
}

.ticket-row:last-child {
    border-bottom: none;
}

.ticket-title {
    font-size: 14px;
    font-weight: 750;
    color: var(--text-main);
    margin-bottom: 4px;
}

.ticket-meta, .ticket-assignee {
    font-size: 12px;
    color: var(--text-muted);
}

.ticket-badges {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    flex-wrap: wrap;
}

.badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 5px 9px;
    font-size: 11px;
    font-weight: 750;
    white-space: nowrap;
}

.priority-critical { background: #FFECEB; color: #AE2A19; }
.priority-high { background: #FFF4E5; color: #974F0C; }
.priority-medium { background: #E9F2FF; color: #0055CC; }
.priority-low { background: #DCFFF1; color: #216E4E; }
.status-open { background: #FFECEB; color: #AE2A19; }
.status-pending { background: #FFF4E5; color: #974F0C; }
.status-resolved { background: #E9F2FF; color: #0055CC; }
.status-closed { background: #DCFFF1; color: #216E4E; }

.empty-state {
    padding: 20px;
    color: var(--text-muted);
    font-size: 14px;
}

.insight-list {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--text-main);
    font-size: 14px;
    line-height: 1.75;
}

div[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 10px 12px;
    box-shadow: 0 10px 24px rgba(9, 30, 66, 0.04);
}

.table-card {
    padding: 0;
    overflow: hidden;
}

.table-scroll {
    overflow-x: auto;
}

.ticket-table {
    width: 100%;
    border-collapse: collapse;
    background: #FFFFFF;
    color: var(--text-main);
    font-size: 13px;
}

.ticket-table thead {
    background: #F1F3F7;
    border-bottom: 1px solid var(--border);
}

.ticket-table th {
    padding: 13px 14px;
    text-align: left;
    font-weight: 800;
    color: #44546F;
    white-space: nowrap;
}

.ticket-table td {
    padding: 13px 14px;
    border-bottom: 1px solid var(--border-soft);
    color: var(--text-main);
    white-space: nowrap;
}

.ticket-table tbody tr:nth-child(even) {
    background: #FAFBFC;
}

.ticket-table tbody tr:hover {
    background: #E9F2FF;
}
</style>
""",
    unsafe_allow_html=True,
)

if not DATA_PATH.exists():
    st.warning("No dataset found. Run `python src/generate_tickets.py` first.")
    st.stop()

tickets = load_data()

with st.sidebar:
    st.markdown("## 🎧 Support Desk")
    st.caption("Synthetic IT support ticket dataset")
    st.markdown("---")
    selected_categories = st.multiselect(
        "Category",
        options=sorted(tickets["category"].dropna().unique()),
        default=sorted(tickets["category"].dropna().unique()),
    )
    selected_sites = st.multiselect(
        "Site",
        options=sorted(tickets["site"].dropna().unique()),
        default=sorted(tickets["site"].dropna().unique()),
    )
    selected_priorities = st.multiselect(
        "Priority",
        options=sorted(tickets["priority"].dropna().unique()),
        default=sorted(tickets["priority"].dropna().unique()),
    )
    selected_statuses = st.multiselect(
        "Status",
        options=sorted(tickets["status"].dropna().unique()),
        default=sorted(tickets["status"].dropna().unique()),
    )

filtered = tickets[
    tickets["category"].isin(selected_categories)
    & tickets["site"].isin(selected_sites)
    & tickets["priority"].isin(selected_priorities)
    & tickets["status"].isin(selected_statuses)
].copy()
filtered_resolved = filtered[filtered["resolved_at"].notna()].copy()

sla_rate = filtered_resolved["sla_met"].mean() if len(filtered_resolved) else 0
avg_resolution = filtered_resolved["resolution_hours"].mean() if len(filtered_resolved) else 0
open_count = filtered[filtered["resolved_at"].isna()].shape[0]
closed_count = filtered[filtered["status"].isin(["Closed", "Resolved"])].shape[0]

category_counts = filtered.groupby("category").size().reset_index(name="ticket_count")
priority_counts = filtered.groupby("priority").size().reset_index(name="ticket_count")
monthly_volume = filtered.groupby("month").size().reset_index(name="ticket_count")

category_resolution = (
    filtered_resolved.groupby("category")
    .agg(
        avg_resolution_hours=("resolution_hours", "mean"),
        ticket_count=("ticket_id", "count"),
        sla_met_rate=("sla_met", "mean"),
    )
    .reset_index()
    .sort_values("avg_resolution_hours", ascending=False)
)

attention_tickets = filtered[
    filtered["status"].isin(["Open", "Pending Vendor", "Pending User"])
    | filtered["priority"].isin(["P1 - Critical", "P2 - High"])
].sort_values(["priority", "created_at"])

st.markdown(
    """
<div class="hero">
    <div class="hero-title">IT Support Ticket Analysis</div>
    <div class="hero-subtitle">
        A portfolio dashboard for service desk reporting: ticket volume, SLA performance,
        issue categories, site workload, and operational improvement opportunities.
    </div>
</div>
""",
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(kpi_card("Open tickets", f"{open_count:,}", "Tickets still open or waiting for action", "red"), unsafe_allow_html=True)
with kpi2:
    st.markdown(kpi_card("Resolved / closed", f"{closed_count:,}", "Tickets completed in the selected view", "green"), unsafe_allow_html=True)
with kpi3:
    st.markdown(kpi_card("SLA met rate", f"{sla_rate:.1%}", "Resolved tickets completed within target", "blue"), unsafe_allow_html=True)
with kpi4:
    st.markdown(kpi_card("Avg resolution", f"{avg_resolution:.1f} hrs", "Average time to resolve completed tickets", "purple"), unsafe_allow_html=True)

left_col, main_col = st.columns([1.05, 2.7], gap="large")

with left_col:
    st.markdown(
        """
<div class="panel">
    <div class="section-title">Updates to your tickets</div>
    <div class="update-card">
        <div class="update-title">Network issues are the top category</div>
        <div class="update-text">Review recurring Wi-Fi, LAN and switch-port incidents for documentation or root-cause follow-up.</div>
    </div>
    <div class="update-card">
        <div class="update-title">SLA tracking is performing well</div>
        <div class="update-text">Use high-priority and open tickets to identify the next operational improvement opportunities.</div>
    </div>
    <div class="update-card">
        <div class="update-title">CCTV tickets take longer</div>
        <div class="update-text">Camera, NVR and IP conflict issues may require field support, vendor checks or better handover notes.</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    top_category = category_counts.sort_values("ticket_count", ascending=False).iloc[0] if len(category_counts) else None
    slowest_category = category_resolution.iloc[0] if len(category_resolution) else None
    top_category_name = escape(str(top_category["category"])) if top_category is not None else "N/A"
    slowest_category_name = escape(str(slowest_category["category"])) if slowest_category is not None else "N/A"

    st.markdown(
        f"""
<div class="panel">
    <div class="section-title">Operational insights</div>
    <ul class="insight-list">
        <li><b>{top_category_name}</b> is the highest-volume category.</li>
        <li><b>{slowest_category_name}</b> has the longest average resolution time.</li>
        <li>Open and pending tickets should be reviewed before they become SLA risks.</li>
        <li>Repeated categories may indicate training, documentation or process gaps.</li>
    </ul>
</div>
""",
        unsafe_allow_html=True,
    )

with main_col:
    st.markdown('<div class="section-title">Tickets requiring attention</div>', unsafe_allow_html=True)
    ticket_rows_html = build_ticket_rows(attention_tickets, max_rows=8)
    st.markdown(f'<div class="ticket-panel">{ticket_rows_html}</div>', unsafe_allow_html=True)

    chart_left, chart_right = st.columns(2)
    with chart_left:
        fig = px.bar(
            category_counts.sort_values("ticket_count", ascending=False),
            x="category",
            y="ticket_count",
            title="Ticket Volume by Category",
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_traces(marker_color="#579DFF", marker_line_color="#0C66E4", marker_line_width=0.6)
        st.plotly_chart(chart_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with chart_right:
        fig = px.bar(
            priority_counts,
            x="priority",
            y="ticket_count",
            title="Ticket Volume by Priority",
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_traces(marker_color="#22A06B", marker_line_color="#1F845A", marker_line_width=0.6)
        st.plotly_chart(chart_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    trend_left, trend_right = st.columns(2)
    with trend_left:
        fig = px.line(
            monthly_volume,
            x="month",
            y="ticket_count",
            markers=True,
            title="Monthly Ticket Trend",
            color_discrete_sequence=["#0C66E4"],
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8, color="#0C66E4"))
        st.plotly_chart(chart_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

    with trend_right:
        fig = px.bar(
            category_resolution,
            x="category",
            y="avg_resolution_hours",
            title="Average Resolution Time by Category",
            color_discrete_sequence=CHART_COLORS,
        )
        fig.update_traces(marker_color="#8270DB", marker_line_color="#6E5DC6", marker_line_width=0.6)
        st.plotly_chart(chart_layout(fig), use_container_width=True, config=PLOTLY_CONFIG)

st.markdown('<div class="section-title">Ticket sample</div>', unsafe_allow_html=True)
display_columns = [
    "ticket_id",
    "created_at",
    "status",
    "priority",
    "category",
    "subcategory",
    "channel",
    "site",
    "assigned_group",
    "resolution_minutes",
    "sla_met",
]
st.markdown(build_ticket_table(filtered[display_columns], max_rows=18), unsafe_allow_html=True)
