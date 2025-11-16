"""
Email service for IMAP operations
"""
import imaplib
import email
from typing import List


class EmailService:
    """Service for IMAP email operations"""

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def fetch_all_emails(self) -> List[str]:
        """Fetch all emails from inbox and return their content"""
        emails_content = []

        try:
            mail = imaplib.IMAP4(self.host, self.port)
            mail.login(self.username, self.password)
            mail.select("INBOX")

            status, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()

            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        body = self._extract_body(msg)
                        if body:
                            emails_content.append(body)

            mail.logout()
        except Exception as e:
            print(f"[!] IMAP Error: {e}")

        return emails_content

    def _extract_body(self, msg) -> str:
        """Extract body from email message"""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type in ["text/plain", "text/html"]:
                    try:
                        return part.get_payload(decode=True).decode()
                    except Exception:
                        pass
        else:
            try:
                return msg.get_payload(decode=True).decode()
            except Exception:
                pass
        return ""

    def purge_inbox(self) -> int:
        """Delete all emails from inbox, returns count of deleted emails"""
        deleted_count = 0

        try:
            mail = imaplib.IMAP4(self.host, self.port)
            mail.login(self.username, self.password)
            mail.select("INBOX")

            status, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()

            for email_id in email_ids:
                mail.store(email_id, '+FLAGS', '\\Deleted')
                deleted_count += 1

            mail.expunge()
            mail.logout()
        except Exception as e:
            raise Exception(f"Failed to purge emails: {e}")

        return deleted_count

    def is_available(self) -> bool:
        """Check if IMAP server is available"""
        try:
            mail = imaplib.IMAP4(self.host, self.port)
            mail.logout()
            return True
        except Exception:
            return False
