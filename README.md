# IT Support Ticket Analysis

A simulated IT support ticket analysis project using Python to explore help desk workload, issue categories, SLA performance, resolution time, and support trends.

This project is designed as a portfolio project to connect practical IT support experience with data analysis and reporting skills.

## Project Purpose

In IT support environments, ticket data can help teams understand:

- What types of issues occur most often
- Which categories take the longest to resolve
- Whether support requests are meeting SLA targets
- Which sites or channels generate the most tickets
- How workload changes over time
- Where documentation, training, or process improvements may be needed

This project uses synthetic help desk ticket data to demonstrate how Python can support practical IT operations reporting.

## Key Questions

This project aims to answer questions such as:

- What are the most common IT support issue categories?
- How many tickets are resolved within SLA?
- Which priority levels have the longest average resolution time?
- Are network, hardware, account, printer, or CCTV issues increasing over time?
- Which support areas may need more documentation or process improvement?

## Dataset

The dataset is fully synthetic and does not contain any real company, customer, employee, or ticket information.

The generated dataset includes fields such as:

- `ticket_id`
- `created_at` and `resolved_at`
- `status`
- `priority`
- `category` and `subcategory`
- `channel`
- `site`
- `assigned_group`
- `resolution_minutes`
- `sla_target_minutes`
- `sla_met`
- `root_cause`
- `customer_satisfaction`

Example ticket categories include network, hardware, software, account, printer, CCTV, and security issues.

## Project Structure

```text
it-support-ticket-analysis/
├── app.py                         # Streamlit dashboard
├── data/                          # Generated synthetic dataset appears here
├── output/                        # Analysis summary tables appear here
├── src/
│   ├── generate_tickets.py         # Synthetic ticket data generator
│   └── analysis.py                 # Summary analysis script
├── requirements.txt
├── .gitignore
└── README.md
```

## Tech Stack

- Python
- pandas
- numpy
- Plotly
- Streamlit
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/MichaelSai103/it-support-ticket-analysis.git
cd it-support-ticket-analysis
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate synthetic ticket data

```bash
python src/generate_tickets.py
```

This creates:

```text
data/synthetic_it_tickets.csv
```

You can also change the number of tickets:

```bash
python src/generate_tickets.py --tickets 1000
```

### 5. Run the analysis script

```bash
python src/analysis.py
```

This prints key findings and saves summary tables to:

```text
output/
```

### 6. Launch the dashboard

```bash
streamlit run app.py
```

## Planned Dashboard Views

The Streamlit dashboard includes:

- Total ticket volume
- Open / pending ticket count
- SLA met rate
- Average resolution time
- Ticket volume by category
- Ticket volume by priority
- Monthly ticket trends
- Average resolution time by category
- Filterable ticket sample table

## Portfolio Relevance

This project demonstrates a combination of:

- IT support process understanding
- Troubleshooting category analysis
- SLA and service performance reporting
- Python data analysis
- Dashboard development
- Clear technical documentation

It is especially relevant to IT Support, Desktop Support, Field IT Support, Junior Network Support, Technical Support, and junior data-focused roles where operational reporting and troubleshooting analysis are useful.

## Project Status

Initial project structure completed. Next steps:

- Add screenshots of the Streamlit dashboard
- Add more detailed business insights
- Add optional Power BI version
- Add a short portfolio case study summary
