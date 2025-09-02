from typing import Dict, Any
import os
import time
import pandas as pd

# Optional LangChain (real LLM path); kept optional to allow offline demo
LC_AVAILABLE = True
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except Exception:
    LC_AVAILABLE = False


class FinancialAnalysisAgent:
    """Production-minded agent that turns tabular financial data into structured insights.
    If OPENAI_API_KEY is set and LangChain is available, `llm_enrich` will call a real LLM.
    Otherwise it will gracefully fall back to a deterministic stub.
    """

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        self.model_name = model_name
        self.temperature = temperature

    def summarize_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if {"revenue", "expenses"}.issubset(df.columns):
            out["revenue_total"] = float(df["revenue"].sum())
            out["expenses_total"] = float(df["expenses"].sum())
            out["profit_total"] = out["revenue_total"] - out["expenses_total"]
            out["margin_pct"] = (
                (out["profit_total"] / out["revenue_total"] * 100.0)
                if out["revenue_total"] else 0.0
            )
        if "date" in df.columns:
            start = df["date"].min()
            end = df["date"].max()
            try:
                start_str = str(start.date())
                end_str = str(end.date())
            except Exception:
                start_str = str(start)
                end_str = str(end)
            out["period_start"] = start_str
            out["period_end"] = end_str
        return out

    def _stub_llm(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        narrative = (
            f"Sur la période {kpis.get('period_start')} → {kpis.get('period_end')}, "
            f"le chiffre d'affaires total est {kpis.get('revenue_total'):.2f}, "
            f"les dépenses {kpis.get('expenses_total'):.2f}, "
            f"soit un profit de {kpis.get('profit_total'):.2f} "
            f"et une marge de {kpis.get('margin_pct'):.1f}%."
        )
        recommendations = [
            "Prioriser les canaux à forte marge.",
            "Rationaliser les coûts variables.",
            "Automatiser un reporting hebdomadaire (Slack/Notion).",
        ]
        metrics = {
            "latency_ms": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "provider": "stub",
        }
        return {"narrative": narrative, "recommendations": recommendations, "metrics": metrics}

    def llm_enrich(self, kpis: Dict[str, Any]) -> Dict[str, Any]:
        # Fallback if no API key or LangChain unavailable
        if not (LC_AVAILABLE and os.environ.get("OPENAI_API_KEY")):
            return self._stub_llm(kpis)

        system = (
            "You are a senior financial analyst. Given KPIs, write a concise business narrative "
            "in French and 3 tactical recommendations for management. Keep it factual."
        )
        user = (
            "KPIs JSON:\n"
            f"{kpis}\n\n"
            "Write:\n- A 2-3 sentence narrative\n- 3 bullet recommendations"
        )

        prompt = ChatPromptTemplate.from_messages([("system", system), ("user", "{user}")])
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)

        t0 = time.time()
        resp = llm.invoke(prompt.format(user=user))
        dt = int((time.time() - t0) * 1000)

        # Token usage when available
        usage = getattr(resp, "usage_metadata", None)
        tokens_in = usage.get("input_tokens") if usage else 0
        tokens_out = usage.get("output_tokens") if usage else 0

        text = resp.content if hasattr(resp, "content") else str(resp)

        # Heuristic split for narrative vs recommendations
        parts = [p.strip() for p in text.split("\n") if p.strip()]
        narrative_lines = []
        recs = []
        for line in parts:
            bullet = line.lstrip("-•* ").strip()
            if len(narrative_lines) < 2 and not line.startswith(("-", "•", "*")):
                narrative_lines.append(bullet)
            else:
                recs.append(bullet)
        if not recs:
            recs = [
                "Optimiser le mix produit.",
                "Améliorer la prévision de trésorerie.",
                "Accélérer le cycle de vente.",
            ]

        metrics = {
            "latency_ms": dt,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "provider": "openai+langchain",
        }
        return {"narrative": " ".join(narrative_lines)[:1000], "recommendations": recs[:3], "metrics": metrics}

    def generate_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        kpis = self.summarize_metrics(df)
        enriched = self.llm_enrich(kpis)
        return {"kpis": kpis, **enriched}
