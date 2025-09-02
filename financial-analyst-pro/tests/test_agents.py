# tests/test_agents.py
import pandas as pd
from src.agents import FinancialAnalysisAgent

def test_summarize_metrics():
    df = pd.DataFrame({
        "date": ["2024-01-01"],
        "revenue": [1000.0],
        "expenses": [400.0]
    })
    agent = FinancialAnalysisAgent()
    kpis = agent.summarize_metrics(df)
    assert round(kpis["profit_total"], 2) == 600.0
    assert round(kpis["margin_pct"], 1) == 60.0
