"""Streamlit dashboard for synthetic IT support ticket analysis."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/synthetic_it_tickets.csv")


@st.cache_data
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    tickets = pd.read_csv(path)
    tickets["created_at"] = pd.to_datetime(tickets["created_at"], errors="coerce")
    tickets["resolved_at"] = pd.to_datetime(tickets["resolved_at"], errors="coerce")
    tickets["sla_met"] = tickets["sla_met"].astype("boolean")
    tickets["resolution_hours"] = tickets["resolution_minutes"] / 60
    tickets["month"] = tickets["created_at"].dt.to_period("M").astype(str)
    return tickets


st.set_page_config(page_title="IT Support Ticket Analysis", layout="wide")

st.title("IT Support Ticket Analysis Dashboard")
st.write(
    "A portfolio dashboard using synthetic help desk data to analyse ticket volume, "
    "SLA performance, resolution time, support channels and common issue categories."
)

if not DATA_PATH.exists():
    st.warning("No dataset found. Run `python src/generate_tickets.py` first.")
    st.stop()

Tickets = load_data()
resolved = Tickets[Tickets["resolved_at"].notna()].copy()

with st.sidebar:
    st.header("Filters")
    selected_categories = st.multiselect(
        "Category",
        options=sorted(Tickets["category"].dropna().unique()),
        default=sorted(Tickets["category"].dropna().unique()),
    )
    selected_sites = st.multiselect(
        "Site",
        options=sorted(Tickets["site"].dropna().unique()),
        default=sorted(Tickets["site"].dropna().unique()),
    )
    selected_priorities = st.multiselect(
        "Priority",
        options=sorted(Tickets["priority"].dropna().unique()),
        default=sorted(Tickets["priority"].dropna().unique()),
    )

filtered = Tickets[
    Tickets["category"].isin(selected_categories)
    & Tickets["site"].isin(selected_sites)
    & Tickets["priority"].isin(selected_priorities)
]
filtered_resolved = filtered[filtered["resolved_at"].notna()].copy()

sla_rate = filtered_resolved["sla_met"].mean() if len(filtered_resolved) else 0
avg_resolution = filtered_resolved["resolution_hours"].mean() if len(filtered_resolved) else 0
open_count = filtered[filtered["resolved_at"].isna()].shape[0]

metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Total tickets", f"{len(filtered):,}")
metric2.metric("Open / pending", f"{open_count:,}")
metric3.metric("SLA met rate", f"{sla_rate:.1%}")
metric4.metric("Avg resolution", f"{avg_resolution:.1f} hrs")

st.divider()

left, right = st.columns(2)

with left:
    category_counts = filtered.groupby("category").size().reset_index(name="ticket_count")
    fig = px.bar(
        category_counts.sort_values("ticket_count", ascending=False),
        x="category",
        y="ticket_count",
        title="Ticket Volume by Category",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    priority_counts = filtered.groupby("priority").size().reset_index(name="ticket_count")
    fig = px.bar(
        priority_counts,
        x="priority",
        y="ticket_count",
        title="Ticket Volume by Priority",
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    monthly_volume = filtered.groupby("month").size().reset_index(name="ticket_count")
    fig = px.line(monthly_volume, x="month", y="ticket_count", markers=True, title="Monthly Ticket Trend")
    st.plotly_chart(fig, use_container_width=True)

with right:
    category_resolution = (
        filtered_resolved.groupby("category")
        .agg(avg_resolution_hours=("resolution_hours", "mean"))
        .reset_index()
        .sort_values("avg_resolution_hours", ascending=False)
    )
    fig = px.bar(
        category_resolution,
        x="category",
        y="avg_resolution_hours",
        title="Average Resolution Time by Category",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Ticket Sample")
st.dataframe(filtered.head(50), use_container_width=True)
