# src/utils.py
import pandas as pd
from typing import Optional

def load_financial_csv(path: str, date_col: Optional[str] = "date") -> pd.DataFrame:
    df = pd.read_csv(path)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    return df

def to_markdown_report(kpis: dict, narrative: str, recommendations: list) -> str:
    lines = [
        "# Financial Analysis Report\n",
        "## KPIs\n",
        f"- Revenue total: {kpis.get('revenue_total'):.2f}",
        f"- Expenses total: {kpis.get('expenses_total'):.2f}",
        f"- Profit total: {kpis.get('profit_total'):.2f}",
        f"- Margin: {kpis.get('margin_pct'):.1f}%\n",
        "## Narrative\n",
        narrative + "\n",
        "## Recommendations\n",
    ]
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")
    return "\n".join(lines) + "\n"

def append_metrics_section(markdown_text: str, metrics: dict) -> str:
    if not metrics:
        return markdown_text
    lines = [markdown_text, "", "## Metrics", ""]
    for k, v in metrics.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    return "\n".join(lines)
