"""
Configuration centralisee pour l'application EchoLeak
"""
import os
import json


class Config:
    """Configuration de l'application"""

    # Ollama
    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3.2:3b"

    # IMAP (GreenMail)
    IMAP_HOST = "localhost"
    IMAP_PORT = 3143
    IMAP_USER = "awa.ndiaye@techsenegal.sn"
    IMAP_PASS = "password"

    # SMTP (GreenMail)
    SMTP_HOST = "localhost"
    SMTP_PORT = 3025

    # Flask
    HOST = "0.0.0.0"
    PORT = 8888
    DEBUG = False

    # Webhook
    WEBHOOK_URL = "http://localhost:5000"

    @classmethod
    def load_from_file(cls, config_path=None):
        """Charge la configuration depuis un fichier JSON"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)

                if "model" in data:
                    cls.MODEL = data["model"]
                if "ollama_url" in data:
                    cls.OLLAMA_URL = data["ollama_url"]
                if "imap_host" in data:
                    cls.IMAP_HOST = data["imap_host"]
                if "imap_port" in data:
                    cls.IMAP_PORT = data["imap_port"]
                if "smtp_host" in data:
                    cls.SMTP_HOST = data["smtp_host"]
                if "smtp_port" in data:
                    cls.SMTP_PORT = data["smtp_port"]
            except Exception as e:
                print(f"[!] Error loading config: {e}")

        return cls


def get_webhook_script_path():
    """Retourne le chemin vers le script webhook"""
    return os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "setup-configs",
        "webhook_server.py"
    )
