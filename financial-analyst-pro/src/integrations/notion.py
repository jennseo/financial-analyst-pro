# src/integrations/notion.py
import os, requests, json

NOTION_API = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"

def create_page_markdown(parent_page_id: str, title: str, markdown_text: str) -> dict:
    """Create a Notion page under a parent page using the markdown in a code block.
    Requires NOTION_TOKEN env var.
    """
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        return {"status": 0, "error": "NOTION_TOKEN not set"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    # Minimal rich text: title + code block with markdown
    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]}
        },
        "children": [{
            "object": "block",
            "type": "code",
            "code": {
                "language": "markdown",
                "rich_text": [{"type": "text", "text": {"content": markdown_text[:1900]}}]
            }
        }]
    }
    try:
        r = requests.post(NOTION_API, headers=headers, data=json.dumps(payload), timeout=15)
        return {"status": r.status_code, "text": r.text[:800]}
    except Exception as e:
        return {"status": 0, "error": str(e)}
