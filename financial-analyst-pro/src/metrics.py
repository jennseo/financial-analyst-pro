# src/metrics.py
import os, time, json

def append_run_metrics(readme_path: str, metrics: dict):
    try:
        with open(readme_path, "a", encoding="utf-8") as f:
            f.write("\n---\n")
            f.write("### Latest run metrics\n\n")
            f.write("```json\n")
            f.write(json.dumps(metrics, indent=2, ensure_ascii=False))
            f.write("\n```\n")
    except Exception:
        pass
