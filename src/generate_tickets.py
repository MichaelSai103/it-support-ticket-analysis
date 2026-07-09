"""Generate synthetic IT support ticket data.

This script creates realistic but fully synthetic help desk tickets for portfolio
analysis. It does not use any real company, customer, or employee information.
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


CATEGORIES = {
    "Network": ["Wi-Fi issue", "LAN outage", "Slow connection", "VPN issue", "Switch port issue"],
    "Hardware": ["Workstation fault", "Monitor issue", "Docking station issue", "Keyboard/mouse", "Peripheral fault"],
    "Software": ["Application error", "Software update", "Installation request", "Performance issue"],
    "Account": ["Password reset", "Access request", "MFA issue", "Account lockout"],
    "Printer": ["Print queue issue", "Driver issue", "Toner/maintenance", "Network printer offline"],
    "CCTV": ["Camera offline", "NVR connectivity", "Video playback issue", "IP address conflict"],
    "Security": ["Suspicious email", "Malware alert", "Firewall alert", "Unauthorized access attempt"],
}

CATEGORY_WEIGHTS = {
    "Network": 0.24,
    "Hardware": 0.18,
    "Software": 0.17,
    "Account": 0.16,
    "Printer": 0.10,
    "CCTV": 0.08,
    "Security": 0.07,
}

PRIORITIES = ["P1 - Critical", "P2 - High", "P3 - Medium", "P4 - Low"]
PRIORITY_WEIGHTS = [0.05, 0.18, 0.55, 0.22]
SLA_TARGET_MINUTES = {
    "P1 - Critical": 240,
    "P2 - High": 480,
    "P3 - Medium": 1440,
    "P4 - Low": 2880,
}

CHANNELS = ["Email", "Phone", "Walk-up", "Monitoring Alert", "Self-service Portal"]
SITES = ["Perth CBD", "Wangara", "Malaga", "Canning Vale", "Osborne Park", "Remote User"]
ASSIGNED_GROUPS = ["Service Desk", "Desktop Support", "Network Support", "Security Support", "Field Support"]
ROOT_CAUSES = [
    "User error",
    "Configuration issue",
    "Hardware failure",
    "Software bug",
    "Network outage",
    "Access permission",
    "Unknown",
]
STATUS_OPTIONS = ["Closed", "Resolved", "Open", "Pending Vendor", "Pending User"]
STATUS_WEIGHTS = [0.67, 0.20, 0.05, 0.04, 0.04]

BASE_RESOLUTION_MINUTES = {
    "Network": 600,
    "Hardware": 720,
    "Software": 540,
    "Account": 160,
    "Printer": 360,
    "CCTV": 900,
    "Security": 480,
}

PRIORITY_MULTIPLIER = {
    "P1 - Critical": 0.45,
    "P2 - High": 0.75,
    "P3 - Medium": 1.00,
    "P4 - Low": 1.40,
}


def generate_tickets(num_tickets: int = 500, seed: int = 42) -> pd.DataFrame:
    """Return a synthetic IT support ticket dataset."""
    random.seed(seed)
    np.random.seed(seed)

    start_date = datetime(2026, 1, 1)
    records: list[dict[str, object]] = []

    for ticket_number in range(1, num_tickets + 1):
        category = random.choices(
            list(CATEGORY_WEIGHTS.keys()),
            weights=list(CATEGORY_WEIGHTS.values()),
            k=1,
        )[0]
        priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS, k=1)[0]
        status = random.choices(STATUS_OPTIONS, weights=STATUS_WEIGHTS, k=1)[0]

        created_at = start_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(7, 18),
            minutes=random.randint(0, 59),
        )

        base_minutes = BASE_RESOLUTION_MINUTES[category] * PRIORITY_MULTIPLIER[priority]
        resolution_minutes = max(10, int(np.random.gamma(shape=2.0, scale=base_minutes / 2.0)))
        sla_target = SLA_TARGET_MINUTES[priority]

        if status in {"Open", "Pending Vendor", "Pending User"}:
            resolved_at = pd.NaT
            final_resolution_minutes = np.nan
            sla_met = np.nan
            customer_satisfaction = np.nan
        else:
            resolved_at = created_at + timedelta(minutes=resolution_minutes)
            final_resolution_minutes = resolution_minutes
            sla_met = resolution_minutes <= sla_target
            customer_satisfaction = random.choices([3, 4, 5], weights=[0.15, 0.35, 0.50], k=1)[0]
            if not sla_met:
                customer_satisfaction = max(1, customer_satisfaction - random.choice([1, 1, 2]))

        records.append(
            {
                "ticket_id": f"TKT-{ticket_number:05d}",
                "created_at": created_at,
                "resolved_at": resolved_at,
                "status": status,
                "priority": priority,
                "category": category,
                "subcategory": random.choice(CATEGORIES[category]),
                "channel": random.choice(CHANNELS),
                "site": random.choice(SITES),
                "assigned_group": random.choice(ASSIGNED_GROUPS),
                "resolution_minutes": final_resolution_minutes,
                "sla_target_minutes": sla_target,
                "sla_met": sla_met,
                "root_cause": random.choice(ROOT_CAUSES),
                "customer_satisfaction": customer_satisfaction,
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic IT support ticket data.")
    parser.add_argument("--tickets", type=int, default=500, help="Number of tickets to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", default="data/synthetic_it_tickets.csv", help="Output CSV path")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tickets = generate_tickets(num_tickets=args.tickets, seed=args.seed)
    tickets.to_csv(output_path, index=False)
    print(f"Generated {len(tickets)} synthetic tickets: {output_path}")


if __name__ == "__main__":
    main()
