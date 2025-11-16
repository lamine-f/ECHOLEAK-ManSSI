"""
Data models for email and service status
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class EmailMessage:
    """Represents an email message"""
    sender: str
    subject: str
    body: str
    is_html: bool = False


@dataclass
class ServiceStatus:
    """Status of all services"""
    ollama: bool = False
    imap: bool = False
    webhook: bool = False
    copilot: bool = True
    model: str = ""


@dataclass
class WebhookLog:
    """A single webhook log entry"""
    timestamp: str
    ip: str
    method: str
    data: Dict[str, Any]


@dataclass
class EmailTemplate:
    """Template for setup emails"""
    sender: str
    subject: str
    body: str
    is_html: bool = False
