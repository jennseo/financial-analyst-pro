# demo.py — CLI entry to run the agent and simulate automation + Notion export
import os
from src.utils import load_financial_csv, to_markdown_report, append_metrics_section
from src.agents import FinancialAnalysisAgent
from src.automation import simulate_make_n8n_job
from src.integrations.notion import create_page_markdown
from src.metrics import append_run_metrics

def main():
    df = load_financial_csv('data/sample.csv')
    agent = FinancialAnalysisAgent()
    analysis = agent.generate_report(df)

    report_md = to_markdown_report(analysis['kpis'], analysis['narrative'], analysis['recommendations'])
    report_md = append_metrics_section(report_md, analysis.get('metrics', {}))

    os.makedirs('outputs', exist_ok=True)
    with open('outputs/report.md', 'w', encoding='utf-8') as f:
        f.write(report_md)

    # Simulate automation (Slack/Make/n8n)
    ack = simulate_make_n8n_job(analysis)

    # Optional: Export to Notion if env is set
    notion_page = None
    parent_page_id = os.environ.get('NOTION_PARENT_PAGE_ID')
    if parent_page_id:
        notion_page = create_page_markdown(parent_page_id, title='Financial Analysis Report', markdown_text=report_md)

    # Append metrics to README
    append_run_metrics('README.md', analysis.get('metrics', {}))

    print('Report saved to outputs/report.md')
    print('Automation response:', ack)
    if notion_page:
        print('Notion response:', notion_page)

if __name__ == '__main__':
    main()
