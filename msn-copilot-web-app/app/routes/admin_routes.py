"""
Admin routes for controlling the demo
"""
from flask import Blueprint, render_template, jsonify
from ..services import EmailService, SMTPService, WebhookService, HealthService
from dataclasses import asdict


def create_admin_blueprint(
    email_service: EmailService,
    smtp_service: SMTPService,
    webhook_service: WebhookService,
    health_service: HealthService
) -> Blueprint:
    """Create admin routes blueprint with injected services"""

    bp = Blueprint('admin', __name__, url_prefix='/admin')

    @bp.route('')
    def admin_page():
        """Admin control panel"""
        return render_template('admin.html')

    @bp.route('/status', methods=['GET'])
    def admin_status():
        """Complete status of all services"""
        status = health_service.check_all()
        return jsonify(asdict(status))

    @bp.route('/emails/send', methods=['POST'])
    def send_setup_emails():
        """Send all setup emails"""
        recipient = email_service.username
        results = smtp_service.send_setup_emails(recipient)
        return jsonify(results)

    @bp.route('/emails/purge', methods=['POST'])
    def purge_emails():
        """Purge all emails from inbox"""
        try:
            deleted = email_service.purge_inbox()
            return jsonify({"success": True, "deleted": deleted})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @bp.route('/webhook/start', methods=['POST'])
    def start_webhook():
        """Start webhook server"""
        try:
            pid = webhook_service.start()
            return jsonify({"success": True, "pid": pid})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @bp.route('/webhook/stop', methods=['POST'])
    def stop_webhook():
        """Stop webhook server"""
        try:
            webhook_service.stop()
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @bp.route('/webhook/logs', methods=['GET'])
    def get_webhook_logs():
        """Get webhook process logs"""
        logs = webhook_service.get_logs()
        return jsonify({"logs": logs})

    @bp.route('/webhook/history', methods=['GET'])
    def get_webhook_history():
        """Get exfiltration history"""
        return jsonify(webhook_service.get_history())

    @bp.route('/webhook/clear', methods=['POST'])
    def clear_webhook_history():
        """Clear exfiltration history"""
        return jsonify(webhook_service.clear_history())

    return bp
