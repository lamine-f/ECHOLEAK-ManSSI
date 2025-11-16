#!/usr/bin/env python3
"""
EchoLeak Web Demo - Copilot Simulator
Refactored with layered architecture
"""
from flask import Flask
from config import Config, get_webhook_script_path
from app.services import (
    EmailService,
    LLMService,
    SMTPService,
    WebhookService,
    HealthService
)
from app.routes import create_main_blueprint, create_admin_blueprint


def create_app(config_path=None):
    """Application factory"""
    # Load configuration
    Config.load_from_file(config_path)

    # Create Flask app
    app = Flask(__name__)

    # Initialize services
    email_service = EmailService(
        host=Config.IMAP_HOST,
        port=Config.IMAP_PORT,
        username=Config.IMAP_USER,
        password=Config.IMAP_PASS
    )

    llm_service = LLMService(
        url=Config.OLLAMA_URL,
        model=Config.MODEL
    )

    smtp_service = SMTPService(
        host=Config.SMTP_HOST,
        port=Config.SMTP_PORT
    )

    webhook_service = WebhookService(
        script_path=get_webhook_script_path(),
        webhook_url=Config.WEBHOOK_URL
    )

    health_service = HealthService(
        email_service=email_service,
        llm_service=llm_service,
        webhook_service=webhook_service
    )

    # Register blueprints
    main_bp = create_main_blueprint(email_service, llm_service, health_service)
    admin_bp = create_admin_blueprint(email_service, smtp_service, webhook_service, health_service)

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app


def print_banner(model):
    """Print startup banner"""
    print(f"""
============================================================
           ECHOLEAK WEB DEMO - COPILOT SIMULATOR
============================================================
  Interface: http://localhost:{Config.PORT}
  Admin:     http://localhost:{Config.PORT}/admin
  Modele:    {model}
  Webhook:   {Config.WEBHOOK_URL}/history
============================================================
    """)


if __name__ == '__main__':
    app = create_app()
    print_banner(Config.MODEL)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True
    )
