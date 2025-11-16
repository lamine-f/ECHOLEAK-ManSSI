"""
Webhook service for managing the exfiltration server subprocess
"""
import subprocess
import threading
import queue
import requests
from typing import List, Dict, Any, Optional


class WebhookService:
    """Service for managing webhook subprocess"""

    def __init__(self, script_path: str, webhook_url: str = "http://localhost:5000"):
        self.script_path = script_path
        self.webhook_url = webhook_url
        self.process: Optional[subprocess.Popen] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.logs: List[str] = []
        self._reader_thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        """Check if webhook process is running"""
        return self.process is not None and self.process.poll() is None

    def start(self) -> int:
        """Start the webhook server, returns PID"""
        if self.is_running():
            raise Exception("Webhook already running")

        # Clear logs
        self.logs = []

        # Start process
        self.process = subprocess.Popen(
            ["python", self.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=False
        )

        # Start reader thread
        self._reader_thread = threading.Thread(
            target=self._read_output,
            daemon=True
        )
        self._reader_thread.start()

        return self.process.pid

    def stop(self) -> None:
        """Stop the webhook server"""
        if not self.is_running():
            raise Exception("Webhook not running")

        self.process.terminate()
        self.process.wait(timeout=5)
        self.process = None

    def _read_output(self) -> None:
        """Thread function to read process output"""
        if self.process and self.process.stdout:
            for line in iter(self.process.stdout.readline, b''):
                self.output_queue.put(line.decode('utf-8', errors='ignore'))
            self.process.stdout.close()

    def get_logs(self, max_lines: int = 100) -> List[str]:
        """Get current logs from the webhook process"""
        # Read new output from queue
        while not self.output_queue.empty():
            try:
                line = self.output_queue.get_nowait()
                self.logs.append(line)
                # Keep only last max_lines
                if len(self.logs) > max_lines:
                    self.logs = self.logs[-max_lines:]
            except queue.Empty:
                break

        return self.logs

    def get_history(self) -> Dict[str, Any]:
        """Get exfiltration history from webhook server"""
        try:
            r = requests.get(f"{self.webhook_url}/history", timeout=2)
            return r.json()
        except Exception as e:
            return {
                "error": str(e),
                "total_leaks": 0,
                "data": []
            }

    def clear_history(self) -> Dict[str, Any]:
        """Clear exfiltration history"""
        try:
            r = requests.post(f"{self.webhook_url}/clear", timeout=2)
            return r.json()
        except Exception as e:
            return {"error": str(e)}
