"""
Health check service for monitoring all services
"""
from ..models import ServiceStatus
from .email_service import EmailService
from .llm_service import LLMService
from .webhook_service import WebhookService


class HealthService:
    """Service for checking health of all services"""

    def __init__(
        self,
        email_service: EmailService,
        llm_service: LLMService,
        webhook_service: WebhookService
    ):
        self.email_service = email_service
        self.llm_service = llm_service
        self.webhook_service = webhook_service

    def check_all(self) -> ServiceStatus:
        """Check status of all services"""
        return ServiceStatus(
            ollama=self.llm_service.is_available(),
            imap=self.email_service.is_available(),
            webhook=self.webhook_service.is_running(),
            copilot=True,  # Always true since we're running
            model=self.llm_service.model
        )

    def check_public(self) -> dict:
        """Check only public services (for /api/status)"""
        return {
            "ollama": self.llm_service.is_available(),
            "imap": self.email_service.is_available(),
            "model": self.llm_service.model
        }
