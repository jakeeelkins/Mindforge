import requests
class SlackAdapter:
    def __init__(self, webhook_url: str | None):
        self.url = webhook_url
    def send(self, subject: str, body: str):
        if not self.url: return
        requests.post(self.url, json={"text": f"*{subject}*\n{body}"}, timeout=5)
