from datetime import datetime
class ConsoleAdapter:
    def send(self, subject: str, body: str):
        print(f"[{datetime.utcnow().isoformat()}] {subject}\n{body}\n")
